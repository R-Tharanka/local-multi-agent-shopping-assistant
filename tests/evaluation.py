from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.tools.query_parser_tool import parse_user_query


@dataclass(frozen=True)
class CaseExpected:
    category: str | None = None
    budget: float | None = None
    use_case: str | None = None
    sort_preference: str | None = None
    must_include_must_have: tuple[str, ...] = ()
    must_include_nice_to_have: tuple[str, ...] = ()
    must_include_preferences: tuple[str, ...] = ()
    must_include_missing_fields: tuple[str, ...] = ()


BENCHMARK: list[tuple[str, CaseExpected]] = [
    (
        "I need a laptop under 200000 for coding with SSD and good battery life",
        CaseExpected(
            category="laptop",
            budget=200000,
            use_case="coding",
            must_include_must_have=("ssd",),
            must_include_nice_to_have=("good battery",),
            must_include_preferences=("coding", "ssd"),
        ),
    ),
    (
        "I need a good phone for photography",
        CaseExpected(
            category="phone",
            budget=None,
            use_case="photography",
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
            use_case="coding",
            must_include_preferences=("coding",),
        ),
    ),
    (
        "Need a laptop under LKR 250000",
        CaseExpected(category="laptop", budget=250000),
    ),
    (
        "best camera phone under $500",
        CaseExpected(category="phone", budget=500, sort_preference="best_camera"),
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
    use_case_ok = 0
    prefs_required = 0
    prefs_hit = 0
    must_have_required = 0
    must_have_hit = 0
    nice_to_have_required = 0
    nice_to_have_hit = 0
    sort_required = 0
    sort_hit = 0
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

        if expected.use_case == got.get("use_case"):
            use_case_ok += 1

        got_prefs = {p.lower() for p in got.get("preferences", [])}
        for pref in expected.must_include_preferences:
            prefs_required += 1
            if pref.lower() in got_prefs:
                prefs_hit += 1

        got_must = {p.lower() for p in got.get("must_have_features", [])}
        for feat in expected.must_include_must_have:
            must_have_required += 1
            if feat.lower() in got_must:
                must_have_hit += 1

        got_nice = {p.lower() for p in got.get("nice_to_have_features", [])}
        for feat in expected.must_include_nice_to_have:
            nice_to_have_required += 1
            if feat.lower() in got_nice:
                nice_to_have_hit += 1

        if expected.sort_preference is not None:
            sort_required += 1
            if expected.sort_preference == got.get("sort_preference"):
                sort_hit += 1

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
                    "use_case": expected.use_case,
                    "sort_preference": expected.sort_preference,
                    "must_include_must_have": list(expected.must_include_must_have),
                    "must_include_nice_to_have": list(expected.must_include_nice_to_have),
                    "must_include_preferences": list(expected.must_include_preferences),
                    "must_include_missing_fields": list(expected.must_include_missing_fields),
                },
                "got": {
                    "category": got.get("category"),
                    "budget": got.get("budget"),
                    "currency": got.get("currency"),
                    "preferences": got.get("preferences", []),
                    "use_case": got.get("use_case"),
                    "must_have_features": got.get("must_have_features", []),
                    "nice_to_have_features": got.get("nice_to_have_features", []),
                    "sort_preference": got.get("sort_preference"),
                    "missing_fields": got.get("missing_fields", []),
                    "confidence": got.get("confidence", 0.0),
                    "warnings": got.get("warnings", []),
                },
            }
        )

    category_accuracy = category_ok / total
    budget_accuracy = budget_ok / total
    use_case_accuracy = use_case_ok / total
    preference_recall = (prefs_hit / prefs_required) if prefs_required else 1.0
    must_have_recall = (must_have_hit / must_have_required) if must_have_required else 1.0
    nice_to_have_recall = (nice_to_have_hit / nice_to_have_required) if nice_to_have_required else 1.0
    sort_accuracy = (sort_hit / sort_required) if sort_required else 1.0
    missing_field_accuracy = (missing_hit / missing_required) if missing_required else 1.0

    score = (
        category_accuracy
        + budget_accuracy
        + use_case_accuracy
        + preference_recall
        + must_have_recall
        + nice_to_have_recall
        + sort_accuracy
        + missing_field_accuracy
    ) / 8.0

    return {
        "cases": total,
        "category_accuracy": round(category_accuracy, 3),
        "budget_accuracy": round(budget_accuracy, 3),
        "use_case_accuracy": round(use_case_accuracy, 3),
        "preference_recall": round(preference_recall, 3),
        "must_have_recall": round(must_have_recall, 3),
        "nice_to_have_recall": round(nice_to_have_recall, 3),
        "sort_accuracy": round(sort_accuracy, 3),
        "missing_field_accuracy": round(missing_field_accuracy, 3),
        "score": round(score, 3),
        "details": details,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(evaluate(), indent=2, ensure_ascii=False))
