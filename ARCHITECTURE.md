# EASM Microservices - Production-Ready Architecture

Implementacja External Attack Surface Management (EASM) na wzór **FastAPI RealWorld Example** z Clean Architecture i najlepszymi praktykami.

## 🏗️ **Architektura na wzór RealWorld**

```
app/
├── 🎯 api/                  # API Layer (FastAPI routes, dependencies, errors)
│   ├── dependencies.py     # Dependency injection
│   └── errors.py          # Exception handlers
├── ⚙️ core/                # Core configuration
│   ├── settings.py        # Pydantic settings
│   └── logging.py         # Structured logging
├── 🧠 services/            # Business Logic Layer
│   └── scan_service.py    # Domain services
├── 📋 schemas/             # Pydantic models (API contracts)
│   └── scan.py           # Request/Response schemas
├── 🗃️ models/              # Database models (SQLAlchemy)
│   └── __init__.py       # Asset, Scan, Finding models
├── 🔧 tasks/               # Celery async tasks
│   └── scan_tasks.py     # Background tasks
└── 📊 risk_engine.py      # Risk calculation engine
```

## 🚀 **Kluczowe Ulepszenia vs Podstawowa Wersja**

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

## 🔄 **Przepływ Request → Response**

```
1. Client → API Gateway (easm-api)
2. API Gateway → Core Service (clean validation)
3. Core Service → Service Layer (business logic)
4. Service Layer → Celery Task (async execution)
5. Scanner → Results Processing (findings extraction)
6. Risk Engine → Risk Calculation (intelligent scoring)
7. Response ← Structured JSON (typed schemas)
```

## 🧪 **Testowanie Ulepszonej Architektury**

```bash
# Start services
./start.sh --detached

# Test improved validation
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

## 🎯 **Benefits tej Architektury**

### **Compared to Basic Implementation:**

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

## 🔮 **Next Steps - Enterprise Features**

```bash
# 1. Add Authentication & Authorization
app/
├── api/
│   └── auth/              # JWT, OAuth2, RBAC
├── services/
│   └── auth_service.py    # User management

# 2. Add Repository Pattern
app/
├── db/
│   ├── repositories/      # Data access layer
│   └── migrations/        # Alembic migrations

# 3. Add Advanced Monitoring
app/
├── monitoring/
│   ├── metrics.py        # Prometheus metrics
│   └── tracing.py        # OpenTelemetry

# 4. Add Testing Framework
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
└── fixtures/             # Test data
```

## 📊 **Porównanie z FastAPI RealWorld**

| Feature | RealWorld (Articles) | EASM (Scans) |
|---------|---------------------|--------------|
| **Domain** | Article Management | Security Scanning |
| **Core Entity** | Article | Scan/Asset |
| **Auth** | JWT Users | Future: RBAC |
| **Async** | Database queries | Celery tasks |
| **Architecture** | Clean Architecture | ✅ Same pattern |
| **Validation** | Pydantic schemas | ✅ Same approach |
| **Error Handling** | Custom exceptions | ✅ Same pattern |

Ta implementacja łączy **sprawdzone wzorce RealWorld** z **specyfiką bezpieczeństwa** dla profesjonalnej aplikacji EASM! 🎯
