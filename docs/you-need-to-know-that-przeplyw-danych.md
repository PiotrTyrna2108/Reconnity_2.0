# Przepływ danych w systemie EASM

## Architektura systemu

System EASM (External Attack Surface Management) jest zbudowany w architekturze mikroserwisowej składającej się z następujących głównych komponentów:

1. **easm-api (API Gateway)** - punkt wejścia dla klientów zewnętrznych
2. **easm-core (Core API)** - centralna logika biznesowa i zarządzanie danymi
3. **skanery** - wyspecjalizowane serwisy do wykonywania zadań skanowania (nmap, masscan, nuclei)

## Przepływ danych dla pełnego skanu organizacji

Poniżej przedstawiony jest kompletny przepływ danych dla przykładowego scenariusza pełnego skanowania organizacji XYZ:

### 1. Żądanie z GUI do API Gateway

Użytkownik w interfejsie GUI wybiera opcję pełnego skanu dla organizacji XYZ, określając docelowy adres (np. xyz.com) i zaznaczając opcję wykorzystania wszystkich skanerów.

**Przykładowe żądanie HTTP wysyłane z GUI do API Gateway:**

```http
POST /api/v1/scan HTTP/1.1
Host: easm-api:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "target": "xyz.com",
  "scanner": "all",
  "organization_id": "org_xyz123",
  "options": {
    "nmap": {
      "ports": "1-65535",
      "scan_type": "SYN",
      "timing": 4,
      "os_detection": true,
      "service_detection": true,
      "script_scan": true,
      "timeout": 1800
    },
    "masscan": {
      "ports": "1-65535",
      "rate": 10000,
      "timeout": 600
    },
    "nuclei": {
      "templates": ["cves", "dns", "file", "headless", "http", "network", "ssl", "workflows"],
      "severity": ["critical", "high", "medium", "low", "info"],
      "timeout": 3600,
      "rate": 150,
      "concurrency": 50,
      "follow_redirects": true,
      "verbose": true
    }
  }
}
```

### 2. API Gateway przetwarza żądanie

`easm-api` otrzymuje żądanie i przekazuje je bezpośrednio do Core API bez modyfikacji, działając jako transparentne proxy:

```python
# Uproszczony fragment kodu w easm-api/app/main.py
@app.api_route(f"{API_PREFIX}/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_endpoint(path: str, request: Request):
    """Universal proxy endpoint that forwards all requests to core API"""
    try:
        # Get request body if it exists
        body = await request.body() if request.method in ["POST", "PUT"] else None
        
        # Get query parameters
        params = dict(request.query_params)
        
        # Log request details
        logger.info(
            f"Proxying {request.method} request to {path}",
            extra={"target": path, "method": request.method}
        )
        
        # Forward request to core API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=f"{CORE_URL}/api/v1/{path}",
                params=params,
                headers={k: v for k, v in request.headers.items() 
                         if k.lower() not in ["host", "content-length"]},
                content=body
            )
            
            # Return response from core API
            content_type = response.headers.get("content-type", "application/json")
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )
```

W przypadku żądania skanowania "all" (wszystkimi skanerami), logika obsługi tego przypadku znajduje się w `easm-core`. API Gateway po prostu przekazuje żądanie dalej bez żadnej modyfikacji czy logiki biznesowej.

### 3. Core API otrzymuje żądania i tworzy zadania skanowania

`easm-core` odbiera żądanie i przetwarza je według typu skanera. W przypadku skanera typu "all", `easm-core` automatycznie tworzy zadania dla wszystkich dostępnych skanerów:

```python
# Uproszczony fragment kodu w easm-core/app/api/routers/scan.py
@router.post("/scan", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    try:
        # Obsługa specjalnego przypadku - skan wszystkimi skanerami
        if request.scanner == "all":
            scan_ids = []
            
            # Wywołaj każdy skaner osobno
            for scanner_type in ["nmap", "masscan", "nuclei"]:
                scanner_options = request.options.get(scanner_type, {})
                
                # Utwórz i uruchom zadanie dla konkretnego skanera
                result = await scan_service.create_scan(
                    target=request.target,
                    scanner=scanner_type,
                    options=scanner_options,
                    organization_id=request.organization_id
                )
                scan_ids.append(result["scan_id"])
            
            # Zwróć listę identyfikatorów wszystkich uruchomionych skanów
            return {
                "scan_ids": scan_ids,
                "status": "queued",
                "message": f"Multiple scans queued for target {request.target}"
            }
        
        # Dla pojedynczego skanera
        return await create_single_scanner_scan(request, scan_service)

# Dla określonych typów skanerów
@router.post("/scan/nmap", response_model=ScanResponse)
async def create_nmap_scan(
    request: NmapScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    try:
        # Użyj serwisu do utworzenia rekordu skanu w bazie danych
        result = await scan_service.create_scan(
            target=request.target,
            scanner=ScannerType.NMAP,
            options=request.options.dict(),
            organization_id=request.organization_id
        )
        
        # Umieść zadanie w kolejce Celery
        celery_app.send_task(
            "app.tasks.scan_asset",
            args=[result["scan_id"], request.model_dump()],
            queue="celery"
        )
        
        return ScanResponse(**result)
```

### 4. Zadanie Celery przetwarza żądanie skanowania

Worker Celery odbiera zadanie i kieruje je do odpowiedniego skanera:

```python
# Uproszczony fragment kodu w easm-core/app/tasks/scan_tasks.py
@celery_app.task(name="app.tasks.scan_asset", bind=True)
def scan_asset(self, scan_id: str, payload: Dict[str, Any]):
    """Main scan orchestration task"""
    target = payload["target"]
    scanner = payload["scanner"]
    options = payload.get("options", {})
    
    logger.info(f"[SCAN_TASK] Starting scan {scan_id} for target={target} scanner={scanner}")
    
    try:
        # Aktualizuj status skanu w bazie danych na "running"
        update_scan_status(scan_id, "running")
        
        # Przekieruj zadanie do odpowiedniego skanera
        if scanner == "nmap":
            celery_app.send_task(
                "scanner-nmap.run",
                args=[scan_id, target, options],
                queue="scanner-nmap"
            )
        elif scanner == "masscan":
            celery_app.send_task(
                "scanner-masscan.run",
                args=[scan_id, target, options],
                queue="scanner-masscan"
            )
        elif scanner == "nuclei":
            celery_app.send_task(
                "scanner-nuclei.run",
                args=[scan_id, target, options],
                queue="scanner-nuclei"
            )
```

### 5. Moduł skanera wykonuje właściwe skanowanie

Każdy skaner otrzymuje zadanie i wykonuje właściwe skanowanie:

```python
# Uproszczony fragment kodu w scanners/scanner-nuclei/app/main.py
@celery_app.task(name="scanner-nuclei.run", bind=True)
def run_nuclei_scan(self, scan_id: str, target: str, options: Dict[str, Any] = None):
    """Execute nuclei vulnerability scan for given target"""
    logger.info(f"[NUCLEI] Starting vulnerability scan for {target} (id={scan_id})")
    
    try:
        # Zbuduj polecenie nuclei z odpowiednimi flagami
        nuclei_args = build_nuclei_command(target, options)
        logger.info(f"[NUCLEI] Running command: {' '.join(nuclei_args)}")
        
        # Uruchom skanowanie
        start_time = time.time()
        result = subprocess.run(
            nuclei_args,
            capture_output=True,
            text=True,
            timeout=int(options.get("timeout", 600))
        )
        scan_duration = time.time() - start_time
        
        # Przetwórz wyniki
        if result.returncode == 0 or result.stdout:
            # Sparsuj wyniki skanowania
            scan_results = parse_nuclei_output(result.stdout, target, scan_id, scan_duration)
            
            # Raportuj wyniki z powrotem do Core API
            report_scan_completion(scan_id, scan_results)
```

### 6. Raportowanie wyników z powrotem do Core API

Po zakończeniu skanowania, skaner wysyła wyniki z powrotem do Core API:

```python
def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/complete",
            json=results,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[REPORT] Scan completion reported: {scan_id}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to report completion: {e}")
```

### 7. Core API zapisuje wyniki w bazie danych

Core API odbiera wyniki i zapisuje je w bazie danych:

```python
@router.post("/scan/{scan_id}/complete")
async def complete_scan(
    scan_id: str,
    results: Dict[str, Any],
    scan_service: ScanService = Depends(get_scan_service)
):
    """Complete a scan and save results"""
    try:
        # Zaktualizuj status skanu i zapisz wyniki
        await scan_service.complete_scan(scan_id, results)
        
        # Przetwórz znalezione podatności
        if "vulnerabilities" in results:
            await scan_service.process_findings(scan_id, results["vulnerabilities"])
        
        # Oblicz poziom ryzyka dla znalezionych podatności
        await scan_service.calculate_risk_score(scan_id)
        
        return {"status": "success", "message": f"Scan {scan_id} completed successfully"}
```

### 8. Odpytywanie o status i wyniki skanowania

GUI regularnie odpytuje API o status skanowania:

```http
GET /api/v1/scan/f82a4c6e-1b3d-4a5c-9d7e-8f6g5h4i3j2k HTTP/1.1
Host: easm-api:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

API Gateway przekazuje zapytanie do Core API i zwraca wyniki do GUI.

## Schemat przepływu danych

```
+------------------------+       +------------------------+      +------------------------+
|                        |  1.   |                        |  2.  |                        |
|  GUI (Interfejs        | ----> |  easm-api              | ---> |  easm-core            |
|  użytkownika)          |       |  (API Gateway)         |      |  (Core API)           |
|                        |       |                        |      |                        |
+------------------------+       +------------------------+      +------------+-----------+
         ^                                 ^                                |
         |                                 |                                |
         | 8.                              | 7.                             | 3.
         |                                 |                                v
+--------+---------+               +-------+----------+      +------------------------+
|                  |               |                  |      |                        |
| Wyniki skanowania| <------------- Wyniki skanowania| <---- | Celery Worker         |
| (w GUI)          |       9.     | (z Core API)     |      | (Zadania skanowania)   |
|                  |               |                  |      |                        |
+------------------+               +------------------+      +------------+-----------+
                                                                          |
                                                                          | 4.
                                                                          v
                                                             +------------------------+
                                                             |                        |
                                                             | Skanery:               |
                                                             | - scanner-nmap         |
                                                             | - scanner-masscan      |
                                                             | - scanner-nuclei       |
                                                             |                        |
                                                             +------------+-----------+
                                                                          |
                                                                          | 5.
                                                                          v
                                                             +------------------------+
                                                             |                        |
                                                             | Wykonanie narzędzi:    |
                                                             | - nmap                 |
                                                             | - masscan              |
                                                             | - nuclei               |
                                                             |                        |
                                                             +------------+-----------+
                                                                          |
                                                                          | 6.
                                                                          v
                                                             +------------------------+
                                                             |                        |
                                                             | Raportowanie wyników   |
                                                             | z powrotem do Core API |
                                                             |                        |
                                                             +------------------------+
```

## Uzasadnienie architektury

Architektura z podziałem na `easm-api` i `easm-core` oraz skanery ma swoje uzasadnienie:

1. **easm-api (API Gateway)** pełni rolę prostego proxy:
   - Stanowi jednolity punkt wejścia dla klientów zewnętrznych
   - Przekazuje wszystkie zapytania bez modyfikacji do easm-core
   - Ukrywa wewnętrzną strukturę systemu przed klientami zewnętrznymi
   - Jest punktem, w którym można wdrożyć warstwę bezpieczeństwa lub monitoringu

2. **easm-core** pełni rolę centralnego serwisu biznesowego:
   - Zarządza całą logiką biznesową
   - Koordynuje pracę wszystkich skanerów
   - Zarządza bazą danych i przechowuje wszystkie wyniki
   - Obsługuje komunikację między różnymi komponentami systemu

3. **skanery** są wykonawcami konkretnych zadań:
   - Zajmują się wyłącznie wykonaniem specyficznego zadania skanowania
   - Nie mają bezpośredniego kontaktu z klientami zewnętrznymi
   - Nie przechowują danych (są bezstanowe)

Ta hierarchiczna struktura pozwala na:
- Centralne zarządzanie danymi - wszystkie dane przechodzą przez jedno miejsce
- Uproszczoną logikę skanerów - skanery skupiają się tylko na skanowaniu
- Lepszą kontrolę nad przepływem pracy - core może koordynować złożone operacje
- Łatwiejszą integrację nowych skanerów - nowy skaner musi tylko komunikować się z core

## Przepływ API dla skanerów

System udostępnia szereg endpointów API dla obsługi skanów:

### Endpointy do uruchamiania skanów
- `POST /api/v1/scan` - ogólny endpoint
- `POST /api/v1/scan/nmap` - specjalizowany dla Nmap
- `POST /api/v1/scan/masscan` - specjalizowany dla Masscan 
- `POST /api/v1/scan/nuclei` - specjalizowany dla Nuclei

### Endpointy do monitorowania skanów
- `GET /api/v1/scan/{scan_id}` - sprawdzanie statusu

### Endpointy informacyjne (do odkrywania opcji)
- `GET /api/v1/scan/options` - wszystkie dostępne opcje
- `GET /api/v1/scan/options/{scanner_type}` - opcje dla konkretnego skanera
- `GET /api/v1/scan/nuclei/templates` - dostępne szablony Nuclei
- `GET /api/v1/scan/nuclei/severity-levels` - poziomy dotkliwości dla Nuclei

## Korzyści z architektury uniwersalnego proxy

Przekształcenie `easm-api` w uniwersalne proxy przyniosło następujące korzyści:

1. **Eliminacja duplikacji kodu** - nie ma już potrzeby powielania modeli danych i logiki biznesowej między `easm-api` i `easm-core`.

2. **Łatwiejsze utrzymanie** - wszystkie zmiany w API muszą być wprowadzane tylko w jednym miejscu (`easm-core`), co upraszcza zarządzanie kodem i zmniejsza ryzyko błędów.

3. **Automatyczna synchronizacja** - gdy wprowadzane są nowe endpointy lub zmiany w `easm-core`, są one natychmiast dostępne poprzez API Gateway bez konieczności aktualizacji kodu proxy.

4. **Jednolite API** - klienci zawsze otrzymują dokładnie te same odpowiedzi, jakie generuje `easm-core`, bez ryzyka rozbieżności między warstwami.

5. **Mniejsza złożoność systemu** - architektura jest prostsza i bardziej przejrzysta, co ułatwia zrozumienie przepływu danych w systemie.
