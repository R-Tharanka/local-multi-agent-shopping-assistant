from app.agents.query_agent import run


def test_query_agent_returns_dict():
    out = run("hello")
    assert isinstance(out, dict)

