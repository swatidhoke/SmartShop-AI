import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def get_llm() -> ChatOpenAI:
    """
    Create and return the LLM used by SmartShop agents.
    """

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )

llm = get_llm()