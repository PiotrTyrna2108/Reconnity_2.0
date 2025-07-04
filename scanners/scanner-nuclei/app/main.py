import subprocess
import json
import os
import time
import logging
import httpx
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ARQ Redis settings from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CORE_URL = os.getenv("CORE_URL", "http://core:8001")

# Parse Redis URL
def parse_redis_url(url: str):
    """Parsuje URL Redis na komponenty wymagane przez ARQ RedisSettings"""
    if url.startswith("redis://"):
        url = url[len("redis://"):]
    
    host_port, *rest = url.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 6379
        
    db = int(rest[0]) if rest else 0
    
    return RedisSettings(
        host=host,
        port=port,
        database=db
    )

async def run_nuclei_scan(ctx: Dict, scan_id: str, target: str, options: Dict[str, Any] = None):
    """
    Główna funkcja wykonująca skan podatności z nuclei.
    Nuclei to skaner podatności używający szablonów do wykrywania problemów bezpieczeństwa.
    """
    logger.info(f"[NUCLEI] Starting vulnerability scan for {target} (id={scan_id})")
    
    if options is None:
        options = {}
    
    try:
        # Zbuduj komendę nuclei z parametrami skanowania podatności
        nuclei_args = build_nuclei_command(target, options)
        logger.info(f"[NUCLEI] Running command: {' '.join(nuclei_args)}")
        
        # Wykonaj skan nuclei
        start_time = time.time()
        process = subprocess.run(
            nuclei_args,
            capture_output=True,
            text=True,
            timeout=int(options.get("timeout", 600))  # timeout w sekundach
        )
        scan_duration = time.time() - start_time
        logger.info(f"[NUCLEI] Scan finished in {scan_duration:.2f} seconds with return code {process.returncode}")
        
        if process.returncode == 0 or process.stdout:  # Sprawdź czy mamy wynik nawet przy błędzie
            # Parsuj wyjście nuclei do struktury danych
            logger.info(f"[NUCLEI] Got output of {len(process.stdout)} bytes")
            if len(process.stdout) > 100:
                logger.info(f"[NUCLEI] Sample output: {process.stdout[:100]}...")
            else:
                logger.info(f"[NUCLEI] Complete output: {process.stdout}")
                
            scan_results = parse_nuclei_output(process.stdout, target, scan_id, scan_duration)
            logger.info(f"[NUCLEI] Scan completed successfully: {scan_id}")
            
            # Wyślij wyniki do serwisu core przez Redis
            await report_scan_completion(ctx, scan_id, scan_results)
        else:
            error_msg = f"Nuclei scan failed with return code {process.returncode}: {process.stderr}"
            logger.error(f"[NUCLEI] {error_msg}")
            # Loguj więcej szczegółów o błędzie
            logger.error(f"[NUCLEI] Stdout: {process.stdout}")
            logger.error(f"[NUCLEI] Stderr: {process.stderr}")
            await report_scan_failure(ctx, scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Nuclei scan timed out after specified timeout"
        logger.error(f"[NUCLEI] {error_msg}")
        await report_scan_failure(ctx, scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during nuclei scan: {str(e)}"
        logger.error(f"[NUCLEI] {error_msg}")
        import traceback
        logger.error(f"[NUCLEI] Exception traceback: {traceback.format_exc()}")
        await report_scan_failure(ctx, scan_id, error_msg)


def build_nuclei_command(target: str, options: Dict[str, Any]) -> list:
    """Buduje komendę nuclei z odpowiednimi flagami do skanowania podatności"""
    cmd = ["nuclei"]
    
    # Specyfikacja celu
    cmd.extend(["-target", target])
    
    # Format wyjścia
    cmd.extend(["-jsonl", "-silent"])  # JSON bez banera
    
    # Ograniczenie szybkości
    rate = options.get("rate", "150")  # żądań na sekundę
    cmd.extend(["-rate-limit", str(rate)])
    
    # Filtrowanie według ważności
    severity = options.get("severity", ["critical", "high", "medium"])
    if severity:
        # Obsłuż zarówno listę jak i string
        if isinstance(severity, list):
            severity_str = ",".join(severity)
        else:
            severity_str = severity
        cmd.extend(["-severity", severity_str])
    
    # Wybór szablonów z jawną ścieżką
    templates_dir = "/root/nuclei-templates"
    templates_type = options.get("templates", ["cves"])
    if templates_type:
        # Obsłuż zarówno listę jak i string
        if isinstance(templates_type, list):
            template_list = templates_type
        else:
            template_list = templates_type.split(",")
        
        # Dla każdego typu szablonu, skonstruuj pełną ścieżkę
        template_paths = []
        for t_type in template_list:
            t_type = t_type.strip()
            # Jeśli to już pełna ścieżka, użyj tak jak jest
            if t_type.startswith("/"):
                template_paths.append(t_type)
            # Jeśli to relatywna ścieżka zaczynająca się od nazwy katalogu szablonów
            elif t_type.startswith("http/") or t_type.startswith("dns/") or t_type.startswith("file/"):
                template_paths.append(f"{templates_dir}/{t_type}")
            # W przeciwnym razie, załóż że to kategoria w katalogu szablonów
            else:
                template_paths.append(f"{templates_dir}/{t_type}")
        
        if template_paths:
            cmd.extend(["-t", ",".join(template_paths)])
    
    # Współbieżność
    concurrency = options.get("concurrency", "25")
    cmd.extend(["-c", str(concurrency)])
    
    # Ponowne próby
    retries = options.get("retries", "1")
    cmd.extend(["-retries", str(retries)])
    
    # Ustawienia timeout
    timeout_seconds = options.get("timeout", "5")  # Timeout żądania w sekundach
    cmd.extend(["-timeout", f"{timeout_seconds}"])
    
    # Szczegółowy output
    if options.get("verbose", False):
        cmd.append("-v")
    
    # Śledź przekierowania
    follow_redirects = options.get("follow_redirects")
    if follow_redirects is not None:
        cmd.extend(["-follow-redirects" if follow_redirects else "-no-redirects"])
    
    # Maksymalne błędy hosta
    max_host_error = options.get("max_host_error")
    if max_host_error is not None:
        cmd.extend(["-max-host-error", str(max_host_error)])
    
    return cmd


def parse_nuclei_output(json_output: str, target: str, scan_id: str, duration: float) -> Dict[str, Any]:
    """Parsuje wyjście JSON z nuclei i wyciąga informacje o podatnościach"""
    try:
        # Obsłuż przypadek gdy nuclei nie zwrócił żadnych wyników
        if not json_output.strip():
            logger.warning(f"[NUCLEI] No output for {target}")
            return {
                "scanner": "nuclei",
                "target": target,
                "scan_id": scan_id,
                "scan_duration": duration,
                "timestamp": time.time(),
                "vulnerabilities": [],
                "stats": {
                    "hosts_found": 0,
                    "total_findings": 0,
                    "processed_lines": 0,
                    "error_count": 0
                }
            }
        
        # Parsuj wyjście JSONL (jeden obiekt JSON na linię)
        results = {
            "scanner": "nuclei",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "vulnerabilities": [],
            "stats": {
                "hosts_found": 0,
                "total_findings": 0,
                "processed_lines": 0,
                "error_count": 0,
                "risk_score": 0
            }
        }
        
        finding_count = 0
        error_count = 0
        
        for line_num, line in enumerate(json_output.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            
            finding_count += 1
            
            try:
                finding = json.loads(line)
                vuln = {
                    "id": finding.get("template-id", "unknown"),
                    "name": finding.get("info", {}).get("name", "Unknown Vulnerability"),
                    "severity": finding.get("info", {}).get("severity", "unknown"),
                    "description": finding.get("info", {}).get("description", "No description"),
                    "url": finding.get("matched-at", target),
                    "details": finding,
                    "timestamp": time.time()
                }
                
                results["vulnerabilities"].append(vuln)
                logger.info(f"[NUCLEI] Found vulnerability: {vuln['name']} (severity: {vuln['severity']})")
                    
            except json.JSONDecodeError as e:
                error_count += 1
                logger.warning(f"[NUCLEI] Failed to parse JSON line {line_num}: {line[:100]}... - {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.warning(f"[NUCLEI] Error processing finding on line {line_num}: {str(e)}")
                continue
        
        # Aktualizuj statystyki
        results["stats"]["hosts_found"] = 1  # Skanujemy pojedynczy cel
        results["stats"]["total_findings"] = len(results["vulnerabilities"])
        results["stats"]["error_count"] = error_count
        results["stats"]["processed_lines"] = finding_count
        
        # Oblicz czynniki ryzyka
        if results["vulnerabilities"]:
            risk_factors = calculate_risk_factors(results["vulnerabilities"])
            results["stats"].update(risk_factors)
        
        return results
        
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to parse output: {e}")
        # Zwróć podstawowe wyniki jeśli parsowanie się nie udało
        return {
            "scanner": "nuclei",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "vulnerabilities": [],
            "stats": {
                "hosts_found": 0,
                "total_findings": 0,
                "error_count": 1,
                "processed_lines": 0
            },
            "raw_output_sample": json_output[:500] if json_output else "No output",
            "parse_error": str(e)
        }


def calculate_risk_factors(vulnerabilities: List[Dict[str, Any]]) -> Dict[str, float]:
    """Oblicza czynniki ryzyka na podstawie znalezionych podatności"""
    # Wagi ważności dla kalkulacji ryzyka
    severity_weights = {
        "critical": 10.0,
        "high": 7.5,
        "medium": 5.0,
        "low": 2.5,
        "info": 0.5,
        "unknown": 1.0
    }
    
    # Policz podatności według ważności
    severity_counts = {k: 0 for k in severity_weights.keys()}
    
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "unknown").lower()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Oblicz wynik ryzyka (suma ważona)
    risk_score = sum(severity_counts[sev] * severity_weights[sev] for sev in severity_counts)
    
    return {
        "risk_score": risk_score,
        "severity_counts": severity_counts
    }


async def report_scan_completion(ctx: Dict, scan_id: str, results: Dict[str, Any]):
    """Wysyła wyniki ukończonego skanu podatności do serwisu core przez kolejkę Redis"""
    try:
        # Wyślij wiadomość z wynikami skanu do kolejki core
        redis_pool = ctx.get('redis') or await create_pool(parse_redis_url(REDIS_URL))
        await redis_pool.enqueue_job(
            'process_scan_result',
            scan_id=scan_id,
            status='completed',
            results=results,
            scanner='nuclei',
            _queue_name='core'
        )
        logger.info(f"[NUCLEI] Scan completion message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to send completion message: {e}")


async def report_scan_failure(ctx: Dict, scan_id: str, error: str):
    """Wysyła informację o błędzie skanu podatności do serwisu core przez kolejkę Redis"""
    try:
        # Wyślij wiadomość o błędzie skanu do kolejki core
        redis_pool = ctx.get('redis') or await create_pool(parse_redis_url(REDIS_URL))
        await redis_pool.enqueue_job(
            'process_scan_result',
            scan_id=scan_id,
            status='failed',
            error=error,
            scanner='nuclei',
            _queue_name='core'
        )
        logger.info(f"[NUCLEI] Scan failure message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[NUCLEI] Failed to send failure message: {e}")


class WorkerSettings:
    """Konfiguracja ARQ worker'a dla skannera nuclei - obsługuje skanowanie podatności"""
    functions = [run_nuclei_scan]
    redis_settings = parse_redis_url(REDIS_URL)
    queue_name = 'scanner-nuclei'


if __name__ == "__main__":
    logger.info("[NUCLEI] Starting Nuclei vulnerability scanner service with ARQ...")
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        import asyncio
        from arq.worker import Worker
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                Worker(WorkerSettings).run()
            )
        except KeyboardInterrupt:
            pass