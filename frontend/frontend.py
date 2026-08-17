print("Starting SmartShop AI frontend...")
import streamlit as st
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from app.services.smartshop_service import answer_customer_query

st.set_page_config(
    page_title="SmartShop AI",
    page_icon="🛍️",
    layout="centered",
)


st.title("🛍️ SmartShop AI")

st.caption(
    "Your AI-powered shopping assistant"
)


# --------------------------------------------------
# Initialize chat history
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Display existing messages
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# User input
# --------------------------------------------------

query = st.chat_input(
    "Ask me about products, prices, reviews or store policies..."
)

if query:
    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # --------------------------------------------------
    # SmartShop Agent
    # --------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "SmartShop agents are working..."
        ):

            try:

                result = answer_customer_query(query)

                answer = result.get(
                    "final_answer",
                    "Unable to generate an answer.",
                )

                st.markdown(answer)

            except Exception as exc:

                answer = (
                    f"Something went wrong: {exc}"
                )

                st.error(answer)

    # Store assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )