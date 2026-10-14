# Galaxy Atlas · Star Wars

Небольшой красивый сайт на **FastAPI**: атлас семи миров Star Wars, включая Камино и Корусант, поиск по названию/ландшафту и фильтр по региону. HTML, CSS и JavaScript без сборки. Планеты нарисованы CSS, внешних сервисов и шрифтов нет. Эндор представлен как лесная луна. Неофициальный учебный фан-проект.

**В репозитории намеренно оставлен один визуальный дефект для тренировки коммуникации DevOps ↔ frontend.** Начните с [задания](docs/exercise.md). Решение отдельно: [памятка наставнику со спойлером](docs/mentor.md). Деплой, облачные ресурсы и CI/CD не настроены.

## Локальный запуск (Python 3.11+)

Запускайте команды из корня репозитория. Активация окружения не требуется.

### Windows / PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Открыть сайт: <http://127.0.0.1:8000>. Остановить: `Ctrl+C`.
Health-check: <http://127.0.0.1:8000/health>. Swagger: <http://127.0.0.1:8000/docs> (его интерфейс использует CDN; самому сайту CDN не нужен).
Если порт занят, укажите другой `--port`, например `8001`. Если `python` отсутствует в PATH Windows, используйте `py -3.11` для создания окружения. Установка пакетов и Chromium требует интернета; после установки сайт работает локально без интернета.

## Тесты

`requirements-lock.txt` фиксирует полный проверенный набор, включая инструменты тестирования. `requirements.txt` и `requirements-dev.txt` описывают прямые зависимости для сознательного обновления. Для минимального запуска без тестов достаточно `pip install -r requirements.txt`.

### Windows / PowerShell

```powershell
# API, выдача HTML и статики, поиск, фильтрация, валидация и 404
.\.venv\Scripts\python.exe -m pytest

# Один раз скачать браузер для UI-тестов
.\.venv\Scripts\python.exe -m playwright install chromium

# UI: каталог, поиск, фильтр, ошибка/повтор, desktop/tablet/mobile
.\.venv\Scripts\python.exe -m pytest tests/ui

# Все тесты вместе
.\.venv\Scripts\python.exe -m pytest tests
```

В Linux/macOS замените `.\.venv\Scripts\python.exe` на `.venv/bin/python`. В Linux для установки системных библиотек браузера может понадобиться `.venv/bin/python -m playwright install --with-deps chromium`.

UI-тесты **сами поднимают и останавливают** FastAPI на свободном loopback-порту. Отдельный сервер для них запускать не нужно. Скриншоты сохраняются в `output/playwright/` (не отслеживается Git).

Нормальный исход до исправления дефекта: API и функциональные UI-тесты проходят, **3 mobile-проверки имеют XFAIL**. Это зафиксированный учебный дефект, а не доказательство отсутствия проблем. Чтобы увидеть обычное падение:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui -k mobile --runxfail
```

После исправления удалите `xfail` у мобильного теста и повторите `pytest tests`. `strict=True` специально делает неожиданное прохождение (XPASS) ошибкой, пока метка не удалена.

## Структура и API

```text
app/main.py             FastAPI, health-check, данные и API
app/static/             HTML, CSS, JS, favicon
tests/api/              тесты через FastAPI TestClient
tests/ui/               настоящие браузерные проверки Playwright
docs/exercise.md         задание ученику
docs/mentor.md           причина и критерии исправления (спойлер)
docs/incident-template.md шаблон сообщения о проблеме
```

| Запрос | Результат |
| --- | --- |
| `GET /` | Главная страница |
| `GET /health` | Статус процесса приложения |
| `GET /api/planets` | Все миры |
| `GET /api/planets?q=hoth` | Поиск по русскому названию, id или ландшафту |
| `GET /api/planets?region=outer` | Внешнее кольцо (`core`, `unknown` также поддерживаются) |
| `GET /api/planets/tatooine` | Один мир; неизвестный id → 404 |

Поиск и регион можно сочетать. Неверный регион или запрос длиннее 100 символов → 422. Данные хранятся в коде; сервер ничего не записывает. `/health` проверяет доступность приложения и не диагностирует визуальное состояние страницы.

Основа API и тестов следует официальной документации [FastAPI StaticFiles](https://fastapi.tiangolo.com/tutorial/static-files/) и [TestClient](https://fastapi.tiangolo.com/tutorial/testing/).

Результаты выполненных проверок и ограничения: [docs/verification.md](docs/verification.md).
