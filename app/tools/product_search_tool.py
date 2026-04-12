from __future__ import annotations

import json
from pathlib import Path


def search_products(query: dict, data_path: str | Path) -> list[dict]:
    _ = query
    path = Path(data_path)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

