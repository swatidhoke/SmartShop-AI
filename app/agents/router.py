from typing import Any
from app.state.smartshop_state import SmartShopState


def route_query(state: Any) -> dict:
    """
    Determine which agents should handle the customer query.

    Accepts either a SmartShopState instance or a plain dict (which will be
    converted to SmartShopState). This keeps the router robust when invoked
    indirectly by frameworks that pass dict-like state objects.
    """

    if isinstance(state, dict):
        state = SmartShopState(**state)

    query = (state.query or "").lower()

    selected_agents: list[str] = []

    product_keywords = [
        "find",
        "recommend",
        "looking",
        "need",
        "product",
        "buy",
        "suggest",
    ]

    price_keywords = [
        "price",
        "compare",
        "cheaper",
        "cost",
        "under",
        "budget",
        "expensive",
    ]

    review_keywords = [
        "review",
        "reviews",
        "customer",
        "rating",
        "ratings",
        "think",
        "feedback",
    ]

    faq_keywords = [
        "return",
        "refund",
        "shipping",
        "policy",
        "exchange",
        "delivery",
        "warranty",
        "repair",
        "financing",
        "finance",
        "preorder",
        "price match",
    ]

    if any(word in query for word in product_keywords):
        selected_agents.append("product_agent")

    if any(word in query for word in price_keywords):
        selected_agents.append("price_agent")

    if any(word in query for word in review_keywords):
        selected_agents.append("review_agent")

    if any(word in query for word in faq_keywords):
        selected_agents.append("faq_agent")

    # Default
    if not selected_agents:
        selected_agents.append("product_agent")

    return {
        "selected_agents": selected_agents
    }