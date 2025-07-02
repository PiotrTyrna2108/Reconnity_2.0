#!/usr/bin/env python3
"""
EASM CLI - Command Line Interface for EASM Microservices
"""

import click
import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8080/api/v1"

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """EASM CLI - External Attack Surface Management"""
    pass

@cli.command()
@click.argument("target")
@click.option("--scanner", "-s", default="nmap", help="Scanner type (nmap, masscan)")
@click.option("--ports", "-p", help="Port range (e.g., '22,80,443' or '1-1000')")
@click.option("--timing", "-T", type=int, help="Timing template (0-5)")
@click.option("--aggressive", "-A", is_flag=True, help="Enable aggressive scanning")
@click.option("--wait", "-w", is_flag=True, help="Wait for scan completion")
@click.option("--format", "-f", type=click.Choice(['json', 'table']), default='table', help="Output format")
def scan(target, scanner, ports, timing, aggressive, wait, format):
    """Create a new scan for TARGET"""
    
    options = {}
    if ports:
        options["ports"] = ports
    if timing is not None:
        options["timing"] = timing
    if aggressive:
        options["aggressive"] = True
    
    scan_data = {
        "target": target,
        "scanner": scanner,
        "options": options if options else None
    }
    
    try:
        click.echo(f"🚀 Starting {scanner} scan for {target}...")
        
        response = requests.post(f"{BASE_URL}/scan", json=scan_data)
        response.raise_for_status()
        
        result = response.json()
        scan_id = result["scan_id"]
        
        if format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✅ Scan created successfully!")
            click.echo(f"📋 Scan ID: {scan_id}")
            click.echo(f"🎯 Target: {target}")
            click.echo(f"🔍 Scanner: {scanner}")
        
        if wait:
            click.echo("\n⏳ Waiting for scan completion...")
            wait_for_completion(scan_id, format)
            
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("scan_id")
@click.option("--format", "-f", type=click.Choice(['json', 'table']), default='table', help="Output format")
@click.option("--follow", is_flag=True, help="Follow scan progress")
def status(scan_id, format, follow):
    """Get status of SCAN_ID"""
    
    try:
        if follow:
            wait_for_completion(scan_id, format)
        else:
            show_scan_status(scan_id, format)
            
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

def show_scan_status(scan_id: str, format: str):
    """Show scan status"""
    response = requests.get(f"{BASE_URL}/scan/{scan_id}")
    response.raise_for_status()
    
    result = response.json()
    
    if format == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        display_scan_table(result)

def wait_for_completion(scan_id: str, format: str):
    """Wait for scan completion with progress updates"""
    
    with click.progressbar(length=100, label="Scanning") as bar:
        last_progress = 0
        
        while True:
            try:
                response = requests.get(f"{BASE_URL}/scan/{scan_id}")
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status")
                progress = result.get("progress", 0)
                
                # Update progress bar
                if progress > last_progress:
                    bar.update(progress - last_progress)
                    last_progress = progress
                
                if status in ["completed", "failed"]:
                    bar.finish()
                    break
                    
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                click.echo(f"\n❌ Error checking status: {e}", err=True)
                break
    
    click.echo(f"\n📊 Final Results:")
    show_scan_status(scan_id, format)

def display_scan_table(result: Dict[str, Any]):
    """Display scan results in table format"""
    
    # Basic info
    click.echo(f"\n📋 Scan Information:")
    click.echo(f"   ID: {result.get('scan_id', 'N/A')}")
    click.echo(f"   Target: {result.get('target', 'N/A')}")
    click.echo(f"   Scanner: {result.get('scanner', 'N/A')}")
    click.echo(f"   Status: {get_status_emoji(result.get('status'))} {result.get('status', 'N/A')}")
    click.echo(f"   Created: {result.get('created_at', 'N/A')}")
    
    if result.get('completed_at'):
        click.echo(f"   Completed: {result.get('completed_at')}")
    
    # Results
    if result.get('results'):
        results = result['results']
        
        # Open ports
        open_ports = results.get('open_ports', [])
        if open_ports:
            click.echo(f"\n🔓 Open Ports ({len(open_ports)}):")
            for port in sorted(open_ports):
                service_info = results.get('services', {}).get(str(port), {})
                service_name = service_info.get('name', 'unknown')
                click.echo(f"   {port}/tcp - {service_name}")
        
        # Risk score
        if result.get('risk_score'):
            risk = result['risk_score']
            risk_emoji = get_risk_emoji(risk.get('level', 'info'))
            click.echo(f"\n🎯 Risk Assessment:")
            click.echo(f"   Score: {risk_emoji} {risk.get('score', 0)}/100 ({risk.get('level', 'unknown')})")
    
    # Findings
    if result.get('findings'):
        findings = result['findings']
        click.echo(f"\n🔍 Findings ({len(findings)}):")
        
        # Group by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'info')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(finding)
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity in by_severity:
                severity_emoji = get_severity_emoji(severity)
                click.echo(f"   {severity_emoji} {severity.upper()}: {len(by_severity[severity])} findings")

def get_status_emoji(status: str) -> str:
    """Get emoji for scan status"""
    emojis = {
        "queued": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌"
    }
    return emojis.get(status, "❓")

def get_risk_emoji(level: str) -> str:
    """Get emoji for risk level"""
    emojis = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "info": "🔵"
    }
    return emojis.get(level, "⚪")

def get_severity_emoji(severity: str) -> str:
    """Get emoji for finding severity"""
    return get_risk_emoji(severity)

@cli.command()
def health():
    """Check API health status"""
    try:
        # Check API Gateway
        response = requests.get("http://localhost:8080/health")
        response.raise_for_status()
        api_health = response.json()
        
        # Check Core Service
        response = requests.get("http://localhost:8001/health")
        response.raise_for_status()
        core_health = response.json()
        
        click.echo("🏥 Health Check Results:")
        click.echo(f"   API Gateway: ✅ {api_health.get('status', 'unknown')}")
        click.echo(f"   Core Service: ✅ {core_health.get('status', 'unknown')}")
        
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()
