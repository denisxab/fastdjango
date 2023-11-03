Инициализация alembic: `alembic init alembic`

Создать миграцию: `alembic revision --autogenerate`

-   `-m "ИмяМиграции"`

Применить все миграции: `alembic upgrade head`

Откатить миграцию на один шаг назад: `alembic downgrade -1`
