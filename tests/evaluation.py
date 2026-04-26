from __future__ import annotations

from dataclasses import dataclass

from app.tools.query_parser_tool import parse_user_query


@dataclass(frozen=True)
class CaseExpected:
    category: str | None = None
    budget: float | None = None
    must_include_preferences: tuple[str, ...] = ()
    must_include_missing_fields: tuple[str, ...] = ()


BENCHMARK: list[tuple[str, CaseExpected]] = [
    (
        "I need a laptop under 200000 for coding with SSD and good battery life",
        CaseExpected(
            category="laptop",
            budget=200000,
            must_include_preferences=("coding", "ssd"),
        ),
    ),
    (
        "I need a good phone for photography",
        CaseExpected(
            category="phone",
            budget=None,
            must_include_preferences=("photography",),
            must_include_missing_fields=("budget",),
        ),
    ),
    (
        "Need something under 100000 with long battery life",
        CaseExpected(
            category=None,
            budget=100000,
            must_include_preferences=("good battery",),
            must_include_missing_fields=("category",),
        ),
    ),
    (
        "Looking for a notebook for programming below 180k",
        CaseExpected(
            category="laptop",
            budget=180000,
            must_include_preferences=("coding",),
        ),
    ),
    (
        "Need a laptop under LKR 250000",
        CaseExpected(category="laptop", budget=250000),
    ),
]


def evaluate() -> dict:
    """
    Rule-based evaluation for Query Understanding extraction quality.

    The goal is to provide defendable metrics for the report without relying on
    an external judge model.
    """
    total = len(BENCHMARK)
    if total == 0:
        return {"cases": 0}

    category_ok = 0
    budget_ok = 0
    prefs_required = 0
    prefs_hit = 0
    missing_required = 0
    missing_hit = 0

    details: list[dict] = []

    for query, expected in BENCHMARK:
        got = parse_user_query(query)

        if expected.category == got.get("category"):
            category_ok += 1
        if expected.budget is None:
            if got.get("budget") is None:
                budget_ok += 1
        else:
            if float(got.get("budget") or 0.0) == float(expected.budget):
                budget_ok += 1

        got_prefs = {p.lower() for p in got.get("preferences", [])}
        for pref in expected.must_include_preferences:
            prefs_required += 1
            if pref.lower() in got_prefs:
                prefs_hit += 1

        got_missing = set(got.get("missing_fields", []))
        for mf in expected.must_include_missing_fields:
            missing_required += 1
            if mf in got_missing:
                missing_hit += 1

        details.append(
            {
                "query": query,
                "expected": {
                    "category": expected.category,
                    "budget": expected.budget,
                    "must_include_preferences": list(expected.must_include_preferences),
                    "must_include_missing_fields": list(expected.must_include_missing_fields),
                },
                "got": {
                    "category": got.get("category"),
                    "budget": got.get("budget"),
                    "currency": got.get("currency"),
                    "preferences": got.get("preferences", []),
                    "missing_fields": got.get("missing_fields", []),
                    "confidence": got.get("confidence", 0.0),
                    "warnings": got.get("warnings", []),
                },
            }
        )

    category_accuracy = category_ok / total
    budget_accuracy = budget_ok / total
    preference_recall = (prefs_hit / prefs_required) if prefs_required else 1.0
    missing_field_accuracy = (missing_hit / missing_required) if missing_required else 1.0

    score = (category_accuracy + budget_accuracy + preference_recall + missing_field_accuracy) / 4.0

    return {
        "cases": total,
        "category_accuracy": round(category_accuracy, 3),
        "budget_accuracy": round(budget_accuracy, 3),
        "preference_recall": round(preference_recall, 3),
        "missing_field_accuracy": round(missing_field_accuracy, 3),
        "score": round(score, 3),
        "details": details,
    }
