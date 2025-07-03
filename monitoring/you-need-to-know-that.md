# Monitoring - Co Musisz Wiedzieć

## 1. Czym jest moduł Monitoring?

Moduł Monitoring to **system obserwacji i kontroli wydajności** dla platformy EASM. Jest to "system monitorujący" całego ekosystemu, który:
- Zbiera metryki z wszystkich usług
- Monitoruje dostępność i działanie komponentów
- Wizualizuje dane na temat wydajności
- Umożliwia wykrywanie problemów i wąskich gardeł
- Wspiera debugowanie i analizę przyczyn problemów

Wyobraź sobie moduł Monitoring jako "centrum nadzoru", które stale obserwuje działanie wszystkich komponentów systemu EASM i ostrzega, gdy coś działa nieprawidłowo.

## 2. Architektura Monitoringu

Moduł Monitoring składa się z dwóch głównych komponentów:

1. **Prometheus** - odpowiedzialny za zbieranie, przechowywanie i przetwarzanie metryk
2. **Grafana** - odpowiedzialna za wizualizację danych i tworzenie dashboardów

### 2.1. Jak to działa:

Prometheus regularnie "pyta" (scrape) poszczególne usługi o ich metryki, takie jak:
- Wykorzystanie CPU
- Zużycie pamięci RAM
- Liczba zapytań HTTP
- Czas odpowiedzi API
- Status zadań ARQ
- Wydajność bazy danych

Dane te są następnie przechowywane i analizowane przez Prometheus, a Grafana wykorzystuje je do tworzenia przejrzystych wykresów i dashboardów.

## 3. Co jest monitorowane?

System monitoruje następujące komponenty:

- **easm-api** (port 8000) - metryki dotyczące API Gateway
- **easm-core** (port 8001) - metryki dotyczące silnika biznesowego
- **redis** (port 6379) - metryki dotyczące brokera wiadomości
- **postgres** (port 5432) - metryki dotyczące bazy danych
- **prometheus** (port 9090) - self-monitoring

Wszystkie usługi są monitorowane pod kątem:
- Dostępności (czy są uruchomione)
- Wydajności (jak szybko odpowiadają)
- Wykorzystania zasobów (CPU, RAM, dysk)
- Błędów i wyjątków

## 4. Konfiguracja Prometheusa

Prometheus jest skonfigurowany w pliku `prometheus.yml`, który zawiera:

- Częstotliwość zbierania danych (**scrape_interval**: 15s)
- Częstotliwość oceny reguł (**evaluation_interval**: 15s)
- Konfigurację celów monitorowania (**scrape_configs**)

Każdy monitorowany serwis jest zdefiniowany jako "job" z informacjami o:
- Nazwie serwisu
- Adresie i porcie
- Ścieżce do metryk
- Częstotliwości zbierania danych dla konkretnego serwisu

## 5. Jak uzyskać dostęp do narzędzi monitorowania?

### 5.1. Prometheus

- **URL**: http://localhost:9090
- **Funkcje**:
  - Przeglądanie surowych metryk
  - Wykonywanie zapytań PromQL
  - Sprawdzanie statusu celów monitorowania
  - Definiowanie alertów

### 5.2. Grafana

- **URL**: http://localhost:3000
- **Dane logowania**: admin/admin
- **Funkcje**:
  - Przeglądanie gotowych dashboardów
  - Tworzenie niestandardowych wizualizacji
  - Konfigurowanie alertów
  - Eksportowanie danych

## 6. Najważniejsze metryki

### 6.1. Metryki API i Core

- **http_requests_total** - łączna liczba zapytań HTTP
- **http_request_duration_seconds** - czas przetwarzania zapytania
- **http_requests_in_progress** - liczba aktualnie przetwarzanych zapytań
- **http_exceptions_total** - liczba wyjątków

### 6.2. Metryki ARQ

- **arq_task_received_total** - liczba otrzymanych zadań
- **arq_task_started_total** - liczba rozpoczętych zadań
- **arq_task_completed_total** - liczba pomyślnie zakończonych zadań
- **arq_task_failed_total** - liczba nieudanych zadań
- **arq_task_duration_seconds** - czas wykonania zadania

### 6.3. Metryki bazy danych

- **postgres_up** - czy baza danych jest dostępna
- **postgres_queries_total** - liczba zapytań SQL
- **postgres_query_duration_seconds** - czas wykonania zapytania
- **postgres_connections** - liczba aktywnych połączeń

## 7. Jak uruchomić moduł monitorowania?

Moduł monitorowania jest oznaczony jako opcjonalny w pliku `docker-compose.yml` za pomocą profilu "monitoring". Aby go uruchomić:

```bash
docker-compose --profile monitoring up -d
```

Aby zatrzymać tylko usługi monitorowania:

```bash
docker-compose stop prometheus grafana
```

## 8. Typowe problemy i rozwiązania

### Problem 1: Prometheus nie zbiera metryk z usługi
**Rozwiązanie**: Sprawdź, czy usługa udostępnia endpoint `/metrics` i czy jest dostępna pod skonfigurowanym adresem i portem.

### Problem 2: Grafana nie pokazuje danych
**Rozwiązanie**: Upewnij się, że Prometheus jest prawidłowo skonfigurowany jako źródło danych w Grafanie.

### Problem 3: Wysokie zużycie dysku przez Prometheus
**Rozwiązanie**: Dostosuj parametry retencji danych w konfiguracji Prometheusa lub dodaj zewnętrzny wolumin z większą pojemnością.

## 9. Dobre praktyki monitorowania

1. **Monitoruj to, co ważne** - skup się na metrykach, które faktycznie wskazują na problemy
2. **Ustaw sensowne alerty** - unikaj zbyt częstych fałszywych alarmów
3. **Używaj dashboardów** - stwórz przejrzyste wizualizacje dla różnych aspektów systemu
4. **Koreluj dane** - łącz dane z różnych źródeł, aby lepiej zrozumieć problemy
5. **Zachowaj historię** - monitoruj trendy długoterminowe, aby wykryć degradację wydajności

## 10. Struktura katalogu monitoringu

```
monitoring/
  prometheus.yml       # Główny plik konfiguracyjny Prometheusa
  rules/               # (opcjonalnie) Katalog z regułami alertów
  dashboards/          # (opcjonalnie) Gotowe dashboardy dla Grafany
```

## 11. Podsumowanie - co musisz wiedzieć na pewno

1. **Moduł Monitoring składa się z Prometheusa i Grafany** - pierwszy zbiera dane, druga je wizualizuje
2. **Monitorowanie jest opcjonalne** - używa profilu "monitoring" w docker-compose
3. **Prometheus nasłuchuje na porcie 9090** - tam znajdziesz surowe dane i możesz wykonywać zapytania
4. **Grafana działa na porcie 3000** - tam znajdziesz dashboardy i wizualizacje
5. **System monitoruje wszystkie kluczowe usługi** - api, core, redis, postgres
6. **Konfiguracja znajduje się w pliku prometheus.yml** - tam definiujesz co ma być monitorowane

## 12. Przykłady użycia Prometheusa

### 12.1. Podstawowe zapytanie PromQL

Aby sprawdzić liczbę żądań HTTP do API w ciągu ostatnich 5 minut:

```
rate(http_requests_total{job="easm-api"}[5m])
```

### 12.2. Sprawdzenie dostępności usług

Aby sprawdzić, które usługi są obecnie niedostępne:

```
up == 0
```

### 12.3. Średni czas odpowiedzi API

```
avg by (route) (http_request_duration_seconds{job="easm-api"})
```

## 13. Diagram działania monitoringu

```
  Komponenty EASM                     System Monitoringu                     Użytkownik
┌───────────────────┐               ┌───────────────────┐               ┌───────────────┐
│                   │  1. Scraping  │                   │  3. Zapytanie │               │
│  easm-api         │◄──────────────┤                   │◄──────────────┤               │
│  (endpoint        │               │                   │               │               │
│   /metrics)       │               │                   │               │               │
│                   │               │   Prometheus      │               │  Przeglądarka │
├───────────────────┤               │   (zbieranie i    │               │  internetowa  │
│                   │  1. Scraping  │   przechowywanie  │               │               │
│  easm-core        │◄──────────────┤   metryk)         │               │               │
│  (endpoint        │               │                   │               │               │
│   /metrics)       │               │                   │               │               │
│                   │               │                   │               │               │
├───────────────────┤               └───────┬───────────┘               │               │
│                   │  1. Scraping          │                           │               │
│  redis            │◄──────────────────────┘                           │               │
│                   │                          2. Pobieranie            │               │
├───────────────────┤                          danych                   │               │
│                   │                       ┌──────────────────────────►│               │
│  postgres         │  1. Scraping          │                           │               │
│                   │◄──────────────────────┤                           │               │
└───────────────────┘                       │                           │               │
                                  ┌─────────┴───────────┐               │               │
                                  │                     │  3. Zapytanie │               │
                                  │  Grafana            │◄──────────────┤               │
                                  │  (wizualizacja      │               │               │
                                  │   danych)           │  4. Wyświetlenie             │
                                  │                     │────────────────►               │
                                  └─────────────────────┘               └───────────────┘
```

## 14. Jak rozszerzyć monitoring?

Jeśli chcesz rozszerzyć monitoring o nowe funkcje, rozważ:

1. **Dodanie eksporterów** - np. node-exporter do monitorowania systemu operacyjnego
2. **Konfigurację alertów** - definiowanie reguł alertów w Prometheusie
3. **Integrację z systemami powiadomień** - np. AlertManager, Slack, PagerDuty
4. **Dodanie niestandardowych metryk** - wzbogacenie aplikacji o dodatkowe metryki biznesowe
5. **Implementację logowania** - uzupełnienie monitoringu o centralne rozwiązanie do logowania (np. ELK Stack)

Monitoring to kluczowy element każdego systemu produkcyjnego, który pozwala na wczesne wykrywanie problemów i zapewnienie wysokiej dostępności dla użytkowników końcowych!
