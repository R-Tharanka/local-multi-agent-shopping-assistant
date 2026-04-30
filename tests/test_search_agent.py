from app.agents.search_agent import run


def test_search_agent_returns_list():
    out = run({"category": "laptop", "budget": 200000, "preferences": ["ssd"]})
    assert isinstance(out, list)
    assert len(out) > 0

