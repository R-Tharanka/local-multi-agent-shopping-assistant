from __future__ import annotations

from app.state.global_state import GLOBAL_STATE
from app.tools.product_search_tool import search_products_from_query
from app.utils.logger import get_logger


def run(parsed_query: dict) -> list[dict]:
    logger = get_logger()
    parsed_query = parsed_query or {}
    logger.info("[Search Agent] Received query: %s", parsed_query)

    products = search_products_from_query(parsed_query)

    GLOBAL_STATE["matched_products"] = products

    logger.info("[Search Agent] Found %s products", len(products))
    return products

