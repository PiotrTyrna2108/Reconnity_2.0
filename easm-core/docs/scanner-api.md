# Scanner API Documentation

## Overview

The EASM Scanner API provides endpoints for running various security scans against targets. Each scanner has its own endpoint with specific options.

## Available Scanners

### Nmap Scanner

Network scanner for port discovery, service detection, and OS fingerprinting.

**Endpoint**: `POST /api/v1/scan/nmap`

**Options**:
- `ports`: Port range to scan (e.g. '1-1000', '22,80,443')
- `scan_type`: Scan type (SYN, TCP, UDP, etc.)
- `timing`: Timing template (0-5, higher is faster)
- `os_detection`: Enable OS detection
- `service_detection`: Enable service version detection
- `script_scan`: Enable default script scan
- `timeout`: Scan timeout in seconds

**Example Request**:
```json
{
  "target": "example.com",
  "options": {
    "ports": "22,80,443",
    "timing": 4,
    "os_detection": true
  }
}
```

### Masscan Scanner

Fast port scanner that can scan the entire internet in under 6 minutes.

**Endpoint**: `POST /api/v1/scan/masscan`

**Options**:
- `ports`: Port range to scan (e.g. '1-10000', '22,80,443')
- `rate`: Packets per second to send
- `timeout`: Scan timeout in seconds

**Example Request**:
```json
{
  "target": "192.168.1.0/24",
  "options": {
    "ports": "1-1000",
    "rate": 5000
  }
}
```

### Nuclei Scanner

Vulnerability scanner with a large template library.

#### Basic Scan

**Endpoint**: `POST /api/v1/scan/nuclei`

**Options**:
- `templates`: Template directories to use (cves, dns, file, http, network, ssl, etc.)
- `severity`: Severity levels to include (critical, high, medium, low, info)
- `timeout`: Scan timeout in seconds
- `rate`: Rate limiting in requests per second
- `concurrency`: Number of concurrent requests
- `exclude_templates`: Templates to exclude (e.g. 'cves/2020/...')
- `retries`: Number of times to retry a failed request
- `verbose`: Enable verbose output for more detailed results
- `follow_redirects`: Follow HTTP redirects during scanning
- `max_host_error`: Maximum number of errors allowed for a host before skipping

**Example Request**:
```json
{
  "target": "example.com",
  "options": {
    "templates": ["http", "cves"],
    "severity": ["critical", "high"],
    "timeout": 300,
    "rate": 100,
    "follow_redirects": true
  }
}
```

#### Available Template Categories

**Endpoint**: `GET /api/v1/scan/nuclei/templates`

Returns information about available Nuclei template categories.

**Example Response**:
```json
[
  {
    "id": "cves",
    "name": "CVEs",
    "description": "Common Vulnerabilities and Exposures templates",
    "count": 5000
  },
  {
    "id": "http",
    "name": "HTTP",
    "description": "HTTP-related vulnerability templates",
    "count": 800
  },
  ...
]
```

#### Available Severity Levels

**Endpoint**: `GET /api/v1/scan/nuclei/severity-levels`

Returns information about supported severity levels for Nuclei templates.

**Example Response**:
```json
[
  {
    "id": "critical",
    "name": "Critical",
    "description": "Severe vulnerabilities that require immediate attention"
  },
  {
    "id": "high",
    "name": "High",
    "description": "Important vulnerabilities that should be addressed soon"
  },
  ...
]
```
```

## Scanner Options

The API provides endpoints to discover available scanner options:

**Endpoint**: `GET /api/v1/scan/options`

Returns configuration options for all available scanners.

**Example Response**:
```json
[
  {
    "scanner": "nmap",
    "description": "Network port scanner with service detection capabilities",
    "options": {
      "ports": "1-1000",
      "scan_type": "SYN",
      "timing": 4,
      "os_detection": false,
      "service_detection": true,
      "script_scan": false,
      "timeout": 300
    }
  },
  {
    "scanner": "nuclei",
    "description": "Vulnerability scanner with template-based detection",
    "options": {
      "templates": ["cves"],
      "severity": ["critical", "high", "medium"],
      "timeout": 600,
      "rate": 150,
      "concurrency": 25
    }
  }
]
```

**Endpoint**: `GET /api/v1/scan/options/{scanner_type}`

Returns configuration options for a specific scanner type.

**Example Request**: `GET /api/v1/scan/options/nuclei`

**Example Response**:
```json
{
  "scanner": "nuclei",
  "description": "Vulnerability scanner with template-based detection",
  "options": {
    "templates": ["cves"],
    "severity": ["critical", "high", "medium"],
    "timeout": 600,
    "rate": 150,
    "concurrency": 25,
    "retries": 1,
    "verbose": false,
    "follow_redirects": true,
    "max_host_error": 30
  }
}
```

## Scan Status and Results

To check the status and results of a scan:

**Endpoint**: `GET /api/v1/scan/{scan_id}`

**Example Response**:
```json
{
  "scan_id": "d274f98e-9a44-40ee-aa7d-ce84c66279a0",
  "target": "example.com",
  "scanner": "nuclei",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-07-03T07:13:15.288847",
  "started_at": "2025-07-03T07:13:15.296000",
  "completed_at": "2025-07-03T07:13:21.799000",
  "results": {
    "scanner": "nuclei",
    "target": "example.com",
    "scan_duration": 6.503220081329346,
    "stats": {
      "total_findings": 0
    }
  },
  "findings": []
}
```

## Discovery Endpoints

The API also includes endpoints to discover available options:

- `GET /api/v1/scan/options`: Get all available scanner options
- `GET /api/v1/scan/options/{scanner_type}`: Get options for a specific scanner
- `GET /api/v1/scan/nuclei/templates`: List available Nuclei template directories
