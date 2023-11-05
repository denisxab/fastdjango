"""
Базовые команды для проекта
"""

import json
from pathlib import Path
from pprint import pprint

import psycopg2
from invoke import Collection, task

from fhelp.utlis import sql_read, sql_write
from settings import APP_PORT, DATABASE_URL


@task
def rundev(ctx):
    """Запустить DEV сервер"""
    ctx.run(f"uvicorn main:app --reload --host 0.0.0.0 --port {APP_PORT}")


@task
def gensecretkey(ctx):
    """Создать SECRET_KEY"""
    import secrets

    print(secrets.token_hex(32))


@task
def makemigrations(ctx):
    """Создать миграцию"""
    ctx.run("alembic revision --autogenerate")


@task
def migrate(ctx):
    """Применить все миграции"""
    ctx.run("alembic upgrade head")


@task
def check(ctx):
    """Проверка проекта"""

    check_res = {"connect_db": False}
    # Проверить подключение к БД
    try:
        connection = psycopg2.connect(dsn=DATABASE_URL)
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
def loaddata(ctx, file_name: str):
    """Прочитать из файла и записать в БД

    invoke loaddata users.json
    """

    file = Path(file_name)
    if not file.exists():
        raise FileNotFoundError(file_name)

    json_data = json.loads(file.read_text(encoding="utf-8"))

    res = 0
    for row in json_data["data"]:
        try:
            sql_query = "INSERT INTO {name} ({keys}) VALUES ({values});".format(
                name=json_data["model"],
                keys=", ".join(json_data["column_name"]),
                values=", ".join(
                    [f"'{v}'" if isinstance(v, str) else str(v) for v in row]
                ),
            )

            res += sql_write(sql_query)
        except psycopg2.errors.UniqueViolation as e:
            print(e)

    print("CREATE ROWS: ", res)


@task
def dumpdata(ctx, name_table: str):
    """Прочитать записи из БД

    invoke dumpdata users > users.json
    """

    sql_query = f"SELECT * FROM {name_table}"
    res = sql_read(sql_query)
    json_data = json.dumps(
        {
            "model": f"{name_table}",
            "column_name": list(res[0].keys()),
            "data": [list(r.values()) for r in res],
        },
        ensure_ascii=False,
        indent=2,
    )
    print(json_data)


@task
def flushtable(ctx, name_table: str):
    """Удалить все записи из таблицы

    invoke flushtable users
    """
    print(sql_write(f"DELETE FROM {name_table}"))


@task
def speedurl(ctx, url: str):
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


namespace_server = Collection()
namespace_server.add_task(rundev)
namespace_server.add_task(check)
namespace_server.add_task(gensecretkey)

namespace_db = Collection()
namespace_db.add_task(makemigrations)
namespace_db.add_task(migrate)
namespace_db.add_task(loaddata)
namespace_db.add_task(dumpdata)
namespace_db.add_task(flushtable)

namespace_test = Collection()
namespace_test.add_task(speedurl)

namespace = Collection()
namespace.add_collection(namespace_server, name="server")
namespace.add_collection(namespace_db, name="db")
namespace.add_collection(namespace_test, name="test")
