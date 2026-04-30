from __future__ import annotations


def _as_number(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.replace(",", "").replace("$", "").strip()
        try:
            return float(normalized)
        except ValueError:
            return None
    return None


def _product_name(product: dict | None) -> str | None:
    if not isinstance(product, dict):
        return None
    name = product.get("name") or product.get("title") or product.get("product")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def _find_rank_entry(product: dict | None, ranked: list[dict]) -> dict | None:
    if not isinstance(product, dict):
        return None
    product_id = product.get("id")
    product_name = _product_name(product)
    for entry in ranked:
        if not isinstance(entry, dict):
            continue
        entry_product = entry.get("product")
        if not isinstance(entry_product, dict):
            continue
        if product_id and entry_product.get("id") == product_id:
            return entry
        if product_name and _product_name(entry_product) == product_name:
            return entry
    return None


def _format_details(product: dict | None, rank_entry: dict | None) -> str:
    if not isinstance(product, dict):
        return ""

    details: list[str] = []
    price = product.get("price")
    rating = product.get("rating")
    features = product.get("features")

    if isinstance(price, (int, float, str)):
        details.append(f"price {price}")
    if isinstance(rating, (int, float, str)):
        details.append(f"rating {rating}")

    if isinstance(features, list):
        feature_list = [f for f in features if isinstance(f, str) and f.strip()]
        if feature_list:
            details.append("features: " + ", ".join(feature_list[:3]))

    if isinstance(rank_entry, dict):
        perf = rank_entry.get("performance_score")
        val = rank_entry.get("value_score")
        if isinstance(perf, (int, float)):
            details.append(f"performance score {perf}")
        if isinstance(val, (int, float)):
            details.append(f"value score {val}")

    return "; ".join(details)


def _pick_recommended_product(comparison: dict) -> tuple[dict | None, str, str]:
    best_value_product = comparison.get("best_value_product")
    best_performance_product = comparison.get("best_performance_product")
    ranked = comparison.get("ranked") or []

    if isinstance(best_value_product, dict):
        entry = _find_rank_entry(best_value_product, ranked)
        details = _format_details(best_value_product, entry)
        reason = "Strong overall value based on price and rating."
        if details:
            reason = f"Strong overall value with {details}."
        return best_value_product, "best_value", reason

    if isinstance(best_performance_product, dict):
        entry = _find_rank_entry(best_performance_product, ranked)
        details = _format_details(best_performance_product, entry)
        reason = "Top performance based on ratings and features."
        if details:
            reason = f"Top performance with {details}."
        return best_performance_product, "best_performance", reason

    if isinstance(ranked, list) and ranked:
        top = ranked[0].get("product") if isinstance(ranked[0], dict) else None
        if isinstance(top, dict):
            entry = _find_rank_entry(top, ranked)
            details = _format_details(top, entry)
            reason = "Highest overall score from comparison results."
            if details:
                reason = f"Highest overall score with {details}."
            return top, "ranked", reason

    products = comparison.get("products")
    if isinstance(products, list) and products:
        first = products[0] if isinstance(products[0], dict) else None
        name = _product_name(first)
        if name:
            return first, "products_fallback", "Only product available after filtering."

    return None, "insufficient_data", "Comparison data did not include ranked products."


def _build_budget_message(comparison: dict) -> str:
    budget = _as_number(comparison.get("budget"))
    selected_price = _as_number(comparison.get("recommended_price"))

    if budget is None:
        return "Budget not provided."
    if selected_price is None:
        return f"Budget considered: {int(budget) if budget.is_integer() else budget}."
    if selected_price <= budget:
        return "The recommendation fits the provided budget."
    return "The recommendation may exceed the provided budget."


def generate_recommendation_report(comparison: dict) -> str:
    product, source, reason = _pick_recommended_product(comparison)
    name = _product_name(product) or "No clear recommendation"
    budget_message = _build_budget_message(comparison)

    alt = ""
    best_perf = comparison.get("best_performance_product")
    best_value = comparison.get("best_value_product")
    if isinstance(best_perf, dict) and isinstance(best_value, dict):
        perf_name = _product_name(best_perf)
        value_name = _product_name(best_value)
        if perf_name and value_name and perf_name != value_name:
            alt = f"Alternative: {perf_name} for performance focus."

    lines = [
        f"Recommended product: {name}",
        f"Decision basis: {source}",
        f"Reason: {reason}",
        f"Budget analysis: {budget_message}",
    ]
    if alt:
        lines.append(alt)

    return "\n".join(lines)


def build_recommendation_payload(comparison: dict) -> dict:
    product, source, reason = _pick_recommended_product(comparison)
    report = generate_recommendation_report(comparison)

    return {
        "recommended_product": _product_name(product) or "No clear recommendation",
        "decision_basis": source,
        "reason": reason,
        "report": report,
    }