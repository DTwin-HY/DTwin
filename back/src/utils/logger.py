import os
import sys

from loguru import logger as _logger


def configure_logger(level: str | None = None):
    _logger.remove()
    lvl = level or os.getenv("LOG_LEVEL", "INFO")
    _logger.add(
        sys.stdout,
        level=lvl,
        backtrace=True,
        diagnose=True,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )
    return _logger


logger = configure_logger()
