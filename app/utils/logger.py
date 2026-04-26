from __future__ import annotations

import logging
import os
from pathlib import Path


def get_logger(name: str = "shopping-assistant") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    disable_file_logging = os.getenv("DISABLE_FILE_LOGGING") == "1" or "PYTEST_CURRENT_TEST" in os.environ
    if not disable_file_logging:
        try:
            Path("logs").mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler("logs/execution.log", encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            pass

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
