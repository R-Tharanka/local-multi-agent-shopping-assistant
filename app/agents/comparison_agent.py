from __future__ import annotations

from app.state.global_state import GLOBAL_STATE
from app.tools.comparison_tool import compare_products
from app.utils.logger import get_logger


def run(products: list[dict]) -> dict:
    logger = get_logger()
    logger.info("[Comparison Agent] Comparing %s products", len(products))

    comparison = compare_products(products)
    GLOBAL_STATE["comparison_result"] = comparison

    logger.info("[Comparison Agent] Comparison complete")
    return {"products": products, "comparison": comparison}

