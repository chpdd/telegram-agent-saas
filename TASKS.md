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
| 3.2 | `models/product.py` | Базовые поля + JSONB attributes + FTS. | | 3.1 | [ ] |
| 3.3 | `models/chat.py` | session_id, status (enum), user_id. | | 3.1 | [ ] |
| 3.4 | `models/message.py` | role, content, latency_ms. | | 3.3 | [ ] |
| 3.5 | `models/order.py` | items (JSONB), total_price. | | 3.3 | [ ] |
| 3.6 | Alembic Multi-Env | Настройка миграций. | | 3.2 | [ ] |

## 4. Динамический Поиск и Каталог
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | **Dynamic Filter Generator** | Трансформация фильтров в SQL к JSONB. | | 3.2 | [ ] |
| 4.2 | PostgreSQL FTS Setup | Миграция для `tsvector` и триггера. | | 3.6 | [ ] |
| 4.3 | Search Service | Метод `search` (FTS + JSONB). | | 4.1, 4.2 | [ ] |

## 5. Dashboard (Streamlit Management)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | UI: Auth Mock | Вход по "ID магазина". | | 3.1 | [ ] |
| 5.2 | UI: Schema Designer | CRUD для `catalog_schemas`. | | 3.2 | [ ] |
| 5.3 | UI: Catalog Upload | Загрузка CSV/Excel. | | 4.2 | [ ] |
| 5.4 | UI: Live Chat Monitor | Список активных чатов. | | 3.3 | [ ] |

## 6. Telegram & AI Integration
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 | Webhook Multi-Bot | Регистрация вебхуков. | | 3.1 | [ ] |
| 6.2 | AI Service Interface | Обертка над OpenRouter. | | 2.1 | [ ] |
| 6.3 | Tool: `catalog_tool` | Инструментарий для LLM. | | 4.3, 6.2 | [ ] |
| 6.4 | AI Conversation Loop | Цикл: История -> LLM -> Ответ. | | 6.3, 3.5 | [ ] |

## 7. Background Workers (The Analyzer)
| ID | Task | Description | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 7.1 | **30s Watchdog (Redis)** | Мониторинг таймаутов в Redis. | | 6.4 | [ ] |
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
