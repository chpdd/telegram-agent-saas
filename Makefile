# Переменные
DC = docker-compose
APP_CONTAINER = tca_api
DASHBOARD_CONTAINER = tca_dashboard

.PHONY: help build up down restart logs test lint migrate-gen migrate-upgrade

help:
	@echo "Использование: make <команда>"
	@echo "Команды:"
	@echo "  build            Собрать Docker-образы"
	@echo "  up               Запустить проект в Docker"
	@echo "  down             Остановить и удалить контейнеры"
	@echo "  restart          Перезагрузить проект"
	@echo "  logs             Просмотр логов API"
	@echo "  test             Запустить тесты (через uv)"
	@echo "  lint             Проверить код линтером Ruff"
	@echo "  migrate-gen      Создать новую миграцию (нужен флаг m='описание')"
	@echo "  migrate-upgrade  Применить миграции"

build:
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

restart:
	$(DC) restart

logs:
	$(DC) logs -f $(APP_CONTAINER)

test:
	uv run pytest

lint:
	uv run ruff check . --fix
	uv run ruff format .

migrate-gen:
	uv run alembic revision --autogenerate -m "$(m)"

migrate-upgrade:
	uv run alembic upgrade head
