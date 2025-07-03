# EASM API Gateway - Co musisz wiedzieć

## 1. Czym jest EASM API Gateway?

EASM API Gateway to transparentne proxy, które służy jako punkt wejścia dla wszystkich żądań zewnętrznych do mikrousług EASM (External Attack Surface Management). Głównym zadaniem tej bramy API jest przekierowanie wszystkich żądań do właściwego serwisu core API, bez dodatkowej logiki biznesowej i duplikacji kodu.

## 2. Jak działa?

### Podstawowy przepływ:

```
Klient (np. przeglądarka) --> EASM API Gateway (port 8080) --> EASM Core API (port 8001)
```

### Kluczowe cechy:

1. **Transparentne proxy** - Wszystkie zapytania są przekazywane do Core API bez modyfikacji
2. **Zachowanie oryginalnych parametrów** - Przekazuje wszystkie nagłówki, parametry zapytań i ciało zapytania
3. **Obsługa wszystkich metod HTTP** - Obsługuje GET, POST, PUT i DELETE
4. **Spójne mapowanie ścieżek** - Wszystkie ścieżki są mapowane bezpośrednio z `/api/v1/{path}` na odpowiadające im ścieżki w Core API
5. **Obsługa błędów** - Przekazuje odpowiednie kody HTTP i komunikaty błędów z Core API

## 3. Jak korzystać z EASM API Gateway?

Wszystkie zapytania do API powinny być kierowane na adres Gateway API:

```
http://localhost:8080/api/v1/{endpoint}
```

Na przykład:
- Endpoint skanowania: `http://localhost:8080/api/v1/scan`
- Endpoint zasobów: `http://localhost:8080/api/v1/assets`

Wszystkie te żądania zostaną automatycznie przekierowane do odpowiednich endpointów Core API.

## 4. Integracja z GUI

Przy tworzeniu interfejsu użytkownika (GUI) należy:

1. **Skonfigurować bazowy URL** - Ustaw bazowy URL API na adres Gateway: `http://localhost:8080/api/v1`
2. **Wykorzystać standardowe ścieżki endpointów** - Używaj ścieżek dokładnie takich, jakie są zdefiniowane w Core API
3. **Obsługiwać kody odpowiedzi** - API Gateway przekazuje oryginalne kody odpowiedzi i komunikaty błędów z Core API

### Przykład integracji (JavaScript/Fetch):

```javascript
// Konfiguracja bazowego URL
const API_BASE_URL = 'http://localhost:8080/api/v1';

// Funkcja do wykonywania żądań API
async function callApi(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_BASE_URL}/${endpoint}`, options);
  
  // Sprawdzenie statusu odpowiedzi
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Wystąpił błąd API');
  }

  return await response.json();
}

// Przykład użycia
async function startScan(scanOptions) {
  try {
    const result = await callApi('scan', 'POST', scanOptions);
    return result;
  } catch (error) {
    console.error('Błąd podczas rozpoczynania skanowania:', error);
    throw error;
  }
}
```

## 5. Uwagi dotyczące implementacji

1. **Timeout** - Gateway ma ustawiony timeout 30 sekund dla żądań do Core API
2. **Logowanie** - Wszystkie przekierowane żądania są logowane z poziomem INFO
3. **Adres Core API** - Domyślnie Core API jest dostępne pod adresem `http://core:8001` (można zmienić przez zmienną środowiskową CORE_URL)
4. **Kontrola zdrowia** - Endpoint `/health` zwraca status API Gateway (nie wymaga dostępu do Core API)

## 6. Rozwiązywanie problemów

### Typowe problemy:

1. **Timeout (503)** - Sprawdź czy Core API jest dostępne i odpowiada
2. **Błędy 500** - Sprawdź logi Gateway i Core API
3. **Problemy z przekierowaniem** - Upewnij się, że zmienna środowiskowa CORE_URL jest poprawnie ustawiona

### Logi:

Wszystkie operacje są logowane na poziomie INFO, co ułatwia debugowanie:
- Szczegóły przekierowanych żądań
- Błędy podczas komunikacji z Core API
- Timeout i inne problemy z połączeniem

---

## 7. Rozszerzanie API Gateway

Jeśli potrzebujesz rozszerzyć funkcjonalność Gateway API, rozważ:

1. **Dodanie autentykacji** - Walidacja tokenów JWT przed przekazaniem do Core API
2. **Rate limiting** - Ograniczanie liczby żądań od pojedynczego klienta
3. **Transformacja danych** - Dodanie logiki transformacji zapytań lub odpowiedzi
4. **Cache** - Dodanie cache'owania dla często używanych endpointów
5. **Metryk** - Zbieranie metryk dotyczących użycia API

Pamiętaj jednak, że główną zaletą obecnej implementacji jest jej prostota i transparentność - każda dodatkowa logika powinna być dokładnie przemyślana.