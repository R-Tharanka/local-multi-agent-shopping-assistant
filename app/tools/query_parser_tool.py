from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from app.models.query_model import MissingField, ParsedQuery


def parse_user_query(
    query: str,
    *,
    supported_categories: Sequence[str] = ("laptop", "phone"),
) -> dict:
    """
    Extracts structured shopping requirements from a raw user query.

    This tool is intentionally rule-based (deterministic) to avoid hallucinating
    missing information and to keep unit tests stable.

    Returns a dict with (at minimum):
    - category: str | None
    - budget: float | None
    - preferences: list[str]
    Plus helpful metadata (currency, missing_fields, confidence, warnings).
    """
    original_query = query or ""
    cleaned = _normalize_query(original_query)

    result = ParsedQuery(original_query=original_query)
    if not cleaned:
        result.missing_fields = ["category", "budget"]
        result.warnings = ["empty_query"]
        result.confidence = 0.0
        return result.model_dump()

    detected_categories = _detect_categories(cleaned)
    if detected_categories:
        supported = [c for c in detected_categories if c in set(supported_categories)]
        if supported:
            result.category = supported[0]
            if len(supported) > 1:
                result.warnings.append(f"multiple_categories:{','.join(supported)}")
        else:
            result.warnings.append(f"unsupported_category:{','.join(detected_categories)}")

    currency, budget_min, budget_max, budget_warnings = _extract_budget(cleaned)
    result.currency = currency
    if budget_warnings:
        result.warnings.extend(budget_warnings)

    if budget_min is not None:
        result.warnings.append("budget_min_detected")
    result.budget = budget_max

    result.preferences = _extract_preferences(cleaned, category=result.category)

    missing_fields: list[MissingField] = []
    if result.category is None:
        missing_fields.append("category")
    if result.budget is None:
        missing_fields.append("budget")
    result.missing_fields = missing_fields

    result.confidence = _compute_confidence(
        has_category=result.category is not None,
        has_budget=result.budget is not None,
        preference_count=len(result.preferences),
        warning_count=len(result.warnings),
    )

    return result.model_dump()


def parse_query(query: str) -> dict:
    """
    Backward-compatible alias for older code paths.
    """
    return parse_user_query(query)


def _normalize_query(query: str) -> str:
    q = query.strip()
    q = q.replace("\u00a0", " ")
    q = re.sub(r"\s+", " ", q)
    return q.lower()


def _detect_categories(query: str) -> list[str]:
    mappings: dict[str, Iterable[str]] = {
        "laptop": (
            "laptop",
            "notebook",
            "notebook pc",
            "ultrabook",
            "macbook",
            "chromebook",
        ),
        "phone": ("phone", "smartphone", "mobile", "iphone", "android"),
    }

    found: list[str] = []
    for category, keywords in mappings.items():
        if any(re.search(rf"\b{re.escape(k)}\b", query) for k in keywords):
            found.append(category)
    return found


def _extract_budget(query: str) -> tuple[str | None, float | None, float | None, list[str]]:
    warnings: list[str] = []

    currency = _detect_currency(query)

    q = query.replace(",", "")
    q = re.sub(r"\s+", " ", q)

    between = re.search(
        r"\bbetween\s+(?P<a>\d+(?:\.\d+)?)\s*(?P<asuf>k|m|thousand|million)?\s+and\s+(?P<b>\d+(?:\.\d+)?)\s*(?P<bsuf>k|m|thousand|million)?\b",
        q,
    )
    if between:
        a = _apply_number_suffix(float(between.group("a")), between.group("asuf"))
        b = _apply_number_suffix(float(between.group("b")), between.group("bsuf"))
        lo, hi = (a, b) if a <= b else (b, a)
        return currency, lo, hi, warnings

    range_dash = re.search(
        r"\b(?P<a>\d+(?:\.\d+)?)\s*(?P<asuf>k|m)?\s*[-–]\s*(?P<b>\d+(?:\.\d+)?)\s*(?P<bsuf>k|m)?\b",
        q,
    )
    if range_dash:
        a = _apply_number_suffix(float(range_dash.group("a")), range_dash.group("asuf"))
        b = _apply_number_suffix(float(range_dash.group("b")), range_dash.group("bsuf"))
        lo, hi = (a, b) if a <= b else (b, a)
        warnings.append("budget_range_detected")
        return currency, lo, hi, warnings

    qualifiers = (
        r"under|below|less than|<=|at most|upto|up to|within|around|approx(?:\.|imately)?|about",
        r"budget\s*(?:of|:)?",
    )
    qual_re = re.compile(rf"\b(?:{qualifiers[0]}|{qualifiers[1]})\s*(?P<cur>\$|usd|lkr|rs|inr|eur|gbp|£)?\s*(?P<num>\d+(?:\.\d+)?)\s*(?P<suf>k|m|thousand|million)?\b")
    m = qual_re.search(q)
    if m:
        if currency is None and m.group("cur"):
            currency = _normalize_currency_token(m.group("cur"))
        budget = _apply_number_suffix(float(m.group("num")), m.group("suf"))
        return currency, None, budget, warnings

    symbol_then_num = re.search(r"(?P<cur>\$|£)\s*(?P<num>\d+(?:\.\d+)?)\s*(?P<suf>k|m)?\b", q)
    if symbol_then_num:
        if currency is None:
            currency = _normalize_currency_token(symbol_then_num.group("cur"))
        budget = _apply_number_suffix(float(symbol_then_num.group("num")), symbol_then_num.group("suf"))
        warnings.append("budget_without_qualifier")
        return currency, None, budget, warnings

    bare = re.search(r"\b(?P<num>\d{3,})(?:\s*(?P<suf>k|m))?\b", q)
    if bare:
        budget = _apply_number_suffix(float(bare.group("num")), bare.group("suf"))
        warnings.append("budget_ambiguous")
        return currency, None, budget, warnings

    return currency, None, None, warnings


def _detect_currency(query: str) -> str | None:
    if "$" in query or re.search(r"\busd\b", query):
        return "USD"
    if re.search(r"\blkr\b", query) or re.search(r"\brs\b", query) or "රු" in query:
        return "LKR"
    if re.search(r"\binr\b", query) or "₹" in query:
        return "INR"
    if re.search(r"\beur\b", query) or "€" in query:
        return "EUR"
    if re.search(r"\bgbp\b", query) or "£" in query:
        return "GBP"
    return None


def _normalize_currency_token(token: str) -> str | None:
    t = token.strip().lower()
    if t == "$" or t == "usd":
        return "USD"
    if t == "£" or t == "gbp":
        return "GBP"
    if t in {"lkr", "rs"}:
        return "LKR"
    if t == "inr":
        return "INR"
    if t == "eur":
        return "EUR"
    return None


def _apply_number_suffix(value: float, suffix: str | None) -> float:
    if suffix is None:
        return value
    s = suffix.lower().strip(".")
    if s == "k":
        return value * 1_000
    if s == "m":
        return value * 1_000_000
    if s == "thousand":
        return value * 1_000
    if s == "million":
        return value * 1_000_000
    return value


def _extract_preferences(query: str, *, category: str | None) -> list[str]:
    preferences: list[str] = []

    def add(pref: str) -> None:
        if pref not in preferences:
            preferences.append(pref)

    if re.search(r"\bssd\b", query):
        add("ssd")
    if re.search(r"\bhdd\b", query):
        add("hdd")
    if re.search(r"\blight(?:weight)?\b", query):
        add("lightweight")
    if re.search(r"\b(good|long|excellent)\s+battery\b", query) or re.search(r"\bbattery\s+life\b", query):
        add("good battery")
    elif re.search(r"\bbattery\b", query):
        add("battery")

    if re.search(r"\bgaming\b", query):
        add("gaming")
    if re.search(r"\b(coding|programming|developer|dev)\b", query):
        add("coding")
    if re.search(r"\b(photography|camera)\b", query):
        add("photography")
    if re.search(r"\bfast charging\b", query):
        add("fast charging")
    if re.search(r"\b(performance|fast|smooth)\b", query):
        add("high performance")
    if re.search(r"\bbacklit\b", query):
        add("backlit keyboard")
    if re.search(r"\brtx\b", query) or re.search(r"\bgpu\b", query):
        add("gpu")
    if re.search(r"\bpremium\b", query):
        add("premium")
    if re.search(r"\b(cheap|affordable|budget|not too expensive)\b", query):
        add("affordable")
    if re.search(r"\b(student|uni|university)\b", query):
        add("student")
    if re.search(r"\b(office|work)\b", query):
        add("office")

    if category == "phone":
        if "photography" in preferences and "good camera" not in preferences:
            add("good camera")
    return preferences


def _compute_confidence(
    *,
    has_category: bool,
    has_budget: bool,
    preference_count: int,
    warning_count: int,
) -> float:
    score = 0.0
    if has_category:
        score += 0.45
    if has_budget:
        score += 0.45
    if preference_count:
        score += 0.10
    if warning_count:
        score -= min(0.20, warning_count * 0.05)
    return max(0.0, min(1.0, score))
