"""
Выгрузка и загрузка данных в JSON структуру
"""
import json
from pathlib import Path

from fhelp.database import sql_read, sql_write


def loaddata_(file: Path):
    """Прочитать из файла и записать в БД"""
    json_data = json.loads(file.read_text(encoding="utf-8"))

    res = 0
    for row in json_data["data"]:
        sql_query = "INSERT INTO {name} ({keys}) VALUES ({values});".format(
            name=json_data["model"],
            keys=", ".join(json_data["column_name"]),
            values=", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in row]),
        )
        res += sql_write(sql_query)
    return res


def dumpdata_(name_table: str):
    """Прочитать из БД"""
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
    return json_data
