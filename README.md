# Использование

Запустить проект:

`uvicorn main:app --reload --host 0.0.0.0 --port 8000` или `invoke rundev`

# Миграции

## Alembic

### CLI команды

Инициализация Alembic: `alembic init alembic`

Создать миграцию: `alembic revision --autogenerate`

-   `-m "ИмяМиграции"`

Применить все миграции к БД: `alembic upgrade head`

Откатить миграцию на один шаг назад: `alembic downgrade -1`
