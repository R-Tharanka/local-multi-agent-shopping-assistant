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


def _pick_recommended_product(comparison: dict) -> tuple[str, str, str]:
    best_performance = comparison.get("best_performance")
    best_value = comparison.get("best_value")

    if isinstance(best_performance, str) and best_performance.strip():
        return best_performance, "best_performance", "Top performance candidate from comparison results."

    if isinstance(best_value, str) and best_value.strip():
        return best_value, "best_value", "Best value candidate from comparison results."

    products = comparison.get("products")
    if isinstance(products, list) and products:
        first = products[0]
        if isinstance(first, dict):
            name = first.get("name") or first.get("title") or first.get("product")
            if isinstance(name, str) and name.strip():
                return name, "products_fallback", "Fallback to first available product in the input list."

    return "No clear recommendation", "insufficient_data", "Comparison data did not include ranked products."


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
    recommendation, source, reason = _pick_recommended_product(comparison)
    need = comparison.get("user_need", "general use")
    budget_message = _build_budget_message(comparison)

    lines = [
        f"Recommended product: {recommendation}",
        f"Decision basis: {source}",
        f"Reason: {reason}",
        f"User need: {need}",
        f"Budget analysis: {budget_message}",
    ]
    return "\n".join(lines)


def build_recommendation_payload(comparison: dict) -> dict:
    recommendation, source, reason = _pick_recommended_product(comparison)
    report = generate_recommendation_report(comparison)

    return {
        "recommended_product": recommendation,
        "decision_basis": source,
        "reason": reason,
        "report": report,
    }