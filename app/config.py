from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

