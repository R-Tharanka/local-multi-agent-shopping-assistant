from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str = "shopping-assistant") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    Path("logs").mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler("logs/execution.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

