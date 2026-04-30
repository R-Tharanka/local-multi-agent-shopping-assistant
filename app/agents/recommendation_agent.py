from __future__ import annotations

from app.tools.recommendation_tool import build_recommendation_payload, generate_recommendation_report

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


def run(comparison: dict) -> dict:
    """Return a structured recommendation result for workflow/tests."""
    payload = build_recommendation_payload(comparison)
    payload["comparison"] = comparison
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