from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.smartshop_service import (
    answer_customer_query,
)
from app.state.smartshop_state import AgentName
router = APIRouter(
    tags=["chat"]
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
    )

    thread_id: str = Field(
        ...,
        min_length=1,
    )


class ChatResponse(BaseModel):
    thread_id: str
    selected_agents: list[AgentName]
    final_answer: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:

    result = answer_customer_query(
        query=request.message,
        thread_id=request.thread_id,
    )

    return ChatResponse(
        thread_id=request.thread_id,
        selected_agents=result.get(
            "selected_agents",
            [],
        ),
        final_answer=result.get(
            "final_answer",
            "",
        ),
    )