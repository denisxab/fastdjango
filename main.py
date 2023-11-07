from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models import Person, User
from api.view import router_persons
from fhelp.fadmin import add_model_in_admin, router_admin
from fhelp.fjwt import add_handler_login_jwt, router_jwt
from fhelp.flogger import basicConfigLogger

app = FastAPI()

# Добавляем миддлвару для обработки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можете заменить "*" на домен вашего фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем роутер к приложению
app.include_router(router_persons)


def handler_login_jwt(username: str, password: str):
    """Проверка авторизации пользователя"""
    return True


add_handler_login_jwt(handler_login_jwt)
app.include_router(router_jwt)


# Подключить модели в админ панель:

add_model_in_admin(model=User)
add_model_in_admin(model=Person)

app.include_router(router_admin)

# Настраиваем логгер
basicConfigLogger(path_log_dir=Path(__file__).parent / "log", level="DEBUG")
