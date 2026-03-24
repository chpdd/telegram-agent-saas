# Telegram Chat Agent

Monorepo для multi-tenant SaaS платформы с Telegram bot runtime, API, worker и admin dashboard.

## Services

- `services/api`: FastAPI API, webhook intake, catalog search, conversation loop
- `services/worker`: background runtime для watchdog, inactivity и session review
- `services/bot`: multi-bot webhook registration runtime
- `services/admin`: Streamlit dashboard

## Requirements

- `uv`
- `docker` + `docker compose`
- Python `3.13`

## Environment

Создай `.env` на основе `.env.example`.

Минимально нужны:

```bash
LLM_API_KEY=...
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/telegram_ai_agent
REDIS_URL=redis://localhost:6379/0
BOT_WEBHOOK_BASE_URL=https://example.com
BOT_WEBHOOK_SECRET=change_me
MODE=DEV
```

По умолчанию webhook conversation flow использует модель `qwen/qwen3-coder:free`.

## Docker Compose

Поднять весь стек:

```bash
docker compose up --build
```

Сервисы:

- API: `http://localhost:8000`
- Admin: `http://localhost:8501`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

Проверить конфиг compose:

```bash
docker compose config
```

## Database Migration

Применить первую migration:

```bash
uv run alembic upgrade head
```

Initial revision:

- `alembic/versions/20260324_0001_initial_schema.py`

## Local Run

Установить зависимости:

```bash
uv sync
```

Запустить API:

```bash
cd services/api/src
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Запустить worker:

```bash
cd services/worker/src
uv run python main.py
```

Запустить bot runtime:

```bash
cd services/bot/src
uv run python main.py
```

Запустить admin:

```bash
cd services/admin/src
uv run streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## Smoke Check

1. Подними `db` и `redis`
2. Выполни `uv run alembic upgrade head`
3. Запусти `api`, `worker`, `bot`, `admin`
4. Проверь:
   - `GET /health`
   - `POST /catalog/search`
   - `POST /conversations/{conversation_id}/messages`
   - `POST /webhooks/{tenant_id}`
5. Выполни тесты:

```bash
uv run ruff check . --fix
uv run pytest
```
