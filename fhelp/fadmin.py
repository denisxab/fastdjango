"""Реализация API простой админ панели"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from fhelp.database import get_session
from fhelp.database_async import async_get_session
from fhelp.viewset import view_delete, view_list, view_retrieve, view_update

router_admin = APIRouter(prefix="/admin")


ADMIN_SETTINGS: dict = {}


def add_model_in_admin(model: DeclarativeMeta):
    ADMIN_SETTINGS[model.__name__] = model


@router_admin.get("/models")
async def models():
    return [{"name": k} for k in ADMIN_SETTINGS.keys()]


@router_admin.get("/rows")
async def rows_model(model: str, session: AsyncSession = Depends(async_get_session)):
    model_obj = ADMIN_SETTINGS.get(model)

    if model_obj is None:
        raise HTTPException(status_code=404, detail="Model not found")

    rows = await view_list(
        session,
        model_obj,
        order_by=(model_obj.__table__.primary_key.columns.values()[0].name,),
    )

    names = model_obj.__table__.c.keys()

    return [{k: getattr(row, k) for k in names} for row in rows]


@router_admin.get("/row/{pk}")
async def row_model_from_pk_get(
    pk: int, model: str, session: AsyncSession = Depends(async_get_session)
):
    model_obj = ADMIN_SETTINGS.get(model)
    row = await view_retrieve(session, model_obj, pk)

    names = model_obj.__table__.c.keys()

    return {k: getattr(row, k) for k in names}


@router_admin.delete("/row/{pk}")
def row_model_from_pk_delete(
    pk: int, model: str, session: Session = Depends(get_session)
):
    model_obj = ADMIN_SETTINGS.get(model)
    return view_delete(session, model_obj, pk)


@router_admin.put("/row/{pk}")
async def row_model_from_pk_update(
    request: Request, pk: int, model: str, session: Session = Depends(get_session)
):
    data = await request.json()
    model_obj = ADMIN_SETTINGS.get(model)
    return view_update(session, model_obj, pk, data)
