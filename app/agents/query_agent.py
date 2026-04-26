from __future__ import annotations

from app.state.global_state import GLOBAL_STATE
from app.state.state_manager import StateManager
from app.tools.query_parser_tool import parse_user_query
from app.utils.logger import get_logger

def run(query: str) -> dict:
    return run_with_state(query)


def run_with_state(query: str, *, state: StateManager | None = None) -> dict:
    logger = get_logger()
    logger.info("[Query Agent] query received: %s", query)

    logger.info("[Query Agent] parser invoked")
    parsed = parse_user_query(query)

    GLOBAL_STATE.update(
        {
            "user_query": query,
            "category": parsed.get("category"),
            "budget": parsed.get("budget"),
            "currency": parsed.get("currency"),
            "preferences": parsed.get("preferences", []),
            "missing_fields": parsed.get("missing_fields", []),
            "query_confidence": parsed.get("confidence", 0.0),
            "query_warnings": parsed.get("warnings", []),
        }
    )

    if state is not None:
        state.set("user_query", query)
        state.set("parsed_query", parsed)

    logger.info(
        "[Query Agent] structured result generated: category=%s budget=%s prefs=%s confidence=%.2f missing=%s",
        parsed.get("category"),
        parsed.get("budget"),
        parsed.get("preferences", []),
        float(parsed.get("confidence") or 0.0),
        parsed.get("missing_fields", []),
    )
    logger.info("[Query Agent] state updated")
    return parsed
