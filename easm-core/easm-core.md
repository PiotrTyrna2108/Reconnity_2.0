# Struktura i szczegółowy opis folderów oraz plików EASM Core

## app/
Główny katalog kodu aplikacji. Zawiera całą logikę backendu EASM Core.

---

### app/api/
Warstwa wejściowa – obsługa żądań HTTP (FastAPI).
- **__init__.py** – Inicjalizuje pakiet API.
- **dependencies.py** – Definiuje zależności FastAPI (np. pobieranie sesji bazy, autoryzacja).
- **errors.py** – Obsługa wyjątków i błędów HTTP.
- **routers/** – Endpointy REST API:
  - **__init__.py** – Rejestruje routery do głównej aplikacji.
  - **health.py** – Endpoint `/health` (sprawdzenie stanu systemu, opcjonalnie sprawdza połączenie z bazą).
  - **scan.py** – Endpointy do zarządzania skanami (`/api/v1/scan`, `/api/v1/scan/{scan_id}`, `/api/v1/scan/{scan_id}/complete`, `/api/v1/scan/{scan_id}/fail`).
  - **nuclei_templates.py** – Endpointy do zarządzania szablonami Nuclei (jeśli używane).
  - **scan_options.py** – Endpointy do pobierania dostępnych opcji skanowania.

---

### app/core/
Konfiguracja, narzędzia, logowanie, bezpieczeństwo.
- **__init__.py** – Inicjalizuje pakiet core.
- **logging.py** – Konfiguracja loggera, funkcja `get_logger()`.
- **security.py** – Funkcje związane z bezpieczeństwem (np. tokeny, autoryzacja).
- **settings.py** – Wczytywanie ustawień aplikacji (np. z env).

---

### app/db/
Operacje na bazie danych.
- **migrations/** – Migracje bazy danych (Alembic).
- **repositories/** – Repozytoria do operacji CRUD na modelach.

---

### app/models/
Modele bazy danych (SQLAlchemy).
- **__init__.py** – Inicjalizuje pakiet modeli.
- **asset.py** – Model `Asset` – zasób do skanowania (IP, domena).
- **base.py** – Klasa bazowa dla modeli (`Base = declarative_base()`).
- **finding.py** – Model `Finding` (znalezisko: port, usługa, podatność), `RiskScore`.
- **scan.py** – Model `Scan` – pojedyncze zadanie skanowania.

---

### app/schemas/
Schematy Pydantic do walidacji i serializacji danych w API.
- **__init__.py** – Inicjalizuje pakiet schemas.
- **asset.py** – Schematy do walidacji danych zasobów (`Asset`).
- **finding.py** – Schematy do walidacji znalezisk i ocen ryzyka.
- **health.py** – Schemat odpowiedzi dla `/health`.
- **scan.py** – Schematy do żądań i odpowiedzi związanych ze skanami.
- **scan_options.py** – Schematy opcji skanowania.

---

### app/services/
Logika biznesowa.
- **__init__.py** – Inicjalizuje pakiet services.
- **asset_service.py** – Operacje na zasobach (`Asset`).
- **finding_service.py** – Operacje na znaleziskach (`Finding`).
- **risk_service.py** – Logika oceny ryzyka.
- **scan_service.py** – Główna logika zarządzania skanami: tworzenie, aktualizacja, pobieranie, delegowanie do tasks.

---

### app/tasks/
Zadania asynchroniczne (Celery/ARQ).
- **__init__.py** – Inicjalizuje pakiet tasks.
- **config/** – Konfiguracja kolejek, Redis, retry helpers:
  - **__init__.py** – Inicjalizuje pakiet config.
  - **queue_config.py** – Konfiguracja kolejki zadań, worker settings.
  - **redis_config.py** – Konfiguracja połączenia z Redis.
  - **retry_helpers.py** – Funkcje pomocnicze do retry.
- **monitoring/** – Monitorowanie zadań:
  - **__init__.py** – Inicjalizuje pakiet monitoring.
  - **task_metrics.py** – Metryki zadań.
- **tasks/** – Zadania Celery/ARQ:
  - **__init__.py** – Inicjalizuje pakiet tasks.
  - **scan_tasks.py** – Zadania związane ze skanowaniem (`scan_asset`, `process_scan_result`).

---

### app/risk_engine.py
Silnik analizy ryzyka – oblicza poziom ryzyka na podstawie znalezisk.

---

### app/models.py
Prawdopodobnie stary plik lub agregator modeli (jeśli nie jest używany – można usunąć).

---

### Pliki główne i narzędziowe
- **main.py** – Główny plik uruchamiający aplikację FastAPI.
- **database.py** – Konfiguracja połączenia z bazą danych, sesje, inicjalizacja tabel.
- **Dockerfile** – Buduje obraz Dockera (instaluje zależności, kopiuje kod, ustawia entrypoint).
- **alembic.ini** – Konfiguracja migracji bazy danych (Alembic).
- **requirements.txt** – Zależności Pythona.

---

## Powiązania między plikami i warstwami
- **API (routers)** → **Services** → **Models/DB**
- **Services** → **Tasks**
- **Tasks** → **Services/Models**
- **Risk Engine** używany przez serwisy i tasks
- **Schemas** używane przez API i serwisy
- **Core** dostarcza narzędzia i konfigurację

---

## Przykładowy przepływ danych
1. Użytkownik wysyła żądanie skanowania przez API (`api/routers/scan.py`).
2. Router waliduje dane (`schemas/scan.py`), przekazuje do serwisu (`services/scan_service.py`).
3. Serwis tworzy rekord w bazie (`models/scan.py`), deleguje zadanie do kolejki (`tasks/scan_tasks.py`).
4. Task wykonuje skan, zapisuje wyniki (`models/finding.py`), uruchamia analizę ryzyka (`risk_engine.py`).
5. Wyniki trafiają do bazy, są dostępne przez API.
