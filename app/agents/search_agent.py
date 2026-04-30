from __future__ import annotations

from pathlib import Path

from app.tools.product_search_tool import search_products
from app.utils.logger import get_logger


def run(parsed_query: dict) -> list[dict]:
    logger = get_logger()
    logger.info("[Search Agent] Received query: %s", parsed_query)

    data_path = Path(__file__).resolve().parents[1] / "data" / "products.json"
    products = search_products(parsed_query, data_path)

    logger.info("[Search Agent] Found %s products", len(products))
    return products

