"""
Утилиты для работы с БД
"""
from typing import Any, Callable

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

# Инициализация подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция зависимости для получения сессии базы данных
def get_db():
    """
    @router_persons.get("/users/")
    def read_user_all(db: Session = Depends(get_db)):
        users = get_all_users(db)
        return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def connect_db(fun: Callable) -> Any:
    with connect(dsn=DATABASE_URL) as conn, conn.cursor() as cur:
        return fun(cur)


def dictfetchall(cursor) -> list[dict[str, Any]]:
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def sql_read(sql_query: str):
    def _iner(cur):
        cur.execute(sql_query)
        return dictfetchall(cur)

    return connect_db(_iner)


def sql_write(sql_query: str):
    def _iner(cur):
        cur.execute(sql_query)
        cur.connection.commit()
        return cur.rowcount

    return connect_db(_iner)
