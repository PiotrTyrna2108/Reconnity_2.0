.PHONY: help build up down restart logs clean test performance cli

# Default target
help:
	@echo "EASM Microservices - Available Commands:"
	@echo ""
	@echo "  🚀 Deployment:"
	@echo "  make up              - Start all services"
	@echo "  make up-monitoring   - Start all services with monitoring"
	@echo "  make build           - Build all Docker images"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo ""
	@echo "  📋 Monitoring:"
	@echo "  make logs            - Show logs for all services"
	@echo "  make logs-api        - Show API gateway logs"
	@echo "  make logs-core       - Show core service logs"
	@echo "  make logs-worker     - Show worker logs"
	@echo "  make logs-nmap       - Show nmap scanner logs"
	@echo "  make logs-masscan    - Show masscan scanner logs"
	@echo ""
	@echo "  🧪 Testing & Quality:"
	@echo "  make test            - Run API tests"
	@echo "  make test-unit       - Run unit tests"
	@echo "  make performance     - Run performance tests"
	@echo "  make cli             - Install and run CLI tool"
	@echo ""
	@echo "  🗃️  Database:"
	@echo "  make db-connect      - Connect to PostgreSQL database"
	@echo "  make redis-cli       - Connect to Redis CLI"
	@echo ""
	@echo "  🧹 Cleanup:"
	@echo "  make clean           - Remove all containers, volumes, and images"

# Check if docker compose or docker-compose is available
COMPOSE_CMD := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

# Start services
up:
	$(COMPOSE_CMD) up --build -d
	@echo "✅ Services started!"
	@echo "🌐 API Gateway: http://localhost:8080"
	@echo "🔧 Core Service: http://localhost:8001"

# Start with monitoring
up-monitoring:
	$(COMPOSE_CMD) --profile monitoring up --build -d
	@echo "✅ Services started with monitoring!"
	@echo "🌐 API Gateway: http://localhost:8080"
	@echo "🔧 Core Service: http://localhost:8001"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📈 Grafana: http://localhost:3000 (admin/admin)"

# Build images
build:
	$(COMPOSE_CMD) build

# Stop services
down:
	$(COMPOSE_CMD) down

# Restart services
restart:
	$(COMPOSE_CMD) restart

# Show logs
logs:
	$(COMPOSE_CMD) logs -f

logs-api:
	$(COMPOSE_CMD) logs -f api

logs-core:
	$(COMPOSE_CMD) logs -f core

logs-worker:
	$(COMPOSE_CMD) logs -f worker

logs-nmap:
	$(COMPOSE_CMD) logs -f scanner-nmap

logs-masscan:
	$(COMPOSE_CMD) logs -f scanner-masscan

logs-nuclei:
	$(COMPOSE_CMD) logs -f scanner-nuclei

# Unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	cd easm-core && python -m pytest tests/ -v

# Performance tests
performance:
	@echo "🚀 Running performance tests..."
	python -m tests.performance.performance_test

# CLI tool
cli:
	@echo "🛠️  Installing CLI dependencies..."
	pip install click requests aiohttp
	@echo "✅ CLI ready! Usage examples:"
	@echo "  ./easm-cli.py scan 192.168.1.1"
	@echo "  ./easm-cli.py scan example.com --scanner masscan --wait"
	@echo "  ./easm-cli.py status <scan-id>"
	@echo "  ./easm-cli.py health"

# Clean everything
clean:
	$(COMPOSE_CMD) down -v --rmi all --remove-orphans
	docker system prune -f

# Database connection
db-connect:
	$(COMPOSE_CMD) exec db psql -U easm -d easm

# Redis CLI
redis-cli:
	$(COMPOSE_CMD) exec redis redis-cli

# Test API
test:
	@echo "🧪 Testing API endpoints..."
	@echo "1. Health check:"
	curl -s http://localhost:8080/health | jq .
	@echo ""
	@echo "2. Creating test scan:"
	curl -s -X POST "http://localhost:8080/api/v1/scan" \
		-H "Content-Type: application/json" \
		-d '{"target": "scanme.nmap.org", "scanner": "nmap", "options": {"ports": "22,80,443"}}' | jq .
