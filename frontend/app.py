import streamlit as st
import requests
import os
from dotenv import load_dotenv


load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Board Game Rules Chatbot", page_icon="🎲")
st.title("🎲 Board Game Rules Retriever")
st.markdown("Ask any rule-related question about a Stonemaier board game.")


# Chat history stored in session state if available
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["content"])

# Input box
if question := st.chat_input("Ask a question about a game rule..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Send to FastAPI backend
    try:
        response = requests.post(
            BACKEND_URL + "/ask", json={"question": question, "k": 8}, timeout=10
        )
        response.raise_for_status()
        answer = response.json().get("answer", "No response from model.")
    except Exception as e:
        answer = f"❌ Error: {e}"

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
