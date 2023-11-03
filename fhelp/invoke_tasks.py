"""
Базовые команды для проекта
"""

from pathlib import Path
from pprint import pprint

import psycopg2
from invoke import task

from fhelp.database import sql_write
from fhelp.fixtures import dumpdata_, loaddata_
from settings import APP_PORT, DATABASE_URL


@task
def rundev(ctx):
    """Запустить DEV сервер"""
    ctx.run(f"uvicorn main:app --reload --host 0.0.0.0 --port {APP_PORT}")


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
    rows = loaddata_(file)
    print("CREATE ROWS: ", rows)


@task
def dumpdata(ctx, name_table: str):
    """Прочитать записи из БД

    invoke dumpdata users > users.json
    """
    rows = dumpdata_(name_table)
    print(rows)


@task
def flushtable(ctx, name_table: str):
    """Удалить все записи из таблицы

    invoke flushtable users
    """
    print(sql_write(f"DELETE FROM {name_table}"))
