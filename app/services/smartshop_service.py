from langgraph.graph import END, START, StateGraph
from app.agents.faq_agent import faq_agent
from app.agents.price_agent import price_agent
from app.agents.product_agent import product_agent
from app.agents.review_agent import review_agent
from app.agents.router import route_query
from app.state.smartshop_state import SmartShopState

def dispatch_agents(state: SmartShopState) -> dict:
    """
    Execute only the agents selected by the router.
    """

    selected_agents = state.get(
        "selected_agents",
        []
    )

    updates = {}

    if "product_agent" in selected_agents:
        updates.update(product_agent(state))

    if "price_agent" in selected_agents:
        updates.update(price_agent(state))

    if "review_agent" in selected_agents:
        updates.update(review_agent(state))

    if "faq_agent" in selected_agents:
        updates.update(faq_agent(state))

    return updates


def combine_responses(state: SmartShopState) -> dict:
    """
    Combine responses from selected agents.
    """

    responses = []

    product_response = state.get("product_response")
    price_response = state.get("price_response")
    review_response = state.get("review_response")
    faq_response = state.get("faq_response")

    if product_response:
        responses.append(
            f"🛍️ Product Recommendations\n\n{product_response}"
        )

    if price_response:
        responses.append(
            f"💰 Price Analysis\n\n{price_response}"
        )

    if review_response:
        responses.append(
            f"⭐ Customer Reviews\n\n{review_response}"
        )

    if faq_response:
        responses.append(
            f"📋 Store Policy\n\n{faq_response}"
        )

    final_answer = "\n\n---\n\n".join(responses)

    if not final_answer:
        final_answer = (
            "Sorry, I could not find information "
            "to answer your question."
        )

    return {
        "final_answer": final_answer
    }


# ---------------------------------------------------
# Build LangGraph
# ---------------------------------------------------

workflow = StateGraph(SmartShopState)

workflow.add_node(
    "router",
    route_query,
)

workflow.add_node(
    "agents",
    dispatch_agents,
)

workflow.add_node(
    "combine",
    combine_responses,
)


# ---------------------------------------------------
# Edges
# ---------------------------------------------------

workflow.add_edge(
    START,
    "router",
)

workflow.add_edge(
    "router",
    "agents",
)

workflow.add_edge(
    "agents",
    "combine",
)

workflow.add_edge(
    "combine",
    END,
)

# Compile graph
smartshop_graph = workflow.compile()

def answer_customer_query(query: str):
    result = smartshop_graph.invoke(
        {
            "query": query
        }
    )

    return result