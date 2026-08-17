from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.data_loader import load_products
from app.state.smartshop_state import SmartShopState

def product_agent(state: SmartShopState) -> dict:
    """
    Product agent recommends products using products.csv.
    """

    query = state["query"]

    products_df = load_products()

    product_data = products_df.to_csv(index=False)

    prompt = f"""
You are the Product Recommendation Agent for SmartShop AI.

Your responsibility is to recommend products using ONLY the provided
product catalog.

Customer query:
{query}

Product catalog:
{product_data}

Instructions:
- Recommend the most relevant products.
- Do not invent products.
- Use information available in the product catalog.
- Give a short explanation for each recommendation.
- Mention product name, category, brand and price when available.
- Return a concise customer-friendly response.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "product_response": response.content
    }