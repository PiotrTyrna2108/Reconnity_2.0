# 🔍 Skaner Nuclei - Kompletny przewodnik po opcjach i scenariuszach

## 📋 Wprowadzenie

Nuclei to zaawansowany skaner podatności oparty na szablonach, który jest integralną częścią platformy EASM. Umożliwia automatyczne wykrywanie podatności, błędnych konfiguracji i problemów bezpieczeństwa w aplikacjach webowych i infrastrukturze sieciowej.

---

## 🚀 Jak uruchomić skan Nuclei

### Metoda 1: Quick Scan (proste parametry URL)
```bash
POST /api/v1/scan/quick?target=https://example.com&scanner=nuclei&templates=tech-detect&severity=high,critical
```

### Metoda 2: Standard Scan (JSON)
```json
{
  "target": "https://example.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["tech-detect", "cves"],
    "severity": ["critical", "high"],
    "timeout": 600,
    "rate": 150,
    "concurrency": 25
  }
}
```

---

## ⚙️ Wszystkie dostępne opcje

### 🎯 **templates** - Szablony skanowania
**Opis:** Określa które kategorie szablonów będą użyte podczas skanowania.

**Wartość domyślna:** `["cves"]`

**Dostępne opcje:**
- `cves` - Szablony dla Common Vulnerabilities and Exposures (najważniejsze)
- `tech-detect` - Wykrywanie technologii używanych przez aplikację
- `ssl` - Testy SSL/TLS i certyfikatów
- `dns` - Testy konfiguracji DNS
- `http` - Ogólne testy HTTP
- `network` - Testy sieciowe
- `file` - Wykrywanie ekspozycji plików
- `workflows` - Złożone wieloetapowe testy
- `headless` - Testy wymagające przeglądarki
- `vulnerabilities` - Ogólne vulnerabilities

**Przykłady użycia:**
```json
// Podstawowe skanowanie CVE
"templates": ["cves"]

// Wykrywanie technologii + CVE
"templates": ["tech-detect", "cves"]

// Kompleksowe skanowanie
"templates": ["cves", "vulnerabilities", "ssl", "dns"]

// Tylko wykrywanie technologii
"templates": ["tech-detect"]

// Tylko testy SSL
"templates": ["ssl"]
```

**Scenariusze:**
- **Audyt bezpieczeństwa:** `["cves", "ssl", "dns"]`
- **Rekonesans techniczny:** `["tech-detect", "http"]`  
- **Test penetracyjny:** `["cves", "workflows", "file"]`
- **Compliance SSL:** `["ssl"]`

---

### 🚨 **severity** - Poziomy krytyczności
**Opis:** Filtruje podatności według poziomu krytyczności.

**Wartość domyślna:** `["critical", "high", "medium"]`

**Dostępne opcje:**
- `critical` - Krytyczne (natychmiastowa akcja wymagana)
- `high` - Wysokie (pilna akcja wymagana)
- `medium` - Średnie (akcja planowana)
- `low` - Niskie (monitoring)
- `info` - Informacyjne (bez ryzyka)

**Przykłady użycia:**
```json
// Tylko najbardziej krytyczne
"severity": ["critical"]

// Pilne do naprawy
"severity": ["critical", "high"]

// Wszystkie poziomy
"severity": ["critical", "high", "medium", "low", "info"]

// Szybki przegląd
"severity": ["critical", "high", "medium"]
```

**Scenariusze:**
- **Incident response:** `["critical"]`
- **Security review:** `["critical", "high"]`
- **Compliance audit:** `["critical", "high", "medium"]`
- **Pełny assessment:** wszystkie poziomy

---

### ⏱️ **timeout** - Limit czasu skanowania
**Opis:** Maksymalny czas trwania całego skanowania w sekundach.

**Wartość domyślna:** `600` (10 minut)

**Zakres:** 60-3600 sekund

**Przykłady użycia:**
```json
// Szybki test (5 minut)
"timeout": 300

// Standardowy czas (10 minut)  
"timeout": 600

// Długi scan (30 minut)
"timeout": 1800

// Bardzo dokładny (1 godzina)
"timeout": 3600
```

**Wytyczne:**
- **Małe aplikacje:** 300-600s
- **Średnie portale:** 600-1800s  
- **Duże systemy:** 1800-3600s
- **API endpoints:** 300s

---

### 🏃‍♂️ **rate** - Limit requestów na sekundę
**Opis:** Kontroluje intensywność skanowania przez ograniczenie liczby żądań HTTP na sekundę.

**Wartość domyślna:** `150` żądań/sekundę

**Zakres:** 1-1000 żądań/sekundę

**Przykłady użycia:**
```json
// Bardzo delikatne (stabilne środowiska produkcyjne)
"rate": 10

// Ostrożne (środowiska produkcyjne)
"rate": 50

// Standardowe (większość przypadków)
"rate": 150

// Agresywne (środowiska testowe)
"rate": 500

// Maksymalne (laboratoria)
"rate": 1000
```

**Wytyczne według środowiska:**
- **Produkcja (live):** 10-50
- **Staging:** 100-200
- **Development:** 200-500
- **Pentest lab:** 500-1000

---

### 🔄 **concurrency** - Równoległe żądania
**Opis:** Liczba jednoczesnych połączeń HTTP.

**Wartość domyślna:** `25` połączeń

**Zakres:** 1-100 połączeń

**Przykłady użycia:**
```json
// Pojedyncze żądania (bardzo delikatne)
"concurrency": 1

// Niskie obciążenie
"concurrency": 5

// Standardowe
"concurrency": 25

// Wysokie obciążenie
"concurrency": 50

// Maksymalne (tylko w lab)
"concurrency": 100
```

**Wpływ na performance:**
- **1-5:** Bardzo powolne, bezpieczne
- **10-25:** Optymalne dla większości
- **25-50:** Szybkie, może obciążać serwer
- **50+:** Bardzo szybkie, ryzykowne dla produkcji

---

### 🔄 **retries** - Liczba powtórzeń
**Opis:** Ile razy powtórzyć nieudane żądania.

**Wartość domyślna:** `1`

**Zakres:** 0-5

**Przykłady użycia:**
```json
// Bez powtórzeń (szybkie)
"retries": 0

// Standardowe
"retries": 1  

// Dla niestabilnych połączeń
"retries": 3

// Dla bardzo niestabilnych
"retries": 5
```

---

### 📝 **verbose** - Szczegółowe wyniki
**Opis:** Włącza szczegółowe raportowanie z dodatkowym debug info.

**Wartość domyślna:** `false`

**Przykłady użycia:**
```json
// Standardowe wyniki
"verbose": false

// Szczegółowe wyniki (troubleshooting)
"verbose": true
```

**Kiedy używać:**
- `false` - Normalne skanowanie
- `true` - Debugging, analiza problemów

---

### 🔄 **follow_redirects** - Podążanie za przekierowaniami
**Opis:** Czy skaner ma podążać za przekierowaniami HTTP (301, 302, etc.).

**Wartość domyślna:** `true`

**Przykłady użycia:**
```json
// Podążaj za przekierowaniami (domyślne)
"follow_redirects": true

// Nie podążaj (test specyficznych endpoint'ów)
"follow_redirects": false
```

**Scenariusze:**
- `true` - Większość skanowań webowych
- `false` - Test load balancerów, proxy, specific endpoints

---

### ❌ **max_host_error** - Maksymalne błędy na host
**Opis:** Po ilu błędach pominąć dalsze testowanie danego hosta.

**Wartość domyślna:** `30`

**Zakres:** 1-100

**Przykłady użycia:**
```json
// Szybkie pominięcie problematycznych hostów
"max_host_error": 10

// Standardowe
"max_host_error": 30

// Bardzo wytrwałe skanowanie
"max_host_error": 100
```

---

### 🚫 **exclude_templates** - Wykluczenie szablonów
**Opis:** Lista szablonów do pominięcia podczas skanowania.

**Wartość domyślna:** `null` (brak wykluczeń)

**Format:** Lista stringów z ścieżkami szablonów

**Przykłady użycia:**
```json
// Wyłącz stare CVE
"exclude_templates": ["cves/2020/", "cves/2019/"]

// Wyłącz konkretne szablony
"exclude_templates": ["tech-detect/wordpress.yaml"]

// Wyłącz całe kategorie
"exclude_templates": ["headless/"]
```

---

## 🎯 Przykładowe scenariusze użycia

### 1. 🚨 **Security Incident Response**
```json
{
  "target": "https://compromised-site.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["cves"],
    "severity": ["critical"],
    "timeout": 300,
    "rate": 200,
    "concurrency": 50,
    "verbose": true
  }
}
```
**Cel:** Szybka identyfikacja krytycznych podatności

---

### 2. 🔍 **Rekonesans techniczny**
```json
{
  "target": "https://target-app.com", 
  "scanner": "nuclei",
  "options": {
    "templates": ["tech-detect", "http"],
    "severity": ["info", "low", "medium"],
    "timeout": 600,
    "rate": 100,
    "concurrency": 25
  }
}
```
**Cel:** Odkrycie używanych technologii bez agresywnego testowania

---

### 3. 🛡️ **Compliance Audit**
```json
{
  "target": "https://banking-app.com",
  "scanner": "nuclei", 
  "options": {
    "templates": ["ssl", "dns", "cves"],
    "severity": ["critical", "high", "medium"],
    "timeout": 1800,
    "rate": 10,
    "concurrency": 5,
    "retries": 3,
    "verbose": true
  }
}
```
**Cel:** Dokładny audit zgodności z standardami bezpieczeństwa

---

### 4. ⚡ **Szybki health check**
```json
{
  "target": "https://internal-api.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["tech-detect"],
    "severity": ["critical", "high"],
    "timeout": 180,
    "rate": 50,
    "concurrency": 10
  }
}
```
**Cel:** Szybka weryfikacja podstawowego bezpieczeństwa

---

### 5. 🔬 **Penetration Testing**
```json
{
  "target": "https://pentest-target.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["cves", "workflows", "file", "http"],
    "severity": ["critical", "high", "medium", "low"],
    "timeout": 3600,
    "rate": 300,
    "concurrency": 50,
    "retries": 2,
    "verbose": true,
    "follow_redirects": true
  }
}
```
**Cel:** Kompleksowe testowanie penetracyjne

---

### 6. 🌐 **Multi-domain scan**
```bash
# Quick scan dla wielu domen
POST /api/v1/scan/quick?target=domain1.com&scanner=nuclei&templates=cves,ssl&severity=critical,high
POST /api/v1/scan/quick?target=domain2.com&scanner=nuclei&templates=cves,ssl&severity=critical,high
POST /api/v1/scan/quick?target=domain3.com&scanner=nuclei&templates=cves,ssl&severity=critical,high
```

---

## 📊 Interpretacja wyników

### Struktura wyniku
```json
{
  "scan_id": "uuid",
  "target": "https://example.com",
  "scanner": "nuclei", 
  "status": "completed",
  "results": {
    "vulnerabilities": [
      {
        "template_id": "CVE-2021-44228",
        "name": "Apache Log4j RCE",
        "severity": "critical",
        "description": "Remote code execution in Log4j",
        "url": "https://example.com/app",
        "method": "GET",
        "evidence": "log4j-core-2.14.1.jar detected"
      }
    ],
    "technologies": [
      {
        "name": "nginx",
        "version": "1.18.0",
        "confidence": "high"
      }
    ]
  },
  "findings": [...],
  "risk_score": {
    "score": 85,
    "level": "critical"
  }
}
```

### Poziomy krytyczności - co robić
- **🔴 Critical:** Natychmiastowa akcja (0-24h)
- **🟠 High:** Pilna akcja (1-7 dni)  
- **🟡 Medium:** Planowana akcja (1-30 dni)
- **🟢 Low:** Monitoring (1-90 dni)
- **ℹ️ Info:** Do wiadomości

---

## 🛠️ Troubleshooting

### Częste problemy i rozwiązania

#### 1. **Timeout errors**
```json
"error": "Scan timed out after 600 seconds"
```
**Rozwiązanie:** Zwiększ `timeout` lub zmniejsz `templates`

#### 2. **Rate limiting**
```json  
"error": "Too many requests - rate limited"
```
**Rozwiązanie:** Zmniejsz `rate` i `concurrency`

#### 3. **No results**
```json
"results": {"vulnerabilities": []}
```
**Możliwe przyczyny:**
- Target nie jest dostępny
- Wszystkie podatności zostały naprawione  
- Zbyt restrykcyjne `severity`
- Nieprawidłowe `templates`

#### 4. **Connection errors**
```json
"error": "Connection refused"
```
**Rozwiązanie:** Sprawdź dostępność targetu, firewall, DNS

---

## 🚀 Tips & Best Practices

### Optymalizacja performance
1. **Rozpocznij od tech-detect** - poznaj target
2. **Użyj odpowiedniego rate** dla środowiska
3. **Dostosuj timeout** do wielkości aplikacji
4. **Monitoruj obciążenie** serwera docelowego

### Bezpieczeństwo
1. **Zawsze uzyskaj zgodę** przed skanowaniem
2. **Używaj niskich rate** dla produkcji
3. **Testuj na staging** przed produkcją
4. **Dokumentuj wszystkie skany**

### Efektywność
1. **Rozpocznij od critical/high** severity
2. **Użyj exclude_templates** dla znanych false positives
3. **Kombajnuj z innymi skanerami** (nmap + nuclei)
4. **Automatyzuj regularne skany**

---

## 📈 Integracja z innymi skanerami

### Nuclei + Nmap (kompleksowy skan)
```bash
# 1. Nmap - znajdź otwarte porty i usługi
POST /api/v1/scan/quick?target=example.com&scanner=nmap&ports=1-1000

# 2. Nuclei - skanuj podatności na znalezionych usługach  
POST /api/v1/scan/quick?target=example.com&scanner=nuclei&templates=cves,tech-detect
```

### Workflow recommendation
1. **Nmap** → Odkryj infrastrukturę
2. **Nuclei** → Znajdź podatności
3. **Masscan** → Skanuj szersze zakresy
4. **Analiza** → Priorityzuj naprawy

---

# Przewodnik po skanerze Nuclei - Opcje konfiguracyjne

## Wszystkie dostępne opcje dla skanera Nuclei

### 1. **templates** - Szablony vulnerabilities
```json
{
  "templates": ["cves", "tech-detect", "vulnerabilities"]
}
```

**Dostępne kategorie szablonów:**
- `cves` - Szablony CVE (Common Vulnerabilities and Exposures)
- `dns` - Vulnerabilities związane z DNS
- `file` - Vulnerabilities w plikach
- `headless` - Szablony wymagające przeglądarki
- `http` - HTTP-related vulnerabilities
- `network` - Vulnerabilities sieciowe
- `ssl` - Vulnerabilities SSL/TLS
- `workflows` - Złożone wieloetapowe testy
- `tech-detect` - Wykrywanie technologii
- `vulnerabilities` - Ogólne vulnerabilities

**Przykłady użycia:**
```json
// Tylko CVE
{"templates": ["cves"]}

// Wykrywanie technologii + CVE
{"templates": ["tech-detect", "cves"]}

// Kompleksowe skanowanie
{"templates": ["cves", "vulnerabilities", "ssl", "dns"]}
```

### 2. **severity** - Poziomy ważności
```json
{
  "severity": ["critical", "high", "medium"]
}
```

**Dostępne poziomy:**
- `critical` - Krytyczne (10.0 points)
- `high` - Wysokie (7.5 points)
- `medium` - Średnie (5.0 points)
- `low` - Niskie (2.5 points)
- `info` - Informacyjne (0.5 points)

**Przykłady:**
```json
// Tylko krytyczne i wysokie
{"severity": ["critical", "high"]}

// Wszystkie poza informacyjnymi
{"severity": ["critical", "high", "medium", "low"]}

// Tylko do monitoringu
{"severity": ["info"]}
```

### 3. **timeout** - Timeout skanowania
```json
{
  "timeout": 600
}
```
- **Jednostka:** sekundy
- **Domyślna wartość:** 600 sekund (10 minut)
- **Zalecane:** 300-900s dla standardowych skanów

**Przykłady:**
```json
// Szybkie skanowanie
{"timeout": 300}

// Szczegółowe skanowanie
{"timeout": 1200}

// Testowanie pojedynczego hosta
{"timeout": 180}
```

### 4. **rate** - Ograniczenie prędkości
```json
{
  "rate": 150
}
```
- **Jednostka:** requests per second
- **Domyślna wartość:** 150 req/s
- **Zakres:** 1-1000 req/s

**Zalecenia według typu celu:**
```json
// Serwery produkcyjne (ostrożnie)
{"rate": 50}

// Środowiska testowe
{"rate": 150}

// Własne serwery (można więcej)
{"rate": 300}

// Powolne cele
{"rate": 25}
```

### 5. **concurrency** - Współbieżność
```json
{
  "concurrency": 25
}
```
- **Jednostka:** równoczesne połączenia
- **Domyślna wartość:** 25
- **Zakres:** 1-100

**Przykłady dostosowania:**
```json
// Wrażliwe cele
{"concurrency": 10}

// Standardowe skanowanie
{"concurrency": 25}

// Szybkie skanowanie własnych serwerów
{"concurrency": 50}

// Pojedyncze żądania
{"concurrency": 1}
```

### 6. **retries** - Ponowne próby
```json
{
  "retries": 1
}
```
- **Jednostka:** liczba ponownych prób
- **Domyślna wartość:** 1
- **Zakres:** 0-5

**Zastosowania:**
```json
// Niestabilne połączenie
{"retries": 3}

// Szybkie skanowanie bez retry
{"retries": 0}

// Standardowe (domyślne)
{"retries": 1}
```

### 7. **verbose** - Szczegółowe logi
```json
{
  "verbose": true
}
```
- **Typ:** boolean
- **Domyślna wartość:** false

**Kiedy używać:**
```json
// Debugowanie problemów
{"verbose": true}

// Produkcja (mniej logów)
{"verbose": false}
```

### 8. **follow_redirects** - Podążanie za przekierowaniami
```json
{
  "follow_redirects": true
}
```
- **Typ:** boolean
- **Domyślna wartość:** true

**Przykłady:**
```json
// Standardowe web skanowanie
{"follow_redirects": true}

// Testowanie tylko bezpośrednich odpowiedzi
{"follow_redirects": false}
```

### 9. **max_host_error** - Maksymalne błędy na host
```json
{
  "max_host_error": 30
}
```
- **Jednostka:** liczba błędów
- **Domyślna wartość:** 30

**Dostosowanie:**
```json
// Tolerancja na błędy
{"max_host_error": 50}

// Szybkie pomijanie problematycznych hostów
{"max_host_error": 10}

// Bardzo rygorystyczne
{"max_host_error": 5}
```

### 10. **exclude_templates** - Wykluczenie szablonów
```json
{
  "exclude_templates": ["cves/2020/CVE-2020-1234", "dns/dns-cache-poisoning"]
}
```
- **Format:** lista ścieżek szablonów
- **Użycie:** gdy pewne testy są niepotrzebne

## Scenariusze konfiguracji

### Skanowanie produkcyjne (ostrożne)
```json
{
  "target": "https://production-site.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["cves"],
    "severity": ["critical", "high"],
    "rate": 50,
    "concurrency": 10,
    "timeout": 900,
    "follow_redirects": true,
    "verbose": false
  }
}
```

### Kompleksowy audit bezpieczeństwa
```json
{
  "target": "https://test-environment.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["cves", "vulnerabilities", "ssl", "dns", "http"],
    "severity": ["critical", "high", "medium", "low"],
    "rate": 150,
    "concurrency": 25,
    "timeout": 1800,
    "retries": 2,
    "verbose": true
  }
}
```

### Szybkie skanowanie CVE
```json
{
  "target": "192.168.1.100",
  "scanner": "nuclei",
  "options": {
    "templates": ["cves"],
    "severity": ["critical", "high"],
    "rate": 200,
    "concurrency": 30,
    "timeout": 300,
    "retries": 1
  }
}
```

### Wykrywanie technologii (rozpoznanie)
```json
{
  "target": "https://unknown-site.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["tech-detect"],
    "severity": ["info", "low"],
    "rate": 100,
    "concurrency": 20,
    "timeout": 600
  }
}
```

### Skanowanie SSL/TLS
```json
{
  "target": "https://ssl-site.com",
  "scanner": "nuclei",
  "options": {
    "templates": ["ssl"],
    "severity": ["high", "medium", "low"],
    "rate": 75,
    "concurrency": 15,
    "timeout": 450
  }
}
```

## Risk Score System

System oceny ryzyka w Nuclei:

### Wagi severity
- **Critical:** 10.0 punktów
- **High:** 7.5 punktów  
- **Medium:** 5.0 punktów
- **Low:** 2.5 punktów
- **Info:** 0.5 punktów

### Przykład kalkulacji
```
2 x Critical (2 × 10.0 = 20.0)
3 x High (3 × 7.5 = 22.5)
5 x Medium (5 × 5.0 = 25.0)
Total Risk Score: 67.5
```

### Interpretacja wyników
- **0-10:** Bardzo niskie ryzyko
- **11-25:** Niskie ryzyko
- **26-50:** Średnie ryzyko  
- **51-75:** Wysokie ryzyko
- **76+:** Krytyczne ryzyko

## Best Practices

### 1. **Optymalizacja wydajności**
```json
{
  "rate": 100,           // Nie przeciążaj celu
  "concurrency": 20,     // Rozsądna współbieżność
  "timeout": 600,        // Wystarczający czas
  "retries": 1          // Minimalne retry
}
```

### 2. **Bezpieczeństwo skanowania**
- Zawsze uzyskaj pozwolenie przed skanowaniem
- Używaj niskich rate dla serwerów produkcyjnych
- Monitoruj logi aplikacji docelowej
- Unikaj agresywnych szablonów w godzinach szczytu

### 3. **Troubleshooting**
```json
{
  "verbose": true,       // Włącz przy problemach
  "retries": 3,         // Więcej prób przy błędach
  "max_host_error": 10  // Szybko pomiń problematyczne hosty
}
```

### 4. **Monitorowanie postępu**
- Sprawdzaj status skanowania: `GET /api/v1/scan/{scan_id}`
- Obserwuj logi kontenerów: `docker logs scanner-nuclei`
- Monitoruj wydajność Redis queue

---

*Ten przewodnik pokrywa wszystkie opcje konfiguracyjne dostępne w systemie EASM dla skanera Nuclei. W przypadku pytań sprawdź dokumentację API lub logi serwisu.*
