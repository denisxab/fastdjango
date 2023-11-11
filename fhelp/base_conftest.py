"""Файл конфигурации pytest"""
import sys

import pytest

from fhelp.ftest import run_test


@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    """Код, который нужно выполнить перед запуском всех тестов"""

    print("Выполнение кода перед запуском тестов")

    try:
        sys.argv.index("--reuse-db")
        reuse_db = True
    except ValueError:
        reuse_db = False

    run_test(reuse_db=reuse_db)
