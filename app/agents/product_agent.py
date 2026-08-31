import logging

from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.retrieval import (
    documents_to_context,
    recent_conversation,
    semantic_search,
)
from app.database.index_vector_stores import (
    get_products_vector_store,
)
from app.state.smartshop_state import SmartShopState


logger = logging.getLogger(__name__)


def product_agent(
    state: SmartShopState,
) -> dict:
    """
    Recommend products using semantic product search.
    """

    query = state["query"]
    messages = state.get("messages", [])

    logger.info(
        "Product Agent started | query=%s",
        query[:100],
    )

    try:
        products_vector_store = (
            get_products_vector_store()
        )

        products = semantic_search(
            products_vector_store,
            query,
            k=5,
        )

    except Exception:
        logger.exception(
            "Product Agent vector search failed"
        )

        return {
            "product_response":
                "I could not search the product catalog."
        }

    if not products:
        logger.warning(
            "Product Agent found no products"
        )

        return {
            "product_response":
                "I could not find a matching product."
        }

    product_context = documents_to_context(
        products
    )

    conversation_context = recent_conversation(
        messages
    )

    prompt = f"""
You are the Product Recommendation Agent for SmartShop AI.

Customer question:
{query}

Recent conversation:
{conversation_context}

Relevant products:
{product_context}

Instructions:
- Recommend only products shown above.
- Do not invent products, prices, ratings, or features.
- Explain briefly why each recommendation fits.
- Respect requirements mentioned earlier in the conversation.
- Keep the response clear and concise.
"""

    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        logger.info(
            "Product Agent completed successfully"
        )

        return {
            "product_response": response.content
        }

    except Exception:
        logger.exception(
            "Product Agent LLM call failed"
        )

        return {
            "product_response":
                "I found matching products but could not generate a recommendation."
        }