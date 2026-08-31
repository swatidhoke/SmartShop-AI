import logging

from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.retrieval import (
    documents_to_context,
    recent_conversation,
    semantic_search,
)
from app.database.index_vector_stores import (
    get_reviews_vector_store,
)
from app.state.smartshop_state import SmartShopState


logger = logging.getLogger(__name__)


def review_agent(
    state: SmartShopState,
) -> dict:
    """
    Summarize relevant customer reviews and sentiment.
    """

    query = state["query"]
    messages = state.get("messages", [])

    logger.info(
        "Review Agent started | query=%s",
        query[:100],
    )

    try:
        reviews_vector_store = (
            get_reviews_vector_store()
        )

        reviews = semantic_search(
            reviews_vector_store,
            query,
            k=8,
        )

    except Exception:
        logger.exception(
            "Review Agent vector search failed"
        )

        return {
            "review_response":
                "I could not search customer reviews."
        }

    if not reviews:
        logger.warning(
            "Review Agent found no reviews"
        )

        return {
            "review_response":
                "I could not find relevant customer reviews."
        }

    review_context = documents_to_context(
        reviews
    )

    conversation_context = recent_conversation(
        messages
    )

    prompt = f"""
You are the Customer Review Agent for SmartShop AI.

Customer question:
{query}

Recent conversation:
{conversation_context}

Relevant customer reviews:
{review_context}

Instructions:
- Use ONLY the reviews provided.
- Summarize overall sentiment.
- Mention common positive themes.
- Mention common negative themes.
- Do not invent customer opinions.
- Do not treat one review as representing everyone.
- Keep the response concise.
"""

    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        logger.info(
            "Review Agent completed successfully"
        )

        return {
            "review_response": response.content
        }

    except Exception:
        logger.exception(
            "Review Agent LLM call failed"
        )

        return {
            "review_response":
                "I found customer reviews but could not summarize them."
        }