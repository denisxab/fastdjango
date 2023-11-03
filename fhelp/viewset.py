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


def view_list(db, model, filters: Optional[dict[str, Any]] = None):
    """Получить список записей, с возможностью фильтрации"""

    rows = db.query(model)

    if filters:
        filters = {k: v for k, v in filters.items() if v}
        rows = rows.filter_by(**filters)
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
        # Класс модели
        getattr(self, "model")
        # Путь по которому подключить
        getattr(self, "url")
        # Схема ответа для GET, POST
        getattr(self, "response_model")
        # Схема для POST и PUT
        getattr(self, "schema_body")

        self.add_api_routes()

    def add_api_routes(self):
        # Динамически указываем тип для Body
        tmp_create_model = lambda data: self.create_model(data)  # noqa E731
        tmp_create_model.__annotations__ = deepcopy(self.create_model.__annotations__)
        tmp_create_model.__annotations__["data"] = self.schema_body
        tmp_update_model = lambda pk, data: self.update_model(pk, data)  # noqa E731
        tmp_update_model.__annotations__ = deepcopy(self.update_model.__annotations__)
        tmp_update_model.__annotations__["data"] = self.schema_body

        # Добавляем фильтры
        self.filters = getattr(self, "filters", None)

        # Настройка маршрутизатора
        self.get(f"/{self.url}/", response_model=list[self.response_model])(
            self.list_model
        )
        self.get(f"/{self.url}" + "/{pk}", response_model=self.response_model)(
            self.retrieve_model
        )
        self.post(
            f"/{self.url}/",
            response_model=self.response_model,
        )(tmp_create_model)
        self.delete(f"/{self.url}" + "/{pk}")(self.delete_model)
        self.put(f"/{self.url}" + "/{pk}")(tmp_update_model)

    def list_model(self, request: Request, db: Session = Depends(get_db)):
        filters = None
        if self.filters:
            query_params = request.query_params._dict
            filters = {f: query_params.get(f) for f in self.filters}

        return view_list(db, self.model, filters)

    def retrieve_model(self, pk: int, db: Session = Depends(get_db)):
        return view_retrieve(db, self.model, pk)

    def create_model(self, data: BaseModel, db: Depends = Depends(get_db)):
        db_connect = db.dependency().__next__()
        return view_create(db_connect, self.model, data)

    def delete_model(self, pk: int, db: Session = Depends(get_db)):
        return view_delete(db, self.model, pk)

    def update_model(self, pk: int, data: BaseModel, db: Depends = Depends(get_db)):
        db_connect = db.dependency().__next__()
        return view_update(db_connect, self.model, pk, data)
