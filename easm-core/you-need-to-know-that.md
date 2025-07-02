# EASM Core - Co Musisz Wiedzieć

## 1. Czym jest EASM Core?

EASM Core to **centralny moduł biznesowy** w systemie External Attack Surface Management (EASM). Jest to "mózg" całego systemu, który:
- Zarządza skanowaniem zasobów internetowych
- Przechowuje dane w bazie danych
- Koordynuje pracę skanerów bezpieczeństwa
- Analizuje wyniki i oblicza poziom ryzyka
- Udostępnia API dla innych usług

Wyobraź sobie EASM Core jako centrum dowodzenia, które zleca zadania specjalistycznym jednostkom (skanerom), a następnie analizuje i przechowuje zebrane przez nie informacje.

## 2. Architektura EASM Core

EASM Core został zaprojektowany zgodnie z **zasadami Clean Architecture**, co oznacza, że kod jest podzielony na warstwy z jasno określonymi odpowiedzialnościami:

### 2.1. Warstwy architektury:

1. **Interfejsy API** (`app/api/`) - przyjmują żądania HTTP i przekazują je do odpowiednich usług
2. **Usługi** (`app/services/`) - zawierają logikę biznesową
3. **Modele** (`app/models/`) - reprezentują struktury danych w bazie
4. **Schematy** (`app/schemas/`) - definiują struktury danych na poziomie API
5. **Baza danych** (`app/database.py`) - zarządza połączeniem i sesjami bazy danych
6. **Zadania** (`app/tasks/`) - obsługują zadania asynchroniczne i długotrwałe
7. **Silnik analizy ryzyka** (`app/risk_engine.py`) - oblicza poziom ryzyka na podstawie znalezisk

Taki podział na warstwy sprawia, że kod jest:
- Łatwiejszy do zrozumienia
- Łatwiejszy do testowania
- Łatwiejszy do rozbudowy
- Odporny na zmiany w jednej warstwie, które nie wpływają na inne

## 3. Kluczowe funkcje EASM Core

### 3.1. Zarządzanie skanami

EASM Core pozwala na:
- **Tworzenie skanów** - przyjmowanie żądań skanowania z podanym celem i opcjami
- **Monitorowanie postępu** - śledzenie statusu skanów (kolejkowane, uruchomione, zakończone, nieudane)
- **Pobieranie wyników** - dostęp do wyników skanowania i analizy ryzyka

### 3.2. Koordynacja skanerów

Core deleguje faktyczne skanowanie do wyspecjalizowanych modułów:
- **scanner-nmap** - dla szczegółowych skanów portów i usług
- **scanner-masscan** - dla szybkich skanów dużych zakresów IP

### 3.3. Analiza ryzyka

Po otrzymaniu wyników skanowania, EASM Core:
1. Identyfikuje znalezione problemy (otwarte porty, usługi, podatności)
2. Klasyfikuje je według poziomu ryzyka
3. Oblicza ogólny wskaźnik ryzyka dla skanowanego zasobu

## 4. Przepływ danych w EASM Core

Oto jak dane przepływają przez system:

1. **Przyjęcie żądania** - API otrzymuje żądanie utworzenia nowego skanu
2. **Zapisanie w bazie danych** - tworzony jest nowy rekord skanu w statusie "queued"
3. **Delegowanie do skanera** - zadanie jest wysyłane do odpowiedniego skanera przez Celery
4. **Oczekiwanie na wyniki** - skaner wykonuje skan i wysyła wyniki z powrotem
5. **Aktualizacja w bazie danych** - wyniki są zapisywane w bazie danych
6. **Analiza ryzyka** - obliczany jest poziom ryzyka
7. **Udostępnienie wyników** - wyniki są dostępne przez API

## 5. Szczegóły techniczne

### 5.1. Technologie i zależności

EASM Core korzysta z następujących technologii:

- **FastAPI** - szybki framework webowy
- **SQLAlchemy** - ORM do komunikacji z bazą danych
- **PostgreSQL** - baza danych relacyjna
- **Celery** - system zarządzania zadaniami asynchronicznymi
- **Redis** - broker wiadomości dla Celery
- **Pydantic** - walidacja i serializacja danych

### 5.2. Modele danych

Główne modele w systemie:

- **Scan** - reprezentuje pojedyncze zadanie skanowania
- **Asset** - reprezentuje skanowany zasób (IP, domena)
- **Finding** - reprezentuje pojedyncze znalezisko (port, usługa, podatność)

### 5.3. Endpointy API

EASM Core udostępnia następujące endpointy:

- **GET /health** - endpoint sprawdzający stan systemu
- **POST /api/v1/scan** - tworzenie nowego skanu
- **GET /api/v1/scan/{scan_id}** - pobieranie statusu i wyników skanu
- **POST /api/v1/scan/{scan_id}/complete** - oznaczenie skanu jako zakończonego (używane przez skanery)
- **POST /api/v1/scan/{scan_id}/fail** - oznaczenie skanu jako nieudanego (używane przez skanery)

## 6. Cykl życia skanu

Poniżej przedstawiam pełny cykl życia skanu w systemie EASM:

1. **Utworzenie** - API Gateway przekazuje żądanie do Core, który tworzy rekord w bazie danych
2. **Kolejkowanie** - Skan jest kolejkowany do wykonania (status "queued")
3. **Delegowanie** - Core wysyła zadanie do odpowiedniego skanera przez Celery
4. **Uruchomienie** - Skaner rozpoczyna skanowanie i aktualizuje status na "running"
5. **Wykonanie** - Skaner wykonuje wszystkie niezbędne operacje
6. **Zakończenie** - Skaner wysyła wyniki z powrotem do Core, który aktualizuje bazę danych
7. **Analiza** - Core analizuje znalezione problemy i oblicza poziom ryzyka
8. **Udostępnienie** - Wyniki są dostępne przez API dla innych usług i użytkowników

## 7. Silnik analizy ryzyka

EASM Core zawiera zaawansowany silnik analizy ryzyka, który:

1. Analizuje otwarte porty (przypisując wyższe ryzyko niestandardowym portom)
2. Ocenia wykryte usługi (zwracając szczególną uwagę na przestarzałe lub niezabezpieczone)
3. Klasyfikuje podatności według ich krytyczności
4. Łączy te czynniki w ogólny wskaźnik ryzyka

Wagi ryzyka:
- Otwarte porty: 30%
- Usługi: 25%
- Podatności: 35%
- Ekspozycja: 10%

## 8. Konfiguracja i uruchamianie

EASM Core można skonfigurować za pomocą zmiennych środowiskowych:

- `DATABASE_URL` - URL do bazy danych PostgreSQL
- `CELERY_BROKER_URL` - URL do brokera Redis
- `LOG_LEVEL` - poziom logowania (debug, info, warning, error)

Usługa jest uruchamiana jako kontener Docker na porcie 8001.

## 9. Typowe problemy i rozwiązania

### Problem 1: Skan pozostaje w statusie "queued"
**Rozwiązanie**: Sprawdź, czy odpowiedni skaner jest uruchomiony. Sprawdź logi Celery, aby upewnić się, że zadanie zostało poprawnie wysłane.

### Problem 2: Skaner nie może wysłać wyników z powrotem do Core
**Rozwiązanie**: Upewnij się, że zmienna środowiskowa `CORE_URL` jest prawidłowo ustawiona w kontenerze skanera.

### Problem 3: Błąd "Database connection failed" przy uruchamianiu Core
**Rozwiązanie**: Upewnij się, że baza danych PostgreSQL jest uruchomiona i dostępna pod adresem określonym w `DATABASE_URL`.

## 10. Schemat struktury projektu

```
easm-core/
  app/
    api/                  # Warstwa API
      routers/            # Endpointy REST API
        health.py         # Endpoint zdrowia
        scan.py           # Endpointy skanowania
      dependencies.py     # Zależności FastAPI
      errors.py           # Obsługa błędów
    
    core/                 # Konfiguracja i narzędzia podstawowe
      logging.py          # Konfiguracja logowania
      security.py         # Funkcje bezpieczeństwa
      settings.py         # Ustawienia aplikacji
    
    db/                   # Operacje na bazie danych
      migrations/         # Migracje bazy danych
      repositories/       # Repozytoria dla operacji CRUD
    
    models/               # Modele bazy danych (SQLAlchemy)
      asset.py            # Model Asset
      base.py             # Klasa bazowa dla modeli
      finding.py          # Model Finding i RiskScore
      scan.py             # Model Scan
    
    schemas/              # Schematy Pydantic dla API
      asset.py            # Schema Asset
      finding.py          # Schematy Finding i RiskScore
      health.py           # Schema HealthCheck
      scan.py             # Schematy ScanRequest, ScanResponse
    
    services/             # Warstwa usług (logika biznesowa)
      scan_service.py     # Usługa zarządzająca skanami
    
    tasks/                # Zadania Celery
      scan_tasks.py       # Zadania związane ze skanowaniem
    
    database.py           # Konfiguracja bazy danych
    main.py               # Główny plik aplikacji
    risk_engine.py        # Silnik analizy ryzyka
```

## 11. Podsumowanie - co musisz wiedzieć na pewno

1. **EASM Core to "mózg" systemu** - zawiera całą logikę biznesową i zarządza danymi
2. **Korzysta z architektury warstwowej** - zgodnie z zasadami Clean Architecture
3. **Działa jako koordynator skanerów** - deleguje zadania do wyspecjalizowanych modułów
4. **Przechowuje wszystkie dane** - wyniki skanów, znaleziska, oceny ryzyka
5. **Udostępnia API** - dla zewnętrznych usług (np. EASM API)
6. **Analizuje ryzyko** - oblicza poziom ryzyka na podstawie znalezionych problemów
7. **Dostępny na porcie 8001** - ale zwykle nie jest bezpośrednio dostępny z zewnątrz

## 12. Diagram przepływu danych

```
Zewnętrzne żądanie    EASM API             EASM Core              Skanery             Baza danych
     │                   │                    │                      │                    │
     │                   │                    │                      │                    │
     │    Żądanie        │                    │                      │                    │
     │ ────────────────► │    Przekazanie     │                      │                    │
     │                   │ ────────────────► │                      │                    │
     │                   │                    │  Zapis żądania       │                    │
     │                   │                    │ ───────────────────────────────────────► │
     │                   │                    │                      │                    │
     │                   │                    │  Delegowanie zadania │                    │
     │                   │                    │ ────────────────────► │                    │
     │                   │                    │                      │   Skanowanie       │
     │                   │                    │                      │ ◄─────────────────►│
     │                   │                    │                      │                    │
     │                   │                    │  Wysłanie wyników    │                    │
     │                   │                    │◄─────────────────────┤                    │
     │                   │                    │                      │                    │
     │                   │                    │  Analiza ryzyka      │                    │
     │                   │                    │◄───────────────────► │                    │
     │                   │                    │                      │                    │
     │                   │                    │  Zapis wyników       │                    │
     │                   │                    │ ───────────────────────────────────────► │
     │                   │   Odpowiedź        │                      │                    │
     │                   │◄─────────────────── │                      │                    │
     │    Odpowiedź      │                    │                      │                    │
     │◄─────────────────┤                    │                      │                    │
     │                   │                    │                      │                    │
     ▼                   ▼                    ▼                      ▼                    ▼
```

## 13. Wskazówki dla programistów

1. **Zachowaj warstwy** - Nie mieszaj logiki API z logiką biznesową. Używaj warstwy serwisów.
2. **Używaj zależności** - Korzystaj z systemu wstrzykiwania zależności FastAPI.
3. **Waliduj dane** - Używaj schematów Pydantic do walidacji danych wejściowych.
4. **Loguj ważne zdarzenia** - Korzystaj z `get_logger()` z modułu `core.logging`.
5. **Obsługuj błędy** - Używaj niestandardowych wyjątków z `api.errors`.
6. **Tesuj kod** - Pisz testy dla każdej warstwy (API, usługi, modele).

Pamiętaj, że EASM Core jest sercem całego systemu - jakiekolwiek zmiany tutaj mogą wpłynąć na wszystkie inne komponenty, dlatego zawsze dokładnie testuj wprowadzane modyfikacje!
