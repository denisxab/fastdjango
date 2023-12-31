"""
Базовые команды для проекта
"""

from pprint import pprint

import psycopg2
from invoke import Collection, Context, task

from fhelp.database import sql_write
from fhelp.ffiextures import base_dumpdata, base_loaddata
from main import app
from settings import SettingsFastApi

settings = SettingsFastApi()


@task
def rundev(ctx: Context):
    """Запустить DEV сервер"""
    ctx.run(f"uvicorn main:app --reload --host 0.0.0.0 --port {settings.APP_PORT}")


@task
def runprod(ctx: Context):
    """Запустить PROD сервер"""
    import multiprocessing

    workers = multiprocessing.cpu_count() * 2 + 1

    ctx.run(
        f"uvicorn main:app --host 0.0.0.0 --port {settings.APP_PORT} --workers {workers} --limit-max-requests 1000"
    )


@task
def gensecretkey(ctx: Context):
    """Создать SECRET_KEY"""
    import secrets

    print(secrets.token_hex(32))


@task
def clearredis(ctx: Context):
    """Отчистить redis"""

    import asyncio

    from redis import Redis
    from redis import asyncio as aioredis

    async def _inner():
        redis: Redis = aioredis.from_url(settings.REDIS_URL)
        keys_to_delete = await redis.keys("*")
        if keys_to_delete:
            await redis.delete(*keys_to_delete)

    asyncio.run(_inner())
    print("Redis очищен")


@task
def downloadpip(ctx: Context):
    """Скачать все файлы зависимостей локально"""
    ctx.run("poetry export -f requirements.txt --output requirements.txt")
    ctx.run("mkdir downloaded_libraries")
    ctx.run("pip install -r requirements.txt -t downloaded_libraries")
    # Архивируем папку
    # ctx.run("tar -czvf downloaded_libraries.tar.gz downloaded_libraries")
    # Скачать все зависимости из локальных файлов в папке downloaded_libraries
    # ctx.run("pip install --no-index --find-links=./downloaded_libraries -r requirements.txt")


@task
def makemigrations(ctx: Context):
    """Создать миграцию"""
    print(ctx.run("alembic revision --autogenerate"))


@task
def migrate(ctx: Context):
    """Применить все миграции"""
    print(ctx.run("alembic upgrade head"))


@task
def check(ctx: Context):
    """Проверка проекта"""

    check_res = {"connect_db": False}
    # Проверить подключение к БД
    try:
        connection = psycopg2.connect(dsn=settings.DATABASE_URL)
        connection.close()
        check_res["connect_db"] = True
    except psycopg2.Error as e:
        raise e

    # Проверить что все проверки прошли
    for k, v in check_res.items():
        if not v:
            raise ValueError(f'Проверка не прошла "{k}"')

    pprint(check_res)


@task
def loaddata(ctx: Context, files_pattern: str):
    """Прочитать из файла и записать в БД

    invoke db.loaddata users.json
    """
    base_loaddata(files_pattern)


@task
def dumpdata(ctx: Context, name_table: str, out_file: str = None):
    """Прочитать записи из БД

    invoke db.dumpdata users -o='users.json'
    """
    base_dumpdata(name_table, out_file)


@task
def flushtable(ctx: Context, name_table: str):
    """Удалить все записи из таблицы

    invoke db.flushtable users
    """
    print(sql_write(f"DELETE FROM {name_table};"))


@task
def speedurl(ctx: Context, url: str):
    """Замерить скорость выполнения URL запроса в миллисекундах

    invoke speedurl http://localhost:8000/users/
    """
    import time

    import requests

    num_requests = 1000
    response_times = []

    for _ in range(num_requests):
        start_time = time.time()
        response = requests.get(url)
        if response.status_code > 400:
            raise ValueError(f"response.status_code: {response.status_code}")
        end_time = time.time()
        request_time = (end_time - start_time) * 1000  # Переводим в миллисекунды
        response_times.append(request_time)

    average_response_time = sum(response_times) / num_requests
    print(f"Average response time: {average_response_time:.2f} milliseconds")


@task
def pytest(ctx: Context):
    """Запустить тесты через pytest"""
    ctx.run("pytest")


@task
def listurl(ctx: Context):
    """Получение всех маршрутов"""
    all_routes = app.routes
    paths = list(set(route.path for route in all_routes))
    paths.sort()
    print("===========")
    for path in paths:
        print(path)
    print("===========")


namespace_server = Collection()
namespace_server.add_task(rundev)
namespace_server.add_task(runprod)
namespace_server.add_task(check)
namespace_server.add_task(gensecretkey)
namespace_server.add_task(clearredis)
namespace_server.add_task(downloadpip)
namespace_server.add_task(listurl)

namespace_db = Collection()
namespace_db.add_task(makemigrations)
namespace_db.add_task(migrate)
namespace_db.add_task(loaddata)
namespace_db.add_task(dumpdata)
namespace_db.add_task(flushtable)

namespace_test = Collection()
namespace_test.add_task(speedurl)
namespace_test.add_task(pytest)

namespace = Collection()
namespace.add_collection(namespace_server, name="server")
namespace.add_collection(namespace_db, name="db")
namespace.add_collection(namespace_test, name="test")
