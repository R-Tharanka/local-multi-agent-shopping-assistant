from __future__ import annotations


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _feature_count(product: dict) -> int:
    features = product.get("features")
    if isinstance(features, (list, tuple)):
        return sum(1 for f in features if isinstance(f, str) and f.strip())
    return 0


def _normalize(value: float, min_value: float, max_value: float) -> float:
    if max_value <= min_value:
        return 0.0
    return (value - min_value) / (max_value - min_value)


def _product_name(product: dict) -> str | None:
    name = product.get("name") or product.get("title") or product.get("product")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def compare_products(products: list[dict]) -> dict:
    items = [p for p in products if isinstance(p, dict)]
    if not items:
        return {
            "best_performance": None,
            "best_value": None,
            "ranked": [],
        }

    prices = [_safe_float(p.get("price")) for p in items]
    ratings = [_safe_float(p.get("rating")) for p in items]
    feature_counts = [_feature_count(p) for p in items]

    min_price, max_price = min(prices), max(prices)
    min_rating, max_rating = min(ratings), max(ratings)
    min_features, max_features = min(feature_counts), max(feature_counts)

    ranked: list[dict] = []
    for product, price, rating, features in zip(items, prices, ratings, feature_counts):
        price_norm = _normalize(price, min_price, max_price)
        rating_norm = _normalize(rating, min_rating, max_rating)
        features_norm = _normalize(float(features), float(min_features), float(max_features))

        performance_score = (0.6 * rating_norm) + (0.4 * features_norm)
        value_score = (0.7 * (1.0 - price_norm)) + (0.3 * rating_norm)

        ranked.append(
            {
                "product": product,
                "performance_score": round(performance_score, 3),
                "value_score": round(value_score, 3),
            }
        )

    ranked_by_performance = sorted(ranked, key=lambda r: r["performance_score"], reverse=True)
    ranked_by_value = sorted(ranked, key=lambda r: r["value_score"], reverse=True)

    best_perf_product = ranked_by_performance[0]["product"]
    best_value_product = ranked_by_value[0]["product"]

    return {
        "best_performance": _product_name(best_perf_product),
        "best_value": _product_name(best_value_product),
        "best_performance_product": best_perf_product,
        "best_value_product": best_value_product,
        "ranked": ranked,
    }


def compare(products: list[dict]) -> dict:
    return compare_products(products)

