"""
Утилиты для синхронной работы с БД
"""
from typing import Any, Callable

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fhelp.utlis import dictfetchall
from settings import SettingsFastApi

settings = SettingsFastApi()

# Инициализация подключения к базе данных
engine = create_engine(settings.DATABASE_URL, echo=True if settings.DEBUG else False)
# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция зависимости для получения сессии базы данных
def get_session() -> Session:
    """
    from fastapi import Depends
    from sqlalchemy.orm import Session
    from .models import User


    @router_persons.get("/users/")
    def read_user_all(session: Session = Depends(get_session)):
        return db.query(model).all()
    """
    with SessionLocal() as session:
        yield session


def connect_db(fun: Callable, dsn=None) -> Any:
    with connect(
        dsn=dsn if dsn else settings.DATABASE_URL
    ) as conn, conn.cursor() as cur:
        return fun(cur)


def sql_read(sql_query: str, dsn=None):
    """Выполнить RAW SQL чтение"""

    def _inner(cur):
        cur.execute(sql_query)
        return dictfetchall(cur)

    return connect_db(_inner, dsn)


def sql_write(sql_query: str, dsn=None):
    """Выполнить RAW SQL запись"""

    def _inner(cur):
        cur.execute(sql_query)
        cur.connection.commit()
        return cur.rowcount

    return connect_db(_inner, dsn)
