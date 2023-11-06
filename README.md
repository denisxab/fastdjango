# Использование

## Запустить проект

Запустить DEV сервер:

```bash
invoke server.rundev
```

Запустить сервер:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Работа с фикстурами

Прочитать записи из таблицы БД

```bash
invoke db.dumpdata ИмяТаблицы > ИмяТаблицы.json
```

Прочитать из файла и записать в БД

```bash
invoke db.loaddata ИмяТаблицы.json
```

Удалить все записи из таблицы БД

```bash
invoke db.flushtable users
```

## Проверки проекта

Запустить проверки:

1. Проверить подключение к БД

```bash
invoke server.check
```

## Аналог ViewSet

Есть аналог ViewSet из Django:

```python
from fhelp.viewset import FViews
from api.schema import CU_UserSchema, UserSchema
from .models import User

router_persons = APIRouter()

class UsersRouter(FViews, APIRouter):
    model = User
    url = "users"
    response_model = UserSchema
    schema_body = CU_UserSchema
    filter_column_eq = ("level",)
    filter_column_like = ("snils",)
    page_size = 2
    order_by = ("id",)

router_persons.include_router(UsersRouter())
```

## Админ панель

Подключить админ панель:

```python
from fastapi import FastAPI
from fhelp.fadmin import add_model_in_admin, router_admin
from api.models import Person, User

app = FastAPI()

# Добавляем миддлвару для обработки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можете заменить "*" на домен вашего фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключить модели в админ панель:

add_model_in_admin(model=User)
add_model_in_admin(model=Person)

app.include_router(router_admin)
```

Теперь можно пользоваться API админ панели:

- ![](./doc/Screenshot_20231106_124724.png)
- ![](./doc/Screenshot_20231106_124814.png)

## Авторизация по JWT

### 1. Создать SECRET_KEY

Сгенерировать секретный ключ:

```bash
invoke server.gensecretkey
```

Вставьте этот ключ в `settings.py`:

```bash
SECRET_KEY = "f58f7156911ebf46b9d9ad35b43e60388dc8f639b356f59eac3aa8df45290d47"
```

### 2. Подключить к проекту

Подключите аутентификацию и авторизацию по JWT:

```python
from fhelp.fjwt import router_jwt,add_handler_login_jwt

app = FastAPI()

def handler_login_jwt(username: str, password: str):
    """Проверка аутентификации пользователя перед выдачей токена"""

    ...

    # Если False то будет исключение
    return True

add_handler_login_jwt(handler_login_jwt)
app.include_router(router_jwt)
```

### 3. Аутентификация

Выполнить аутентификацию и получить JWT:

```bash
curl -X 'POST' \
  'http://localhost:8000/login_jwt?username=Имя&password=Пароль' \
  -H 'accept: application/json' \
```

### 4. Авторизация

Использовать авторизацию для функций:

```python
from fhelp.fjwt import get_current_user

@app.get("/Имя")
async def Имя(current_user: dict = Depends(get_current_user)):
    # Только авторизованный пользователь попадет в эту функцию
    return current_user
```

Выполнить запрос с JWT:

```bash
curl --location 'http://localhost:8000/Путь' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkMTIzMTIzIiwiZXhwIjoxNjk5MjAyNzc4fQ.xv5G6e3HUS3rahvdYFwCzx7rK5cNplOFmbe4RQw5xig'
```

Текст ошибки авторизации:

```http
HTTP 403

{
    "detail": "Could not validate credentials"
}
```

### 4.1 Авторизация для Views

Используйте класс `FViewsJwt` вместо `FViews`

# Оформление проекта

-   `ИмяПриложения`
    -   `__init__.py`
    -   `models.py` - Файл с определением моделей данных
    -   `query_db.py` - Модуль для выполнения запросов к базе данных
    -   `view.py` - Модуль для маршрутизации URL и обработки запросов
    -   `schema.py` - Схема запросов и ответов
-   `main.py` - Файл, откуда запускается проект
-   `models.py` - Файл, где происходит подключение моделей
-   `settings.py` - Файл с настройками проекта
-   `tasks.py` - Модуль для автоматизации задач через командную строку
-   `README.md` - Документация проекта
-   `pyproject.toml` - Файл с описанием зависимостей библиотек
-   `alembic.ini` - Файл с настройками для инструмента `alembic`

# Миграции

## Использовать готовый CLI

-   `invoke db.makemigrations` - Создать миграцию
-   `invoke db.migrate` - Применить миграцию

## Alembic

### CLI Alembic

Инициализация Alembic: `alembic init alembic`

Создать миграцию: `alembic revision --autogenerate`

-   `-m "ИмяМиграции"`

Применить все миграции к БД: `alembic upgrade head`

Откатить миграцию на один шаг назад: `alembic downgrade -1`
