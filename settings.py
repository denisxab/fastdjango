from pathlib import Path

BASE_DIR = Path(__file__).parent

DATABASE_CONF = "username:password@db"
DATABASE_NAME = "dbname"

DATABASE_URL = f"postgresql://{DATABASE_CONF}/{DATABASE_NAME}"
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DATABASE_CONF}/{DATABASE_NAME}"

TEST_DATABASE_NAME = "test_db"
TEST_DATABASE_URL = f"postgresql://{DATABASE_CONF}/{TEST_DATABASE_NAME}"
TEST_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DATABASE_CONF}/{TEST_DATABASE_NAME}"

REDIS_URL = "redis://redis/0"
APP_PORT = 8000
DEBUG = True

SECRET_KEY = "f58f7156911ebf46b9d9ad35b43e60388dc8f639b356f59eac3aa8df45290d47"
