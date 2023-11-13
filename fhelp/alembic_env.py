"""
Шаблон для alembic/env.py
"""
import os

from sqlalchemy import engine_from_config, pool

from alembic import context

# Эти две строки подключаются к вашей базе данных
from main import app  # noqa F401 # Импортируем FastAPI app
from models import Base  # Предполагаем, что у вас есть модели
from settings import SettingsFastApi

settings = SettingsFastApi()

DATABASE_URL = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

# Инициализация базы данных
target_metadata = Base.metadata

# Alembic Config объект
config = context.config

# Связь с базой данных
config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Подключение к базе данных
def run_migrations_offline():
    """Соединяется с базой данных, которая уже существует. Это полезно при создании файла миграции."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Для создания новой базы данных
def run_migrations_online():
    """Создает новую базу данных и применяет миграции."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Если Alembic запущен через 'stamped'
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
