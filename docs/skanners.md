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