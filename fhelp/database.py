"""
Утилиты для синхронной работы с БД
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL, DEBUG

# Инициализация подключения к базе данных
engine = create_engine(DATABASE_URL, echo=True if DEBUG else False)
# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция зависимости для получения сессии базы данных
def get_session():
    """
    from sqlalchemy.orm import Session
    from .models import User

    @router_persons.get("/users/")
    def read_user_all(session: Session = Depends(get_session)):
        return db.query(model).all()
    """
    with SessionLocal() as session:
        yield session
