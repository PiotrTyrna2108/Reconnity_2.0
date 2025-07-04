# Struktura i funkcje plików w folderach skanerów

## scanner-nmap/

- **Dockerfile**
  - **Do czego służy:** Buduje obraz Dockera z Pythonem i narzędziem nmap.
  - **Funkcje:** Instalacja nmap, zależności Pythona, kopiowanie kodu, ustawienie uruchamiania workerów ARQ.
  - **Integracja z Core:** Pozwala uruchomić mikroserwis, który odbiera zadania z Core przez Redis/ARQ.

- **requirements.txt**
  - **Do czego służy:** Lista zależności Pythona.
  - **Funkcje:** Instalacja bibliotek wymaganych do działania mikroserwisu.
  - **Integracja z Core:** Umożliwia komunikację z Redis (kolejka zadań) i ewentualnie z Core przez HTTP.

- **app/__init__.py**
  - **Do czego służy:** Inicjalizuje pakiet Pythona dla aplikacji skanera.
  - **Funkcje:** Pozwala na import modułów z `app/`.
  - **Integracja z Core:** Brak bezpośredniej, pośrednio przez `main.py`.

- **app/main.py**
  - **Do czego służy:** Główny plik logiki mikroserwisu skanera nmap.
  - **Funkcje:**  
    - Definiuje worker ARQ i funkcję zadania (`run_nmap_scan`).
    - Buduje polecenie nmap na podstawie opcji.
    - Uruchamia skanowanie, przetwarza wyniki, wysyła je do EASM Core przez Redis/ARQ.
  - **Integracja z Core:**  
    - Odbiera zadania z kolejki Redis/ARQ wrzucane przez Core (`run_nmap_scan`).
    - Wysyła wyniki do Core przez Redis/ARQ (`process_scan_result`) lub przez REST API (jeśli zaimplementowane).
    - Korzysta z ENV (`REDIS_URL`, `CORE_URL`).

---

## scanner-masscan/

- **Dockerfile**
  - **Do czego służy:** Buduje obraz Dockera z Pythonem i narzędziem masscan.
  - **Funkcje:** Instalacja masscan, zależności Pythona, kopiowanie kodu, ustawienie uruchamiania workerów ARQ.
  - **Integracja z Core:** Pozwala uruchomić mikroserwis, który odbiera zadania z Core przez Redis/ARQ.

- **requirements.txt**
  - **Do czego służy:** Lista zależności Pythona.
  - **Funkcje:** Instalacja bibliotek wymaganych do działania mikroserwisu.
  - **Integracja z Core:** Umożliwia komunikację z Redis (kolejka zadań) i ewentualnie z Core przez HTTP.

- **app/__init__.py**
  - **Do czego służy:** Inicjalizuje pakiet Pythona dla aplikacji skanera.
  - **Funkcje:** Pozwala na import modułów z `app/`.
  - **Integracja z Core:** Brak bezpośredniej, pośrednio przez `main.py`.

- **app/main.py**
  - **Do czego służy:** Główny plik logiki mikroserwisu skanera masscan.
  - **Funkcje:**  
    - Definiuje worker ARQ i funkcję zadania (`run_masscan_scan`).
    - Buduje polecenie masscan na podstawie opcji.
    - Uruchamia skanowanie, przetwarza wyniki, wysyła je do EASM Core przez Redis/ARQ.
  - **Integracja z Core:**  
    - Odbiera zadania z kolejki Redis/ARQ wrzucane przez Core (`run_masscan_scan`).
    - Wysyła wyniki do Core przez Redis/ARQ (`process_scan_result`) lub przez REST API (jeśli zaimplementowane).
    - Korzysta z ENV (`REDIS_URL`, `CORE_URL`).

---

## scanner-nuclei/

- **Dockerfile**
  - **Do czego służy:** Buduje obraz Dockera z Pythonem i narzędziem nuclei (Go).
  - **Funkcje:** Buduje nuclei, kopiuje do obrazu Pythona, instaluje zależności, pobiera szablony, ustawia workerów ARQ.
  - **Integracja z Core:** Pozwala uruchomić mikroserwis, który odbiera zadania z Core przez Redis/ARQ.

- **requirements.txt**
  - **Do czego służy:** Lista zależności Pythona.
  - **Funkcje:** Instalacja bibliotek wymaganych do działania mikroserwisu.
  - **Integracja z Core:** Umożliwia komunikację z Redis (kolejka zadań) i ewentualnie z Core przez HTTP.

- **README.md**
  - **Do czego służy:** Dokumentacja mikroserwisu skanera nuclei.
  - **Funkcje:** Opis konfiguracji, opcji skanowania, integracji z Core, troubleshooting.
  - **Integracja z Core:** Opisuje jak działa komunikacja z EASM Core przez Redis/ARQ i REST API.

- **app/__init__.py**
  - **Do czego służy:** Inicjalizuje pakiet Pythona dla aplikacji skanera.
  - **Funkcje:** Pozwala na import modułów z `app/`.
  - **Integracja z Core:** Brak bezpośredniej, pośrednio przez `main.py`.

- **app/main.py**
  - **Do czego służy:** Główny plik logiki mikroserwisu skanera nuclei.
  - **Funkcje:**  
    - Definiuje worker ARQ i funkcję zadania (`run_nuclei_scan`).
    - Buduje polecenie nuclei na podstawie opcji.
    - Uruchamia skanowanie, przetwarza wyniki, wysyła je do EASM Core przez Redis/ARQ.
    - Obsługuje opcje skanowania (templates, severity, timeout, rate, concurrency, retries, verbose, follow_redirects, max_host_error).
  - **Integracja z Core:**  
    - Odbiera zadania z kolejki Redis/ARQ wrzucane przez Core (`run_nuclei_scan`).
    - Wysyła wyniki do Core przez Redis/ARQ (`process_scan_result`) lub przez REST API (jeśli zaimplementowane).
    - Korzysta z ENV (`REDIS_URL`, `CORE_URL`).

---

# Integracja skanerów z EASM Core

- **Skanery nie importują kodu Core bezpośrednio.**
- **Integrują się przez:**
  - Kolejkę Redis/ARQ (odbierają zadania wrzucane przez Core, np. `run_nmap_scan`, `run_masscan_scan`, `run_nuclei_scan`)
  - REST API Core (opcjonalnie, np. POST `/api/v1/scan/{scan_id}/complete`)
  - Zmienne środowiskowe (`REDIS_URL`, `CORE_URL`)

- **Wysyłka wyników:**  
  Skanery po zakończeniu zadania wysyłają wyniki do Core przez Redis/ARQ (`process_scan_result`) lub przez REST API.

---

**Podsumowanie:**  
Każdy plik w folderach skanerów odpowiada za uruchamianie, konfigurację, odbiór zadań i wysyłkę wyników do EASM Core – zawsze przez kolejkę Redis/ARQ lub REST API, nigdy przez bezpośredni import kodu Core.


---------------------------------

**Twoje skanery (scanner-nmap, scanner-masscan, scanner-nuclei)** nie wystawiają własnych endpointów HTTP/REST – komunikują się z EASM Core wyłącznie przez kolejkę zadań (Redis/ARQ) i ewentualnie wysyłają wyniki przez kolejkę lub REST do Core.

**To jest bardzo dobre podejście!**  
Dlaczego?

- **Bezpieczeństwo:** Skanery nie mają publicznego API, więc nie można ich atakować bezpośrednio z zewnątrz.
- **Izolacja:** Cała komunikacja idzie przez Core, który kontroluje przepływ zadań i wyników.
- **Prostota:** Skanery są prostymi workerami – odbierają zadania, wykonują je, raportują wyniki.

**Kiedy warto dodać endpointy do skanerów?**
- Jeśli chcesz mieć healthcheck (`/health`) do monitoringu kontenerów.
- Jeśli chcesz dynamicznie zarządzać szablonami (np. w nuclei: reload templates).
- Jeśli chcesz mieć endpoint do sprawdzania wersji narzędzia.

**Podsumowanie:**  
Jeśli Twoje skanery nie wystawiają żadnych endpointów HTTP – to jest poprawne i bezpieczne rozwiązanie dla architektury mikroserwisowej EASM.  
Jeśli chcesz, możesz dodać prosty `/health` tylko do monitoringu, ale nie jest to wymagane do działania systemu!

---

# Różnice między Quick Scan a Standard Scan - Dlaczego taki podział?

## 📋 Porównanie endpointów

### 🟢 Quick Scan: `/api/v1/scan/quick` - Parametry URL
```
POST /api/v1/scan/quick?target=scanme.nmap.org&scanner=nmap&ports=80,443&scan_type=SYN
```

**Charakterystyka:**
- ✅ **Parametry w URL** (query parameters)
- ✅ **Łatwe testowanie** w Swagger UI
- ✅ **Można skopiować URL** i uruchomić w przeglądarce/curl
- ✅ **Proste dla początkujących**
- ✅ **Szybkie prototypowanie**
- ⚠️ **Ograniczone opcje** (tylko podstawowe parametry)
- ⚠️ **Brak walidacji typów** (wszystko to stringi)

### 🟡 Standard Scan: `/api/v1/scan` - JSON Body
```json
{
  "target": "scanme.nmap.org",
  "scanner": "nmap", 
  "options": {
    "ports": "80,443,22",
    "scan_type": "SYN",
    "service_detection": true,
    "timing": 4,
    "os_detection": false
  }
}
```

**Charakterystyka:**
- ✅ **Pełna walidacja schematów** (Pydantic)
- ✅ **Type safety** (number, boolean, arrays)
- ✅ **Zaawansowane opcje** (obiekty, listy, nested data)
- ✅ **Produkcyjne API** dla aplikacji
- ✅ **Lepsze error handling**
- ⚠️ **Wymaga JSON knowledge**
- ⚠️ **Bardziej skomplikowane** do testowania

---

## 🎯 Przypadki użycia

### Quick Scan - Kiedy używać?
- **Testowanie i eksperymentowanie** z API
- **Debugging** - szybkie sprawdzenie czy skaner działa
- **Prototypowanie** nowych funkcji
- **Demonstracje** i prezentacje
- **Proste integracje** (np. skrypty bash)
- **Learning** - nauka jak działa API

**Przykłady:**
```bash
# Szybki test nmap
curl -X POST "http://localhost:8001/api/v1/scan/quick?target=scanme.nmap.org&scanner=nmap&ports=80,443"

# Test nuclei
curl -X POST "http://localhost:8001/api/v1/scan/quick?target=httpbin.org&scanner=nuclei&templates=tech-detect"

# Test masscan  
curl -X POST "http://localhost:8001/api/v1/scan/quick?target=192.168.1.1&scanner=masscan&ports=1-1000&rate=1000"
```

### Standard Scan - Kiedy używać?
- **Aplikacje produkcyjne**
- **Automatyzacja** (CI/CD, orchestracja)
- **Kompleksne konfiguracje** skanowania
- **API klienty** (JavaScript, Python, Go)
- **Bezpieczeństwo** - pełna walidacja danych
- **Skalowalne rozwiązania**

**Przykłady:**
```python
# Python API client
import requests

scan_config = {
    "target": "example.com",
    "scanner": "nmap",
    "options": {
        "ports": "1-65535",
        "scan_type": "SYN", 
        "service_detection": True,
        "os_detection": True,
        "timing": 3,
        "timeout": 600
    }
}

response = requests.post("http://localhost:8001/api/v1/scan", json=scan_config)
```

---

## 🔧 Implementacja techniczna

### Dlaczego nie wszystkie parametry w Quick Scan?

**1. Ograniczenia URL:**
- URL ma limity długości (~2000 znaków)
- Query parameters są zawsze stringami
- Brak wsparcia dla obiektów/tablic

**2. Type Safety:**
```bash
# W Quick Scan - wszystko to string
?ports=80,443&timing=4&os_detection=true

# W Standard Scan - właściwe typy
{
  "ports": "80,443",     // string
  "timing": 4,           // number  
  "os_detection": true   // boolean
}
```

**3. Zaawansowane opcje:**
```json
// Niemożliwe w URL, możliwe w JSON
{
  "options": {
    "nuclei": {
      "templates": ["tech-detect", "cves", "vulnerabilities"],
      "severity": ["high", "critical"],
      "custom_headers": {
        "User-Agent": "EASM-Scanner",
        "Authorization": "Bearer token123"
      }
    }
  }
}
```

### Architektura endpointów

**Quick Scan processing:**
1. Odbiera query parameters
2. Konwertuje na proste opcje
3. Przekazuje do tego samego `ScanService.create_scan()`
4. Kolejkuje zadanie przez Redis/ARQ

**Standard Scan processing:**  
1. Waliduje JSON schema (Pydantic)
2. Type checking i validation
3. Przekazuje do `ScanService.create_scan()`
4. Kolejkuje zadanie przez Redis/ARQ

**→ Oba endpointy używają tej samej logiki biznesowej!**

---

## 📚 Najlepsze praktyki

### Dla deweloperów/testerów:
```bash
# 1. Zacznij od Quick Scan
curl -X POST "http://localhost:8001/api/v1/scan/quick?target=scanme.nmap.org&scanner=nmap&ports=80"

# 2. Sprawdź status  
curl "http://localhost:8001/api/v1/scan/{scan_id}"

# 3. Gdy już rozumiesz API, przejdź na Standard Scan
```

### Dla aplikacji produkcyjnych:
```javascript
// Zawsze używaj Standard Scan w aplikacjach
const scanConfig = {
  target: userInput.target,
  scanner: "nmap",
  options: {
    ports: userInput.ports || "1-1000",
    scan_type: "SYN",
    service_detection: true
  }
};

const response = await fetch('/api/v1/scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(scanConfig)
});
```

### Dla DevOps/Automatyzacji:
```yaml
# docker-compose.yml lub Kubernetes
environment:
  - EASM_API_URL=http://easm-core:8001
  - SCAN_CONFIG={"target":"${TARGET}","scanner":"nmap","options":{"ports":"80,443"}}
```

---

## 🎨 Swagger UI Experience

### Quick Scan w Swagger:
- 📝 **Formularze** z polami input
- 🎛️ **Dropdowny** dla scanner type
- ✅ **Przykłady** w każdym polu
- 🚀 **Przycisk Execute** - natychmiastowy test

### Standard Scan w Swagger:
- 📄 **JSON Editor** z syntax highlighting  
- 🔍 **Schema validation** w czasie rzeczywistym
- 📋 **Przykłady** dla każdego skanera
- 🧪 **Pełna kontrola** nad wszystkimi opcjami

---

**Podsumowanie:** Quick Scan i Standard Scan to komplementarne podejścia - pierwsze dla wygody i szybkości, drugie dla mocy i elastyczności. Wybierz odpowiednie narzędzie do odpowiedniego zadania! 🚀