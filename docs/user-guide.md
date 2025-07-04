# 🎓 RECONNITY EASM - KOMPLETNY PRZEWODNIK

> **External Attack Surface Management** - Przewodnik po architekturze, implementacji i użytkowaniu

---

## 📚 Spis treści

1. [🎯 Co to jest EASM i po co ten projekt?](#1--co-to-jest-easm-i-po-co-ten-projekt)
2. [🏗️ Architektura systemu - jak to wszystko działa](#2--architektura-systemu---jak-to-wszystko-działa)
3. [📁 Struktura plików - gdzie co znajdziesz](#3--struktura-plików---gdzie-co-znajdziesz)
4. [🔄 Przepływ danych - jak przebiega skanowanie](#4--przepływ-danych---jak-przebiega-skanowanie)
5. [🛠️ Technologie użyte - dlaczego akurat te](#5-️-technologie-użyte---dlaczego-akurat-te)
6. [🔧 Jak dodać nowy skaner - praktyczny przykład](#6--jak-dodać-nowy-skaner---praktyczny-przykład)
7. [🧭 Nawigacja po projekcie - pierwsze kroki](#7--nawigacja-po-projekcie---pierwsze-kroki)
8. [🚀 Konfiguracja i uruchomienie](#8--konfiguracja-i-uruchomienie)
9. [🐛 Debugowanie i rozwiązywanie problemów](#9--debugowanie-i-rozwiązywanie-problemów)
10. [📖 API Reference](#10--api-reference)
11. [🗄️ Baza danych i modele](#11-️-baza-danych-i-modele)
12. [🔒 Bezpieczeństwo i uwierzytelnianie](#12--bezpieczeństwo-i-uwierzytelnianie)
13. [📊 Monitoring i logi](#13--monitoring-i-logi)
14. [🧪 Testy i quality assurance](#14--testy-i-quality-assurance)
15. [🎯 Podsumowanie dla kolegi](#15--podsumowanie-dla-kolegi)

---

## 1. 🎯 Co to jest EASM i po co ten projekt?

### Co to jest EASM?

**EASM = External Attack Surface Management**

- **Attack Surface** = wszystkie punkty, przez które haker może zaatakować firmę
- **External** = widoczne z internetu (IP, domeny, porty, aplikacje)
- **Management** = zarządzanie, monitorowanie, skanowanie

### Po co ten projekt?

```
🏢 Firma ma:
├── 50 domen (example.com, api.example.com, admin.example.com)
├── 200 serwerów z różnymi portami
├── 500 aplikacji webowych
└── 1000 potencjalnych podatności

❓ Jak to wszystko monitorować?
✅ EASM automatycznie skanuje i raportuje!
```

### Przykład z życia:

```
🚨 Scenariusz: Firma zapomniała o starym serwerze test.firma.com
├── Serwer ma otwarte SSH na porcie 22
├── Ma stare oprogramowanie z lukami
├── Haker znajduje go i włamuje się
└── 💥 Wyciek danych klientów!

✅ EASM by to wykrył:
├── Nmap znalazłby otwarty port 22
├── Nuclei wykryłby stare oprogramowanie  
└── Admin dostałby alert!
```

---

## 2. 🏗️ Architektura systemu - jak to wszystko działa

### Mikroservices = Małe, niezależne aplikacje

```
┌─────────────────────────────────────────────────────────────┐
│                    RECONNITY EASM                           │
├─────────────────────────────────────────────────────────────┤
│  Vue.js Frontend  │  FastAPI Core  │  PostgreSQL  │ Redis  │
│  (Interfejs)      │  (Mózg)        │  (Baza)      │ (Kolejka) │
└─────────────────────────────────────────────────────────────┘
│
├── Scanner Nmap     (Skanowanie portów)
├── Scanner Masscan  (Szybkie skanowanie)  
├── Scanner Nuclei   (Podatności)
└── Scanner [Twój]   (Co chcesz dodać)
```

### Dlaczego mikroservices?

**🔴 Monolityczna aplikacja (źle):**
```python
# Jedna wielka aplikacja
def scan_everything():
    run_nmap()      # Jeśli nmap się wywali
    run_masscan()   # to cała aplikacja umiera
    run_nuclei()    # 💥💥💥
```

**🟢 Mikroservices (dobrze):**
```python
# Każdy skaner to oddzielna aplikacja
Scanner-Nmap:    run_nmap()      # Nmap umiera - inne działają
Scanner-Masscan: run_masscan()   # Masscan umiera - inne działają  
Scanner-Nuclei:  run_nuclei()    # Nuclei umiera - inne działają
```

---

## 3. 📁 Struktura plików - gdzie co znajdziesz

### Główna struktura:
```
/easm-microservices/
├── easm-core/           # 🧠 Mózg aplikacji (FastAPI)
├── scanners/            # 🔍 Wszystkie skanery
│   ├── scanner-nmap/    # Port scanning
│   ├── scanner-masscan/ # Fast scanning
│   └── scanner-nuclei/  # Vulnerability scanning
├── docker-compose.yml   # 🐳 Konfiguracja kontenerów
└── docs/               # 📚 Dokumentacja
```

### EASM Core - szczegóły:
```
easm-core/
├── app/
│   ├── api/
│   │   └── routers/
│   │       ├── scan.py        # 🌐 API endpoints (/scan)
│   │       ├── health.py      # 🏥 Health checks
│   │       └── scan_options.py # ⚙️ Opcje skanowania
│   ├── models/
│   │   ├── scan.py           # 🗄️ Model skanów
│   │   ├── asset.py          # 🎯 Model zasobów
│   │   └── finding.py        # 🔍 Model znalezisk
│   ├── services/
│   │   ├── scan_service.py   # 📋 Logika skanowania
│   │   ├── asset_service.py  # 🎯 Zarządzanie zasobami
│   │   └── risk_service.py   # ⚠️ Ocena ryzyka
│   ├── tasks/             # ⚙️ Zadania asynchroniczne
│   └── main.py           # 🚀 Startowanie aplikacji
├── alembic/              # 🔄 Migracje bazy danych
└── requirements.txt      # 📦 Biblioteki Python
```

### Struktura skanera:
```
scanner-nmap/
├── app/
│   └── main.py              # 🔧 Kod skanera
├── Dockerfile               # 🐳 Jak zbudować kontener
└── requirements.txt         # 📦 Biblioteki skanera
```

---

## 4. 🔄 Przepływ danych - jak przebiega skanowanie

### Szczegółowy przepływ z lokalizacją plików:

```
1. 👤 USER: "Zeskanuj google.com portem nmap"
   │
   ▼
2. 🌐 Vue.js Frontend: POST /api/v1/scan
   📁 frontend/src/services/api.js
   📁 frontend/src/components/ScanForm.vue
   │
   ▼  
3. 🧠 EASM Core - odbiera request:
   📁 easm-core/app/main.py (FastAPI app)
   📁 easm-core/app/api/routers/scan.py (endpoint /scan)
   │
   ├── Zapisuje skan w PostgreSQL
   │   📁 easm-core/app/models/scan.py (model Scan)
   │   📁 easm-core/app/database.py (połączenie z DB)
   │
   ├── Dodaje zadanie do Redis
   │   📁 easm-core/app/tasks/tasks/scan_tasks.py (funkcja scan_asset)
   │
   └── Zwraca scan_id
       📁 easm-core/app/api/routers/scan.py (response)
   │
   ▼
4. 📡 Redis Queue: "run_nmap_scan" task
   🐳 redis:6379 (kontener Redis)
   │
   ▼
5. 🔍 Scanner Nmap - odbiera zadanie:
   📁 scanners/scanner-nmap/app/main.py (ARQ worker)
   │
   ├── Odbiera zadanie z Redis
   │   📁 scanners/scanner-nmap/app/main.py (funkcja run_nmap_scan)
   │
   ├── Wykonuje: nmap -p 80,443 google.com
   │   📁 scanners/scanner-nmap/app/main.py (subprocess call)
   │
   ├── Parsuje wyniki
   │   📁 scanners/scanner-nmap/app/main.py (parse_nmap_results)
   │
   └── Wysyła wyniki z powrotem do Redis
       📁 scanners/scanner-nmap/app/main.py (send_results_to_core)
   │
   ▼
6. 🧠 EASM Core - odbiera wyniki:
   📁 easm-core/app/tasks/tasks/scan_tasks.py (funkcja process_scan_result)
   │
   ├── Odbiera wyniki z Redis
   │   📁 easm-core/app/tasks/worker.py (ARQ worker config)
   │
   ├── Aktualizuje PostgreSQL
   │   📁 easm-core/app/tasks/tasks/scan_tasks.py (update database)
   │   📁 easm-core/app/models/scan.py (model Scan)
   │
   └── Wyniki dostępne przez API
       📁 easm-core/app/api/routers/scan.py (GET /scan/{scan_id})
   │
   ▼
7. 👤 USER: Widzi wyniki w interfejsie
   📁 frontend/src/components/ScanResults.vue
   📁 frontend/src/services/api.js (getScanStatus)
```

---

## 5. 🛠️ Technologie użyte - dlaczego akurat te

### Dlaczego akurat te technologie?

#### **FastAPI** (Backend Core)
```python
# Dlaczego FastAPI a nie Flask/Django?
✅ Automatyczna dokumentacja API
✅ Szybkie (async/await)
✅ Walidacja danych
✅ Typed Python

# Przykład
@app.post("/scan")
async def create_scan(scan_data: ScanCreate):
    # FastAPI automatycznie waliduje dane
    return {"scan_id": "123"}
```

#### **Redis + ARQ** (Kolejka zadań)
```python
# Dlaczego Redis a nie Celery?
✅ Szybki (in-memory)
✅ ARQ = async Celery
✅ Prosty w konfiguracji

# Przykład
await redis.enqueue("run_nmap_scan", scan_data)
```

#### **PostgreSQL** (Baza danych)
```python
# Dlaczego PostgreSQL a nie MySQL/SQLite?
✅ JSON support (wyniki skanów)
✅ Skalowalne
✅ ACID compliance

# Przykład
scan.results = {"ports": [80, 443]}  # JSON w PostgreSQL
```

#### **Docker** (Konteneryzacja)
```yaml
# Dlaczego Docker?
✅ Każdy skaner ma swoje narzędzia
✅ Izolacja (nmap nie wpływa na nuclei)
✅ Łatwe skalowanie
✅ Jednakowe środowisko (dev = prod)

# Przykład
services:
  scanner-nmap:
    image: scanner-nmap:latest
    environment:
      - REDIS_URL=redis://redis:6379
```

---

## 6. 🔧 Jak dodać nowy skaner - praktyczny przykład

### Przykład: Dodawanie TestSSL skanera

#### Krok 1: Tworzenie struktury
```bash
mkdir -p scanners/scanner-testssl/app
cd scanners/scanner-testssl
```

#### Krok 2: Implementacja skanera
```python
# scanners/scanner-testssl/app/main.py
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
import subprocess
import json
import os

REDIS_SETTINGS = RedisSettings.from_dsn(
    os.getenv("REDIS_URL", "redis://localhost:6379")
)

async def run_testssl_scan(ctx, scan_data):
    """Skanuje SSL/TLS konfigurację"""
    target = scan_data["target"]
    scan_id = scan_data["scan_id"]
    
    # Budowanie komendy
    cmd = f"testssl.sh --jsonfile-pretty {target}"
    
    # Wykonanie
    result = await execute_command(cmd)
    
    # Parsowanie wyników
    scan_results = parse_testssl_results(result)
    
    # Wysłanie wyników
    await send_results_to_core(scan_id, scan_results, "completed")

async def execute_command(cmd):
    """Wykonuje komendę shell"""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()

def parse_testssl_results(output):
    """Parsuje wyniki TestSSL"""
    try:
        return json.loads(output)
    except:
        return {"raw_output": output}

async def send_results_to_core(scan_id, results, status):
    """Wysyła wyniki do Core"""
    redis = await create_pool(REDIS_SETTINGS)
    await redis.enqueue("process_scan_result", {
        "scan_id": scan_id,
        "results": results,
        "status": status
    })

class WorkerSettings:
    redis_settings = REDIS_SETTINGS
    functions = [run_testssl_scan]

if __name__ == "__main__":
    from arq import run_worker
    run_worker(WorkerSettings)
```

#### Krok 3: Dockerfile
```dockerfile
# scanners/scanner-testssl/Dockerfile
FROM ubuntu:20.04

# Instalacja TestSSL
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Klonowanie TestSSL
RUN git clone https://github.com/drwetter/testssl.sh.git /opt/testssl
RUN chmod +x /opt/testssl/testssl.sh
RUN ln -s /opt/testssl/testssl.sh /usr/local/bin/testssl.sh

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Kod aplikacji
COPY app/ ./app/

CMD ["python3", "-m", "app.main"]
```

#### Krok 4: Rejestracja w Core
```python
# easm-core/app/services/scan_service.py
async def scan_asset(ctx, scan_data):
    scanner = scan_data.get("scanner")
    
    if scanner == "nmap":
        await ctx["redis"].enqueue("run_nmap_scan", scan_data)
    elif scanner == "masscan":
        await ctx["redis"].enqueue("run_masscan_scan", scan_data)
    elif scanner == "nuclei":
        await ctx["redis"].enqueue("run_nuclei_scan", scan_data)
    elif scanner == "testssl":  # <-- DODANE!
        await ctx["redis"].enqueue("run_testssl_scan", scan_data)
    else:
        logger.error(f"Unknown scanner: {scanner}")
```

#### Krok 5: Opcje API
```python
# easm-core/app/api/routers/scan_options.py
@router.get("/options")
async def get_scan_options():
    return {
        "scanners": {
            # ...existing scanners...
            "testssl": {  # <-- DODANE!
                "name": "TestSSL",
                "description": "SSL/TLS scanner",
                "options": {
                    "protocols": {"type": "array", "default": ["tls1_2", "tls1_3"]},
                    "ciphers": {"type": "boolean", "default": True},
                    "vulnerabilities": {"type": "boolean", "default": True}
                }
            }
        }
    }
```

#### Krok 6: Docker Compose
```yaml
# docker-compose.yml
services:
  # ...existing services...
  
  scanner-testssl:  # <-- DODANE!
    build:
      context: ./scanners/scanner-testssl
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - easm-network
```

---

## 7. 🧭 Nawigacja po projekcie - pierwsze kroki

### Jak się poruszać po projekcie?

#### **1. Zaczynaj od przeglądu struktury:**
```bash
# Najpierw zobacz główną strukturę
ls -la
# Wynik: easm-core/ scanners/ docker-compose.yml docs/

# Sprawdź co jest w easm-core
ls -la easm-core/
# Wynik: app/ alembic/ requirements.txt Dockerfile

# Sprawdź skanery
ls -la scanners/
# Wynik: scanner-nmap/ scanner-masscan/ scanner-nuclei/
```

#### **2. Kluczowe pliki do zrozumienia (w tej kolejności):**

**📋 Krok 1: Zrozum konfigurację**
```bash
# 1. Główna konfiguracja kontenerów
cat docker-compose.yml

# 2. Zależności głównej aplikacji
cat easm-core/requirements.txt

# 3. Konfiguracja bazy danych
cat easm-core/app/database.py
```

**📋 Krok 2: Zrozum API**
```bash
# 1. Główna aplikacja FastAPI
cat easm-core/app/main.py

# 2. Endpointy skanowania
cat easm-core/app/api/routers/scan.py

# 3. Modele danych
cat easm-core/app/models/scan.py
```

**📋 Krok 3: Zrozum logikę biznesową**
```bash
# 1. Serwisy biznesowe
cat easm-core/app/services/scan_service.py

# 2. Zadania asynchroniczne
cat easm-core/app/tasks/
```

**📋 Krok 4: Zrozum skanery**
```bash
# 1. Przykład skanera Nmap
cat scanners/scanner-nmap/app/main.py

# 2. Konfiguracja kontenera
cat scanners/scanner-nmap/Dockerfile
```

#### **3. Ważne katalogi i ich przeznaczenie:**

```
📁 easm-core/app/api/           # REST API endpoints
📁 easm-core/app/models/        # Modele bazy danych (SQLAlchemy)
📁 easm-core/app/schemas/       # Pydantic schemas (walidacja)
📁 easm-core/app/services/      # Logika biznesowa
📁 easm-core/app/tasks/         # Zadania asynchroniczne (ARQ)
📁 easm-core/alembic/           # Migracje bazy danych
📁 scanners/scanner-*/          # Implementacje skanerów
📁 docs/                        # Dokumentacja projektu
```

#### **4. Jak znaleźć konkretną funkcjonalność:**

**🔍 Szukasz endpoint API?**
```bash
# Wszystkie endpointy są w:
find easm-core/app/api/routers/ -name "*.py"
```

**🔍 Szukasz logikę biznesową?**
```bash
# Wszystkie serwisy są w:
find easm-core/app/services/ -name "*.py"
```

**🔍 Szukasz implementację skanera?**
```bash
# Wszystkie skanery są w:
find scanners/ -name "main.py"
```

**🔍 Szukasz konfigurację?**
```bash
# Pliki konfiguracyjne:
find . -name "*.yml" -o -name "*.yaml" -o -name "*.env"
```

---

## 8. 🚀 Konfiguracja i uruchomienie

### Pierwszy raz - krok po kroku

#### **1. Wymagania systemowe:**
```bash
# Sprawdź czy masz Docker
docker --version
# Wynik: Docker version 20.10.x

# Sprawdź czy masz Docker Compose
docker-compose --version
# Wynik: docker-compose version 1.29.x

# Sprawdź dostępne porty
netstat -an | grep :8001  # Port Core
netstat -an | grep :5432  # Port PostgreSQL
netstat -an | grep :6379  # Port Redis
```

#### **2. Pierwsze uruchomienie:**
```bash
# Sklonuj projekt
git clone <repository-url>
cd easm-microservices

# Zbuduj wszystkie obrazy
docker-compose build

# Uruchom w tle
docker-compose up -d

# Sprawdź status
docker-compose ps
```

#### **3. Oczekiwany wynik po uruchomieniu:**
```bash
docker-compose ps
# Wynik:
Name                 Command               State           Ports
----------------------------------------------------------------
easm_easm-core_1       python -m app.main            Up      0.0.0.0:8001->8001/tcp
easm_postgres_1        docker-entrypoint.sh postgres Up      5432/tcp
easm_redis_1           docker-entrypoint.sh redis    Up      6379/tcp
easm_scanner-nmap_1    python -m app.main            Up
easm_scanner-masscan_1 python -m app.main           Up
easm_scanner-nuclei_1  python -m app.main           Up
```

#### **4. Weryfikacja że wszystko działa:**
```bash
# Test API Core
curl http://localhost:8001/health
# Wynik: {"status": "healthy"}

# Test endpointu options
curl http://localhost:8001/api/v1/scan/options
# Wynik: {"scanners": {"nmap": {...}, "masscan": {...}, "nuclei": {...}}}

# Test bazy danych
docker-compose exec postgres psql -U postgres -d easm -c "SELECT version();"

# Test Redis
docker-compose exec redis redis-cli ping
# Wynik: PONG
```

#### **5. Konfiguracja zmiennych środowiskowych:**

```bash
# Utwórz plik .env w głównym katalogu
cat > .env << EOF
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=easm
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/easm

# Redis
REDIS_URL=redis://redis:6379

# Core API
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=True

# JWT Secret (wygeneruj własny!)
JWT_SECRET_KEY=super-secret-key-change-in-production
EOF
```

#### **6. Zarządzanie bazą danych:**
```bash
# Sprawdź migracje
docker-compose exec easm-core alembic current

# Wykonaj migracje
docker-compose exec easm-core alembic upgrade head

# Utwórz nową migrację (jeśli zmieniłeś modele)
docker-compose exec easm-core alembic revision --autogenerate -m "Description"
```

---

## 9. 🐛 Debugowanie i rozwiązywanie problemów

### Jak debugować system krok po kroku

#### **1. Sprawdzanie statusu serwisów**
```bash
# Status wszystkich kontenerów
docker-compose ps

# Szczegółowe informacje
docker-compose top

# Zużycie zasobów
docker stats
```

#### **2. Analiza logów**
```bash
# Logi wszystkich serwisów
docker-compose logs

# Logi konkretnego serwisu
docker-compose logs -f easm-core

# Logi z ostatnich 100 linii
docker-compose logs --tail=100 scanner-nmap

# Logi z konkretnego czasu
docker-compose logs --since="2024-01-01T10:00:00"
```

#### **3. Debugowanie API**
```bash
# Sprawdź health check
curl -v http://localhost:8001/health

# Sprawdź dokumentację API
curl http://localhost:8001/docs

# Test konkretnego endpointa
curl -X POST http://localhost:8001/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "scanner": "nmap"}'
```

#### **4. Debugowanie bazy danych**
```bash
# Wejdź do kontenera PostgreSQL
docker-compose exec postgres psql -U postgres -d easm

# Sprawdź tabele
\dt

# Sprawdź dane
SELECT * FROM scans LIMIT 5;

# Sprawdź indeksy
\di
```

#### **5. Debugowanie Redis**
```bash
# Wejdź do Redis CLI
docker-compose exec redis redis-cli

# Sprawdź kolejki
KEYS *
LLEN arq:queue:default
LRANGE arq:queue:default 0 -1

# Sprawdź połączenia
CLIENT LIST
```

#### **6. Debugowanie skanerów**
```bash
# Wejdź do kontenera skanera
docker-compose exec scanner-nmap bash

# Sprawdź czy narzędzie działa
nmap --version

# Sprawdź logi Python
python -c "import app.main; print('OK')"

# Testuj ręcznie
python -m app.main
```

### 🚨 Częste problemy i rozwiązania

#### Problem: "Connection refused" do Redis
```bash
# Diagnoza
docker-compose exec easm-core ping redis

# Rozwiązanie
docker-compose restart redis
docker-compose restart easm-core
```

#### Problem: Skan się nie wykonuje
```bash
# Sprawdź kolejki Redis
docker-compose exec redis redis-cli
LLEN arq:queue:default

# Sprawdź logi workera
docker-compose logs -f easm-core | grep arq

# Sprawdź logi skanera
docker-compose logs -f scanner-nmap
```

#### Problem: Baza danych nie zapisuje
```bash
# Sprawdź migracje
docker-compose exec easm-core alembic current
docker-compose exec easm-core alembic upgrade head

# Sprawdź uprawnienia
docker-compose exec postgres psql -U postgres -d easm -c "SELECT current_user;"
```

---

## 10. 📖 API Reference

### Kompletna dokumentacja API

#### Base URL: `http://localhost:8001/api/v1`

### 🔍 Endpointy skanowania

#### **GET /scan/options**
Zwraca dostępne opcje skanowania

**Response:**
```json
{
  "scanners": {
    "nmap": {
      "name": "Nmap",
      "description": "Network port scanner",
      "options": {
        "ports": {
          "type": "string",
          "default": "1-1000",
          "description": "Port range to scan"
        },
        "scan_type": {
          "type": "string", 
          "options": ["SYN", "TCP", "UDP"],
          "default": "SYN"
        },
        "service_detection": {
          "type": "boolean",
          "default": false,
          "description": "Enable service detection"
        }
      }
    },
    "masscan": {
      "name": "Masscan",
      "description": "Fast port scanner",
      "options": {
        "ports": {
          "type": "string",
          "default": "80,443",
          "description": "Comma-separated ports"
        },
        "rate": {
          "type": "integer",
          "default": 1000,
          "description": "Packets per second"
        }
      }
    },
    "nuclei": {
      "name": "Nuclei",
      "description": "Vulnerability scanner",
      "options": {
        "templates": {
          "type": "array",
          "default": ["cves"],
          "description": "Template categories"
        },
        "severity": {
          "type": "array",
          "default": ["critical", "high"],
          "description": "Severity levels"
        },
        "rate": {
          "type": "integer",
          "default": 100,
          "description": "Requests per second"
        }
      }
    }
  }
}
```

#### **POST /scan**
Tworzy nowy skan

**Request body:**
```json
{
  "target": "example.com",
  "scanner": "nmap",
  "options": {
    "ports": "80,443",
    "scan_type": "SYN",
    "service_detection": true
  }
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "target": "example.com",
  "scanner": "nmap",
  "status": "pending",
  "options": {
    "ports": "80,443",
    "scan_type": "SYN",
    "service_detection": true
  },
  "created_at": "2025-07-04T10:30:00Z",
  "completed_at": null,
  "results": null
}
```

#### **GET /scan/{scan_id}**
Pobiera status i wyniki skanu

**Response (completed):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "target": "example.com",
  "scanner": "nmap",
  "status": "completed",
  "options": {...},
  "created_at": "2025-07-04T10:30:00Z",
  "completed_at": "2025-07-04T10:35:00Z",
  "results": {
    "open_ports": [
      {
        "port": 80,
        "protocol": "tcp",
        "service": "http",
        "version": "Apache 2.4.41"
      },
      {
        "port": 443,
        "protocol": "tcp",
        "service": "https",
        "version": "Apache 2.4.41"
      }
    ],
    "closed_ports": [],
    "scan_time": 45.2,
    "raw_output": "Starting Nmap 7.80..."
  }
}
```

#### **GET /scan**
Lista wszystkich skanów (z paginacją)

**Query parameters:**
- `page`: numer strony (default: 1)
- `limit`: liczba wyników na stronę (default: 20)
- `scanner`: filtr po skanerze
- `status`: filtr po statusie
- `target`: filtr po celu

**Response:**
```json
{
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "scans": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "target": "example.com",
      "scanner": "nmap",
      "status": "completed",
      "created_at": "2025-07-04T10:30:00Z",
      "completed_at": "2025-07-04T10:35:00Z"
    }
  ]
}
```

#### **DELETE /scan/{scan_id}**
Usuwa skan

**Response:**
```json
{
  "message": "Scan deleted successfully"
}
```

### 🔧 Endpointy systemowe

#### **GET /health**
Health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-04T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

#### **GET /metrics**
Metryki systemu

**Response:**
```json
{
  "total_scans": 1250,
  "active_scans": 5,
  "completed_scans": 1200,
  "failed_scans": 45,
  "scanners": {
    "nmap": {
      "total": 800,
      "active": 2,
      "avg_duration": 45.2
    },
    "masscan": {
      "total": 300,
      "active": 1,
      "avg_duration": 12.5
    },
    "nuclei": {
      "total": 150,
      "active": 2,
      "avg_duration": 180.7
    }
  }
}
```

### 📊 Kody błędów

| Kod | Opis | Przykład |
|-----|------|----------|
| 200 | OK | Sukces |
| 201 | Created | Skan utworzony |
| 400 | Bad Request | Nieprawidłowe dane |
| 404 | Not Found | Skan nie znaleziony |
| 422 | Validation Error | Błąd walidacji |
| 500 | Internal Server Error | Błąd serwera |

**Przykład błędu walidacji:**
```json
{
  "detail": [
    {
      "loc": ["body", "target"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 11. 🗄️ Baza danych i modele

### Struktura bazy danych

#### **Tabela: scans**
```sql
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target VARCHAR(255) NOT NULL,
    scanner VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    options JSONB,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    duration_seconds INTEGER
);

-- Indeksy
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_scanner ON scans(scanner);
CREATE INDEX idx_scans_target ON scans(target);
CREATE INDEX idx_scans_created_at ON scans(created_at);
```

#### **Tabela: assets**
```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target VARCHAR(255) NOT NULL UNIQUE,
    asset_type VARCHAR(50) NOT NULL,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scanned TIMESTAMP WITH TIME ZONE,
    risk_score INTEGER DEFAULT 0,
    metadata JSONB
);
```

#### **Tabela: findings**
```sql
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    evidence JSONB,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'open'
);
```

### Modele SQLAlchemy

#### **Model Scan:**
```python
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from enum import Enum
import uuid

from app.models.base import Base

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScannerType(str, Enum):
    NMAP = "nmap"
    MASSCAN = "masscan"
    NUCLEI = "nuclei"

class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target = Column(String(255), nullable=False, index=True)
    scanner = Column(SQLEnum(ScannerType), nullable=False, index=True)
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.PENDING, index=True)
    options = Column(JSONB, nullable=True)
    results = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Scan(id={self.id}, target={self.target}, scanner={self.scanner}, status={self.status})>"
```

### Migracje Alembic

#### **Tworzenie migracji:**
```bash
# Utwórz nową migrację
docker-compose exec easm-core alembic revision --autogenerate -m "Add scan results table"

# Wykonaj migracje
docker-compose exec easm-core alembic upgrade head

# Sprawdź historię migracji
docker-compose exec easm-core alembic history

# Cofnij migrację
docker-compose exec easm-core alembic downgrade -1
```

### Zapytania SQL - przykłady

#### **Statystyki skanów**
```sql
-- Statystyki skanów
SELECT 
    scanner,
    COUNT(*) as total_scans,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds
FROM scans 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY scanner;

-- Najczęściej skanowane targety
SELECT 
    target, 
    COUNT(*) as scan_count,
    MAX(created_at) as last_scan
FROM scans 
GROUP BY target 
ORDER BY scan_count DESC 
LIMIT 10;

-- Wyniki z otwartymi portami
SELECT 
    target,
    scanner,
    results->'open_ports' as open_ports,
    created_at
FROM scans 
WHERE results->'open_ports' IS NOT NULL
AND jsonb_array_length(results->'open_ports') > 0;
```

---

## 12. 🔒 Bezpieczeństwo i uwierzytelnianie

### Obecny stan bezpieczeństwa

**⚠️ UWAGA:** Obecna wersja Reconnity EASM nie ma implementowanego uwierzytelniania. To demo/development setup. Dla produkcji MUSISZ dodać bezpieczeństwo!

### Implementacja uwierzytelniania JWT

#### **1. Konfiguracja JWT:**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os

# Konfiguracja
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Sprawdza hasło"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashuje hasło"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tworzy JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Weryfikuje JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

#### **2. Model użytkownika:**
```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from enum import Enum
import uuid

from app.models.base import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
```

#### **3. Dependency dla uwierzytelniania:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import verify_token

# HTTP Bearer token scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Pobiera obecnego użytkownika z tokenu"""
    token = credentials.credentials
    payload = verify_token(token)
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )
    
    return user

def require_role(required_role: UserRole):
    """Decorator wymagający określonej roli"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Shortcuts dla ról
require_admin = require_role(UserRole.ADMIN)
require_operator = require_role(UserRole.OPERATOR)
require_viewer = require_role(UserRole.VIEWER)
```

### Zabezpieczanie endpointów

```python
# app/api/routers/scan.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_active_user, require_operator
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator)  # Wymaga roli operator lub admin
):
    """Tworzy nowy skan - wymaga uprawnień operator"""
    # Logika tworzenia skanu...
    pass

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Wymaga logowania
):
    """Pobiera skan - wymaga uwierzytelnienia"""
    # Logika pobierania skanu...
    pass
```

---

## 13. 📊 Monitoring i logi

### Konfiguracja logowania

```python
import logging
import sys
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/app.log')
        ]
    )
    
    # JSON formatter dla produkcji
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger("easm-core")
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)
```

### Metryki aplikacji

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metryki
scan_requests_total = Counter('scan_requests_total', 'Total scan requests', ['scanner', 'status'])
scan_duration_seconds = Histogram('scan_duration_seconds', 'Scan duration', ['scanner'])
active_scans = Gauge('active_scans', 'Currently active scans')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Wywołanie aplikacji
            await self.app(scope, receive, send)
            
            # Zbieranie metryk
            duration = time.time() - start_time
            path = scope["path"]
            method = scope["method"]
            
            if path.startswith("/api/v1/scan"):
                scan_requests_total.labels(scanner="unknown", status="success").inc()
                scan_duration_seconds.labels(scanner="unknown").observe(duration)
        else:
            await self.app(scope, receive, send)

# Uruchomienie serwera metryk
start_http_server(8000)
```

### Health Check zaawansowany

```python
from fastapi import APIRouter
from app.database import get_db
from redis import Redis
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Sprawdzenie bazy danych
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Sprawdzenie Redis
    try:
        redis_client = Redis.from_url(os.getenv("REDIS_URL"))
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
```

---

## 14. 🧪 Testy i quality assurance

### Struktura testów

#### **Pytest konfiguracja**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models.base import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

#### **Testy API**
```python
import pytest
from fastapi.testclient import TestClient

def test_create_scan(client):
    """Test tworzenia nowego skanu"""
    response = client.post("/api/v1/scan", json={
        "target": "google.com",
        "scanner": "nmap",
        "options": {"ports": "80,443"}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "google.com"
    assert data["scanner"] == "nmap"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_scan_options(client):
    """Test pobierania opcji skanowania"""
    response = client.get("/api/v1/scan/options")
    
    assert response.status_code == 200
    data = response.json()
    assert "scanners" in data
    assert "nmap" in data["scanners"]

def test_health_check(client):
    """Test health check"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
```

#### **Uruchamianie testów**
```bash
# Instalacja zależności testowych
pip install pytest pytest-asyncio pytest-mock

# Uruchomienie wszystkich testów
pytest

# Uruchomienie z coverage
pytest --cov=app

# Uruchomienie konkretnych testów
pytest tests/test_api.py::test_create_scan -v

# Uruchomienie testów w trybie watch
pytest-watch
```

---

## 15. 🎯 Podsumowanie dla kolegi

### Gdy ktoś pyta "Co to za projekt?":

**"To jest EASM - External Attack Surface Management. System do automatycznego skanowania i monitorowania wszystkich zasobów firmy widocznych z internetu."**

### Gdy ktoś pyta "Jak to działa?":

**"To mikroservices w Dockerze. Masz FastAPI Core jako mózg, PostgreSQL jako bazę danych, Redis jako kolejkę zadań, i osobne kontenery dla każdego skanera - Nmap, Masscan, Nuclei. Wszystko komunikuje się przez Redis."**

### Gdy ktoś pyta "Jak dodać nowy skaner?":

**"Tworzysz nowy folder w /scanners, implementujesz funkcję run_X_scan w Python z ARQ, dodajesz Dockerfile, rejestrujesz w scan_service.py i dodajesz do docker-compose.yml. Gotowe!"**

### Gdy ktoś pyta "Jakie technologie?":

**"FastAPI bo szybkie i async, PostgreSQL bo obsługuje JSON, Redis bo szybka kolejka, Docker bo izolacja skanerów, ARQ bo async Celery, Vue.js na frontend."**

---

## 🏆 Gratulacje!

Teraz znasz Reconnity EASM na wylot! Możesz:

- ✅ Wytłumaczyć architekturę mikroservices
- ✅ Pokazać gdzie co się znajduje w kodzie
- ✅ Dodać nowy skaner krok po kroku
- ✅ Debugować problemy systemowe
- ✅ Korzystać z API i bazy danych
- ✅ Skonfigurować bezpieczeństwo
- ✅ Monitorować system i analizować logi
- ✅ Pisać i uruchamiać testy
- ✅ Opowiedzieć koledze o całym projekcie

### 📚 Dalsze kroki:

1. **Praktyka** - Dodaj swój pierwszy skaner
2. **Rozbudowa** - Zaimplementuj frontend Vue.js
3. **Produkcja** - Wdróż system na prawdziwym serwerze
4. **Społeczność** - Podziel się projektem z innymi

---

> **Autor:** GitHub Copilot  
> **Data:** Lipiec 2025  
> **Wersja:** 1.0
