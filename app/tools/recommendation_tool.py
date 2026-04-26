from typing import Dict

def generate_recommendation_report(comparison_result: Dict) -> str:
    """
    Generate a final recommendation message based on comparison results.
    """

    print("[Recommendation Tool] Processing recommendation...")

    try:
        best_perf = comparison_result.get("best_performance")
        best_value = comparison_result.get("best_value")
        budget = comparison_result.get("budget")
        user_need = comparison_result.get("user_need", "general use")

        if not best_perf:
            return "No suitable products found for your requirements."

        message = f"{best_perf} is the best choice for your needs."

        if user_need:
            message += f" It is ideal for {user_need}."

        if budget:
            message += f" It fits within your budget of Rs. {budget}."

        if best_value and best_value != best_perf:
            message += f" Alternatively, {best_value} is a more budget-friendly option."

        return message

    except Exception as e:
        return f"Error generating recommendation: {str(e)}"