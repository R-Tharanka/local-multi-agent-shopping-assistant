from __future__ import annotations

import json
from pathlib import Path


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


def search_products(query: dict, data_path: str | Path) -> list[dict]:
    query = query or {}
    path = Path(data_path)
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    original_query = _normalize_str(query.get("original_query") or "")
    if original_query:
        exact_matches: list[dict] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = _normalize_str(item.get("name") or "")
            if name and name in original_query:
                exact_matches.append(item)
        if exact_matches:
            return exact_matches

    category = _normalize_str(query.get("category") or query.get("product_category") or "")
    budget = query.get("budget")
    preferences = query.get("preferences") or []
    if isinstance(preferences, str):
        preferences = [preferences]

    results: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue

        if category:
            product_category = _normalize_str(item.get("category") or "")
            if not product_category or product_category != category:
                continue

        if budget is not None:
            try:
                price = float(item.get("price"))
            except (TypeError, ValueError):
                continue
            if price > float(budget):
                continue

        if preferences:
            if not _matches_preferences(item, preferences):
                continue

        results.append(item)

    return results

