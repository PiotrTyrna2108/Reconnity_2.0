# EASM API - Co Musisz Wiedzieć

## 1. Czym jest EASM API?

EASM API to brama API (API Gateway) w systemie External Attack Surface Management (EASM). Jest to **pierwszy punkt kontaktu** dla klientów zewnętrznych, którzy chcą korzystać z funkcji systemu EASM. Działa jak "transparent proxy" - przyjmuje wszystkie zapytania od użytkowników i przekazuje je bezpośrednio do odpowiednich usług wewnętrznych, ukrywając wewnętrzną architekturę systemu.

## 2. Jak działa EASM API?

### 2.1. Schemat działania w prostych krokach:

1. **Klient** (np. aplikacja webowa, aplikacja mobilna lub inny system) wysyła żądanie do EASM API.
2. **EASM API** odbiera to żądanie i przekazuje je bez modyfikacji do serwisu `easm-core`.
3. **EASM API** odbiera odpowiedź od `easm-core`.
4. **EASM API** przekazuje tę odpowiedź bez modyfikacji z powrotem do klienta.

EASM API działa jako "przezroczysty pośrednik" - przekazuje zapytania i odpowiedzi bez zmiany ich treści, zapewniając jednocześnie, że wszystkie zewnętrzne żądania przechodzą przez jeden punkt wejścia.

### 2.2. Techniczne aspekty działania:

- **Framework**: Moduł używa FastAPI - szybkiego i nowoczesnego frameworka webowego dla Pythona.
- **Proxy uniwersalne**: Używa jednego uniwersalnego endpointu, który obsługuje wszystkie ścieżki i metody HTTP (GET, POST, PUT, DELETE).
- **Komunikacja między usługami**: Używa biblioteki `httpx` do asynchronicznego wykonywania zapytań HTTP do `easm-core`.
- **Logowanie**: Wykorzystuje standardową bibliotekę `logging` do rejestrowania ważnych zdarzeń i błędów.

## 3. Jakie są dostępne endpointy?

EASM API udostępnia następujące endpointy:

### 3.1. Endpoint zdrowia systemu
- **URL**: `/health`
- **Metoda**: GET
- **Opis**: Pozwala sprawdzić, czy API działa prawidłowo.
- **Przykładowa odpowiedź**:
  ```json
  {"status": "healthy", "service": "easm-api"}
  ```

### 3.2. Uniwersalny endpoint proxy
- **URL**: `/api/v1/*` (wszystkie ścieżki)
- **Metody**: GET, POST, PUT, DELETE
- **Opis**: Przekazuje wszystkie żądania do odpowiadających im endpointów w `easm-core`.

#### Przykłady popularnych ścieżek:

- **Tworzenie skanu** - `POST /api/v1/scan`
  ```json
  {
    "target": "example.com",
    "scanner": "nmap",
    "options": {"ports": "80,443"}
  }
  ```
  
- **Sprawdzanie statusu** - `GET /api/v1/scan/{scan_id}`
  ```json
  {
    "scan_id": "1cad57a9-b4d3-4579-bd1b-5d43ffb8e5cf",
    "target": "example.com",
    "scanner": "nmap",
    "status": "completed",
    "progress": 100,
    "created_at": "2025-07-02T21:37:36.518143",
    "started_at": "2025-07-02T21:37:38.123456",
    "completed_at": "2025-07-02T21:40:12.345678",
    "results": { /* Szczegółowe wyniki skanowania */ },
    "findings": [ /* Lista znalezionych podatności */ ],
    "risk_score": { /* Ocena ryzyka */ },
    "error": null
  }
  ```

## 4. Jak EASM API komunikuje się z innymi usługami?

### 4.1. Komunikacja z easm-core

EASM API przekazuje wszystkie żądania do usługi `easm-core` używając HTTP, zachowując oryginalne metody, nagłówki, parametry zapytań i ciała żądań. Adres `easm-core` jest konfigurowany przez zmienną środowiskową `CORE_URL` (domyślnie `http://core:8001`).

**Przykład przepływu żądania:**
1. Klient wysyła żądanie: `POST /api/v1/scan` do EASM API (port 8080)
2. EASM API przekazuje to żądanie do easm-core: `POST /api/v1/scan` (port 8001)
3. EASM API otrzymuje odpowiedź z easm-core
4. EASM API przekazuje niezmienioną odpowiedź klientowi, zachowując oryginalny kod statusu, nagłówki i zawartość

**Szczegóły procesu proxy:**
- Wszystkie metody HTTP (GET, POST, PUT, DELETE) są obsługiwane
- Wszystkie nagłówki są przekazywane (z wyjątkiem technicznych jak "host" i "content-length")
- Parametry zapytania (query strings) są zachowane
- Ciała żądań JSON są przesyłane bez zmian
- Typy zawartości (Content-Type) są zachowane w obu kierunkach

### 4.2. Obsługa błędów

EASM API obsługuje różne rodzaje błędów:

- **Timeout**: Gdy easm-core nie odpowiada w ciągu 30 sekund, klient otrzymuje błąd 503 (Service Unavailable).
- **Błędy HTTP**: Gdy easm-core zwraca błąd (np. 404 Not Found), EASM API przekazuje ten sam kod statusu klientowi, zachowując oryginalny komunikat błędu.
- **Nieoczekiwane błędy**: W przypadku wewnętrznych problemów z proxy, klient otrzymuje błąd 500 (Internal Server Error).

## 5. Aspekty techniczne i wdrożeniowe

### 5.1. Wymagania i zależności

EASM API ma bardzo minimalne zależności:
- fastapi v0.111.0+ - do obsługi zapytań HTTP
- uvicorn[standard] v0.29.0+ - jako serwer ASGI
- httpx v0.27.0+ - do asynchronicznego przekazywania żądań do easm-core
- pydantic v2.7.1+ - używana przez FastAPI

### 5.2. Uruchamianie i konfiguracja

EASM API jest uruchamiane jako kontener Dockera na porcie 8080 (mapowanym z portu 8000 wewnątrz kontenera). Można go skonfigurować za pomocą następującej zmiennej środowiskowej:

- `CORE_URL`: URL do usługi easm-core (domyślnie: `http://core:8001`)

### 5.3. Kontener Dockera

EASM API używa obrazu bazowego `python:3.11-slim`, instaluje minimalne zależności z `requirements.txt` i uruchamia aplikację FastAPI za pomocą Uvicorn na porcie 8000 wewnątrz kontenera.

### 5.4. Zalety uproszczonego podejścia proxy

Implementacja EASM API jako prostego proxy ma kilka istotnych zalet:

- **Eliminacja duplikacji kodu** - brak konieczności synchronizacji modeli danych między API i Core
- **Automatyczna zgodność** - wszystkie zmiany w API Core są natychmiast dostępne przez API Gateway 
- **Uproszczona konserwacja** - mniej kodu do utrzymania i testowania
- **Jednolite API** - klienci zawsze otrzymują tę samą strukturę odpowiedzi, co zapewnia Core
- **Centralizacja logiki biznesowej** - cała logika biznesowa, w tym obsługa złożonych żądań (np. skanowanie typu "all" używające wielu skanerów), znajduje się w `easm-core`

## 6. Podsumowanie - co musisz wiedzieć na pewno

1. **EASM API to uniwersalny proxy** - wszystkie zewnętrzne zapytania przechodzą przez niego i są przekazywane bezpośrednio do easm-core.
2. **Zero logiki biznesowej** - API Gateway nie zawiera żadnej własnej logiki biznesowej, co eliminuje duplikację kodu i upraszcza utrzymanie. Wszystkie złożone operacje (w tym obsługa skanowania typu "all") są realizowane wyłącznie w easm-core.
3. **Dostępny na porcie 8080** - jest to główny punkt wejścia API dla klientów.
4. **Obsługuje wszystkie metody HTTP** - GET, POST, PUT, DELETE są przekazywane w niezmienionej formie.
5. **Zachowuje wszystkie szczegóły żądań** - nagłówki, parametry zapytania i ciała żądań są przekazywane bez zmian.
6. **Zapewnia przejrzysty endpoint zdrowia** - `/health` pozwala monitorować status samego API Gateway.
7. **Dostęp do pełnego API easm-core** - wszystkie endpointy dostępne w easm-core są automatycznie dostępne przez API Gateway pod tą samą ścieżką.
8. **Automatyczna zgodność z nowymi funkcjami** - każda nowa funkcjonalność dodana do easm-core jest natychmiast dostępna przez API Gateway bez konieczności aktualizacji kodu proxy.

## 7. Najczęstsze problemy i rozwiązania

### Problem 1: API zwraca błąd "Core service timeout"
**Rozwiązanie**: Sprawdź, czy usługa easm-core działa poprawnie. Może być przeciążona, niedostępna lub zajęta długotrwałym zadaniem.

### Problem 2: API zwraca błąd HTTP (np. 404 Not Found, 400 Bad Request)
**Rozwiązanie**: Sprawdź dokumentację easm-core, aby zrozumieć wymagania endpointu. Błędy HTTP są przekazywane bezpośrednio z easm-core, więc rozwiązanie należy szukać tam.

### Problem 3: API zwraca błąd 500 (Internal Server Error)
**Rozwiązanie**: Sprawdź logi kontenerów:
- W `easm-api` - aby sprawdzić, czy problem wystąpił podczas przekazywania żądania
- W `easm-core` - aby sprawdzić, czy problem wystąpił podczas przetwarzania żądania

### Problem 4: Problemy z przekazywaniem specjalnych nagłówków
**Rozwiązanie**: Sprawdź, czy używasz nagłówków, które mogą być filtrowane przez API Gateway (np. `host`, `content-length`). W razie potrzeby ustaw odpowiednie nagłówki na poziomie aplikacji.

## 8. Schemat architektoniczny (uproszczona wersja proxy)

```
  Klient                 EASM API (port 8080)                EASM Core (port 8001)
    │                           │                                    │
    │                           │                                    │
    │    Dowolne żądanie        │                                    │
    │  (GET, POST, PUT, DELETE) │                                    │
    ├──────────────────────────►│                                    │
    │                           │                                    │
    │                           │    Przekazanie żądania             │
    │                           │    bez modyfikacji                 │
    │                           ├───────────────────────────────────►│
    │                           │                                    │
    │                           │                                    │
    │                           │                                    │
    │                           │                                    │
    │                           │                                    │
    │                           │    Odpowiedź z easm-core           │
    │                           │    (status, nagłówki, ciało)       │
    │                           │◄───────────────────────────────────┤
    │                           │                                    │
    │                           │                                    │
    │    Odpowiedź przekazana   │                                    │
    │    bez modyfikacji        │                                    │
    │◄──────────────────────────┤                                    │
    │                           │                                    │
    ▼                           ▼                                    ▼
```

To jest EASM API w pigułce! Prostota jest kluczem - API Gateway działa jako przezroczyste proxy, eliminując duplikację kodu i upraszczając architekturę systemu.
