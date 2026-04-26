from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

# CTSE MAS constraint: local-only execution (no paid/cloud API keys).
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3:8b")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
