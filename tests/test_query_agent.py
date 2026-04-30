from app.agents.query_agent import run
from app.state.global_state import GLOBAL_STATE
from app.tools.query_parser_tool import parse_user_query


def test_query_agent_returns_dict():
    GLOBAL_STATE.clear()
    out = run("hello")
    assert isinstance(out, dict)


def test_happy_path_laptop_under_budget_with_preferences():
    parsed = parse_user_query("I need a laptop under 200000 for coding with SSD and good battery life")
    assert parsed["category"] == "laptop"
    assert parsed["budget"] == 200000
    assert "coding" in parsed["preferences"]
    assert "ssd" in parsed["preferences"]
    assert "good battery" in parsed["preferences"]
    assert parsed["use_case"] == "coding"
    assert "ssd" in parsed["must_have_features"]
    assert "good battery" in parsed["nice_to_have_features"]
    assert "category" not in parsed["missing_fields"]
    assert "budget" not in parsed["missing_fields"]


def test_missing_budget_is_not_invented():
    parsed = parse_user_query("I need a good phone for photography")
    assert parsed["category"] == "phone"
    assert parsed["budget"] is None
    assert "budget" in parsed["missing_fields"]


def test_missing_category_is_not_invented():
    parsed = parse_user_query("I need something under 100000 with long battery life")
    assert parsed["category"] is None
    assert parsed["budget"] == 100000
    assert "category" in parsed["missing_fields"]


def test_synonym_notebook_maps_to_laptop_and_programming_to_coding():
    parsed = parse_user_query("Looking for a notebook for programming below 180k")
    assert parsed["category"] == "laptop"
    assert parsed["budget"] == 180000
    assert "coding" in parsed["preferences"]


def test_currency_handling_lkr():
    parsed = parse_user_query("Need a laptop under LKR 250000")
    assert parsed["budget"] == 250000
    assert parsed["currency"] == "LKR"


def test_currency_handling_usd_symbol():
    parsed = parse_user_query("best phone under $500 with good camera")
    assert parsed["budget"] == 500
    assert parsed["currency"] == "USD"
    assert parsed["sort_preference"] == "best_value"


def test_sort_preference_best_camera():
    parsed = parse_user_query("best camera phone under $500")
    assert parsed["category"] == "phone"
    assert parsed["budget"] == 500
    assert parsed["sort_preference"] == "best_camera"


def test_empty_query_is_safe():
    parsed = parse_user_query("")
    assert parsed["category"] is None
    assert parsed["budget"] is None
    assert parsed["confidence"] == 0.0
    assert "empty_query" in parsed["warnings"]
    assert "category" in parsed["missing_fields"]
    assert "budget" in parsed["missing_fields"]


def test_noise_handling_still_extracts_key_fields():
    parsed = parse_user_query("uhh hi can you maybe find me like a laptop sort of around 200k for dev work")
    assert parsed["category"] == "laptop"
    assert parsed["budget"] == 200000
    assert "coding" in parsed["preferences"]


def test_budget_range_sets_max_budget_and_flags_min_detected():
    parsed = parse_user_query("Need a laptop between 100k and 200k for coding")
    assert parsed["category"] == "laptop"
    assert parsed["budget"] == 200000
    assert "budget_min_detected" in parsed["warnings"]


def test_ambiguous_language_does_not_invent_category_or_budget():
    parsed = parse_user_query("Need a decent one for uni work, not too expensive")
    assert parsed["category"] is None
    assert parsed["budget"] is None
    assert "student" in parsed["preferences"]
    assert "affordable" in parsed["preferences"]


def test_use_case_extraction_studies_is_safe():
    parsed = parse_user_query("I need something good for studies")
    assert parsed["category"] is None
    assert parsed["budget"] is None
    assert parsed["use_case"] == "studies"
    assert "studies" in parsed["preferences"]
    assert "category" in parsed["missing_fields"]
    assert "budget" in parsed["missing_fields"]


def test_multiple_categories_are_flagged_and_first_supported_is_chosen():
    parsed = parse_user_query("Need a phone or laptop under 200000")
    assert parsed["category"] in {"laptop", "phone"}
    assert parsed["budget"] == 200000
    assert any(w.startswith("multiple_categories:") for w in parsed["warnings"])
