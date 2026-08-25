from typing import Any
from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.db import get_connection
from app.state.smartshop_state import SmartShopState


def product_agent(state: Any) -> dict:

    # Accept either a SmartShopState instance or a plain dict.
    if isinstance(state, dict):
        state = SmartShopState(**state)

    print("🛍️ Product Agent received state:", state)

    query = state.query or ""

    # Read products from PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, name, brand, category,
                       price, description, stock, rating
                FROM products
                LIMIT 50
                """
            )

            products = cursor.fetchall()

    if not products:
        return {
            "product_response": "No products were found."
        }

    # Send database results to LLM
    prompt = f"""
You are the Product Recommendation Agent for SmartShop AI.

Customer question:
{query}

Products from PostgreSQL:
{products}

Instructions:
- Recommend only products from the data above.
- Do not invent products.
- Recommend the most relevant products.
- Mention product name, brand, category and price.
- Consider rating and stock when useful.
- Keep the answer short and customer friendly.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "product_response": response.content
    }