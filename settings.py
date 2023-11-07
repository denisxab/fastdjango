DATABASE_CONF = "username:password@db/dbname"
DATABASE_URL = f"postgresql://{DATABASE_CONF}"
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DATABASE_CONF}"
REDIS_URL = "redis://redis/0"
APP_PORT = 8000
DEBUG = False
SECRET_KEY = "f58f7156911ebf46b9d9ad35b43e60388dc8f639b356f59eac3aa8df45290d47"
