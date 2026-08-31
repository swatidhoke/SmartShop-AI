import logging

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.vectorstores import VectorStore

logger = logging.getLogger(__name__)

def semantic_search(
    vector_store: VectorStore,
    query: str,
    *,
    k: int = 5,
) -> list[Document]:
    """
    Find documents that are semantically similar to a query.
    """

    logger.info(
        "Semantic search started | query=%s | k=%s",
        query[:100],
        k,
    )

    documents = vector_store.similarity_search(
        query,
        k=k,
    )

    logger.info(
        "Semantic search completed | matches=%s",
        len(documents),
    )

    return documents


def documents_to_context(
    documents: list[Document],
) -> str:
    """
    Convert retrieved documents into text for an LLM prompt.
    """

    return "\n\n".join(
        document.page_content
        for document in documents
    )


def recent_conversation(
    messages: list[BaseMessage],
    *,
    limit: int = 6,
) -> str:
    """
    Format a small amount of recent conversation history
    for an agent prompt.
    """

    recent_messages = messages[-limit:]

    conversation = []

    for message in recent_messages:
        role = message.type
        content = str(message.content)

        conversation.append(
            f"{role}: {content}"
        )

    return "\n".join(conversation)