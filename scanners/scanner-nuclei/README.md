# Nuclei Scanner

This service provides integration with the Nuclei vulnerability scanner for the EASM platform.

## Configuration

The scanner is configured to use the following environment variables:
- `CELERY_BROKER_URL`: URL to the Redis broker (default: "redis://redis:6379/0")
- `CORE_URL`: URL to the core service (default: "http://core:8001")

## Usage

The scanner is called by the core service via a Celery task:

```python
celery_app.send_task(
    "scanner-nuclei.run",
    args=[scan_id, target, options],
    queue="scanner-nuclei"
)
```

### Options

The following options are supported:

- `templates`: Comma-separated list of template directories to use (default: "cves")
- `severity`: Comma-separated list of severity levels to include (default: "critical,high,medium")
- `timeout`: Timeout in seconds for the scan (default: 600)
- `rate`: Rate limiting in requests per second (default: 150)
- `concurrency`: Number of concurrent requests (default: 25)

## API Endpoints

The scanner reports results to the following endpoints in the core service:
- `POST /api/v1/scan/{scan_id}/complete`: Report successful scan completion
- `POST /api/v1/scan/{scan_id}/fail`: Report scan failure

## Troubleshooting

Common issues:
- **Timeout errors**: Increase the `timeout` option
- **No templates found**: Check that the template directory exists in `/root/.config/nuclei/templates/`
- **No results**: Verify that the target is accessible and the templates are appropriate

## Recent Fixes

1. Fixed API endpoint URLs from `/internal/scan/` to `/api/v1/scan/`
2. Updated flag from `-json` to `-jsonl` for the newer version of nuclei (v2.9.15)
3. Enhanced error handling and reporting
4. Improved results parsing to handle different output formats
5. Added more detailed logging for better diagnostics
