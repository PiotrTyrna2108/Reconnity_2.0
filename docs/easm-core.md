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

// ...existing code...

---

## **📁 Struktura projektu - Dla kompletnego laika**

### **📂 app/**
**Co to:** Główny folder z całą aplikacją - serce projektu.
**Prościej:** To jak główna szafa z wszystkimi ubraniami - wszystko ważne jest tutaj.

### **📂 app/api/**
**Co to:** Folder z endpointami API - punktami gdzie frontend rozmawia z backendem.
**Prościej:** To jak recepcja w hotelu - tutaj przyjmujesz wszystkie zapytania od klientów.

### **📂 app/api/routers/**
**Co to:** Konkretne ścieżki API pogrupowane tematycznie.
**Prościej:** To jak różne okienka w urzędzie - każde załatwia inne sprawy.

### **📂 app/core/**
**Co to:** Podstawowe ustawienia i konfiguracja aplikacji.
**Prościej:** To jak instrukcja obsługi - mówi aplikacji jak się zachowywać.

### **📂 app/models/**
**Co to:** Definicje tabel bazodanowych - jak wyglądają dane w bazie.
**Prościej:** To jak formularze - określają jakie pola masz wypełnić w bazie danych.

### **📂 app/schemas/**
**Co to:** Schematy Pydantic do walidacji danych wejściowych/wyjściowych.
**Prościej:** To jak kontrola bezpieczeństwa na lotnisku - sprawdza czy dane są OK.

### **📂 app/services/**
**Co to:** Logika biznesowa - główne operacje aplikacji.
**Prościej:** To jak kuchnia w restauracji - tutaj dzieje się prawdziwa robota.

### **📂 app/utils/**
**Co to:** Pomocnicze funkcje używane w całej aplikacji.
**Prościej:** To jak przybornik - małe narzędzia które pomagają w różnych sytuacjach.

### **📂 tests/**
**Co to:** Testy automatyczne sprawdzające czy kod działa poprawnie.
**Prościej:** To jak egzamin dla kodu - sprawdza czy wszystko działa jak powinno.

### **📂 migrations/**
**Co to:** Pliki zmieniające strukturę bazy danych w czasie.
**Prościej:** To jak historia zmian - zapisuje co i kiedy zmieniłeś w bazie.

---



## **📄 Pliki - Dla kompletnego laika** czytaj Piotrka

### **⚙️ app/core/config.py**
**Co to:** Główne ustawienia aplikacji (baza danych, API keys, etc.).
**Prościej:** To jak panel sterowania - tutaj ustawiasz wszystkie ważne opcje.

### **⚙️ app/core/database.py**
**Co to:** Połączenie z bazą danych i konfiguracja SQLAlchemy.
**Prościej:** To jak kabel łączący komputer z internetem - łączy aplikację z bazą.

### **🔌 app/api/routers/health.py**
**Co to:** Endpoint sprawdzający czy aplikacja żyje i działa.
**Prościej:** To jak puls - szybko sprawdzasz czy aplikacja jeszcze oddycha.

### **🔍 app/api/routers/findings.py**
**Co to:** Endpointy do zarządzania znaleziskami (dodawanie, pobieranie, etc.).
**Prościej:** To jak biuro zgłoszeń - tutaj zgłaszasz i przeglądasz wszystkie znaleziska.

### **📊 app/models/finding.py**
**Co to:** Model bazy danych dla znalezisk - struktura tabeli.
**Prościej:** To jak szablon formularza - określa jakie pola ma każde znalezisko.

### **✅ app/schemas/finding.py**
**Co to:** Schematy walidacji dla znalezisk (wejście/wyjście API).
**Prościej:** To jak kontroler biletów - sprawdza czy dane wyglądają jak powinny.

### **💚 app/schemas/health.py**
**Co to:** Schemat odpowiedzi dla endpointu health.
**Prościej:** To jak standardowa odpowiedź "wszystko OK" - zawsze wygląda tak samo.

### **🔧 app/services/finding_service.py**
**Co to:** Logika biznesowa dla znalezisk (operacje CRUD).
**Prościej:** To jak pracownik który faktycznie załatwia sprawy - robi prawdziwą robotę.

### **🛠️ app/utils/helpers.py**
**Co to:** Pomocnicze funkcje używane w różnych miejscach.
**Prościej:** To jak multitool - małe przydatne narzędzia na różne okazje.

### **🚀 main.py**
**Co to:** Główny plik uruchamiający aplikację FastAPI.
**Prościej:** To jak przycisk START - uruchamia całą aplikację.

### **📋 requirements.txt**
**Co to:** Lista wszystkich bibliotek Pythona potrzebnych do uruchomienia.
**Prościej:** To jak lista zakupów - wszystko co musisz zainstalować żeby aplikacja działała.

### **🐳 Dockerfile**
**Co to:** Przepis na stworzenie kontenera Docker z aplikacją.
**Prościej:** To jak instrukcja pakowania - mówi jak zapakować aplikację w pudełko.

### **🔧 docker-compose.yml**
**Co to:** Konfiguracja do uruchomienia aplikacji i bazy danych jednym poleceniem.
**Prościej:** To jak pilot uniwersalny - jednym kliknięciem włącza całe kino domowe.