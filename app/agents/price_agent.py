from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.data_loader import load_products
from app.state.smartshop_state import SmartShopState

def price_agent(state: SmartShopState) -> dict:
    """
    Compare product prices using products.csv.
    """

    query = state["query"]

    products_df = load_products()

    product_data = products_df.to_csv(index=False)

    prompt = f"""
You are the Price Comparison Agent for SmartShop AI.

Customer query:
{query}

Available products:
{product_data}

Your responsibilities:
- Compare relevant product prices.
- Respect the customer's budget when provided.
- Identify cheaper and more expensive alternatives.
- Do not invent prices.
- Only use the supplied product data.
- Clearly explain which product offers better value.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "price_response": response.content
    }