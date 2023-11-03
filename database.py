from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

# Инициализация подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
