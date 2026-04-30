from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "products.json"


def _normalize_str(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _collect_search_text(product: dict) -> str:
    parts: list[str] = []
    for val in product.values():
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, (list, tuple)):
            parts.extend([v for v in val if isinstance(v, str)])
    return _normalize_str(" ".join(parts))


def _matches_preferences(product: dict, preferences: list[str]) -> bool:
    haystack = _collect_search_text(product)
    for pref in preferences:
        if _normalize_str(pref) not in haystack:
            return False
    return True


def _load_products(data_path: str | Path) -> list[dict]:
    path = Path(data_path)
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    items = [item for item in data if isinstance(item, dict)]
    return items


def search_products(
    category: str | None,
    budget: float | int | None,
    preferences: list[str] | None,
    *,
    data_path: str | Path = DATA_PATH,
) -> list[dict]:
    items = _load_products(data_path)
    if not items:
        return []

    category_norm = _normalize_str(category or "")
    pref_list = preferences or []
    if isinstance(pref_list, str):
        pref_list = [pref_list]

    results: list[dict] = []
    for item in items:
        if category_norm:
            product_category = _normalize_str(item.get("category") or "")
            if not product_category or product_category != category_norm:
                continue

        if budget is not None:
            try:
                price = float(item.get("price"))
            except (TypeError, ValueError):
                continue
            if price > float(budget):
                continue

        if pref_list:
            if not _matches_preferences(item, pref_list):
                continue

        results.append(item)

    return results


def search_products_from_query(query: dict, data_path: str | Path = DATA_PATH) -> list[dict]:
    query = query or {}

    original_query = _normalize_str(query.get("original_query") or "")
    if original_query:
        exact_matches: list[dict] = []
        for item in _load_products(data_path):
            name = _normalize_str(item.get("name") or "")
            if name and name in original_query:
                exact_matches.append(item)
        if exact_matches:
            return exact_matches

    category = query.get("category") or query.get("product_category")
    budget = query.get("budget")
    preferences = query.get("preferences") or []
    if isinstance(preferences, str):
        preferences = [preferences]

    return search_products(category, budget, preferences, data_path=data_path)

