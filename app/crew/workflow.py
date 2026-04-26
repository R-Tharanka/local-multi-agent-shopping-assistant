from __future__ import annotations

from app.agents.comparison_agent import run as comparison_run
from app.agents.query_agent import run as query_run
from app.agents.recommendation_agent import run as recommendation_run
from app.agents.search_agent import run as search_run
from app.state.state_manager import StateManager
from app.utils.logger import get_logger


def run_workflow(query: str = "example: best phone under $500") -> dict:
    logger = get_logger()
    state = StateManager()

    logger.info("Starting workflow")

    parsed = query_run(query)
    state.set("parsed_query", parsed)

    products = search_run(parsed)
    state.set("products", products)

    comparison = comparison_run(products)
    state.set("comparison", comparison)

    recs = recommendation_run(comparison)
    state.set("recommendations", recs)

    logger.info("Finished workflow")
    return state.snapshot()
