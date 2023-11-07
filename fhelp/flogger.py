"""Логгер для fhelp"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def basicConfigLogger(path_log_dir: Path, level=logging.DEBUG):
    """Запустить эту функцию в main.py, чтобы она настроила логгер"""
    logger = logging.getLogger("fhelp")
    # Устанавливаем уровень логирования для этого конкретного логгера
    logger.setLevel(level=level)

    # Создаем обработчик для записи логов в файл
    # Файл будет сам отчищаться при достижение 100 килобайт
    file_handler = RotatingFileHandler(
        Path(path_log_dir, "fhelp.log"),
        # 100 килобайт
        maxBytes=100 * 1024,
        # Храним одну копию прошлйо версии лога, до отчистки
        backupCount=1,
    )
    file_handler.setLevel(
        logging.DEBUG
    )  # Устанавливаем уровень логирования для этого обработчика

    # Создаем форматтер для форматирования записей в логах
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def getLogger():
    """получить логгер"""
    return logging.getLogger("fhelp")
