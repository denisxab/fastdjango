from fastapi import FastAPI

from api.view import router_persons
from fhelp.fjwt import router_jwt,add_handler_login_jwt

app = FastAPI()

# Добавляем роутер к приложению
app.include_router(router_persons)

def handler_login_jwt(username: str, password: str):
    """Проверка авторизации пользователя"""
    return True

add_handler_login_jwt(handler_login_jwt)
app.include_router(router_jwt)

