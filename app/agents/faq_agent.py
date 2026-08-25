from typing import Any
from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.db import get_connection
from app.state.smartshop_state import SmartShopState


def faq_agent(state: Any) -> dict:

    # Accept dict or SmartShopState
    if isinstance(state, dict):
        state = SmartShopState(**state)

    print("🔍 FAQ Agent received state:", state)

    query = (state.query or "").lower()

    # Decide policy type
    if "return" in query or "refund" in query:
        policy_type = "returns"

    elif "warranty" in query:
        policy_type = "warranty"

    elif "shipping" in query or "delivery" in query:
        policy_type = "shipping"

    elif "exchange" in query:
        policy_type = "exchanges"

    else:
        return {
            "faq_response": "I could not find a matching store policy."
        }

    # Read from PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT description, conditions, timeframe
                FROM store_policies
                WHERE policy_type = %s
                """,
                (policy_type,)
            )

            policies = cursor.fetchall()

    # No database result
    if not policies:
        return {
            "faq_response": "No matching policy was found."
        }

    # Send database results to LLM
    prompt = f"""
You are the SmartShop FAQ Agent.

Customer question:
{query}

Store policies:
{policies}

Answer using ONLY these policies.
Do not invent information.
Keep the answer short and clear.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "faq_response": response.content
    }