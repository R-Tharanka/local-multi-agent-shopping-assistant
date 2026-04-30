from __future__ import annotations

from app.tools.comparison_tool import compare
from app.utils.logger import get_logger


def run(products: list[dict]) -> dict:
    logger = get_logger()
    logger.info("[Comparison Agent] Comparing %s products", len(products))

    comparison = compare(products)

    logger.info("[Comparison Agent] Comparison complete")
    return {"products": products, "comparison": comparison}

