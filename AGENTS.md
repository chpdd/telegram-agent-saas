# AGENTS.md: Developer Protocol for SaaS AI Platform

## 1. Project Context
Multi-tenant SaaS platform for AI Telegram bots, built with a monorepo-style service architecture.

## 2. Mandatory Coding Conventions (from task-planner-app)

### 2.1. Tooling & Dependencies
- **Package Manager:** **uv**. Use `uv add <package>` to manage dependencies.
- **Linting:** **Ruff**. Configuration must be present in `pyproject.toml`.
- **Testing:** **pytest** with `pytest-asyncio`. Tests reside in `services/<service>/tests/`.

### 2.2. Service Architecture (services/<service>/src/)
- **`api/`**: FastAPI routers.
- **`core/`**: `config.py` (BaseSettings), `database.py` (DeclarativeBase), `dependencies.py`.
- **`models/`**: SQLAlchemy 2.0 `Mapped` styles. File-per-model approach.
- **`schemas/`**: Pydantic v2 validation models.
- **`crud/`**: Database access logic, inheriting from `BaseCRUD`.

## 3. Mandatory Constraints
1. **Async-First**: Strictly use `async/await` for DB and external requests.
2. **Tenant Isolation**: Every SQL query must be filtered by `tenant_id`.
3. **No Vector DB**: Use **PostgreSQL Full Text Search** (FTS) for semantics and **JSONB** for flexible catalog attributes.
4. **LLM Watchdog**: A separate background observer must handle the 30s timeout for responses.
5. **Model Strategy**: Use **Gemini 3.1 Pro** for complex architectural tasks, logic-heavy implementations (e.g., Dynamic SQL Query Builder), and session analysis.

## 5. Task Execution Protocol (CRITICAL)
1. **Selection**: Always look at `TASKS.md` and pick the first task with status `[ ]` (Todo) in chronological order.
2. **Status Update (Start)**: Immediately change the status to `[/]` (In Progress) before starting the task.
3. **Execution**: Perform the task strictly according to the context provided.
4. **Context Logging**: Record significant actions, architectural decisions, or file changes in the `Context` column of the task table.
5. **Status Update (End)**: Change the status to `[x]` (Done) once the task is fully verified (tested/linted).
6. **Iteration**: Move to the next `[ ]` task automatically.

