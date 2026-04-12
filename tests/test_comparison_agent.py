from app.agents.comparison_agent import run


def test_comparison_agent_returns_dict():
    out = run([])
    assert isinstance(out, dict)

