from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MissingField = Literal["category", "budget"]


class ParsedQuery(BaseModel):
    original_query: str
    category: str | None = None
    budget: float | None = None
    currency: str | None = None
    preferences: list[str] = Field(default_factory=list)
    missing_fields: list[MissingField] = Field(default_factory=list)
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
