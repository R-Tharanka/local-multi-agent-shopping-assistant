from __future__ import annotations

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "USD"
    rating: float | None = None

