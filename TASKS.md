# ТРЕКЕР ЗАДАЧ ПРОЕКТА: SaaS Telegram AI Platform (Ultra Detailed)

## Легенда
- **ID:** Номер задачи
- **Task:** Краткое название
- **Description:** Что именно нужно сделать (план)
- **Context:** Что было сделано (отчет: файлы, коммиты, тесты)
- **Deps:** От каких задач зависит (ID)
- **Status:** [ ] - Todo, [/] - In Progress, [x] - Done

---

## 1. Окружение и Инфраструктура
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | Инициализация TASKS.md | Создание подробного трекера задач. | Файл создан и структурирован. | - | [x] |
| 1.2 | `uv` Workspace Setup | `uv init`, создание `pyproject.toml`, настройка зависимостей. | Инициализирован uv, добавлены базовые либы. Commit: a18ce42. | - | [x] |
| 1.3 | Ruff & Pre-commit | Настройка линтинга и хуков стиля. | Ruff сконфигурирован в pyproject.toml. Commit: c40f645. | 1.2 | [x] |
| 1.4 | Pytest Async Config | Настройка асинхронных тестов. | Настроен pytest-asyncio, создан conftest.py и первый тест. Commit: 36cc4e4. | 1.2 | [x] |
| 1.5 | Makefile Automation | Команды: `up`, `down`, `test`, `lint`, `migrate`, `logs`. | Makefile создан, команды lint/test проверены. Commit: f56f27e. | 1.2 | [x] |
| 1.6 | `.env.example` | Шаблон переменных окружения. | | - | [/] |

## 2. Базовая Архитектура (Core Service Layer)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | `core/config.py` | Pydantic Settings с валидацией. | Создан базовый конфиг в api сервисе. | 1.2 | [/] |
| 2.2 | `core/database.py` | SQLAlchemy engine + Base class. | Реализованы `Base`, `engine`, `async_session_maker`, `get_session`; тест `services/api/tests/test_database.py`. Ruff: ok. Pytest: ok. Commit: f6e47a1. | 1.2 | [x] |
| 2.3 | **Tenant Isolation Utility** | Механизм принудительного `tenant_id`. | Добавлен `services/api/src/core/tenancy.py` с `apply_tenant_filter`; тесты `services/api/tests/test_tenant_isolation.py`. Ruff: ok. Pytest: ok. Commit: 7e1df83. | 2.2 | [x] |
| 2.4 | `crud/base.py` | `BaseCRUD` и `SchemaCRUD`. | Добавлены `BaseCRUD`/`SchemaCRUD` в `services/api/src/crud/base.py`; тест `services/api/tests/test_crud_base.py`. Ruff: ok. Pytest: ok. Commit: 2dc3ede. | 2.2 | [x] |
| 2.5 | `core/logging.py` | JSON-логирование. | Добавлен `services/api/src/core/logging.py` с JSON formatter; тест `services/api/tests/test_logging.py`. Ruff: ok. Pytest: ok. Commit: daf3f4a. | 1.2 | [x] |

## 3. Модели и Миграции (Database Schema)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | `models/tenant.py` | UUID PK, bot_token, system_prompt. | Добавлен `services/api/src/models/tenant.py` + тест `services/api/tests/test_models_tenant.py`. Ruff: ok. Pytest: ok. Commit: 04102a0. | 2.2 | [x] |
| 3.2 | `models/product.py` | Базовые поля + JSONB attributes. | Добавлен `services/api/src/models/product.py` (JSONB). Удален `search_vector` и FTS-индекс. Тест `services/api/tests/test_models_product.py` обновлен. Ruff: ok. Pytest: ok. Commit: ce1b7c9. | 3.1 | [x] |
| 3.3 | `models/chat.py` | session_id, status (enum), user_id. | Добавлен `services/api/src/models/chat.py` и тест `services/api/tests/test_models_chat.py`. Ruff: ok. Pytest: ok. Commit: a683f9a. | 3.1 | [x] |
| 3.4 | `models/message.py` | role, content, latency_ms. | Добавлен `services/api/src/models/message.py` и тест `services/api/tests/test_models_message.py`. Ruff: ok. Pytest: ok. Commit: 526101a. | 3.3 | [x] |
| 3.5 | `models/order.py` | items (JSONB), total_price. | Добавлен `services/api/src/models/order.py` и тест `services/api/tests/test_models_order.py`. Ruff: ok. Pytest: ok. Commit: dcb8ea9. | 3.3 | [x] |
| 3.6 | Alembic Multi-Env | Настройка миграций. | Добавлены `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/.gitkeep`, `services/api/src/models/__init__.py`, тест `services/api/tests/test_alembic_setup.py`. Ruff: ok. Pytest: ok. Commit: 5bb1b44. | 3.2 | [x] |

## 4. Динамический Поиск и Каталог
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | **Dynamic Filter Generator** | Трансформация фильтров в SQL к JSONB. | Добавлен `services/api/src/core/filters.py` и тест `services/api/tests/test_dynamic_filter_generator.py`. Ruff: ok. Pytest: ok. Commit: a4a13fa. | 3.2 | [x] |
| 4.3 | Search Service | Метод `search` (JSONB). | Добавлен `services/api/src/services/search.py` и тест `services/api/tests/test_search_service.py`. Ruff: ok. Pytest: ok. Commit: 4d70ed4. | 4.1 | [x] |

## 5. Dashboard (Streamlit Management)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | UI: Auth Mock | Вход по "ID магазина". | Добавлены `services/admin/src/main.py`, `services/admin/src/auth.py`, тест `services/admin/tests/test_auth.py`. Ruff: ok. Pytest: ok. Commit: 183c22e. | 3.1 | [x] |
| 5.2 | UI: Schema Designer | CRUD для `catalog_schemas`. | Добавлены колонки (key/label/description) и CRUD в `services/admin/src/schema_designer.py`, обновлен `services/admin/src/main.py`, тест `services/admin/tests/test_schema_designer.py`. Ruff: ok. Pytest: ok. Commit: 183f0b6. | 3.2 | [x] |
| 5.4 | UI: Live Chat Monitor | Список активных чатов. | Добавлены `services/admin/src/chat_monitor.py`, обновлен `services/admin/src/main.py`, тест `services/admin/tests/test_chat_monitor.py`. Ruff: ok. Pytest: ok. Commit: 035ab29. | 3.3 | [x] |

## 6. Telegram & AI Integration
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 | Webhook Multi-Bot | Регистрация вебхуков. | Добавлены `services/bot/src/core/config.py`, `services/bot/src/core/bot.py`, `services/bot/src/webhooks.py`, тест `services/bot/tests/test_webhooks.py`, env в `.env.example`, pytest-mock. Ruff: ok. Pytest: ok. Commit: e33b75e. | 3.1 | [x] |
| 6.2 | AI Service Interface | Обертка над OpenRouter. | Добавлен `services/api/src/services/ai.py` (LangChain v1 `ChatOpenAI` с памятью диалога по `conversation_id`), тест `services/api/tests/test_ai_service.py`. Ruff: ok. Pytest: ok. Commit: ea1e523. | 2.1 | [x] |
| 6.3 | Tool: `catalog_tool` | Инструментарий для LLM. | Добавлен `services/api/src/services/catalog_tool.py` как LangChain `StructuredTool` поверх поиска каталога; тест `services/api/tests/test_catalog_tool.py`. Ruff: ok. Pytest: ok. Commit: 97ed2fd. | 4.3, 6.2 | [x] |
| 6.4 | AI Conversation Loop | Цикл: История -> LLM -> Ответ. | Добавлен `services/api/src/services/conversation.py` с LangChain tool-calling циклом и сохранением `Message`; обновлен `services/api/src/services/ai.py`, тест `services/api/tests/test_conversation_service.py`. Ruff: ok. Pytest: ok. Commit: af9c426. | 6.3, 3.5 | [x] |

## 7. Background Workers (The Analyzer)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 7.1 | **30s Watchdog (Redis)** | Мониторинг таймаутов в Redis. | Добавлены `services/worker/src/core/config.py`, `services/worker/src/watchdog.py`, тест `services/worker/tests/test_watchdog.py`. Ruff: ok. Pytest: ok. Commit: 8ccead2. | 6.4 | [x] |
| 7.2 | Inactivity Task | Проверка сессий > 2 часов. | Добавлен `services/worker/src/inactivity.py` с выборкой и закрытием неактивных чатов; в `services/api/src/models/chat.py` добавлен `updated_at`; тесты `services/worker/tests/test_inactivity.py` и `services/api/tests/test_models_chat.py` обновлены. Ruff: ok. Pytest: ok. Commit: ad80ce2. | 3.3 | [x] |
| 7.3 | **LLM Session Reviewer** | Аналитика: Summary, Sentiment. | Добавлен `services/worker/src/session_reviewer.py` с LangChain structured output для summary/sentiment/intents; тест `services/worker/tests/test_session_reviewer.py`. Ruff: ok. Pytest: ok. Commit: 442a095. | 7.2, 6.2 | [x] |
| 7.4 | Analytics Aggregator | Сбор данных для графиков. | Добавлен `services/worker/src/analytics.py` с агрегацией метрик и chart-ready breakdowns по чатам, latency, выручке и review; тест `services/worker/tests/test_analytics.py`. Ruff: ok. Pytest: ok. Commit: bfb09ff. | 7.3 | [x] |

## 8. Качество и Тестирование
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 8.1 | Unit: CRUD Base | Тесты базовых методов БД. | Расширен `services/api/tests/test_crud_base.py`: добавлены unit-тесты на `None`-ветки для `get`, `update`, `delete`; покрыты базовые CRUD-операции и schema CRUD. Ruff: ok. Pytest: ok. Commit: bebb0f1. | 2.4 | [x] |
| 8.2 | Integration: Search | Тесты на точность поиска. | Расширен `services/api/tests/test_search_service.py`: добавлен интеграционный сценарий `search + filters + tenancy` с `or`-логикой, пагинацией и проверкой возврата результатов. Ruff: ok. Pytest: ok. Commit: c209bf4. | 4.3 | [x] |
| 8.3 | Mock: LLM API | Заглушки для OpenRouter. | Добавлен `services/api/tests/fakes.py` с переиспользуемым fake LLM для `ainvoke`, tool binding и structured output; обновлен `services/api/tests/test_ai_service.py`. Ruff: ok. Pytest: ok. Commit: b64689d. | 6.2 | [x] |
| 8.4 | E2E: Bot Conversation | Полный цикл общения. | Расширен `services/api/tests/test_conversation_service.py`: добавлен e2e-сценарий полного диалога с tool-call, сохранением `Message`, повторным ходом в том же `conversation_id` и проверкой памяти диалога. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 6.4 | [x] |

## 9. Deployment (Docker Compose)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 9.1 | UV Docker Layering | Оптимизация Dockerfile. | Добавлены `Dockerfile` и `.dockerignore`: двухстадийная сборка через `uv`, кэшируемая установка зависимостей по `pyproject.toml`/`uv.lock`, venv вынесен в `/opt/venv` для совместимости с bind mount. Проверки: `docker compose config`, `uv run pytest`. Commit: 9d129b9. | 1.2 | [x] |
| 9.2 | Network Isolation | Настройка сетей Docker. | Обновлен `docker-compose.yml`: сервисы разведены по сетям `edge`, `db_net`, `redis_net`, внутренние сети БД и Redis отмечены как `internal`. Проверки: `docker compose config`, `uv run pytest`. Commit: a3ad488. | - | [x] |
| 9.3 | Healthchecks | Проверки готовности сервисов. | Обновлен `docker-compose.yml`: добавлены healthchecks для `redis`, `api`, `dashboard`; `api` теперь зависит от `redis` по `service_healthy`. Проверки: `docker compose config`, `uv run pytest`. Commit: current HEAD at completion. | - | [x] |

## 10. Runtime Stabilization
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10.1 | API App Bootstrap | Создать реальный `FastAPI` app в `services/api/src/main.py`: lifespan, `/health`, базовый router registry. | Добавлен `FastAPI` bootstrap в `services/api/src/main.py`: `create_app`, lifespan, `/health`, базовый router registry, инициализация logging и `app.state.settings`; добавлен тест `services/api/tests/test_main.py`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 2.1, 2.2 | [x] |
| 10.2 | API Config Alignment | Привести env-названия и settings к единому runtime-контракту (`DATABASE_URL`, `REDIS_URL`, `LLM_*`, webhook settings). | Обновлены `services/api/src/core/config.py`, `services/worker/src/core/config.py`, `services/bot/src/core/config.py`, `services/api/src/services/ai.py`, `.env.example`, `docker-compose.yml`: введены generic `LLM_API_KEY` / `LLM_BASE_URL`, сохранена совместимость с legacy `OPENROUTER_*`, `DATABASE_URL`/`REDIS_URL` получили приоритет над split vars; добавлены тесты `services/api/tests/test_api_config.py`, `services/worker/tests/test_worker_config.py`, `services/bot/tests/test_bot_config.py`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.1 | [x] |
| 10.3 | API Routers: Health & Search | Добавить реальные FastAPI routers: `/health`, `/catalog/search`, валидацию входа и DI для async session. | Добавлены `services/api/src/core/dependencies.py`, `services/api/src/api/routers/system.py`, `services/api/src/api/routers/catalog.py`, `services/api/src/api/routers/__init__.py`, `services/api/src/schemas/catalog.py`; `services/api/src/main.py` переведен на router registry. Добавлен тест `services/api/tests/test_api_routes.py` на `/health`, `/catalog/search`, dependency override и `422`-валидацию. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.1, 10.2, 4.3 | [x] |
| 10.4 | API Router: Conversation | Добавить endpoint для диалога (`/conversations/{id}/messages`) поверх `run_conversation_turn`. | Добавлены `services/api/src/api/routers/conversations.py` и `services/api/src/schemas/conversation.py`; router подключен в `services/api/src/api/routers/__init__.py`. Расширен `services/api/tests/test_api_routes.py`: проверены обычный ответ, tool-call response и `422` на пустой `content`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.3, 6.4 | [x] |
| 10.5 | Worker Entrypoint | Создать `services/worker/src/main.py` с async loop: watchdog polling, inactivity close, session review pipeline. | Добавлен `services/worker/src/main.py` с `WorkerRuntime`, `build_worker_runtime`, `run_once`, `run_forever`, обработкой watchdog/inactivity и review hook; в `services/worker/src/core/config.py` добавлены интервалы worker loop. Добавлен тест `services/worker/tests/test_worker_main.py` на runtime сборку, single iteration и polling loop. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 7.1, 7.2, 7.3, 7.4 | [x] |
| 10.6 | Bot Runtime Bootstrap | Добавить entrypoint для bot-сервиса: загрузка tenant bot configs, регистрация webhook/multi-bot startup. | Добавлен `services/bot/src/main.py` с `TenantBotConfig`, загрузкой tenant bot configs из API БД, сборкой webhook registration batch и runtime entrypoint `main()`; `services/bot/src/core/config.py` расширен DB runtime-настройками для чтения tenant configs; добавлены тесты `services/bot/tests/test_bot_runtime.py` и обновлен `services/bot/tests/test_bot_config.py`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 6.1, 10.2 | [x] |
| 10.7 | Webhook Intake API | Добавить webhook endpoint в API для Telegram update intake и проксирования в bot logic. | Добавлены `services/api/src/api/routers/webhooks.py` и `services/api/src/services/telegram_webhook.py`: API принимает `POST /webhooks/{tenant_id}`, проверяет `X-Telegram-Bot-Api-Secret-Token`, извлекает текстовый Telegram update, находит tenant/chat, запускает `run_conversation_turn` с `DEFAULT_LLM_MODEL=qwen/qwen3-coder:free` и отправляет ответ через Telegram Bot API. Обновлен `services/api/src/core/config.py`, router registry и тесты `services/api/tests/test_api_routes.py`, добавлен `services/api/tests/test_telegram_webhook_service.py`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.4, 10.6 | [x] |
| 10.8 | Admin Runtime Wiring | Привести Streamlit dashboard к реальному запуску из `services/admin/src/main.py` и runtime env. | Добавлен `services/admin/src/core/config.py` с runtime settings (`DATABASE_URL`, `REDIS_URL`, `MODE`); `services/admin/src/main.py` получил `bootstrap_runtime()` с `st.set_page_config(...)` и сохранением settings в `st.session_state`; добавлен тест `services/admin/tests/test_admin_runtime.py`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.2 | [x] |
| 10.9 | Compose Runtime Fix | Обновить `docker-compose.yml` под реальные entrypoints и команды запуска для `api`, `worker`, `bot`, `admin`. | Обновлен `docker-compose.yml`: реальные entrypoints для `api`, `worker`, `bot`, `admin`, добавлены сервисы `worker` и `bot`, выровнены env и `depends_on`; `services/bot/src/main.py` и `services/worker/src/main.py` больше не импортируют код из `api`, вместо этого добавлены локальные `core/database.py` и идентичные runtime-модели `services/bot/src/models/tenant.py`, `services/worker/src/models/chat.py`, плюс обновлены тесты runtime/wiring. Ruff: ok. Pytest: ok. `docker compose config`: ok. Commit: current HEAD at completion. | 10.5, 10.6, 10.7, 10.8 | [x] |
| 10.10 | DB Migration Bootstrap | Создать первую рабочую Alembic migration и команду применения в runtime startup docs. | Добавлена первая рабочая migration `alembic/versions/20260324_0001_initial_schema.py` с таблицами `tenants`, `products`, `chats`, `messages`, `orders` и индексами; расширен `services/api/tests/test_alembic_setup.py`, чтобы проверять наличие initial revision. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 3.6, 10.9 | [x] |
| 10.11 | Runtime Smoke Tests | Добавить smoke/integration тесты на запуск FastAPI app, worker loop bootstrap и compose config. | Добавлены smoke-тесты `services/api/tests/test_runtime_smoke.py`, `services/bot/tests/test_bot_runtime_smoke.py`, `services/worker/tests/test_worker_runtime_smoke.py`: проверяются `docker compose config`, entrypoint `bot.main()` и entrypoint `worker.main()`. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.3, 10.5, 10.9 | [x] |
| 10.12 | Launch Docs | Обновить `README.md` командами запуска, переменными окружения и минимальным сценарием локальной проверки. | Обновлен `README.md`: описаны сервисы, env, `docker compose up --build`, `alembic upgrade head`, локальный запуск `api/worker/bot/admin` и минимальный smoke-check сценарий. Ruff: ok. Pytest: ok. Commit: current HEAD at completion. | 10.9, 10.10, 10.11 | [x] |

## 11. Admin Productive UX
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 11.1 | Admin: Tenant Management | Добавить в админ-панель создание tenant с `tenant_id`, `bot_token`, `system_prompt` без ручного SQL. | Добавлены `services/admin/src/core/database.py` и `services/admin/src/tenant_management.py` для async CRUD tenant-ов из Streamlit; `services/admin/src/main.py` расширен секцией создания/listing tenant-ов с автогенерацией UUID и masked token view; добавлен тест `services/admin/tests/test_tenant_management.py`. Ruff: ok. Pytest: ok. Commit: current HEAD. | 10.8, 10.10 | [x] |
| 11.2 | Admin: DB Loop Stability | Исправить работу admin DB-запросов в Streamlit без конфликтов event loop. | `services/admin/src/main.py` переведен с `asyncio.run(...)` на выделенный event loop (`get_admin_event_loop`, `run_async`), чтобы Streamlit и asyncpg не переиспользовали разные loops; добавлен тест `services/admin/tests/test_admin_runtime.py` на стабильный `run_async`. Ruff: ok. Pytest: ok. Commit: 4d589c5. | 11.1 | [x] |
| 11.3 | Admin: Core Package Import | Исправить импорт `core.database` в Streamlit runtime. | Добавлен `services/admin/src/core/__init__.py`, чтобы `core.database` корректно импортировался в Streamlit runtime. Pytest admin: ok. Commit: fd87293. | 11.1 | [x] |
| 11.4 | Admin: Catalog Seed Import | Добавить импорт демо-каталога из `data/services.json` для выбранного tenant в таблицу `products`. | Добавлены `services/admin/src/catalog_seed.py` и UI-кнопка в `services/admin/src/main.py` для импорта `data/services.json` в `products` текущего tenant-а с заменой существующих записей; admin DB wiring вынесен в `services/admin/src/admin_database.py`, убраны конфликтующие `core`-импорты; добавлен тест `services/admin/tests/test_catalog_seed.py`. Ruff: ok. Pytest: ok. Commit: current HEAD. | 11.1, 10.10 | [x] |
| 11.5 | Admin: Catalog Browser | Показать в админке реальные записи каталога tenant-а из БД с фильтрацией и базовыми полями (`name`, `category`, `measure`, `price`). | Добавлены `services/admin/src/catalog_browser.py` и секция просмотра каталога в `services/admin/src/main.py`: чтение `products` tenant-а из БД, фильтры по категории и названию, лимит выдачи; добавлен тест `services/admin/tests/test_catalog_browser.py`. Ruff: ok. Pytest: ok. Commit: 3b50843. | 11.4 | [x] |
| 11.6 | Admin: Catalog CRUD | Добавить ручное создание, редактирование и удаление записей каталога tenant-а без CSV/Excel. | Добавлен `services/admin/src/catalog_crud.py` с async create/update/delete для `products` c tenant isolation; `services/admin/src/main.py` расширен формой CRUD поверх выбранной записи каталога; `services/admin/src/catalog_browser.py` теперь возвращает `id` для выбора записи; добавлен тест `services/admin/tests/test_catalog_crud.py`, обновлен `services/admin/tests/test_catalog_browser.py`. Ruff: ok. Pytest: ok. Commit: 3b9f9b8. | 11.5 | [x] |
| 11.7 | Admin: Sync DB Layer | Перевести admin c asyncpg на sync DB layer, совместимый со Streamlit runtime, и убрать loop-related ошибки из логов. | `services/admin/src/admin_database.py` переведен на sync SQLAlchemy engine/session (`psycopg`), admin service modules (`tenant_management`, `catalog_seed`, `catalog_browser`, `catalog_crud`, `main`) переведены на sync DB calls; убраны `asyncio` loop helpers, `st.dataframe(..., width=\"stretch\")` заменил deprecated `use_container_width`; добавлена зависимость `psycopg[binary]`. Ruff: ok. Pytest: ok (114 passed). `docker compose up -d --build admin`: ok, loop-related ошибок в логах больше нет. | 11.6 | [x] |
| 11.8 | Admin: Catalog Filter SQL Fix | Исправить ошибку PostgreSQL `AmbiguousParameter` при пустых фильтрах каталога. | `services/admin/src/catalog_browser.py` переведен на динамическую сборку `WHERE` без nullable SQL-параметров `:category is null` / `:query is null`; добавлен тест `services/admin/tests/test_catalog_browser.py`, проверяющий отсутствие null-параметров в SQL. Ruff: ok. Pytest: ok (115 passed). Commit: 693301a. | 11.7 | [x] |
| 11.9 | Bot: Aiogram Init Fix | Исправить создание `aiogram.Bot` под v3.7+ для успешной регистрации webhook. | `services/bot/src/core/bot.py` переведен на `DefaultBotProperties(parse_mode=\"HTML\")` вместо deprecated `parse_mode` в конструкторе `Bot`; добавлен тест в `services/bot/tests/test_webhooks.py`. Ruff: ok. Pytest: ok (116 passed). `docker compose up -d --build bot`: ok, `docker compose logs bot` показывает `bot runtime bootstrapped`. | 10.6 | [x] |
