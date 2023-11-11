from datetime import datetime, timedelta
from typing import Callable, Final

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from settings import SECRET_KEY

ALGORITHM: Final[str] = "HS256"


def create_jwt(data: dict, expires_delta: timedelta) -> str:
    """Создать JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_token(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    return authorization.credentials


def get_current_user(token: str = Security(get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


router_jwt = APIRouter()


list_handler_login_jwt: Callable = []


def add_handler_login_jwt(callback):
    list_handler_login_jwt.append(callback)


@router_jwt.post("/login_jwt")
async def login_jwt(username: str, password: str):
    # Проверка логина и пароля (это может зависеть от вашей системы аутентификации)
    for handler in list_handler_login_jwt:
        status, text = handler(username, password)
        if not status:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=text,
            )

    # Если пользователь успешно аутентифицирован, создаем токен
    access_token_expires = timedelta(minutes=30)
    access_token = create_jwt(
        data={"sub": username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "Authorization Bearer"}
