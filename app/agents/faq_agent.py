import logging

from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.database.retrieval import (
    documents_to_context,
    recent_conversation,
    semantic_search,
)
from app.database.index_vector_stores import (
    get_policies_vector_store,
)
from app.state.smartshop_state import SmartShopState


logger = logging.getLogger(__name__)


def faq_agent(
    state: SmartShopState,
) -> dict:
    """
    Answer store-policy questions using semantic search.
    """

    query = state["query"]
    messages = state.get("messages", [])

    logger.info(
        "FAQ Agent started | query=%s",
        query[:100],
    )

    try:
        policies_vector_store = (
            get_policies_vector_store()
        )

        policies = semantic_search(
            policies_vector_store,
            query,
            k=2,
        )

    except Exception:
        logger.exception(
            "FAQ Agent vector search failed"
        )

        return {
            "faq_response":
                "I could not search store policies."
        }

    if not policies:
        return {
            "faq_response":
                "I could not find a matching store policy."
        }

    policy_context = documents_to_context(
        policies
    )

    conversation_context = recent_conversation(
        messages
    )

    prompt = f"""
You are the SmartShop Store Policy Agent.

Customer question:
{query}

Recent conversation:
{conversation_context}

Relevant store policies:
{policy_context}

Instructions:
- Answer using ONLY the policies provided.
- Do not invent information.
- If the policies do not answer the question, say so.
- Keep the answer short and clear.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    logger.info(
        "FAQ Agent completed successfully"
    )

    return {
        "faq_response": response.content
    }