from typing import Annotated, Literal, Required, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

AgentName = Literal[
    "product_agent",
    "price_agent",
    "review_agent",
    "faq_agent",
]

class SmartShopState(TypedDict, total=False):
    """Shared state passed between SmartShop AI agents."""

    # User request
    query: Required[str]

    # Conversation history
    messages: Annotated[list[BaseMessage], add_messages]

    # Router decision
    selected_agents: list[AgentName]

    # Individual agent outputs
    product_response: str
    price_response: str
    review_response: str
    faq_response: str

    # Combined response to the customer
    final_answer: str