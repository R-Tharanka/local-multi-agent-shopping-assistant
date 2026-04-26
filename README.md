# Local Multi-Agent Shopping Assistant

This repo contains a scaffold for a CrewAI-based multi-agent shopping assistant.

## Structure
- `app/`: application code (agents, tools, crew orchestration, state, utilities, models)
- `tests/`: unit tests + evaluation harness
- `logs/`: runtime logs
- `docs/`: diagrams/report placeholders
- `demo/`: demo placeholders

## Quickstart
1. Create and activate a virtual environment
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Set environment variables in `.env`
4. Run:
   - Interactive prompt: `python -m app.main`
   - One-shot query: `python -m app.main --query "I need a laptop under 200000 for coding with SSD and good battery life"`

## Query Agent evaluation
- Unit tests: `pytest -q`
- Rule-based benchmark: `python tests/evaluation.py`
