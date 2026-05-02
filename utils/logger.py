# utils/logger.py
# Configuración del logger global para DinoReserve ERP.


import logging
from logging.handlers import RotatingFileHandler

from utils.constants import LOG_PATH

_LOGGER_NAME = "dinoreserve"
_logger_initialized = False


def get_logger() -> logging.Logger:
    """Devuelve el logger global. Se inicializa una sola vez."""
    global _logger_initialized
    logger = logging.getLogger(_LOGGER_NAME)
    if _logger_initialized:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    _logger_initialized = True
    logger.info("Logger inicializado — archivo %s", LOG_PATH)
    return logger
