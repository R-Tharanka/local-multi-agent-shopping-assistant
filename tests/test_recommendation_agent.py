from app.agents.recommendation_agent import run


def test_recommendation_agent_returns_dict():
    out = run({"comparison": {}})
    assert isinstance(out, dict)
    assert "final_recommendation" in out

