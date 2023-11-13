"""Настройки"""

from pathlib import Path
from pprint import pprint

from pydantic_settings import BaseSettings


class SettingsFastApi(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent

    DATABASE_CONF: str = "username:password@db"
    DATABASE_NAME: str = "dbname"

    DATABASE_URL: str = f"postgresql://{DATABASE_CONF}/{DATABASE_NAME}"
    DATABASE_URL_ASYNC: str = f"postgresql+asyncpg://{DATABASE_CONF}/{DATABASE_NAME}"

    REDIS_URL: str = "redis://redis/0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    SECRET_KEY: str = "f58f7156911ebf46b9d9ad35b43e60388dc8f639b356f59eac3aa8df45290d47"


settings = SettingsFastApi()
print("SettingApp")
pprint(settings.__dict__)
