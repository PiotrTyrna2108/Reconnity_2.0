from celery import Celery
import subprocess
import json
import os
import time
import logging
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("scanner_nuclei", broker=broker_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")

@celery_app.task(name="scanner-nuclei.run", bind=True)
def run_nuclei_scan(self, scan_id: str, target: str, options: Dict[str, Any] = None):
    """
    Execute nuclei vulnerability scan for given target
    """
    logger.info(f"[NUCLEI] Starting vulnerability scan for {target} (id={scan_id})")
    
    if options is None:
        options = {}
    
    try:
        # Build nuclei command
        nuclei_args = build_nuclei_command(target, options)
        logger.info(f"[NUCLEI] Running command: {' '.join(nuclei_args)}")
        
        # Execute nuclei scan
        start_time = time.time()
        result = subprocess.run(
            nuclei_args,
            capture_output=True,
            text=True,
            timeout=int(options.get("timeout", 600))  # timeout in seconds
        )
        scan_duration = time.time() - start_time
        logger.info(f"[NUCLEI] Scan finished in {scan_duration:.2f} seconds with return code {result.returncode}")
        
        if result.returncode == 0 or result.stdout:  # Check if we have output even with non-zero return code
            # Parse nuclei output
            logger.info(f"[NUCLEI] Got output of {len(result.stdout)} bytes")
            if len(result.stdout) > 100:
                logger.info(f"[NUCLEI] Sample output: {result.stdout[:100]}...")
            else:
                logger.info(f"[NUCLEI] Complete output: {result.stdout}")
                
            scan_results = parse_nuclei_output(result.stdout, target, scan_id, scan_duration)
            logger.info(f"[NUCLEI] Scan completed successfully: {scan_id}")
            
            # Report results to core service
            report_scan_completion(scan_id, scan_results)
        else:
            error_msg = f"Nuclei scan failed with return code {result.returncode}: {result.stderr}"
            logger.error(f"[NUCLEI] {error_msg}")
            # Log more details about the error
            logger.error(f"[NUCLEI] Stdout: {result.stdout}")
            logger.error(f"[NUCLEI] Stderr: {result.stderr}")
            report_scan_failure(scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Nuclei scan timed out after specified timeout"
        logger.error(f"[NUCLEI] {error_msg}")
        report_scan_failure(scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during nuclei scan: {str(e)}"
        logger.error(f"[NUCLEI] {error_msg}")
        import traceback
        logger.error(f"[NUCLEI] Exception traceback: {traceback.format_exc()}")
        report_scan_failure(scan_id, error_msg)

def build_nuclei_command(target: str, options: Dict[str, Any]) -> list:
    """Build nuclei command with appropriate flags"""
    cmd = ["nuclei"]
    
    # Target specification
    cmd.extend(["-target", target])
    
    # Output format
    cmd.extend(["-jsonl", "-silent"])  # JSON output without banner
    
    # Rate limiting
    rate = options.get("rate", "150")  # requests per second
    cmd.extend(["-rate-limit", str(rate)])
    
    # Severity filtering
    severity = options.get("severity", "critical,high,medium")
    if severity:
        cmd.extend(["-severity", severity])
    
    # Template selection with explicit path
    templates_dir = "/root/.config/nuclei/templates"
    templates_type = options.get("templates", "cves")
    if templates_type:
        # For each template type, construct full path
        template_paths = []
        for t_type in templates_type.split(","):
            template_paths.append(f"{templates_dir}/{t_type}")
        
        cmd.extend(["-t", ",".join(template_paths)])
    
    # Other optional parameters
    if options.get("timeout"):
        cmd.extend(["-timeout", str(options["timeout"])])
    
    # Concurrent executions
    concurrency = options.get("concurrency", "25")
    cmd.extend(["-c", str(concurrency)])
    
    return cmd

def parse_nuclei_output(json_output: str, target: str, scan_id: str, duration: float) -> Dict[str, Any]:
    """Parse nuclei JSON output and extract relevant information"""
    try:
        results = {
            "scanner": "nuclei",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "vulnerabilities": [],
            "raw_output": json_output[:5000] if len(json_output) > 5000 else json_output,  # Include truncated raw output for debugging
            "stats": {
                "templates_executed": 0,
                "hosts_found": 0,
                "total_findings": 0
            }
        }
        
        # If output is empty, return basic results
        if not json_output or json_output.strip() == "":
            logger.warning(f"[NUCLEI] Empty output received for scan {scan_id}")
            return results
        
        # Check if output might not be JSON
        if json_output.startswith("[") and "]" in json_output and not json_output.startswith("[{"):
            # This might be a regular non-JSON output, try to extract meaningful data
            logger.warning(f"[NUCLEI] Output doesn't appear to be in JSON format: {json_output[:100]}...")
            
            # Add a simple finding for non-JSON output
            results["vulnerabilities"].append({
                "name": "Nuclei Scan Completed",
                "severity": "info",
                "type": "info",
                "host": target,
                "matched_at": target,
                "description": "Scan completed but output wasn't in expected JSON format",
                "raw_output": json_output[:1000] if len(json_output) > 1000 else json_output,
            })
            results["stats"]["total_findings"] = 1
            return results
        
        # Parse JSON lines (nuclei outputs one JSON object per line)
        finding_count = 0
        valid_findings = 0
        error_count = 0
        
        for line_num, line in enumerate(json_output.strip().split('\n')):
            if not line.strip():
                continue
                
            try:
                logger.info(f"[NUCLEI] Processing line {line_num}: {line[:100]}...")
                finding = json.loads(line)
                finding_count += 1
                
                # Check if this is a statistics record rather than a finding
                if "stats" in finding and "templates" in finding.get("stats", {}):
                    logger.info(f"[NUCLEI] Found statistics record: {finding.get('stats', {})}")
                    results["stats"]["templates_executed"] = finding.get("stats", {}).get("templates", {}).get("total", 0)
                    continue
                
                # Process findings - be more flexible with format
                vuln = {
                    "name": "Unknown",
                    "severity": "unknown",
                    "type": "unknown",
                    "host": target,
                    "matched_at": "",
                    "description": "",
                    "cve_ids": [],
                    "tags": [],
                    "timestamp": time.time(),
                }
                
                # Try to extract data using multiple possible schemas
                if "info" in finding:
                    info = finding.get("info", {})
                    vuln["name"] = info.get("name", "Unknown")
                    vuln["severity"] = info.get("severity", "unknown")
                    vuln["description"] = info.get("description", "")
                    vuln["cve_ids"] = info.get("reference", [])
                    vuln["tags"] = info.get("tags", [])
                
                if "host" in finding:
                    vuln["host"] = finding.get("host", "")
                
                if "matched-at" in finding:
                    vuln["matched_at"] = finding.get("matched-at", "")
                elif "matched" in finding:
                    vuln["matched_at"] = finding.get("matched", "")
                
                if "type" in finding:
                    vuln["type"] = finding.get("type", "unknown")
                    
                if "timestamp" in finding:
                    vuln["timestamp"] = finding.get("timestamp", "")
                    
                # Add the vulnerability to results
                results["vulnerabilities"].append(vuln)
                results["stats"]["total_findings"] += 1
                valid_findings += 1
                logger.info(f"[NUCLEI] Found vulnerability: {vuln['name']} (severity: {vuln['severity']})")
                    
            except json.JSONDecodeError as e:
                error_count += 1
                logger.warning(f"[NUCLEI] Failed to parse JSON line {line_num}: {line[:100]}... - {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.warning(f"[NUCLEI] Error processing finding on line {line_num}: {str(e)}")
                continue
        
        # Update stats
        results["stats"]["hosts_found"] = 1  # Since we're scanning a single target
        results["stats"]["total_findings"] = len(results["vulnerabilities"])
        results["stats"]["error_count"] = error_count
        results["stats"]["processed_lines"] = finding_count
        
        # Log summary of findings
        if results["vulnerabilities"]:
            logger.info(f"[NUCLEI] Found {len(results['vulnerabilities'])} vulnerabilities for target {target}")
        else:
            logger.info(f"[NUCLEI] No vulnerabilities found for target {target}")
            
        # Calculate risk score based on vulnerabilities
        results["risk_factors"] = calculate_risk_factors(results["vulnerabilities"])
        
        # Add scan metadata
        results["metadata"] = {
            "valid_findings": valid_findings,
            "error_count": error_count,
            "processed_lines": finding_count,
            "output_size": len(json_output),
        }
        
        return results
        
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to parse output: {e}")
        import traceback
        logger.error(f"[NUCLEI] Exception traceback: {traceback.format_exc()}")
        
        # Return basic results with error information
        return {
            "scanner": "nuclei",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "error": str(e),
            "vulnerabilities": [],
            "stats": {
                "templates_executed": 0,
                "hosts_found": 0,
                "total_findings": 0,
                "error": True
            }
        }
        import traceback
        logger.error(f"[NUCLEI] Exception traceback: {traceback.format_exc()}")
        # Return basic results if parsing fails
        return {
            "scanner": "nuclei",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "vulnerabilities": [],
            "raw_output_sample": json_output[:500] if json_output else "No output",
            "parse_error": str(e)
        }

def calculate_risk_factors(vulnerabilities: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate risk factors based on vulnerability findings"""
    risk_factors = {
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "info_count": 0,
        "has_cve": False,
        "exposed_services": False,
        "misconfigurations": False
    }
    
    # Count vulnerabilities by severity
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "").lower()
        if severity == "critical":
            risk_factors["critical_count"] += 1
        elif severity == "high":
            risk_factors["high_count"] += 1
        elif severity == "medium":
            risk_factors["medium_count"] += 1
        elif severity == "low":
            risk_factors["low_count"] += 1
        elif severity == "info":
            risk_factors["info_count"] += 1
        
        # Check for CVEs
        if vuln.get("cve_ids") or "cve" in vuln.get("name", "").lower():
            risk_factors["has_cve"] = True
        
        # Check for exposed services
        tags = vuln.get("tags", [])
        if any(tag in ["exposed", "exposure", "open-service"] for tag in tags):
            risk_factors["exposed_services"] = True
        
        # Check for misconfigurations
        if any(tag in ["misconfiguration", "config", "default-config"] for tag in tags):
            risk_factors["misconfigurations"] = True
    
    return risk_factors

def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        logger.info(f"[NUCLEI] Reporting scan completion for {scan_id} to {CORE_URL}/api/v1/scan/{scan_id}/complete")
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/complete",
            json=results,
            timeout=10
        )
        logger.info(f"[NUCLEI] Response status code: {response.status_code}")
        response.raise_for_status()
        logger.info(f"[NUCLEI] Scan completion reported successfully: {scan_id}")
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to report completion: {e}")
        if hasattr(e, "response") and e.response:
            logger.error(f"[NUCLEI] Response content: {e.response.content}")

def report_scan_failure(scan_id: str, error: str):
    """Report scan failure to core service"""
    try:
        logger.info(f"[NUCLEI] Reporting scan failure for {scan_id} to {CORE_URL}/api/v1/scan/{scan_id}/fail")
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/fail",
            json={"error": error},
            timeout=10
        )
        logger.info(f"[NUCLEI] Response status code: {response.status_code}")
        response.raise_for_status()
        logger.info(f"[NUCLEI] Scan failure reported successfully: {scan_id}")
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to report failure: {e}")
        if hasattr(e, "response") and e.response:
            logger.error(f"[NUCLEI] Response content: {e.response.content}")

if __name__ == "__main__":
    logger.info("[NUCLEI] Starting Nuclei vulnerability scanner service...")
    celery_app.start()
