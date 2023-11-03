# Использование

## Запустить проект

Запустить DEV сервер:

```bash
invoke rundev
```

Запустить сервер:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Работа с фикстурами

Прочитать записи из таблицы БД

```bash
invoke dumpdata ИмяТаблицы > ИмяТаблицы.json
```

Прочитать из файла и записать в БД

```bash
invoke loaddata ИмяТаблицы.json
```

Удалить все записи из таблицы БД

```bash
invoke flushtable users
```

## Проверки

Запустить проверки:

1. Проверить подключение к БД

```bash
invoke check
```

# Миграции

## Alembic

### CLI команды

Инициализация Alembic: `alembic init alembic`

Создать миграцию: `alembic revision --autogenerate`

-   `-m "ИмяМиграции"`

Применить все миграции к БД: `alembic upgrade head`

Откатить миграцию на один шаг назад: `alembic downgrade -1`
