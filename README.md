# EASM Microservices - Development Environment

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up --build
   ```

2. **Test the API:**
   ```bash
   # Create a scan
   curl -X POST "http://localhost:8080/api/v1/scan" \
        -H "Content-Type: application/json" \
        -d '{
          "target": "scanme.nmap.org",
          "scanner": "nmap",
          "options": {"ports": "22,80,443"}
        }'

   # Check scan status (replace with actual scan_id)
   curl "http://localhost:8080/api/v1/scan/{scan_id}"
   ```

3. **Start with monitoring (optional):**
   ```bash
   docker compose --profile monitoring up --build
   ```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/UI     │───▶│   easm-api      │───▶│   easm-core     │
│                 │    │  (FastAPI)      │    │ (Business Logic)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  scanner-nmap   │◀───│     Redis       │◀───│  Celery Worker  │
│  (Celery Task)  │    │   (Broker)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │   PostgreSQL    │
                                               │   (Database)    │
                                               └─────────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| easm-api | 8080 | Public REST API Gateway |
| easm-core | 8001 | Internal business logic service |
| postgresql | 5432 | Database (exposed for debugging) |
| redis | 6379 | Message broker |
| prometheus | 9090 | Metrics collection (with monitoring profile) |
| grafana | 3000 | Metrics visualization (with monitoring profile) |

## API Endpoints

### Public API (easm-api:8080)

- `GET /health` - Health check
- `POST /api/v1/scan` - Create new scan
- `GET /api/v1/scan/{scan_id}` - Get scan status/results

### Internal API (easm-core:8001)

- `GET /health` - Health check
- `POST /internal/scan` - Internal scan creation
- `GET /internal/scan/{scan_id}` - Internal scan status
- `POST /internal/scan/{scan_id}/complete` - Mark scan complete
- `POST /internal/scan/{scan_id}/fail` - Mark scan failed

## Development

### Adding New Scanners

1. Create new scanner directory: `scanner-{name}/`
2. Implement Celery task for the scanner
3. Add service to `docker-compose.yml`
4. Update core service to route to new scanner

### Database Operations

```bash
# Connect to database
docker compose exec db psql -U easm -d easm

# View logs
docker compose logs -f core
docker compose logs -f worker
```

### Monitoring

Access monitoring services:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| CELERY_BROKER_URL | redis://redis:6379/0 | Celery broker URL |
| DATABASE_URL | postgresql://easm:easm@db:5432/easm | Database connection |
| CORE_URL | http://core:8001 | Core service URL |

## Security Considerations

- Change default passwords in production
- Use proper secrets management
- Implement authentication/authorization
- Use TLS certificates
- Network isolation
- Regular security updates

## Next Steps

1. **Authentication**: Add JWT/OAuth2 to API Gateway
2. **Persistence**: Replace in-memory storage with PostgreSQL
3. **More Scanners**: Add masscan, nuclei, httpx scanners
4. **UI**: Create React/Vue.js frontend
5. **Alerting**: Add Alertmanager configuration
6. **CI/CD**: Setup GitLab CI or GitHub Actions