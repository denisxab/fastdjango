"""Реализация API простой админ панели"""
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from fhelp.database import get_session
from fhelp.database_async import async_get_session
from fhelp.fcached import RedisCached
from fhelp.utlis import absolute_url, get_pk_name_mode
from fhelp.viewset import view_delete, view_list, view_retrieve, view_update

router_admin = APIRouter(prefix="/admin")
templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "admin_static" / "templates")
)


ADMIN_SETTINGS: dict = {}


def base_admin_html_prams(request: Request):
    return {"main_url": absolute_url(request, router_admin.url_path_for("index_admin"))}


def add_model_in_admin(model: DeclarativeMeta | list[DeclarativeMeta], app: FastAPI):
    """Добавить модель в админ панель"""
    if isinstance(model, list):
        for m in model:
            ADMIN_SETTINGS[m.__name__] = m
    else:
        ADMIN_SETTINGS[model.__name__] = model
    # Минируем статические файлы для фронта админ панели
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).parent / "admin_static")),
        name="admin_static",
    )


@router_admin.get("/", response_class=HTMLResponse)
async def index_admin(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "body_html": "index_admin.html",
            "urls": [
                {
                    "name": "DataBase",
                    "url": absolute_url(
                        request, router_admin.url_path_for(admin_models.__name__)
                    ),
                },
                {
                    "name": "Redis",
                    "url": absolute_url(
                        request, router_admin.url_path_for(admin_rediskeys.__name__)
                    ),
                },
            ],
            **base_admin_html_prams(request),
        },
    )


@router_admin.get("/rediskeys", response_class=HTMLResponse)
async def admin_rediskeys(
    request: Request,
):
    redis = RedisCached()

    all_keys: list[str] = await redis.get_all_keys()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "body_html": "redis_all_keys.html",
            "data": [
                {
                    "key": key,
                    "value": await redis.get(key),
                    "ttl": await redis.get_ttl(key),
                    "delete_key_url": absolute_url(
                        request,
                        router_admin.url_path_for(
                            admin_redis_delete_key.__name__, key=key
                        ),
                    ),
                }
                for key in all_keys
                if key
            ],
            **base_admin_html_prams(request),
        },
    )


@router_admin.delete("/rediskeys/{key}")
async def admin_redis_delete_key(request: Request, key: str):
    redis = RedisCached()
    await redis.delete(key)
    return {"status": "ok"}


@router_admin.get("/models", response_class=HTMLResponse)
async def admin_models(
    request: Request,
):
    models: list[dict] = [
        {
            "name": k,
            "url": absolute_url(
                request, router_admin.url_path_for(rows_model.__name__, model=k)
            ),
        }
        for k in ADMIN_SETTINGS.keys()
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "body_html": "models.html",
            "models": models,
            **base_admin_html_prams(request),
        },
    )


@router_admin.get("/rows/{model}")
async def rows_model(
    request: Request, model: str, session: AsyncSession = Depends(async_get_session)
):
    model_obj = ADMIN_SETTINGS.get(model)

    if model_obj is None:
        raise HTTPException(status_code=404, detail="Model not found")

    rows = await view_list(
        session,
        model_obj,
        order_by=(model_obj.__table__.primary_key.columns.values()[0].name,),
    )

    names = model_obj.__table__.c.keys()
    pk_name = get_pk_name_mode(model_obj)

    result = []
    result_url = []
    for index, row in enumerate(rows):
        result.append({})
        for k in names:
            result[index][k] = getattr(row, k)

        result_url.append(
            absolute_url(
                request,
                router_admin.url_path_for(
                    row_model_from_pk_get.__name__,
                    pk=result[index][pk_name],
                )
                + f"?model={model}",
            )
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "body_html": "rows_model.html",
            "rows": result,
            "rows_url": result_url,
            "column_name": names,
            **base_admin_html_prams(request),
        },
    )


@router_admin.get("/row/{pk}")
async def row_model_from_pk_get(
    request: Request,
    pk: int,
    model: str,
    session: AsyncSession = Depends(async_get_session),
):
    model_obj = ADMIN_SETTINGS.get(model)
    row = await view_retrieve(session, model_obj, pk)

    names = model_obj.__table__.c.keys()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "body_html": "retrieve_row.html",
            "column": {k: getattr(row, k) for k in names},
            "url_back": absolute_url(
                request, router_admin.url_path_for(rows_model.__name__, model=model)
            ),
            "url_update": absolute_url(
                request,
                router_admin.url_path_for(
                    row_model_from_pk_update.__name__,
                    pk=pk,
                )
                + f"?model={model}",
            ),
            "url_delete": absolute_url(
                request,
                router_admin.url_path_for(
                    row_model_from_pk_delete.__name__,
                    pk=pk,
                )
                + f"?model={model}",
            ),
            **base_admin_html_prams(request),
        },
    )


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
