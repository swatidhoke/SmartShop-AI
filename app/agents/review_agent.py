from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.data_loader import load_reviews
from app.state.smartshop_state import SmartShopState


def review_agent(state: SmartShopState) -> dict:
    """
    Summarize customer reviews using reviews.csv.
    """

    query = state["query"]

    reviews_df = load_reviews()

    review_data = reviews_df.to_csv(index=False)

    prompt = f"""
You are the Customer Review Agent for SmartShop AI.

Customer query:
{query}

Customer reviews:
{review_data}

Your responsibilities:
- Summarize relevant customer feedback.
- Identify common positive comments.
- Identify common negative comments.
- Mention ratings when available.
- Do not make up reviews.
- Give the customer a concise recommendation based on the reviews.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "review_response": response.content
    }