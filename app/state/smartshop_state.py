from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SmartShopState(TypedDict, total=False):
    query: str
    selected_agents: list[str]

    product_response: str
    price_response: str
    review_response: str
    faq_response: str

    final_answer: str