# EASM API - Co Musisz Wiedzieć

## 1. Czym jest EASM API?

EASM API to brama API (API Gateway) w systemie External Attack Surface Management (EASM). Jest to **pierwszy punkt kontaktu** dla klientów zewnętrznych, którzy chcą korzystać z funkcji systemu EASM. Działa jak "recepcjonista" całego systemu - przyjmuje zapytania od użytkowników i kieruje je do odpowiednich usług wewnętrznych.

## 2. Jak działa EASM API?

### 2.1. Schemat działania w prostych krokach:

1. **Klient** (np. aplikacja webowa, aplikacja mobilna lub inny system) wysyła żądanie do EASM API.
2. **EASM API** odbiera to żądanie, sprawdza jego poprawność i przekazuje je do właściwej usługi wewnętrznej (najczęściej do `easm-core`).
3. **EASM API** odbiera odpowiedź od usługi wewnętrznej.
4. **EASM API** formatuje tę odpowiedź i odsyła ją z powrotem do klienta.

To tak, jakbyś rozmawiał z pracownikiem recepcji (EASM API), który przekazuje Twoje pytanie odpowiedniemu specjaliście (easm-core), a następnie przekazuje Ci jego odpowiedź.

### 2.2. Techniczne aspekty działania:

- **Framework**: Moduł używa FastAPI - szybkiego i nowoczesnego frameworka webowego dla Pythona.
- **Komunikacja między usługami**: Używa biblioteki `httpx` do asynchronicznego wykonywania zapytań HTTP do innych usług.
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

### 3.2. Endpoint tworzenia skanowania
- **URL**: `/api/v1/scan`
- **Metoda**: POST
- **Opis**: Pozwala stworzyć nowe zadanie skanowania bezpieczeństwa dla podanego celu.
- **Dane wejściowe**:
  ```json
  {
    "target": "example.com",
    "scanner": "nmap",
    "options": {"ports": "80,443"}
  }
  ```
- **Przykładowa odpowiedź**:
  ```json
  {
    "scan_id": "1cad57a9-b4d3-4579-bd1b-5d43ffb8e5cf",
    "status": "queued",
    "message": "Scan queued for target example.com"
  }
  ```

### 3.3. Endpoint sprawdzania statusu skanowania
- **URL**: `/api/v1/scan/{scan_id}`
- **Metoda**: GET
- **Opis**: Pozwala sprawdzić status i wyniki konkretnego skanowania.
- **Przykładowa odpowiedź**:
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

EASM API przekazuje żądania do usługi `easm-core` używając HTTP. Adres tej usługi jest konfigurowany przez zmienną środowiskową `CORE_URL` (domyślnie `http://core:8001`).

Przykład:
1. Klient wysyła żądanie: `POST /api/v1/scan` do EASM API (port 8080)
2. EASM API przekazuje to żądanie do easm-core: `POST /api/v1/scan` (port 8001)
3. EASM API otrzymuje odpowiedź z easm-core i przekazuje ją klientowi

### 4.2. Obsługa błędów

EASM API obsługuje różne rodzaje błędów:

- **Timeout**: Gdy easm-core nie odpowiada w ciągu 30 sekund, klient otrzymuje błąd 503 (Service Unavailable).
- **Błędy HTTP**: Gdy easm-core zwraca błąd (np. 404 Not Found), EASM API przekazuje ten sam kod statusu klientowi z odpowiednim komunikatem.
- **Nieoczekiwane błędy**: W przypadku innych problemów, klient otrzymuje błąd 500 (Internal Server Error).

## 5. Aspekty techniczne i wdrożeniowe

### 5.1. Wymagania i zależności

EASM API wymaga następujących bibliotek:
- fastapi v0.111.0
- uvicorn[standard] v0.29.0
- httpx v0.27.0
- pydantic v2.7.1
- python-jose[cryptography] v3.3.0
- python-multipart ≥0.0.7

### 5.2. Uruchamianie i konfiguracja

EASM API jest uruchamiane jako kontener Dockera na porcie 8080 (mapowanym z portu 8000 wewnątrz kontenera). Można go skonfigurować za pomocą następujących zmiennych środowiskowych:

- `CORE_URL`: URL do usługi easm-core (domyślnie: `http://core:8001`)
- `CELERY_BROKER_URL`: URL do brokera Redis (domyślnie: `redis://redis:6379/0`)

### 5.3. Kontener Dockera

EASM API używa obrazu bazowego `python:3.11-slim`, instaluje zależności z `requirements.txt` i uruchamia aplikację FastAPI za pomocą Uvicorn na porcie 8000 wewnątrz kontenera.

## 6. Podsumowanie - co musisz wiedzieć na pewno

1. **EASM API to brama do całego systemu** - wszystkie zewnętrzne zapytania przechodzą przez niego.
2. **Służy jako "fasada"** - upraszcza interakcję z systemem, ukrywając jego wewnętrzną złożoność.
3. **Przekazuje żądania do easm-core** - nie zawiera własnej logiki biznesowej, tylko przekierowuje zapytania.
4. **Dostępny na porcie 8080** - jest to główny punkt wejścia API dla klientów.
5. **Zapewnia 3 główne endpointy**:
   - `/health` - sprawdzenie stanu systemu
   - `/api/v1/scan` (POST) - tworzenie nowego skanu
   - `/api/v1/scan/{scan_id}` (GET) - sprawdzenie statusu/wyników skanu
6. **Obsługuje błędy i timeouty** - zapewnia spójne i czytelne komunikaty o błędach.

## 7. Najczęstsze problemy i rozwiązania

### Problem 1: API zwraca błąd "Core service timeout"
**Rozwiązanie**: Sprawdź, czy usługa easm-core działa poprawnie. Może być przeciążona lub niedostępna.

### Problem 2: API zwraca błąd "Scan not found"
**Rozwiązanie**: Upewnij się, że używasz prawidłowego identyfikatora skanowania (scan_id). Skanowanie mogło zostać usunięte lub nigdy nie istniało.

### Problem 3: API zwraca błąd 500 (Internal Server Error)
**Rozwiązanie**: Sprawdź logi kontenera easm-api i easm-core, aby znaleźć przyczynę problemu. Może to być problem z bazą danych, nieoczekiwany format danych lub inny błąd serwera.

## 8. Schemat architektoniczny

```
   Klient                EASM API (port 8080)              EASM Core (port 8001)
     │                         │                                   │
     │  ┌─────────────┐        │                                   │
     ├──► POST /scan  ├────────┼───────────────────────────────────┤
     │  └─────────────┘        │                                   │
     │                         │     ┌─────────────────────┐       │
     │                         │     │ Sprawdzenie żądania │       │
     │                         │     └─────────────────────┘       │
     │                         │                │                  │
     │                         │                ▼                  │
     │                         │     ┌─────────────────────┐       │
     │                         │     │   Przekazanie do    │       │
     │                         │     │     easm-core       ├───────┼────▶
     │                         │     └─────────────────────┘       │
     │                         │                                   │     ┌─────────────┐
     │                         │                                   │     │ Przetwarzanie│
     │                         │                                   │     │    skanu     │
     │                         │                                   │     └─────────────┘
     │                         │                                   │            │
     │                         │     ┌─────────────────────┐       │            ▼
     │                         │     │  Odbiór odpowiedzi  │◄──────┼────────────
     │                         │     └─────────────────────┘       │
     │                         │                │                  │
     │  ┌─────────────┐        │                ▼                  │
     │◄─┤  Odpowiedź  │◄───────┼───────────────────────────────────┤
     │  └─────────────┘        │                                   │
     ▼                         ▼                                   ▼
```

To jest EASM API w pigułce! Jeśli cokolwiek będzie niejasne lub będziesz potrzebować dodatkowych informacji, zawsze możesz wrócić do tego dokumentu lub bezpośrednio przeanalizować kod źródłowy.
