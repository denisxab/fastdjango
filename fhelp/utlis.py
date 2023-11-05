from typing import Any, Callable

from psycopg2 import connect
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import DeclarativeMeta

from settings import DATABASE_URL


def dictfetchall(cursor) -> list[dict[str, Any]]:
    """Вернуть dict из ORM SQL ответа"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def connect_db(fun: Callable) -> Any:
    with connect(dsn=DATABASE_URL) as conn, conn.cursor() as cur:
        return fun(cur)


def sql_read(sql_query: str):
    """Выполнить RAW SQL чтение"""

    def _inner(cur):
        cur.execute(sql_query)
        return dictfetchall(cur)

    return connect_db(_inner)


def sql_write(sql_query: str):
    """Выполнить RAW SQL запись"""

    def _inner(cur):
        cur.execute(sql_query)
        cur.connection.commit()
        return cur.rowcount

    return connect_db(_inner)


async def count_rows(session: AsyncSession, model: DeclarativeMeta):
    """Получить количество записей в таблице"""

    result = await session.execute(func.count(model.id))
    count = result.scalar()
    return count
