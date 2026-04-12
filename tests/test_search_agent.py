from app.agents.search_agent import run


def test_search_agent_returns_list():
    out = run({"query": "hello"})
    assert isinstance(out, list)

