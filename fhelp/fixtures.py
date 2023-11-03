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
    for row in json_data["rows"]:
        sql_query = "INSERT INTO {name} ({keys}) VALUES ({values});".format(
            name=json_data["model"],
            keys=", ".join(row.keys()),
            values=", ".join(
                [f"'{v}'" if isinstance(v, str) else str(v) for v in row.values()]
            ),
        )
        res += sql_write(sql_query)
    return res


def dumpdata_(name_table: str):
    """Прочитать из БД"""
    sql_query = f"SELECT * FROM {name_table}"
    res = sql_read(sql_query)
    json_data = json.dumps(
        {"model": f"{name_table}", "rows": res}, ensure_ascii=False, indent=4
    )
    return json_data
