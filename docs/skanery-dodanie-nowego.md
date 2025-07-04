----------------------
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Dodawanie nowego skanera wszystko co musisz wiedzeic:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

Oto **uniwersalna, dobra praktyka struktury folderu skanera** oraz checklistę, co i gdzie dodać, aby nowy skaner był spójny z całą aplikacją EASM Core:

---

## **Przykładowa struktura folderu nowego skanera**

```
scanner-nowy/
├── Dockerfile
├── requirements.txt
└── app/
    ├── __init__.py
    └── main.py
```

**Opcjonalnie, jeśli potrzebujesz:**
- `utils.py` (funkcje pomocnicze)
- `config.py` (konfiguracja, parsowanie ENV)
- `README.md` (dokumentacja skanera)

---

## **Co powinno być w `main.py` skanera?**

- Definicja funkcji zadania (np. `async def run_nowy_scan(ctx, scan_id, payload):`)
- Parsowanie opcji skanowania z `payload`
- Budowanie polecenia CLI lub wywołanie biblioteki skanującej
- Przetwarzanie wyników do formatu akceptowanego przez Core
- Wysyłka wyników do Core przez Redis/ARQ (`ctx['redis'].enqueue_job("process_scan_result", ...)`)
- Obsługa wyjątków i logowanie

**Przykład szkieletu:**
```python
# app/main.py
import os
from arq import create_pool
from arq.connections import RedisSettings

async def run_nowy_scan(ctx, scan_id, payload):
    # 1. Parsuj payload
    # 2. Uruchom skanowanie (CLI lub lib)
    # 3. Przetwórz wynik
    # 4. Wyślij wynik do Core przez Redis
    await ctx['redis'].enqueue_job("process_scan_result", scan_id, status, results)

class WorkerSettings:
    functions = [run_nowy_scan]
    redis_settings = RedisSettings(host=os.getenv("REDIS_HOST", "redis"))
```

---

## **Co zrobić w EASM Core, żeby dodać nowy skaner?**

1. **W `app/tasks/tasks/scan_tasks.py`:**
   - Dodaj funkcję, która wrzuca zadanie do kolejki dla nowego skanera (np. `run_nowy_scan`).
   - Jeśli masz logikę wyboru skanera, rozbuduj ją o nowy typ.

2. **W `app/tasks/config/queue_config.py`:**
   - Dodaj nazwę funkcji nowego skanera do listy `functions` (jeśli to wymagane przez ARQ).

3. **W `app/services/scan_service.py`:**
   - Rozbuduj logikę delegowania zadań, by obsługiwała nowy typ skanu (np. na podstawie opcji z `/api/v1/scan`).

4. **W `app/schemas/scan_options.py`:**
   - Dodaj nowe opcje, jeśli frontend ma je widzieć (np. nowy typ skanera).

5. **W `app/api/routers/scan_options.py`:**
   - Upewnij się, że endpoint `/api/v1/scan/options` zwraca nowe możliwości.

---

## **Podsumowanie – krok po kroku**

1. **Stwórz folder skanera według wzoru powyżej.**
2. **W `main.py` zaimplementuj funkcję zadania i obsługę Redis/ARQ.**
3. **W EASM Core:**
   - Dodaj obsługę nowego skanera w `scan_tasks.py`, `queue_config.py`, `scan_service.py`.
   - Zaktualizuj opcje w `scan_options.py` i endpoint `/api/v1/scan/options`.
4. **Zbuduj i uruchom nowy kontener skanera.**
5. **Testuj – zleć skan przez `/api/v1/scan` z odpowiednimi opcjami.**

---

**Trzymając się tej struktury i checklisty, każdy nowy skaner będzie spójny z całą aplikacją i łatwy do wdrożenia!**