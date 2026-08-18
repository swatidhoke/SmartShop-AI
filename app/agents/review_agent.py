from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.db import get_connection
from app.state.smartshop_state import SmartShopState


def review_agent(state: SmartShopState) -> dict:

    print("📝 Review Agent received state:", state)

    query = state["query"]

    # Read reviews from PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT product_id, rating, text, date
                FROM reviews
                LIMIT 50
                """
            )

            reviews = cursor.fetchall()

    # No reviews found
    if not reviews:
        return {
            "review_response": "No customer reviews were found."
        }

    # Send database results to LLM
    prompt = f"""
You are the Customer Review Agent for SmartShop AI.

Customer question:
{query}

Customer reviews from PostgreSQL:
{reviews}

Instructions:
- Use ONLY the reviews provided above.
- Summarize relevant customer feedback.
- Mention positive comments.
- Mention negative comments.
- Mention ratings when available.
- Do not make up reviews.
- Keep the answer short and clear.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "review_response": response.content
    }