# Nuclei Scanner

This service provides integration with the Nuclei vulnerability scanner for the EASM platform.

## Configuration

The scanner is configured to use the following environment variables:
- `REDIS_URL`: URL to the Redis broker (default: "redis://redis:6379/0")
- `CORE_URL`: URL to the core service (default: "http://core:8001") - used only for logging, results are reported via Redis

## Usage

The scanner is called by the core service via an ARQ task:

```python
await redis.enqueue_job(
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
- `exclude_templates`: Templates to exclude (e.g. 'cves/2020/...')
- `retries`: Number of times to retry a failed request (default: 1)
- `verbose`: Enable verbose output for more detailed results (default: false)
- `follow_redirects`: Follow HTTP redirects during scanning (default: true)
- `max_host_error`: Maximum number of errors allowed for a host before skipping (default: 30)

## Results Reporting

The scanner reports results back to the core service using Redis messaging:
- Results are sent via Redis ARQ job `process_scan_result` to the `core` queue
- Both success and failure results use the same message queue but with different status parameters

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
