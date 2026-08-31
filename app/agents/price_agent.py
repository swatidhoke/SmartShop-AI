import logging

from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.db import get_connection
from app.database.retrieval import recent_conversation
from app.state.smartshop_state import SmartShopState


logger = logging.getLogger(__name__)


def price_agent(
    state: SmartShopState,
) -> dict:
    """
    Compare product prices using structured PostgreSQL data.
    """

    query = state["query"]
    messages = state.get("messages", [])

    logger.info(
        "Price Agent started | query=%s",
        query[:100],
    )

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        brand,
                        category,
                        price,
                        rating,
                        stock
                    FROM products
                    WHERE stock > 0
                    ORDER BY price ASC
                    """
                )

                products = cursor.fetchall()

    except Exception:
        logger.exception(
            "Price Agent database query failed"
        )

        return {
            "price_response":
                "I could not retrieve current product prices."
        }

    if not products:
        logger.warning(
            "Price Agent found no products"
        )

        return {
            "price_response":
                "No products are currently available for comparison."
        }

    conversation_context = recent_conversation(
        messages
    )

    prompt = f"""
You are the Price Comparison Agent for SmartShop AI.

Customer question:
{query}

Recent conversation:
{conversation_context}

Available products:
{products}

Instructions:
- Compare only the products shown above.
- Use the exact prices provided.
- Respect the customer's budget.
- Identify cheaper alternatives when appropriate.
- Consider rating when discussing value.
- Do not invent prices or products.
- Keep the response concise.
"""

    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        logger.info(
            "Price Agent completed successfully"
        )

        return {
            "price_response": response.content
        }

    except Exception:
        logger.exception(
            "Price Agent LLM call failed"
        )

        return {
            "price_response":
                "I retrieved the prices but could not generate a comparison."
        }