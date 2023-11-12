from typing import Any

from fastapi import Request
from sqlalchemy.orm.decl_api import DeclarativeMeta


def dictfetchall(cursor) -> list[dict[str, Any]]:
    """Вернуть dict из ORM SQL ответа"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def absolute_url(request: Request, add_url: str = ""):
    """Получить абсолютный url путь к серверу"""
    url_obj = request.url
    url = f"{url_obj.scheme}://{url_obj.netloc}{add_url}"
    return url


def get_pk_name_mode(model: DeclarativeMeta):
    """Получить имя PK"""
    return model.__table__.primary_key.columns.values()[0].name
