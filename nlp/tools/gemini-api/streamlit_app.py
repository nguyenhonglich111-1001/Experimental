import streamlit as st
import os
from google import genai

st.set_page_config(page_title="Gemini API Chatbot", page_icon="🤖")
st.title("Gemini API Chatbot (NLP Tools)")

st.markdown("""
This is a minimal chatbot UI using the Gemini API via the official google-genai Python SDK.

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)

**Tip:** Set your API key as the environment variable `GEMINI_API_KEY` for best security.
""")

# --- API Key Input ---
def get_api_key():
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    return st.text_input("Enter your Gemini API Key", type="password")

api_key = get_api_key()

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Input ---
user_input = st.text_input("You:", key="user_input")

# --- Send Button ---
if st.button("Send") and user_input and api_key:
    st.session_state.chat_history.append(("user", user_input))
    try:    
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=user_input
        )
        model_reply = getattr(response, "text", "[No response]")
    except Exception as e:
        model_reply = f"[Error: {e}]"
    st.session_state.chat_history.append(("bot", model_reply))
    st.rerun()

# --- Display Chat ---
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Gemini:** {msg}")

st.markdown("---")
st.info("This is a minimal demo using the official google-genai SDK. For advanced features, see the Gemini API documentation.") 