"""Раота с фикстурами"""

import json
from glob import glob
from pathlib import Path
from typing import List, Union

import psycopg2
from pydantic import BaseModel, RootModel

from fhelp.database import sql_read, sql_write


class ItemFixturesSchema(BaseModel):
    model: str
    column_name: List[str]
    data: List[List[Union[str, int, float]]]


FixturesSchema = RootModel[List[ItemFixturesSchema]]


def base_loaddata(files_pattern: str, dsn: str = None):
    """Прочитать из файла и записать в БД"""
    files: list[str] = glob(files_pattern)

    if not files:
        raise FileNotFoundError(files)

    for file in files:
        raw_json_data = json.loads(Path(file).read_text(encoding="utf-8"))
        json_data: FixturesSchema = FixturesSchema(raw_json_data)

        res = 0
        for row_model in json_data.root:
            for row_data in row_model.data:
                try:
                    sql_query = "INSERT INTO {name} ({keys}) VALUES ({values});".format(
                        name=row_model.model,
                        keys=", ".join(row_model.column_name),
                        values=", ".join(
                            [
                                f"'{v}'" if isinstance(v, str) else str(v)
                                for v in row_data
                            ]
                        ),
                    )

                    res += sql_write(sql_query, dsn)
                except psycopg2.errors.UniqueViolation as e:
                    print(e)

            print(f"FILE {file} - MODEL {row_model.model} - CREATE ROWS: ", res)


def base_dumpdata(name_table: str, out_file: str = None):
    """Прочитать записи из БД"""

    if out_file:
        out_path = Path(out_file)
        if not out_path.exists:
            raise FileNotFoundError(out_path)

    result_sql = sql_read(f"SELECT * FROM {name_table};")
    item_fixtur = ItemFixturesSchema(
        model=name_table,
        column_name=list(result_sql[0].keys()),
        data=[list(r.values()) for r in result_sql],
    ).dict()

    if out_file:
        text = out_path.read_text()
        if text:
            out_json_data = FixturesSchema.parse_file(out_path)
            out_json_data.root.append(item_fixtur)
            out_path.write_text(
                json.dumps(
                    out_json_data.dict(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            # Если файл пустой
            out_path.write_text(
                json.dumps(
                    [item_fixtur],
                    ensure_ascii=False,
                    indent=2,
                )
            )
    else:
        print(
            json.dumps(
                item_fixtur,
                ensure_ascii=False,
                indent=2,
            )
        )
