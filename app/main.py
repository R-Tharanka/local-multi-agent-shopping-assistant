from __future__ import annotations

import argparse
import json

from app.crew.workflow import run_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Local multi-agent shopping assistant (scaffold).")
    parser.add_argument(
        "-q",
        "--query",
        help='Shopping query text (example: "best phone under $500 with good camera").',
    )
    parser.add_argument(
        "query_parts",
        nargs="*",
        help="Shopping query text (positional). If provided, overrides prompting.",
    )
    args = parser.parse_args()

    query = args.query
    if not query and args.query_parts:
        query = " ".join(args.query_parts).strip()

    if not query:
        try:
            query = input("Enter your shopping query: ").strip()
        except EOFError:
            query = ""

    state = run_workflow(query or "example: best phone under $500")
    recommendations = state.get("recommendations")
    if isinstance(recommendations, dict):
        final_text = recommendations.get("final_recommendation")
        if isinstance(final_text, str):
            recommendations["final_recommendation"] = final_text.replace("\n", " ")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
