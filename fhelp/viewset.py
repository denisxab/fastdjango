"""
Автоматизация для построение Views 
"""
from typing import Any, Optional

from fastapi import Depends, HTTPException
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
        getattr(self, "name_path")
        # Схема овтета для GET, POST
        getattr(self, "response_model")
        # Схема для POST и PUT
        getattr(self, "schema_body")

        self.add_api_routes()

    def add_api_routes(self):
        # Настрйока маршутизатора
        self.get(f"/{self.name_path}/", response_model=self.response_model)(
            self.list_model
        )
        self.get(f"/{self.name_path}" + "/{pk}", response_model=self.response_model)(
            self.retrieve_model
        )
        self.post(
            f"/{self.name_path}/",
            response_model=self.response_model,
        )(self.create_model)
        self.delete(f"/{self.name_path}" + "/{pk}")(self.delete_model)
        self.put(f"/{self.name_path}" + "/{pk}")(self.update_model)

    def list_model(self, db: Session = Depends(get_db)):
        return view_list(db, self.model)

    def retrieve_model(self, pk: int, db: Session = Depends(get_db)):
        return view_retrieve(db, self.model, pk)

    def create_model(self, data: BaseModel, db: Session = Depends(get_db)):
        return view_create(db, self.model, data)

    def delete_model(self, pk: int, db: Session = Depends(get_db)):
        return view_delete(db, self.model, pk)

    def update_model(
        self, user_id: int, data: BaseModel, db: Session = Depends(get_db)
    ):
        return view_update(db, self.model, user_id, data)
