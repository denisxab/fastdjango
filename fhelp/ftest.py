import os
import subprocess
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from fhelp.database import engine as real_engine
from fhelp.database import get_session
from fhelp.database_async import async_get_session
from fhelp.ffiextures import base_loaddata
from main import app
from settings import SettingsFastApi

settings = SettingsFastApi()

# Замена DSN бд на тестовую
settings.DATABASE_NAME = "test_db"
settings.DATABASE_URL = (
    f"postgresql://{settings.DATABASE_CONF}/{settings.DATABASE_NAME}"
)

settings.DATABASE_URL_ASYNC = (
    f"postgresql+asyncpg://{settings.DATABASE_CONF}/{settings.DATABASE_NAME}"
)

test_engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Инициализация подключения к базе данных
test_async_engine = create_async_engine(settings.DATABASE_URL_ASYNC)
# Создание сессии
TestingAsyncSessionLocal = sessionmaker(
    bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
)


def override_get_session() -> Session:
    """Переопределение для синхронной тестовой сесси с БД"""
    with TestingSessionLocal() as session:
        yield session


async def override_async_get_session() -> AsyncSession:
    """Переопределение для асинхронной тестовой сесси с БД"""

    async with TestingAsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[async_get_session] = override_async_get_session


def migrate_test_db():
    """Выполнить все миграции к тестовой БД"""
    # Опционально: создайте базу данных если она не существует
    with real_engine.connect() as connection:
        create_db_query = text(
            f"""DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '{settings.DATABASE_NAME}') THEN
        CREATE DATABASE {settings.DATABASE_NAME};
    END IF;
END $$;
"""
        )
        connection.execute(create_db_query)
        connection.commit()

    os.environ["DATABASE_URL"] = settings.DATABASE_URL
    result = subprocess.run(
        "invoke db.migrate",
        shell=True,
        env=os.environ,
        stdout=subprocess.PIPE,
        text=True,
    )
    print(result.stdout)


def load_fixtures(paths: list[Path]):
    """Загрузить фикстуры

    paths: Пути к фикстурам
    """

    for p in paths:
        result = base_loaddata(str(p), dsn=settings.DATABASE_URL)
        print(result)


def refresh_db():
    """Удалить и заново создать БД
    Для этого нужно иметь подключение к нетестовой БД
    """
    # Подключитесь к базе данных и выполните операцию DROP DATABASE
    with real_engine.connect() as connection:
        # Отключитесь от базы данных, чтобы не находиться в транзакции
        connection.connection.connection.set_isolation_level(0)

        # Выполните операцию DROP DATABASE
        drop_db_query = text(f"DROP DATABASE IF EXISTS {settings.DATABASE_NAME};")
        connection.execute(drop_db_query)
        connection.commit()

    # Опционально: создайте базу данных заново после удаления (если это нужно)
    with real_engine.connect() as connection:
        create_db_query = text(f"CREATE DATABASE {settings.DATABASE_NAME};")
        connection.execute(create_db_query)
        connection.commit()


def refresh_tables():
    """Удалить все записи во всех таблицах, но оставить DLL структуру"""
    # Замените 'your_database_uri' на URI вашей базы данных
    metadata = MetaData()

    # Связываем метаданные с мотором
    metadata.reflect(bind=test_engine)

    # Получаем список всех таблиц
    all_tables = list(metadata.tables.keys())
    try:
        all_tables.remove("alembic_version")
    except ValueError:
        pass
    for table_name in all_tables:
        with test_engine.connect() as connection:
            drop_db_query = text(
                f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
            )
            connection.execute(drop_db_query)
            connection.commit()


def run_test(reuse_db: bool = False):
    """
    Логика запуска теста FastApi проекта

    reuse_db: Если True то не будет удалять базу пред запуском
    """
    if reuse_db:
        # Удалить БД и создать по новой
        print("refresh_db", refresh_db())

    # Применить миграции через alembic
    print("migrate_test_db", migrate_test_db())


class BaseFastApiTest:
    @pytest.fixture
    def client(self) -> TestClient:
        """Получить клиента из которого делать запрос"""
        client = TestClient(app)
        return client

    @pytest.fixture
    def app(self) -> FastAPI:
        """Получить клиента из которого делать запрос"""
        return app

    def setup_method(self):
        # Код, который нужно выполнить перед каждым тестом
        # Например, подготовка данных или настройка окружения
        if fixtures := getattr(self, "fixtures", None):
            load_fixtures(paths=fixtures)

    def teardown_method(self):
        # Код, который нужно выполнить после каждого теста
        # Например, очистка данных или восстановление окружения
        refresh_tables()
