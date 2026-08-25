from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

"""
Pydantic model representing the state passed through the SmartShop workflow.

Using a BaseModel improves validation and IDE experience while keeping the
runtime representation explicit. Fields are optional to reflect that different
workflow steps add different pieces of information.
"""

AgentName = Literal["product_agent", "price_agent", "review_agent", "faq_agent"]

class SmartShopState(BaseModel):
    query: Optional[str] = None
    # Agents selected by the router; typed to the known agent names for clarity.
    selected_agents: List[AgentName] = Field(default_factory=list)
    product_response: Optional[str] = None
    price_response: Optional[str] = None
    review_response: Optional[str] = None
    faq_response: Optional[str] = None
    final_answer: Optional[str] = None

    # Optional chat/message history (LLM messages).
    messages: Optional[List[BaseMessage]] = None
    class Config:
        # Allow non-pydantic types (e.g., BaseMessage) in fields.
        arbitrary_types_allowed = True
