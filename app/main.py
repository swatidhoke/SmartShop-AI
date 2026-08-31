from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.memory.conversation_memory import (
    close_conversation_memory,
    setup_conversation_memory,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_conversation_memory()

    yield

    close_conversation_memory()


app = FastAPI(
    title="SmartShop AI",
    lifespan=lifespan,
)


app.include_router(
    chat_router
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }