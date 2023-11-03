"""
Автоматизация для построение Views
"""
from copy import deepcopy
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fhelp.database import get_db


def view_retrieve(db, model, pk):
    """Получить запись по PK"""
    name_pk = model.__table__.primary_key.columns.values()[0].name
    row = db.query(model).filter_by(**{name_pk: pk}).first()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row


def view_list(
    db,
    model,
    filters: Optional[dict[str, Any]] = None,
    limit: int = None,
    offset: int = None,
    order_by: tuple[str] = None,
):
    """Получить список записей, с возможностью фильтрации, limit и offset"""

    rows = db.query(model)

    if filters:
        filters = {k: v for k, v in filters.items() if v}
        rows = rows.filter_by(**filters)

    if order_by:
        rows = rows.order_by(*order_by)

    if limit is not None:
        rows = rows.limit(limit)

    if offset is not None:
        rows = rows.offset(offset)

    return rows.all()


def view_create(db, model, data: BaseModel):
    """Создать запись"""
    new_row = model(**data.dict())
    db.add(new_row)
    db.commit()
    db.refresh(new_row)
    return new_row


def view_delete(db, model, pk):
    """Удалить запись по PK"""
    row = view_retrieve(db, model, pk)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(row)
    db.commit()
    return {"message": "User deleted successfully"}


def view_update(db, model, pk, data: BaseModel):
    """Обновить запись по PK"""

    row = view_retrieve(db, model, pk)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.dict().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


class FBaseRouter:
    def __init__(self):
        super().__init__()
        # R Класс модели
        getattr(self, "model")
        # R Путь по которому подключить
        getattr(self, "url")
        # R Схема ответа для GET, POST
        getattr(self, "response_model")
        # R Схема для POST и PUT
        getattr(self, "schema_body")
        # O Доступные фильтры по полям
        getattr(self, "filter_column", None)
        # O Нужно ли пагинация для List
        getattr(self, "size_page", None)
        # O Сортировка для списка
        getattr(self, "order_by", None)

        self.add_api_routes()

    def add_api_routes(self):
        # Динамически указываем тип для Body
        tmp_create_view = lambda data: self.create_view(data)  # noqa E731
        tmp_create_view.__annotations__ = deepcopy(self.create_view.__annotations__)
        tmp_create_view.__annotations__["data"] = self.schema_body
        tmp_update_view = lambda pk, data: self.update_view(pk, data)  # noqa E731
        tmp_update_view.__annotations__ = deepcopy(self.update_view.__annotations__)
        tmp_update_view.__annotations__["data"] = self.schema_body

        self.filter_column = getattr(self, "filter_column", None)
        self.size_page = getattr(self, "size_page", None)
        self.order_by = getattr(self, "order_by", None)

        if self.size_page and not self.order_by:
            raise ValueError(
                "При использование 'size_page' обязательно используйте 'order_by'"
            )

        # Настройка маршрутизатора
        if self.size_page and self.order_by:
            self.get(f"/{self.url}/")(self.list_view)
        else:
            self.get(f"/{self.url}/", response_model=list[self.response_model])(
                self.list_view
            )
        self.get(f"/{self.url}" + "/{pk}", response_model=self.response_model)(
            self.retrieve_view
        )
        self.post(
            f"/{self.url}/",
            response_model=self.response_model,
        )(tmp_create_view)
        self.delete(f"/{self.url}" + "/{pk}")(self.delete_view)
        self.put(f"/{self.url}" + "/{pk}")(tmp_update_view)

    def list_view(self, request: Request, db: Session = Depends(get_db)):
        filters = None
        query_params = request.query_params._dict
        if self.filter_column:
            filters = {f: query_params.get(f) for f in self.filter_column}
        if self.size_page:
            page = int(query_params.get("page", 0))

            offset = page * self.size_page
            count = db.query(self.model).count()

            u = request.url
            url = f"{u.scheme}://{u.netloc}{u.path}"

            next_page = page + 1 if count > (page + 1) * self.size_page else False
            previous_page = page - 1 if page - 1 > 0 else False

            return {
                "count": count,
                "next": f"{url}?page={next_page}" if next_page else None,
                "previous": f"{url}?page={previous_page}" if previous_page else None,
                "results": view_list(
                    db,
                    self.model,
                    filters,
                    limit=self.size_page,
                    offset=offset,
                    order_by=self.order_by,
                ),
            }
        return view_list(db, self.model, filters, order_by=self.order_by)

    def retrieve_view(self, pk: int, db: Session = Depends(get_db)):
        return view_retrieve(db, self.model, pk)

    def create_view(self, data: BaseModel, db: Depends = Depends(get_db)):
        db_connect = db.dependency().__next__()
        return view_create(db_connect, self.model, data)

    def delete_view(self, pk: int, db: Session = Depends(get_db)):
        return view_delete(db, self.model, pk)

    def update_view(self, pk: int, data: BaseModel, db: Depends = Depends(get_db)):
        db_connect = db.dependency().__next__()
        return view_update(db_connect, self.model, pk, data)
