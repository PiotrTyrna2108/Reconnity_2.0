# EASM Microservices - Production-Ready Architecture

Implementacja External Attack Surface Management (EASM) na wzór **FastAPI RealWorld Example** z Clean Architecture i najlepszymi praktykami.

## 🏗️ **Architektura na wzór RealWorld**

```
app/
├── 🎯 api/                  # API Layer (FastAPI routes, dependencies, errors)
│   ├── dependencies.py     # Dependency injection
│   ├── errors.py          # Exception handlers
│   └── routers/           # Endpoint routers
│       ├── health.py      # Health check endpoints
│       └── scan.py        # Scan management endpoints
├── ⚙️ core/                # Core configuration
│   ├── settings.py        # Pydantic settings
│   ├── logging.py         # Structured logging
│   └── security.py        # Security utilities
├── 🧠 services/            # Business Logic Layer
│   ├── scan_service.py    # Scan domain services
│   ├── asset_service.py   # Asset management services
│   └── finding_service.py # Finding analysis services
├── 📋 schemas/             # Pydantic models (API contracts)
│   ├── scan.py           # Scan request/response schemas
│   ├── asset.py          # Asset data schemas
│   ├── finding.py        # Security finding schemas
│   └── health.py         # Health check schemas
├── 🗃️ models/              # Database models (SQLAlchemy)
│   ├── base.py           # Base model definitions
│   ├── asset.py          # Asset entity model
│   ├── scan.py           # Scan entity model
│   └── finding.py        # Finding entity model
├── 🔧 tasks/               # Celery async tasks
│   └── scan_tasks.py     # Background scan tasks
├── 🗄️ db/                  # Database management
│   ├── migrations/        # Alembic database migrations
│   └── repositories/      # Data access repositories
└── 📊 risk_engine.py      # Risk calculation engine
```

## 🚀 **Kluczowe Aspekty Architektury**

### **1. Clean Architecture** ✨
- **Separation of Concerns**: API ↔ Services ↔ Models
- **Dependency Injection**: FastAPI Dependencies
- **Error Handling**: Structured exception handling
- **Validation**: Pydantic schemas z walidacją

### **2. Professional Logging** 📝
```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Scan created", scan_id=scan_id, target=target)
```

### **3. Configuration Management** ⚙️
```python
# .env support, type hints, validation
class Settings(BaseSettings):
    database_url: str
    celery_broker_url: str
    secret_key: str
```

### **4. Advanced Validation** ✅
```python
class ScanRequest(BaseModel):
    target: str = Field(..., description="IP, domain, or CIDR")
    
    @validator('target')
    def validate_target(cls, v):
        # IP, CIDR, domain validation
        return v
```

### **5. Service Layer Pattern** 🎯
```python
class ScanService:
    async def create_scan(self, target: str, scanner: str):
        # Business logic encapsulation
        pass
```

### **6. Microservice Architecture** 🧩
- **API Gateway**: Centralne miejsce dostępu do systemu
- **Core Service**: Zarządzanie skanami i logika biznesowa
- **Scanner Services**: Wyspecjalizowane serwisy skanujące (nmap, masscan)
- **Worker & Scheduler**: Asynchroniczne zadania i planowanie
- **Shared Database & Message Queue**: Komunikacja między serwisami

## 🔄 **Przepływ Request → Response**

```
1. Client → API Gateway (easm-api)
2. API Gateway → Core Service (clean validation)
3. Core Service → Service Layer (business logic)
4. Service Layer → Celery Task (async execution)
5. Scanner Services → Wyspecjalizowane skanery (nmap, masscan)
6. Scanner → Core Service (wyniki skanowania)
7. Core Service → Asset Management (identyfikacja i aktualizacja)
8. Core Service → Finding Processing (analiza podatności)
9. Risk Engine → Risk Calculation (intelligent scoring)
10. Response ← Structured JSON (typed schemas)
```

## 🧪 **Testowanie i Monitoring**

### **API Testing**

```bash
# Start services
./start.sh --detached

# Test scan creation
curl -X POST "http://localhost:8080/api/v1/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "192.168.1.0/24",
    "scanner": "nmap",
    "options": {"ports": "1-1000", "timing": 4}
  }'

# Get detailed results with risk scoring
curl "http://localhost:8080/api/v1/scan/{scan_id}"
```

### **Performance Testing**

```bash
# Uruchomienie testów wydajności
python -m tests.performance.performance_test

# Uruchomienie z monitoringiem
make up-monitoring
# Dostęp do Grafana: http://localhost:3000
# Dostęp do Prometheus: http://localhost:9090
```

### **Unit Testing**

```bash
# Uruchomienie testów jednostkowych
pytest tests/test_services/

# Uruchomienie wszystkich testów
pytest
```

## 🎯 **Benefits tej Architektury**

### **Kluczowe zalety mikrousług:**

| Aspekt | Tradycyjna architektura | Mikrousługi EASM |
|--------|-------------------------|------------------|
| **Structure** | Monolityczna aplikacja | Mikrousługi z wyspecjalizowanymi zadaniami |
| **Skanery** | Zintegrowane moduły | Niezależne mikrousługi skanerów |
| **Skalowalność** | Utrudniona skalowalność | Selektywne skalowanie poszczególnych usług |
| **Wdrożenia** | Całościowe wdrożenie | Niezależne wdrażanie komponentów |
| **Testowanie** | Testy end-to-end | Testy poszczególnych mikrousług |
| **Odporność** | Pojedynczy punkt awarii | Izolacja awarii w ramach mikrousługi |

### **Zalety Clean Architecture:**

| Aspekt | Basic Version | RealWorld Pattern |
|--------|---------------|-------------------|
| **Structure** | Flat files | Clean Architecture layers |
| **Validation** | Basic Pydantic | Advanced validators + error handling |
| **Logging** | print/logging | Structured logging with context |
| **Config** | ENV vars | Pydantic Settings with validation |
| **Error Handling** | Basic HTTP errors | Custom exceptions + handlers |
| **Business Logic** | Mixed in endpoints | Separated Service layer |
| **Testing** | Hard to test | Dependency injection ready |
| **Maintainability** | Monolithic | Modular, extensible |

### **Production Readiness:**
✅ **Type Safety**: Full mypy compatibility  
✅ **Error Handling**: Graceful error responses  
✅ **Observability**: Structured logs + metrics  
✅ **Configuration**: Environment-based config  
✅ **Validation**: Input sanitization  
✅ **Testability**: Mockable dependencies  
✅ **Documentation**: Auto-generated OpenAPI  

## 🔮 **Enterprise Features**

```bash
# 1. Authentication & Authorization (Planowane)
app/
├── api/
│   └── auth/              # JWT, OAuth2, RBAC
├── services/
│   └── auth_service.py    # User management

# 2. Repository Pattern (Zaimplementowane)
app/
├── db/
│   ├── repositories/      # Data access layer
│   └── migrations/        # Alembic migrations

# 3. Advanced Monitoring (Częściowo zaimplementowane)
monitoring/
├── prometheus.yml        # Prometheus configuration
└── future/
    ├── metrics.py        # Prometheus metrics
    └── tracing.py        # OpenTelemetry

# 4. Testing Framework (Zaimplementowane)
tests/
├── test_api/             # API tests
├── test_services/        # Service layer tests
├── test_schemas/         # Schema validation tests
├── performance/          # Performance tests
└── conftest.py           # Test fixtures and configuration
```

## 📊 **System Overview**

### **Struktura mikrousług**

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  easm-api     │─────▶│   easm-core   │─────▶│  scanner-nmap  │
│  API Gateway  │      │ Core Service  │      │  Nmap Scanner  │
└───────────────┘      └───────────────┘      └───────────────┘
       │                      │                      │
       │                      │                      │
       │                      ▼                      │
       │              ┌───────────────┐              │
       │              │    worker     │              │
       └─────────────▶│ Task Workers  │◀─────────────┘
                      └───────────────┘
                             │
                             ▼
                      ┌───────────────┐
                      │scanner-masscan│
                      │Masscan Scanner│
                      └───────────────┘
```

### **Kluczowe Komponenty**

| Komponent | Rola | Technologie |
|-----------|------|-------------|
| **easm-api** | API Gateway, walidacja, przekazywanie żądań | FastAPI, Pydantic |
| **easm-core** | Główna logika biznesowa, zarządzanie skanami | FastAPI, SQLAlchemy, Celery |
| **scanner-nmap** | Skanowanie portów i usług | Celery, nmap |
| **scanner-masscan** | Szybkie skanowanie dużych zakresów | Celery, masscan |
| **worker** | Wykonywanie zadań asynchronicznych | Celery |
| **celery-scheduler** | Planowanie cyklicznych zadań | Celery Beat |
| **db** | Przechowywanie danych | PostgreSQL |
| **redis** | Message broker, cache | Redis |

Ta architektura łączy **nowoczesne podejście mikrousługowe** z **najlepszymi praktykami FastAPI i Clean Architecture** dla skalowalnego i utrzymywalnego systemu EASM! 🎯
