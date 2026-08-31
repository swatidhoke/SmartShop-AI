import logging

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.agents.faq_agent import faq_agent
from app.agents.price_agent import price_agent
from app.agents.product_agent import product_agent
from app.agents.review_agent import review_agent
from app.memory.conversation_memory import (
    conversation_checkpointer,
)
from app.state.smartshop_state import SmartShopState
logger = logging.getLogger(__name__)

AGENT_HANDLERS = {
    "product_agent": product_agent,
    "price_agent": price_agent,
    "review_agent": review_agent,
    "faq_agent": faq_agent,
}


def prepare_turn(
    state: SmartShopState,
) -> dict:
    """Reset data that belongs only to one user turn."""

    return {
        "selected_agents": [],
        "product_response": "",
        "price_response": "",
        "review_response": "",
        "faq_response": "",
        "final_answer": "",
    }


def route_query(
    state: SmartShopState,
) -> dict:
    query = state["query"].lower()

    selected_agents = []

    if any(
        word in query
        for word in [
            "find",
            "recommend",
            "looking",
            "product",
        ]
    ):
        selected_agents.append("product_agent")

    if any(
        word in query
        for word in [
            "price",
            "cost",
            "cheap",
            "budget",
            "under",
        ]
    ):
        selected_agents.append("price_agent")

    if any(
        word in query
        for word in [
            "review",
            "rating",
            "feedback",
            "customer",
        ]
    ):
        selected_agents.append("review_agent")

    if any(
        word in query
        for word in [
            "return",
            "refund",
            "shipping",
            "delivery",
            "warranty",
            "exchange",
        ]
    ):
        selected_agents.append("faq_agent")

    if not selected_agents:
        selected_agents.append(
            "product_agent"
        )

    logger.info(
        "Router selected agents: %s",
        selected_agents,
    )

    return {
        "selected_agents": selected_agents
    }


def dispatch_agents(
    state: SmartShopState,
) -> dict:
    """
    Run each agent selected by the router.
    """

    updates = {}

    for agent_name in state.get(
        "selected_agents",
        [],
    ):
        agent = AGENT_HANDLERS.get(agent_name)

        if not agent:
            logger.warning(
                "Unknown agent selected: %s",
                agent_name,
            )
            continue

        logger.info(
            "Running agent: %s",
            agent_name,
        )

        result = agent(state)

        updates.update(result)

    return updates


def create_final_answer(
    state: SmartShopState,
) -> dict:
    """
    Combine the selected agent responses.
    """

    responses = []

    for agent_name in state.get(
        "selected_agents",
        [],
    ):

        if (
            agent_name == "product_agent"
            and state.get("product_response")
        ):
            responses.append(
                state["product_response"]
            )

        elif (
            agent_name == "price_agent"
            and state.get("price_response")
        ):
            responses.append(
                state["price_response"]
            )

        elif (
            agent_name == "review_agent"
            and state.get("review_response")
        ):
            responses.append(
                state["review_response"]
            )

        elif (
            agent_name == "faq_agent"
            and state.get("faq_response")
        ):
            responses.append(
                state["faq_response"]
            )

    final_answer = "\n\n".join(responses)

    if not final_answer:
        final_answer = (
            "I could not find an answer for that request."
        )

    logger.info(
        "Final SmartShop response created"
    )

    return {
        "final_answer": final_answer,

        # This is what becomes part of
        # persistent conversation history.
        "messages": [
            AIMessage(
                content=final_answer
            )
        ],
    }


builder = StateGraph(SmartShopState)

builder.add_node(
    "prepare_turn",
    prepare_turn,
)

builder.add_node(
    "router",
    route_query,
)

builder.add_node(
    "agents",
    dispatch_agents,
)

builder.add_node(
    "finalize",
    create_final_answer,
)


builder.add_edge(
    START,
    "prepare_turn",
)

builder.add_edge(
    "prepare_turn",
    "router",
)

builder.add_edge(
    "router",
    "agents",
)

builder.add_edge(
    "agents",
    "finalize",
)

builder.add_edge(
    "finalize",
    END,
)


smartshop_graph = builder.compile(
    checkpointer=conversation_checkpointer
)


def answer_customer_query(
    query: str,
    thread_id: str,
) -> dict:
    """
    Run one customer turn.

    The same thread_id must be reused to retain history.
    """

    logger.info(
        "Customer query received | thread=%s",
        thread_id,
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return smartshop_graph.invoke(
        {
            "query": query,

            "messages": [
                HumanMessage(
                    content=query
                )
            ],
        },
        config=config,
    )