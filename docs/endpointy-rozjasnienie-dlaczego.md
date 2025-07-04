```markdown
# Endpointy EASM Core – szczegółowy opis

---

## 1. **GET /health**

**Do czego służy:**  
Służy do sprawdzania, czy aplikacja EASM Core działa poprawnie. Używany przez load balancery, systemy monitoringu i DevOps.

**Typowe zastosowania:**  
- Monitoring kontenerów (np. Kubernetes liveness/readiness probe)
- Sprawdzanie dostępności usługi przez load balancer

**Co zwraca:**  
Zwykle prostą odpowiedź JSON, np. `{"status": "ok"}` lub szczegóły o stanie bazy.

**Kto korzysta:**  
Systemy monitoringu, administratorzy, DevOps.

---

## 2. **POST /api/v1/scan**

**Do czego służy:**  
Tworzy nowe zadanie skanowania. Przyjmuje dane zasobu do przeskanowania oraz opcje skanowania.

**Typowe zastosowania:**  
- Użytkownik lub system zleca nowy skan (np. domeny, IP)
- Frontend wywołuje ten endpoint po wypełnieniu formularza

**Co przyjmuje:**  
JSON z danymi zasobu (np. IP, domena) oraz opcjami skanowania (np. typ skanu, zakres portów).

**Co zwraca:**  
Identyfikator nowego skanu (`scan_id`), status zadania, ewentualnie szczegóły kolejki.

**Kto korzysta:**  
Frontend, API, automatyzacje, integracje.

---

## 3. **GET /api/v1/scan/{scan_id}**

**Do czego służy:**  
Pozwala pobrać status i wyniki konkretnego skanu.

**Typowe zastosowania:**  
- Frontend wyświetla postęp lub wyniki skanowania użytkownikowi
- System automatycznie sprawdza, czy skan się zakończył i pobiera wyniki

**Co przyjmuje:**  
Parametr ścieżki `scan_id` (identyfikator skanu).

**Co zwraca:**  
Status skanu (`queued`, `running`, `done`, `failed`), wyniki skanowania (np. otwarte porty, podatności), daty, szczegóły błędów.

**Kto korzysta:**  
Frontend, API, automatyzacje, integracje.

---

## 4. **GET /api/v1/scan/options**

**Do czego służy:**  
Zwraca dostępne opcje skanowania, które użytkownik/system może wybrać przy tworzeniu nowego skanu.

**Typowe zastosowania:**  
- Frontend dynamicznie pobiera listę możliwych opcji (np. zakresy portów, typy skanów, dostępne skanery)
- Umożliwia rozbudowę systemu bez konieczności zmiany frontendu

**Co przyjmuje:**  
Brak parametrów.

**Co zwraca:**  
JSON z listą dostępnych opcji, np.:
```json
{
  "scan_types": ["fast", "full", "custom"],
  "port_ranges": ["1-1024", "1-65535"],
  "scanners": ["nmap", "masscan", "nuclei"]
}
```

**Kto korzysta:**  
Frontend (do budowy formularza), API, integracje.

---

## 5. **GET /api/v1/nuclei/templates** *(jeśli korzystasz z nuclei)*

**Do czego służy:**  
Zwraca listę dostępnych szablonów nuclei, które mogą być użyte podczas skanowania podatności.

**Typowe zastosowania:**  
- Frontend pozwala użytkownikowi wybrać szablony do skanowania
- System automatycznie dobiera szablony do zadania

**Co przyjmuje:**  
Brak parametrów.

**Co zwraca:**  
Listę szablonów nuclei (np. nazwy, opisy, poziom krytyczności).

**Kto korzysta:**  
Frontend, API, integracje.

---

## 6. **POST /api/v1/nuclei/templates** *(opcjonalnie, jeśli korzystasz z nuclei)*

**Do czego służy:**  
Pozwala dodać lub odświeżyć szablony nuclei w systemie.

**Typowe zastosowania:**  
- Administrator lub system automatycznie aktualizuje szablony nuclei

**Co przyjmuje:**  
JSON z danymi szablonów lub polecenie odświeżenia.

**Co zwraca:**  
Status operacji (np. sukces, liczba zaktualizowanych szablonów).

**Kto korzysta:**  
Administrator, system automatyzacji.

---

# Podsumowanie

- **/health** – monitoring i sprawdzanie dostępności
- **/api/v1/scan** (POST) – inicjowanie nowego skanu
- **/api/v1/scan/{scan_id}** (GET) – pobieranie statusu i wyników skanu
- **/api/v1/scan/options** (GET) – dynamiczne pobieranie dostępnych opcji skanowania
- **/api/v1/nuclei/templates** (GET/POST) – zarządzanie szablonami nuclei (jeśli używasz nuclei)

Każdy endpoint ma jasno określoną rolę, typowe zastosowania, zwracane dane i grupę odbiorców.
```


-----------------------

Twoje obecne endpointy **są uniwersalne i dobrze zaprojektowane** pod rozbudowę systemu o kolejne skanery – pod warunkiem, że trzymasz się architektury, w której:

- **Tworzenie skanu** (`POST /api/v1/scan`) – zawsze przyjmuje dane zasobu i opcje, a backend sam decyduje, który skaner uruchomić (na podstawie opcji lub typu skanu).
- **Pobieranie statusu/wyników** (`GET /api/v1/scan/{scan_id}`) – zawsze zwraca status i wyniki, niezależnie od tego, który skaner był użyty.
- **Opcje skanowania** (`GET /api/v1/scan/options`) – możesz dynamicznie rozbudowywać, by zwracały nowe typy skanów, nowe zakresy, nowe skanery.
- **Szablony nuclei** – zostają tylko jeśli korzystasz z nuclei, dla innych skanerów nie musisz ich powielać.

**Nie musisz dodawać osobnych endpointów dla każdego nowego skanera!**
- Wystarczy, że backend (Core) będzie rozpoznawał po opcjach, który skaner uruchomić.
- Możesz rozbudowywać `/api/v1/scan/options`, by frontend wiedział, jakie nowe możliwości są dostępne.

**Podsumowanie:**  
Tak, te endpointy są wystarczająco uniwersalne.  
Jeśli będziesz mieć 20 różnych skanerów, nie musisz dodawać nowych endpointów – wystarczy, że rozbudujesz logikę backendu i opcje skanowania.  
**To jest skalowalne i zgodne z dobrymi praktykami!**


####################### opis i rozwów ###############
# Funkcje obecnych skanerów w EASM i możliwości kolejnych mikroserwisów

---

## 1. **Obecne skanery – do czego służą w świecie bezpieczeństwa**

### **Nmap**
- **Do czego służy:**  
  Najpopularniejsze narzędzie do skanowania portów i wykrywania usług sieciowych.
- **Funkcje:**  
  - Skanowanie portów TCP/UDP (otwarte/zamknięte)
  - Wykrywanie usług i ich wersji (service/version detection)
  - Wykrywanie systemu operacyjnego (OS detection)
  - Wykrywanie hostów w sieci (host discovery)
- **W EASM:**  
  Używasz Nmap do identyfikacji otwartych portów, usług, systemów operacyjnych na zasobach (IP, domeny).

---

### **Masscan**
- **Do czego służy:**  
  Najszybszy skaner portów na świecie, używany do bardzo szybkiego przeszukiwania dużych zakresów adresów IP.
- **Funkcje:**  
  - Skanowanie portów TCP (brak UDP)
  - Skanowanie ogromnych zakresów IP w krótkim czasie (np. cały Internet)
  - Brak detekcji usług, tylko informacja o otwartym porcie
- **W EASM:**  
  Używasz Masscan do szybkiego wykrywania otwartych portów na dużych zakresach adresów – idealny do wstępnego rekonesansu.

---

### **Nuclei**
- **Do czego służy:**  
  Skaner podatności oparty na szablonach (template-based vulnerability scanner).
- **Funkcje:**  
  - Wykrywanie podatności webowych (XSS, SQLi, RCE, itp.)
  - Wykrywanie błędnych konfiguracji, ekspozycji plików, itp.
  - Skanowanie na podstawie tysięcy gotowych szablonów (community templates)
  - Możliwość pisania własnych szablonów
- **W EASM:**  
  Używasz Nuclei do automatycznego wykrywania podatności na wykrytych hostach/usługach.

---

## 2. **Możliwości kolejnych skanerów – jakie narzędzia open source możesz dodać i co nimi skanować**

Poniżej lista przykładowych narzędzi, które możesz dodać jako kolejne mikroserwisy – **każdy z nich realizuje inną funkcję** (nie powielają się z obecnymi):

---

### **1. WhatWeb**
- **Do czego służy:**  
  Identyfikacja technologii webowych na stronach (CMS, frameworki, serwery, biblioteki JS).
- **W EASM:**  
  Skanowanie wykrytych domen/hostów pod kątem użytych technologii webowych.
- **Open source:**  
  https://github.com/urbanadventurer/WhatWeb

---

### **2. Subfinder**
- **Do czego służy:**  
  Skanowanie i wykrywanie subdomen dla danej domeny.
- **W EASM:**  
  Rozszerzanie powierzchni ataku przez znajdowanie subdomen organizacji.
- **Open source:**  
  https://github.com/projectdiscovery/subfinder

---

### **3. Amass**
- **Do czego służy:**  
  Zaawansowane rozpoznanie DNS, wykrywanie subdomen, mapowanie infrastruktury.
- **W EASM:**  
  Mapowanie domen, subdomen, relacji DNS, ASN, IP.
- **Open source:**  
  https://github.com/owasp-amass/amass

---

### **4. Shodan CLI**
- **Do czego służy:**  
  Wyszukiwanie informacji o hostach w bazie Shodan (baza otwartych portów i usług z całego świata).
- **W EASM:**  
  Wzbogacanie danych o hostach o informacje z Shodan (np. banery, podatności, geolokalizacja).
- **Open source:**  
  https://github.com/achillean/shodan-python

---

### **5. Wappalyzer CLI**
- **Do czego służy:**  
  Identyfikacja technologii webowych (podobnie jak WhatWeb, ale inny silnik).
- **W EASM:**  
  Alternatywa lub uzupełnienie dla WhatWeb.
- **Open source:**  
  https://github.com/wappalyzer/wappalyzer

---

### **6. Nikto**
- **Do czego służy:**  
  Skaner podatności webowych (głównie błędne konfiguracje, stare wersje serwerów, itp.).
- **W EASM:**  
  Skanowanie serwerów HTTP pod kątem znanych błędów i podatności.
- **Open source:**  
  https://github.com/sullo/nikto

---

### **7. TruffleHog**
- **Do czego służy:**  
  Wyszukiwanie sekretów/API keys/tokenów w repozytoriach git i publicznych zasobach.
- **W EASM:**  
  Wykrywanie wycieków kluczy API, haseł, tokenów w publicznych repozytoriach organizacji.
- **Open source:**  
  https://github.com/trufflesecurity/trufflehog

---

### **8. Aquatone**
- **Do czego służy:**  
  Robienie screenshotów stron WWW, zbieranie metadanych.
- **W EASM:**  
  Automatyczne zrzuty ekranów wykrytych hostów webowych do analizy wizualnej.
- **Open source:**  
  https://github.com/michenriksen/aquatone

---

### **9. SSLyze**
- **Do czego służy:**  
  Skanowanie konfiguracji SSL/TLS na serwerach.
- **W EASM:**  
  Wykrywanie słabych szyfrów, błędnych certyfikatów, podatności w konfiguracji SSL.
- **Open source:**  
  https://github.com/nabla-c0d3/sslyze

---

### **10. GitLeaks**
- **Do czego służy:**  
  Wyszukiwanie sekretów w repozytoriach git.
- **W EASM:**  
  Wykrywanie wycieków haseł, tokenów, kluczy w kodzie organizacji.
- **Open source:**  
  https://github.com/gitleaks/gitleaks

---

### **11. Feroxbuster**
- **Do czego służy:**  
  Skanowanie katalogów i plików na serwerach WWW (content discovery).
- **W EASM:**  
  Odkrywanie ukrytych zasobów na stronach (np. /admin, /backup.zip).
- **Open source:**  
  https://github.com/epi052/feroxbuster

---

### **12. OSINT narzędzia (np. theHarvester)**
- **Do czego służy:**  
  Zbieranie informacji o domenach, mailach, hostach z publicznych źródeł.
- **W EASM:**  
  Automatyczne wzbogacanie wiedzy o organizacji.
- **Open source:**  
  https://github.com/laramies/theHarvester

---

## **Podsumowanie**

- **Każdy skaner powinien mieć unikalną funkcję** – nie powielaj tych samych typów skanów.
- **Wybieraj narzędzia open source** – jest ich bardzo dużo, możesz pokryć praktycznie każdy aspekt rekonesansu i bezpieczeństwa.
- **W EASM** możesz skanować: porty, usługi, podatności, technologie webowe, subdomeny, konfiguracje SSL, wycieki sekretów, katalogi WWW, dane OSINT, screenshoty stron i wiele więcej.

**Dzięki takiej modularności możesz stale rozbudowywać system o nowe mikroserwisy skanujące, nie powielając funkcji i zapewniając szeroki zakres bezpieczeństwa!**

-----------------------------------------------------
Dodatkowe skanery 

# Dodatkowe skanery i ich unikalne funkcje do EASM

Poniżej znajdziesz kolejne propozycje narzędzi open source, które możesz zaimplementować jako mikroserwisy skanujące w EASM. Każdy z nich realizuje inną, niepowtarzającą się funkcję:

---

### **13. Nmap NSE (Nmap Scripting Engine)**
- **Do czego służy:**  
  Automatyczne uruchamianie specjalistycznych skryptów Nmap (np. brute-force, wykrywanie podatności, enumeracja SMB, DNS, itp.).
- **W EASM:**  
  Wykrywanie specyficznych podatności i usług, których nie wykryje zwykły skan portów.
- **Open source:**  
  Wbudowane w Nmap (https://nmap.org/nsedoc/)

---

### **14. ZAP (OWASP Zed Attack Proxy)**
- **Do czego służy:**  
  Dynamiczne testy bezpieczeństwa aplikacji webowych (DAST), automatyczne wykrywanie podatności w aplikacjach webowych.
- **W EASM:**  
  Skanowanie aplikacji webowych pod kątem XSS, SQLi, CSRF, itp. (pełny DAST).
- **Open source:**  
  https://github.com/zaproxy/zaproxy

---

### **15. DNSRecon**
- **Do czego służy:**  
  Zaawansowane rozpoznanie DNS, wykrywanie stref, transferów, rekordów, brute-force subdomen.
- **W EASM:**  
  Wykrywanie błędnych konfiguracji DNS, transferów stref, ukrytych rekordów.
- **Open source:**  
  https://github.com/darkoperator/dnsrecon

---

### **16. SMBMap**
- **Do czego służy:**  
  Enumeracja udziałów SMB, uprawnień, dostępnych plików na serwerach Windows.
- **W EASM:**  
  Wykrywanie otwartych udziałów sieciowych, podatności na nieautoryzowany dostęp do plików.
- **Open source:**  
  https://github.com/ShawnDEvans/smbmap

---

### **17. Enum4linux-ng**
- **Do czego służy:**  
  Enumeracja informacji o usługach Windows (NetBIOS, SMB, RPC, użytkownicy, grupy, polityki).
- **W EASM:**  
  Zbieranie informacji o użytkownikach, grupach, politykach domenowych w sieciach Windows.
- **Open source:**  
  https://github.com/cddmp/enum4linux-ng

---

### **18. WPScan**
- **Do czego służy:**  
  Skanowanie stron opartych o WordPress pod kątem podatności, słabych haseł, nieaktualnych pluginów.
- **W EASM:**  
  Wykrywanie podatności i słabych punktów w instalacjach WordPress.
- **Open source:**  
  https://github.com/wpscanteam/wpscan

---

### **19. S3Scanner**
- **Do czego służy:**  
  Wykrywanie publicznie dostępnych bucketów Amazon S3 i ich zawartości.
- **W EASM:**  
  Wykrywanie wycieków danych przez źle skonfigurowane zasoby chmurowe.
- **Open source:**  
  https://github.com/sa7mon/S3Scanner

---

### **20. GitHub Search (github-dorks)**
- **Do czego służy:**  
  Automatyczne wyszukiwanie w publicznych repozytoriach GitHub (dorking) pod kątem wycieków, sekretów, konfiguracji.
- **W EASM:**  
  Wykrywanie wycieków danych, kluczy, konfiguracji w publicznych repo organizacji.
- **Open source:**  
  https://github.com/techgaun/github-dorks

---

### **21. IVRE**
- **Do czego służy:**  
  Analiza i wizualizacja dużych zbiorów danych z rekonesansu sieciowego (np. z Nmap, Masscan).
- **W EASM:**  
  Agregacja, analiza i wizualizacja danych z wielu skanów, wykrywanie anomalii.
- **Open source:**  
  https://github.com/cea-sec/ivre

---

### **22. EyeWitness**
- **Do czego służy:**  
  Automatyczne robienie screenshotów usług webowych, RDP, VNC, oraz zbieranie metadanych.
- **W EASM:**  
  Wizualna inspekcja wykrytych hostów i usług (nie tylko HTTP!).
- **Open source:**  
  https://github.com/FortyNorthSecurity/EyeWitness

---

### **23. CrackMapExec**
- **Do czego służy:**  
  Automatyzacja testów penetracyjnych w sieciach Windows (SMB, RDP, WinRM, LDAP).
- **W EASM:**  
  Wykrywanie słabych haseł, błędnych konfiguracji, enumeracja użytkowników w sieciach Windows.
- **Open source:**  
  https://github.com/Porchetta-Industries/CrackMapExec

---

### **24. RouterSploit**
- **Do czego służy:**  
  Wykrywanie podatności w urządzeniach sieciowych (routery, IoT).
- **W EASM:**  
  Testowanie urządzeń sieciowych pod kątem znanych podatności.
- **Open source:**  
  https://github.com/threat9/routersploit

---

### **25. XSStrike**
- **Do czego służy:**  
  Zaawansowany skaner podatności XSS.
- **W EASM:**  
  Wykrywanie podatności XSS na stronach webowych.
- **Open source:**  
  https://github.com/s0md3v/XSStrike

---

**Każdy z tych skanerów możesz wdrożyć jako osobny mikroserwis w EASM, zapewniając unikalną funkcjonalność i poszerzając zakres rekonesansu oraz testów bezpieczeństwa!**