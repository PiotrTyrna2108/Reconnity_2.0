## **app/main.py**
- **Do czego służy:**  
  Główny plik uruchamiający aplikację FastAPI.
- **Funkcje:**  
  Tworzy instancję FastAPI, rejestruje routery z `api/routers`, ustawia middleware, eventy start/stop.
- **Integracje:**  
  - `api/routers/` (import routerów)
  - `core/settings.py` (konfiguracja)
  - `database.py` (inicjalizacja bazy)
  - `core/logging.py` (logowanie)

---

## **app/database.py**
- **Do czego służy:**  
  Konfiguracja połączenia z bazą danych (SQLAlchemy), inicjalizacja tabel, sesje.
- **Funkcje:**  
  Tworzy silnik bazy, sesje, funkcje do inicjalizacji bazy.
- **Integracje:**  
  - `models/` (modele bazy)
  - `api/dependencies.py` (dostarcza sesje)
  - `services/` (operacje na bazie)

---

## **app/api/dependencies.py**
- **Do czego służy:**  
  Definiuje zależności FastAPI (np. pobieranie sesji bazy, autoryzacja).
- **Funkcje:**  
  Funkcje zależności do użycia w endpointach.
- **Integracje:**  
  - `database.py` (sesje)
  - `core/security.py` (autoryzacja)
  - `api/routers/` (wykorzystanie zależności)

---

## **app/api/errors.py**
- **Do czego służy:**  
  Obsługa wyjątków i błędów HTTP.
- **Funkcje:**  
  Definiuje własne wyjątki, mapuje je na odpowiedzi HTTP.
- **Integracje:**  
  - `api/routers/` (rzucanie wyjątków)
  - FastAPI (rejestracja handlerów)

---

## **app/api/routers/health.py**
- **Do czego służy:**  
  Endpoint `/health` do sprawdzania stanu systemu.
- **Funkcje:**  
  Zwraca status aplikacji, opcjonalnie sprawdza połączenie z bazą.
- **Integracje:**  
  - `schemas/health.py` (odpowiedź)
  - `database.py` (sprawdzenie bazy)

---

## **app/api/routers/scan.py**
- **Do czego służy:**  
  Endpointy do zarządzania skanami.
- **Funkcje:**  
  Tworzenie skanu, pobieranie statusu, oznaczanie jako zakończony/nieudany.
- **Integracje:**  
  - `schemas/scan.py` (walidacja)
  - `services/scan_service.py` (logika biznesowa)
  - `models/scan.py` (operacje na modelu)
  - `tasks/tasks/scan_tasks.py` (delegowanie zadań)

---

## **app/api/routers/nuclei_templates.py**
- **Do czego służy:**  
  Endpointy do zarządzania szablonami Nuclei.
- **Funkcje:**  
  Pobieranie, odświeżanie szablonów skanera.
- **Integracje:**  
  - `services/` (jeśli jest logika szablonów)
  - `schemas/` (jeśli są schematy szablonów)

---

## **app/api/routers/scan_options.py**
- **Do czego służy:**  
  Endpointy do pobierania opcji skanowania.
- **Funkcje:**  
  Zwraca dostępne opcje (np. zakresy portów, typy skanów).
- **Integracje:**  
  - `schemas/scan_options.py`
  - `services/` (logika opcji)

---

## **app/api/routers/__init__.py**
- **Do czego służy:**  
  Rejestruje routery do głównej aplikacji.
- **Funkcje:**  
  Importuje i łączy routery.
- **Integracje:**  
  - `main.py` (importuje routery)

---

## **app/core/logging.py**
- **Do czego służy:**  
  Konfiguracja loggera.
- **Funkcje:**  
  Funkcja `get_logger()`, ustawienia logowania.
- **Integracje:**  
  - Cały projekt (wszędzie gdzie logujesz)

---

## **app/core/security.py**
- **Do czego służy:**  
  Funkcje bezpieczeństwa (tokeny, autoryzacja).
- **Funkcje:**  
  Generowanie i weryfikacja tokenów, autoryzacja użytkownika.
- **Integracje:**  
  - `api/dependencies.py`
  - `services/`

---

## **app/core/settings.py**
- **Do czego służy:**  
  Wczytywanie ustawień aplikacji (np. z env).
- **Funkcje:**  
  Klasa/config z ustawieniami.
- **Integracje:**  
  - Cały projekt (import ustawień)

---

## **app/models/asset.py**
- **Do czego służy:**  
  Model `Asset` – zasób do skanowania (IP, domena).
- **Funkcje:**  
  Definicja tabeli, relacje.
- **Integracje:**  
  - `services/asset_service.py`
  - `schemas/asset.py`
  - `db/repositories/`

---

## **app/models/base.py**
- **Do czego służy:**  
  Klasa bazowa dla modeli SQLAlchemy.
- **Funkcje:**  
  Deklaracja `Base = declarative_base()`.
- **Integracje:**  
  - Wszystkie modele

---

## **app/models/finding.py**
- **Do czego służy:**  
  Model `Finding` (znalezisko), `RiskScore`.
- **Funkcje:**  
  Definicja tabeli, relacje, scoring.
- **Integracje:**  
  - `services/finding_service.py`
  - `schemas/finding.py`
  - `risk_engine.py`

---

## **app/models/scan.py**
- **Do czego służy:**  
  Model `Scan` – pojedyncze zadanie skanowania.
- **Funkcje:**  
  Definicja tabeli, statusy, relacje.
- **Integracje:**  
  - `services/scan_service.py`
  - `schemas/scan.py`
  - `db/repositories/`

---

## **app/schemas/asset.py**
- **Do czego służy:**  
  Schematy Pydantic dla zasobów (`Asset`).
- **Funkcje:**  
  Walidacja danych wejściowych/wyjściowych.
- **Integracje:**  
  - `api/routers/`
  - `models/asset.py`

---

## **app/schemas/finding.py**
- **Do czego służy:**  
  Schematy Pydantic dla znalezisk i scoringu.
- **Funkcje:**  
  Walidacja danych wejściowych/wyjściowych.
- **Integracje:**  
  - `api/routers/`
  - `models/finding.py`

---

## **app/schemas/health.py**
- **Do czego służy:**  
  Schemat odpowiedzi dla `/health`.
- **Funkcje:**  
  Walidacja odpowiedzi healthcheck.
- **Integracje:**  
  - `api/routers/health.py`

---

## **app/schemas/scan.py**
- **Do czego służy:**  
  Schematy Pydantic dla skanów.
- **Funkcje:**  
  Walidacja żądań i odpowiedzi związanych ze skanami.
- **Integracje:**  
  - `api/routers/scan.py`
  - `models/scan.py`

---

## **app/schemas/scan_options.py**
- **Do czego służy:**  
  Schematy opcji skanowania.
- **Funkcje:**  
  Walidacja opcji skanowania.
- **Integracje:**  
  - `api/routers/scan_options.py`

---

## **app/services/asset_service.py**
- **Do czego służy:**  
  Operacje na zasobach (`Asset`).
- **Funkcje:**  
  Tworzenie, aktualizacja, pobieranie zasobów.
- **Integracje:**  
  - `models/asset.py`
  - `db/repositories/`
  - `schemas/asset.py`

---

## **app/services/finding_service.py**
- **Do czego służy:**  
  Operacje na znaleziskach (`Finding`).
- **Funkcje:**  
  Tworzenie, aktualizacja, pobieranie znalezisk.
- **Integracje:**  
  - `models/finding.py`
  - `db/repositories/`
  - `schemas/finding.py`

---

## **app/services/risk_service.py**
- **Do czego służy:**  
  Logika oceny ryzyka.
- **Funkcje:**  
  Obliczanie scoringu ryzyka na podstawie znalezisk.
- **Integracje:**  
  - `risk_engine.py`
  - `models/finding.py`

---

## **app/services/scan_service.py**
- **Do czego służy:**  
  Główna logika zarządzania skanami.
- **Funkcje:**  
  Tworzenie, aktualizacja, pobieranie skanów, delegowanie do tasks.
- **Integracje:**  
  - `models/scan.py`
  - `db/repositories/`
  - `tasks/tasks/scan_tasks.py`
  - `risk_engine.py`
  - `schemas/scan.py`

---

## **app/tasks/config/queue_config.py**
- **Do czego służy:**  
  Konfiguracja kolejki zadań, worker settings.
- **Funkcje:**  
  Definiuje ustawienia ARQ/Celery, listę funkcji zadań.
- **Integracje:**  
  - `tasks/tasks/scan_tasks.py`
  - `tasks/config/redis_config.py`

---

## **app/tasks/config/redis_config.py**
- **Do czego służy:**  
  Konfiguracja połączenia z Redis.
- **Funkcje:**  
  Ustawienia hosta, portu, bazy, itp.
- **Integracje:**  
  - `queue_config.py`
  - tasks

---

## **app/tasks/config/retry_helpers.py**
- **Do czego służy:**  
  Funkcje pomocnicze do retry.
- **Funkcje:**  
  Dekoratory, logika retry dla zadań.
- **Integracje:**  
  - `scan_tasks.py`
  - inne zadania

---

## **app/tasks/monitoring/task_metrics.py**
- **Do czego służy:**  
  Metryki zadań.
- **Funkcje:**  
  Zliczanie, eksportowanie metryk tasków.
- **Integracje:**  
  - `scan_tasks.py`
  - monitoring

---

## **app/tasks/tasks/scan_tasks.py**
- **Do czego służy:**  
  Zadania asynchroniczne związane ze skanowaniem.
- **Funkcje:**  
  Funkcje `scan_asset`, `process_scan_result` – uruchamianie skanów, przetwarzanie wyników.
- **Integracje:**  
  - `services/scan_service.py`
  - `models/scan.py`
  - `database.py`
  - `risk_engine.py`
  - `tasks/config/queue_config.py`

---

## **app/risk_engine.py**
- **Do czego służy:**  
  Silnik analizy ryzyka.
- **Funkcje:**  
  Oblicza poziom ryzyka na podstawie znalezisk, portów, usług, podatności.
- **Integracje:**  
  - `models/finding.py`
  - `services/risk_service.py`
  - `tasks/tasks/scan_tasks.py`

---

