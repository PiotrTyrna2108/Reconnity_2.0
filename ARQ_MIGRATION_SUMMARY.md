# ARQ Migration - Summary of Changes

## Overview
This document summarizes the migration from Celery to ARQ for asynchronous task processing in the EASM microservices application. The migration has been completed successfully.

## Changes Made

### Core Components
- Updated easm-core/requirements.txt to use ARQ instead of Celery
- Added `prometheus_client==0.20.0` dependency to support ARQ metrics functionality
- Created ARQ-compatible versions of:
  - easm-core/app/tasks/__init__.py
  - easm-core/app/tasks/scan_tasks.py
  - easm-core/app/api/routers/scan.py
- Created a new `redis_config.py` file to resolve circular imports
- Updated environment variable naming from CELERY_BROKER_URL to REDIS_URL
- **Added new `process_scan_result` function to handle scan results via Redis message queue**
- **Removed HTTP callback endpoints from API router in favor of direct database updates**
- **Implemented "smart endpoints, dumb pipes" design pattern using Redis as message bus**

### Scanner Modules
Each scanner module was updated to use ARQ instead of Celery:

1. **Nmap Scanner**
   - Updated requirements.txt to use ARQ and httpx
   - Rewrote main.py to use ARQ worker pattern
   - Modified scan functions to be async
   - Updated reporting functions to use Redis messaging instead of HTTP callbacks
   - Updated Dockerfile to use ARQ worker

2. **Masscan Scanner**
   - Updated requirements.txt to use ARQ and httpx
   - Rewrote main.py to use ARQ worker pattern
   - Modified scan functions to be async
   - Updated reporting functions to use Redis messaging instead of HTTP callbacks
   - Updated Dockerfile to use ARQ worker

3. **Nuclei Scanner**
   - Updated requirements.txt to use ARQ and httpx
   - Rewrote main.py to use ARQ worker pattern
   - Modified scan functions to be async
   - Updated reporting functions to use Redis messaging instead of HTTP callbacks
   - Updated Dockerfile to use ARQ worker

### Docker Configuration
- Updated docker-compose.yml to configure all services to use ARQ workers
- Changed environment variable CELERY_BROKER_URL to REDIS_URL across all services

## Testing Instructions

1. Build and start the application:
   ```bash
   docker compose build
   docker compose up -d
   ```

2. Test the scanner functionality:
   ```bash
   curl -s -X POST "http://localhost:8080/api/v1/scan" \
     -H "Content-Type: application/json" \
     -d '{"target": "scanme.nmap.org", "scanner": "nmap", "options": {"ports": "22,80,443"}}' | jq .
   ```

3. Check the scan status with the returned scan_id:
   ```bash
   curl -s "http://localhost:8080/api/v1/scan/{scan_id}" | jq .
   ```

## Troubleshooting

If you encounter any issues during the ARQ migration, check the following:

1. **Circular Import Issues**: 
   - The application now uses a dedicated `redis_config.py` file to centralize Redis settings
   - This prevents circular imports between `scan_tasks.py` and `queue.py`

2. **Missing Dependencies**:
   - Ensure `prometheus_client==0.20.0` is included in the requirements.txt file
   - Run `docker-compose build core worker scanner-nmap scanner-masscan scanner-nuclei` to rebuild containers with new dependencies

3. **Worker Command Issues**:
   - Ensure the worker commands in docker-compose.yml are correctly formatted
   - Check the logs with `docker-compose logs worker` or specific scanner logs to identify issues

2. Check that all services are running:
   ```bash
   docker compose ps
   ```

3. Send a test scan request:
   ```bash
   curl -X POST "http://localhost:8080/api/v1/scan" \
     -H "Content-Type: application/json" \
     -d '{
       "target": "example.com",
       "scanner": "nmap",
       "options": {"ports": "22,80,443"}
     }'
   ```

4. Check logs to see if tasks are being processed:
   ```bash
   docker compose logs -f core
   docker compose logs -f scanner-nmap
   ```

## Potential Issues

1. Redis URL parsing may need adjustment based on actual Redis configuration
2. Task queuing and naming conventions may need verification
3. Error handling and reporting might need further refinement

## Next Steps

1. Update monitoring configuration to track ARQ tasks instead of Celery tasks
2. Add metrics support for ARQ (in progress)
3. Update documentation in README.md to reflect the change from Celery to ARQ

## Migration Checklist

- [x] Update core service to use ARQ instead of Celery
- [x] Update scanner services to use ARQ instead of Celery
- [x] Fix import syntax for ARQ workers in docker-compose.yml
- [x] Create queue.py for ARQ worker configuration
- [x] Remove all temporary .new files
- [x] Update dependencies.py to include Redis connection
- [x] Update requirements.txt to remove unused Celery dependencies
- [x] Test the full application workflow
