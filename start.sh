#!/bin/bash

# EASM Microservices Startup Script

set -e

echo "🚀 Starting EASM Microservices..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ docker-compose or docker compose is not available."
    exit 1
fi

# Use docker compose if available, fallback to docker-compose
COMPOSE_CMD="docker compose"
if ! docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

# Parse command line arguments
PROFILE=""
BUILD_FLAG="--build"
DETACHED=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --monitoring)
            PROFILE="--profile monitoring"
            shift
            ;;
        --no-build)
            BUILD_FLAG=""
            shift
            ;;
        --detached|-d)
            DETACHED="-d"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --monitoring    Start with monitoring services (Prometheus, Grafana)"
            echo "  --no-build      Skip building images"
            echo "  --detached,-d   Run in detached mode"
            echo "  --help,-h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo "📦 Building and starting services..."
$COMPOSE_CMD $PROFILE up $BUILD_FLAG $DETACHED

if [[ "$DETACHED" == "-d" ]]; then
    echo ""
    echo "✅ Services started in detached mode!"
    echo ""
    echo "📊 Service Status:"
    $COMPOSE_CMD ps
    echo ""
else
    echo ""
    echo "✅ Services started!"
fi

echo "🌐 Service URLs:"
echo "  - API Gateway: http://localhost:8080"
echo "  - Core Service: http://localhost:8001"
echo "  - Database: localhost:5432"

if [[ "$PROFILE" == *"monitoring"* ]]; then
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
fi

echo ""
echo "🧪 Test the API:"
echo "curl -X POST \"http://localhost:8080/api/v1/scan\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"target\": \"scanme.nmap.org\", \"scanner\": \"nmap\"}'"
echo ""
echo "📋 View logs: $COMPOSE_CMD logs -f [service_name]"
echo "🛑 Stop services: $COMPOSE_CMD down"
