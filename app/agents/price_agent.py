from typing import Any
from langchain_core.messages import HumanMessage
from app.config.config import llm
from app.database.db import get_connection
from app.state.smartshop_state import SmartShopState

def price_agent(state: Any) -> dict:

    # Accept dict or SmartShopState
    if isinstance(state, dict):
        state = SmartShopState(**state)

    print("💰 Price Agent received state:", state)

    query = state.query or ""

    # Read products from PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, name, brand, category,
                       price, stock, rating
                FROM products
                LIMIT 50
                """
            )

            products = cursor.fetchall()

    if not products:
        return {
            "price_response": "No product pricing information was found."
        }

    # Send database results to LLM
    prompt = f"""
You are the Price Comparison Agent for SmartShop AI.

Customer question:
{query}

Available products from PostgreSQL:
{products}

Instructions:
- Compare only products from the data above.
- Respect the customer's budget when provided.
- Identify cheaper and more expensive options.
- Do not invent prices.
- Mention product name, brand and price.
- Explain which product offers better value.
- Keep the response short and clear.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "price_response": response.content
    }