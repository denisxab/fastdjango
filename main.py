"""Главный файл FastApi"""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from api.models import Person, User
from api.router import router_persons
from api.schema import UserSchema
from fhelp.database import get_session
from fhelp.database_async import async_get_session
from fhelp.fadmin import add_model_in_admin, router_admin
from fhelp.fexception_handler import f_404_handler
from fhelp.fjwt import add_handler_login_jwt, router_jwt
from fhelp.flogger import basicConfigLogger
from fhelp.fmiddleware import base_middleware_process_time_header

app = FastAPI(title="FastDjango App", default_response_class=ORJSONResponse)

# Добавляем роутер к приложению
app.include_router(router_persons)

# Настраиваем логгер
basicConfigLogger(path_log_dir=Path(__file__).parent / "log", level="DEBUG")

"""Авторизация по JWT"""


def handler_login_jwt(username: str, password: str):
    """Логика проверка авторизации пользователя"""
    return (True, "")


add_handler_login_jwt(handler_login_jwt)
app.include_router(router_jwt)


"""Админ панель"""
# Добавляем миддлвару для обработки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можете заменить "*" на домен вашего фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключить модели в админ панель:
add_model_in_admin(model=[User, Person], app=app)
app.include_router(router_admin)


"""Подключение тестовых router"""


@app.get("/async_test")
async def async_test_main(
    session: AsyncSession = Depends(async_get_session),
) -> list[UserSchema]:
    query = select(User)
    rows = await session.execute(query)
    return rows.scalars().all()


@app.get("/test")
def test_main(
    session: Session = Depends(get_session),
) -> list[UserSchema]:
    query = select(User)
    rows = session.execute(query)
    return rows.scalars().all()


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Обработка 404 HTTP исключения"""
    return await f_404_handler(request, exc, app)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Замерять время волнения запроса"""
    return await base_middleware_process_time_header(request, call_next)
