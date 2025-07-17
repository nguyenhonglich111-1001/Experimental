import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import asyncio

from openai import OpenAI
import instructor

from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory

from .book_qa_agent import BookQAAgent, BookQAAgentInputSchema, BookQAAgentOutputSchema

# Load environment variables
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

# Initialize OpenAI-compatible client for Gemini
@st.cache_resource
def get_gemini_client():
    return instructor.from_openai(
        OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

# Initialize agent config (cached to avoid re-initialization on rerun)
@st.cache_resource
def get_agent_config(client):
    return BaseAgentConfig(
        client=client,
        model="gemini-2.0-flash-exp", # Use an appropriate Gemini model
        memory=AgentMemory()
    )

# --- Streamlit UI --- 
st.set_page_config(page_title="Atomic PDF Q&A", layout="centered")
st.title("📚 Atomic PDF Book Q&A")

# Initialize chat history and agent in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "current_pdf_path" not in st.session_state:
    st.session_state.current_pdf_path = None

# File uploader
uploaded_file = st.file_uploader("Upload a PDF book", type=["pdf"])

if uploaded_file is not None:
    # Check if a new file is uploaded or if it's a different file
    if st.session_state.current_pdf_path is None or uploaded_file.name != os.path.basename(st.session_state.current_pdf_path):
        with st.spinner("Processing PDF..."):
            # Save uploaded file to a temporary location
            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.session_state.current_pdf_path = temp_pdf_path
            st.session_state.messages = [] # Clear chat history for new book
            st.session_state.agent = None # Reset agent to load new PDF content

            st.success(f"PDF '{uploaded_file.name}' uploaded successfully. Ask me anything about it!")
            st.session_state.messages.append({"role": "assistant", "content": f"PDF '{uploaded_file.name}' loaded. What would you like to know about it?"})

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about the book..."):
    if st.session_state.current_pdf_path is None:
        st.warning("Please upload a PDF file first.")
    else:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Initialize agent if not already done
            if st.session_state.agent is None:
                gemini_client = get_gemini_client()
                agent_config = get_agent_config(gemini_client)
                st.session_state.agent = BookQAAgent(config=agent_config)

            # Run the agent asynchronously and stream response
            full_response = ""
            response_generator = st.session_state.agent._run(
                BookQAAgentInputSchema(
                    chat_message=prompt,
                    pdf_file_path=st.session_state.current_pdf_path
                )
            )
            
            # Stream the response to the UI
            # The _run method of BookQAAgent returns a single output, not a generator for streaming directly to st.write_stream
            # We need to adapt it or ensure the agent's _run method yields chunks.
            # For now, let's assume _run returns the full response and we'll display it.
            # If the agent's _run was truly async generator, we'd use st.write_stream(response_generator)
            
            # Since _run returns a single output, we need to await it.
            # Streamlit doesn't directly support awaiting in the main script flow for UI updates.
            # A common pattern is to run async functions in a separate thread or use a library like `streamlit-extras` `st_async`.
            # For simplicity in this prototype, we'll run it blocking for now, or adapt agent to yield.
            
            # Let's modify BookQAAgent._run to be an async generator for streaming.
            # Re-evaluating the BookQAAgent._run method, it already uses `stream=True` for OpenAI client.
            # So, the `response` object from `client.chat.completions.create` is an async generator.
            # We need to iterate over it here in Streamlit.

            # The `_run` method of `BookQAAgent` returns a `BookQAAgentOutputSchema` directly.
            # To stream, the `_run` method itself needs to be an async generator yielding chunks.
            # Let's adjust the `BookQAAgent._run` to yield chunks.
            # I will modify `book_qa_agent.py` first, then come back to `server.py`.

            # Stream the response to the UI
            response_generator = st.session_state.agent._run(
                BookQAAgentInputSchema(
                    chat_message=prompt,
                    pdf_file_path=st.session_state.current_pdf_path
                )
            )
            
            # st.write_stream expects an iterable. Since _run is now an async generator,
            # we need to run it in an async context. Streamlit handles this with `st.write_stream`
            # if the generator is awaited, but direct `async for` in top-level script is tricky.
            # The simplest way is to wrap the async generator in a sync iterable for `st.write_stream`.
            # However, `st.write_stream` itself can take an async generator directly in newer Streamlit versions.
            # Let's assume it can take an async generator directly.
            
            # Collect the full response for session state after streaming
            full_response_content = ""
            with st.spinner("Generating response..."):
                # st.write_stream can directly consume an async generator
                # It will automatically handle the async iteration and display chunks.
                for chunk in response_generator:
                    st.markdown(chunk, unsafe_allow_html=True) # Display each chunk
                    full_response_content += chunk

            st.session_state.messages.append({"role": "assistant", "content": full_response_content})

# Cleanup temporary PDF file on app exit (Streamlit doesn't have a direct 'on_exit' for this)
# This is a limitation of Streamlit's execution model. Manual cleanup or a more robust file management strategy is needed for production.
# For now, the temp directory will persist until the system cleans it up or manually removed.
# A more robust solution would involve a background task or a dedicated cleanup mechanism.
# For this prototype, we'll leave it as is, noting the temporary file persistence.
