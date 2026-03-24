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
| 7.1 | **30s Watchdog (Redis)** | Мониторинг таймаутов в Redis. | Добавлены `services/worker/src/core/config.py`, `services/worker/src/watchdog.py`, тест `services/worker/tests/test_watchdog.py`. Ruff: ok. Pytest: ok. Commit: TBD. | 6.4 | [x] |
| 7.2 | Inactivity Task | Проверка сессий > 2 часов. | | 3.3 | [ ] |
| 7.3 | **LLM Session Reviewer** | Аналитика: Summary, Sentiment. | | 7.2, 6.2 | [ ] |
| 7.4 | Analytics Aggregator | Сбор данных для графиков. | | 7.3 | [ ] |

## 8. Качество и Тестирование
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 8.1 | Unit: CRUD Base | Тесты базовых методов БД. | | 2.4 | [ ] |
| 8.2 | Integration: Search | Тесты на точность поиска. | | 4.3 | [ ] |
| 8.3 | Mock: LLM API | Заглушки для OpenRouter. | | 6.2 | [ ] |
| 8.4 | E2E: Bot Conversation | Полный цикл общения. | | 6.4 | [ ] |

## 9. Deployment (Docker Compose)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 9.1 | UV Docker Layering | Оптимизация Dockerfile. | | 1.2 | [ ] |
| 9.2 | Network Isolation | Настройка сетей Docker. | | - | [ ] |
| 9.3 | Healthchecks | Проверки готовности сервисов. | | - | [ ] |
