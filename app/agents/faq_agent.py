from langchain_core.messages import HumanMessage

from app.config.config import llm
from app.data_loader import load_store_policies
from app.state.smartshop_state import SmartShopState

def faq_agent(state: SmartShopState) -> dict:
    """
    Answer store policy questions using store_policies.csv.
    """

    query = state["query"]

    policies_df = load_store_policies()

    policy_data = policies_df.to_csv(index=False)

    prompt = f"""
You are the Store Policy and FAQ Agent for SmartShop AI.

Customer query:
{query}

Store policies:
{policy_data}

Instructions:
- Answer using ONLY the supplied store policies.
- Do not invent a policy.
- If the requested information is unavailable, say that the store
  policy data does not contain the requested information.
- Keep the response short and customer friendly.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "faq_response": response.content
    }