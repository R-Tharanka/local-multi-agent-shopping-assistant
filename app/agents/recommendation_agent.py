from __future__ import annotations

import json
from urllib import request
from urllib.error import URLError

from app import config
from app.state.global_state import GLOBAL_STATE
from app.tools.recommendation_tool import generate_recommendation_report
from app.utils.logger import get_logger

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


def _build_prompt(comparison: dict) -> str:
    comparison_json = json.dumps(comparison, ensure_ascii=True)
    return (
        "You are a shopping assistant. Summarize the comparison data, then give a clear recommendation. "
        "Keep it concise, use short bullet points, and end with a single-line final recommendation.\n\n"
        f"Comparison data:\n{comparison_json}"
    )


def _call_ollama(prompt: str) -> str | None:
    logger = get_logger()
    host = config.OLLAMA_HOST.rstrip("/")
    url = f"{host}/api/generate"
    body = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        data = json.dumps(body).encode("utf-8")
        req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        response_text = payload.get("response", "").strip()
        return response_text or None
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("[Recommendation Agent] Ollama request failed: %s", exc)
        return None


def run(comparison: dict) -> dict:
    """Return a structured recommendation result for workflow/tests."""
    comparison = comparison or {}
    comparison_result = comparison.get("comparison") if isinstance(comparison.get("comparison"), dict) else comparison

    if config.LLM_PROVIDER.lower() == "ollama":
        llm_report = _call_ollama(_build_prompt(comparison_result))
        final_text = llm_report or generate_recommendation_report(comparison_result)
    else:
        final_text = generate_recommendation_report(comparison_result)

    payload = {"final_recommendation": final_text}
    GLOBAL_STATE["final_recommendation"] = final_text
    return payload


recommendation_agent = None
if Agent is not None:
    try:
        recommendation_agent = Agent(
            role="Recommendation Agent",
            goal="Provide the best product recommendation with clear reasoning",
            backstory=(
                "You are an expert shopping assistant who helps users choose the best product "
                "based on comparison results. You provide clear, honest, and helpful explanations."
            ),
            tools=[generate_recommendation_report],
            verbose=True,
        )
    except Exception:  # pragma: no cover
        recommendation_agent = None