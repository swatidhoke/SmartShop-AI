import os
import uuid

import requests
import streamlit as st


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="SmartShop AI",
    page_icon="🛍️",
    layout="wide",
)


# ---------------------------------------------------------
# Backend API
# ---------------------------------------------------------

API_URL = os.getenv(
    "SMARTSHOP_API_URL",
    "http://127.0.0.1:8001/chat",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_status" not in st.session_state:
    st.session_state.api_status = "Not checked"


# ---------------------------------------------------------
# Agent labels
# ---------------------------------------------------------

AGENT_LABELS = {
    "product_agent": "🛍️ Product Agent",
    "price_agent": "💰 Price Agent",
    "review_agent": "⭐ Review Agent",
    "faq_agent": "📦 Policy Agent",
}


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def reset_conversation():
    """Start a fresh LangGraph conversation."""

    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.api_status = "Not checked"


def call_api(message):
    """Send the customer question to FastAPI."""

    payload = {
        "message": message,
        "thread_id": st.session_state.thread_id,
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=90,
    )

    response.raise_for_status()

    return response.json()


def show_agents(selected_agents):
    """Show which agents handled the request."""

    if not selected_agents:
        return

    labels = [
        AGENT_LABELS.get(agent, agent)
        for agent in selected_agents
    ]

    st.caption(
        "Agents used: " + "  •  ".join(labels)
    )


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.title("🛍️ SmartShop AI")

    st.caption("Multi-agent shopping assistant")

    st.divider()

    st.subheader("AI Specialists")

    st.write("🛍️ Product Agent")
    st.caption("Finds products based on your needs.")

    st.write("💰 Price Agent")
    st.caption("Compares prices and budgets.")

    st.write("⭐ Review Agent")
    st.caption("Summarizes customer reviews.")

    st.write("📦 Policy Agent")
    st.caption("Answers return, shipping and warranty questions.")

    st.divider()

    st.subheader("API Status")

    if st.session_state.api_status == "Connected":
        st.success("Connected")
    elif st.session_state.api_status == "Disconnected":
        st.error("Disconnected")
    else:
        st.info("Not checked")

    st.divider()

    st.caption(
        f"Thread: {st.session_state.thread_id[:8]}..."
    )

    st.caption(
        f"Messages: {len(st.session_state.messages)}"
    )

    if st.button(
        "New conversation",
        use_container_width=True,
    ):
        reset_conversation()
        st.rerun()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🛍️ SmartShop AI")

st.write(
    "Your intelligent shopping assistant for products, "
    "prices, customer reviews, and store policies."
)


# ---------------------------------------------------------
# Example prompts
# ---------------------------------------------------------

if not st.session_state.messages:

    st.subheader("Try an example")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "💻 Laptop under $2,000",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Recommend a laptop under $2,000"
            )
            st.rerun()

    with col2:
        if st.button(
            "⭐ Best reviewed laptop",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Which laptops have the best customer reviews?"
            )
            st.rerun()

    with col3:
        if st.button(
            "🤖 Multi-agent search",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Recommend a laptop under $2,000 "
                "with good customer reviews"
            )
            st.rerun()

    with col4:
        if st.button(
            "📦 Return policy",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Can I return a product if I change my mind?"
            )
            st.rerun()


# ---------------------------------------------------------
# Show conversation history
# ---------------------------------------------------------

for message in st.session_state.messages:

    role = message["role"]

    avatar = "🧑" if role == "user" else "🛍️"

    with st.chat_message(
        role,
        avatar=avatar,
    ):

        st.markdown(
            message["content"]
        )

        if role == "assistant":
            show_agents(
                message.get("agents", [])
            )


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

typed_prompt = st.chat_input(
    "Ask about products, prices, reviews, or policies..."
)

pending_prompt = st.session_state.pop(
    "pending_prompt",
    None,
)

prompt = typed_prompt or pending_prompt


# ---------------------------------------------------------
# Process request
# ---------------------------------------------------------

if prompt:

    prompt = prompt.strip()

    if prompt:

        # Save and show user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message(
            "user",
            avatar="🧑",
        ):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message(
            "assistant",
            avatar="🛍️",
        ):

            with st.spinner(
                "SmartShop agents are working..."
            ):

                try:
                    result = call_api(prompt)

                    selected_agents = result.get(
                        "selected_agents",
                        [],
                    )

                    final_answer = result.get(
                        "final_answer",
                        "",
                    )

                    st.session_state.api_status = (
                        "Connected"
                    )

                except requests.exceptions.ConnectionError:
                    st.session_state.api_status = (
                        "Disconnected"
                    )

                    st.error(
                        "Could not connect to FastAPI. "
                        "Make sure the backend is running."
                    )

                    st.stop()

                except requests.exceptions.Timeout:
                    st.error(
                        "The request took too long."
                    )

                    st.stop()

                except requests.exceptions.HTTPError as error:
                    st.error(
                        f"FastAPI returned an error: {error}"
                    )

                    st.stop()

                except Exception as error:
                    st.error(
                        f"Something went wrong: {error}"
                    )

                    st.stop()

            show_agents(selected_agents)

            if final_answer:
                st.markdown(final_answer)
            else:
                final_answer = (
                    "I could not generate an answer "
                    "for that request."
                )

                st.warning(final_answer)

        # Save assistant message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_answer,
                "agents": selected_agents,
            }
        )
