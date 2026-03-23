# ТРЕКЕР ЗАДАЧ ПРОЕКТА: SaaS Telegram AI Platform (Ultra Detailed)

## Легенда
- **ID:** Номер задачи
- **Task:** Краткое название
- **Context:** Детали реализации
- **Deps:** От каких задач зависит (ID)
- **Status:** [ ] - Todo, [/] - In Progress, [x] - Done

---

## 1. Окружение и Инфраструктура
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1.1 | Инициализация TASKS.md | Создание подробного трекера задач. | - | [x] |
| 1.2 | `uv` Workspace Setup | `uv init` выполнен, зависимости (fastapi, aiogram, etc) добавлены. Commit: a18ce42. | - | [x] |
| 1.3 | Ruff & Pre-commit | Ruff настроен в pyproject.toml. Исправлены первые ошибки. Commit: c40f645. | 1.2 | [x] |
| 1.4 | Pytest Async Config | Настройка `conftest.py` и `pytest.ini` для асинхронных тестов. | 1.2 | [/] |

| 1.5 | Makefile Automation | Команды: `up`, `down`, `test`, `lint`, `migrate`, `logs`. | 1.2 | [ ] |
| 1.6 | `.env.example` | Создание шаблона переменных окружения со всеми секциями. | - | [ ] |

## 2. Базовая Архитектура (Core Service Layer)
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2.1 | `core/config.py` | Pydantic Settings с валидацией URL и API ключей. | 1.2 | [/] |
| 2.2 | `core/database.py` | SQLAlchemy engine + `session_factory` + Base class с `__repr__`. | 1.2 | [ ] |
| 2.3 | **Tenant Isolation Utility** | Механизм перехвата запросов (Query Interceptor) для принудительного `tenant_id`. | 2.2 | [ ] |
| 2.4 | `crud/base.py` | `BaseCRUD` с методами `get_or_404`, `exists`, `list_by_tenant`. | 2.2 | [ ] |
| 2.5 | `core/logging.py` | JSON-логирование с `correlation_id` для отслеживания пути сообщения. | 1.2 | [ ] |

## 3. Модели и Миграции (Database Schema)
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 3.1 | `models/tenant.py` | UUID PK, name, bot_token, system_prompt, schema (JSONB). | 2.2 | [ ] |
| 3.2 | `models/product.py` | name, desc, price, stock + `attributes` (JSONB) + FTS GIN Index. | 3.1 | [ ] |
| 3.3 | `models/chat.py` | session_id, status (enum), user_id, start_at, end_at. | 3.1 | [ ] |
| 3.4 | `models/message.py` | role, content, latency_ms, tool_calls (JSONB). | 3.3 | [ ] |
| 3.5 | `models/order.py` | items (JSONB), total_price, customer_info (JSONB). | 3.3 | [ ] |
| 3.6 | Alembic Multi-Env | Настройка миграций для работы в Docker и локально. | 3.2 | [ ] |

## 4. Динамический Поиск и Каталог
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 4.1 | **Dynamic Filter Generator** | Логика трансформации Pydantic-фильтров в SQL-запросы к JSONB. | 3.2 | [ ] |
| 4.2 | PostgreSQL FTS Setup | Миграция для создания `tsvector` колонки и триггера обновления. | 3.6 | [ ] |
| 4.3 | Search Service | Метод `search(tenant_id, text, **filters)` — объединение FTS и JSONB. | 4.1, 4.2 | [ ] |

## 5. Dashboard (Streamlit Management)
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 4.1 | UI: Auth Mock | Вход по "ID магазина" (пока без пароля). | 3.1 | [ ] |
| 4.2 | UI: Schema Designer | Интерфейс CRUD для `catalog_schemas` (добавление колонок). | 3.2 | [ ] |
| 4.3 | UI: Catalog Upload | Загрузка CSV/Excel с маппингом колонок на динамическую схему. | 4.2 | [ ] |
| 4.4 | UI: Live Chat Monitor | Список активных чатов и кнопка "Перехватить". | 3.3 | [ ] |

## 6. Telegram & AI Integration
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 6.1 | Webhook Multi-Bot | Логика динамической регистрации вебхуков при старте приложения. | 3.1 | [ ] |
| 6.2 | AI Service Interface | Обертка над OpenRouter с обработкой ошибок и ретраями. | 2.1 | [ ] |
| 6.3 | Tool: `catalog_tool` | Интеграция Поискового сервиса с LangChain Function Calling. | 4.3, 6.2 | [ ] |
| 6.4 | AI Conversation Loop | Обработка сообщения: История -> LLM -> Tool -> Ответ -> Лог. | 6.3, 3.5 | [ ] |

## 7. Background Workers (The Analyzer)
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 7.1 | **30s Watchdog (Redis)** | TTL-ключи в Redis для мониторинга подвисших ответов. | 6.4 | [ ] |
| 7.2 | Inactivity Task | Периодическая проверка (APScheduler) на сессии старше 2 часов. | 3.3 | [ ] |
| 7.3 | **LLM Session Reviewer** | Генерация аналитики: Summary, Sentiment, Loss Reason. | 7.2, 6.2 | [ ] |
| 7.4 | Analytics Aggregator | Сбор данных для графиков (Plotly) в Dashboard. | 7.3 | [ ] |

## 8. Качество и Тестирование
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 8.1 | Unit: CRUD Base | Тестирование общих методов базы данных. | 2.4 | [ ] |
| 8.2 | Integration: Search | Тесты на точность FTS и фильтрации JSONB. | 4.3 | [ ] |
| 8.3 | Mock: LLM API | Написание заглушек для имитации ответов OpenRouter. | 6.2 | [ ] |
| 8.4 | E2E: Bot Conversation | Симуляция полного цикла: Юзер -> Бот -> База -> Юзер. | 6.4 | [ ] |

## 9. Deployment (Docker Compose)
| ID | Task | Context | Deps | Status |
| :--- | :--- | :--- | :--- | :--- |
| 9.1 | UV Docker Layering | Оптимизация Dockerfile для кэширования зависимостей uv. | 1.2 | [ ] |
| 9.2 | Network Isolation | Настройка внутренних сетей Docker (frontend, backend, db). | - | [ ] |
| 9.3 | Healthchecks | Настройка проверок готовности для DB и Redis перед стартом API. | - | [ ] |
