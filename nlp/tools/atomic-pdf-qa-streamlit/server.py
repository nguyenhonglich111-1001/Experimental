import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import asyncio

from openai import OpenAI
import instructor

from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory

from book_qa_agent import BookQAAgent, BookQAAgentInputSchema

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Atomic PDF Q&A", layout="wide", initial_sidebar_state="expanded")

# --- Styling ---
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .st-emotion-cache-1c7y2kd {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- Configuration & Caching ---
@st.cache_resource
def get_gemini_client():
    """Initializes and caches the Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    return instructor.from_openai(
        OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

@st.cache_resource
def initialize_agent():
    """Initializes the BookQAAgent and returns it."""
    client = get_gemini_client()
    agent_config = BaseAgentConfig(
        client=client,
        model="gemini-2.0-flash-exp",
        memory=AgentMemory()
    )
    return BookQAAgent(config=agent_config)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = initialize_agent()
if "current_pdf_path" not in st.session_state:
    st.session_state.current_pdf_path = None

# --- Sidebar for File Upload and Controls ---
with st.sidebar:
    st.header("Setup")
    uploaded_file = st.file_uploader("Upload a PDF book", type=["pdf"])
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.agent.memory.reset()
        st.rerun()

# --- Main Chat Interface ---
st.title("📚 Atomic PDF Book Q&A")

# Welcome message
if not st.session_state.messages:
    st.info("Upload a PDF in the sidebar to get started.")

# Handle new file upload
if uploaded_file is not None:
    # Use file's unique ID to avoid reprocessing on every interaction
    if uploaded_file.file_id != st.session_state.get("uploaded_file_id"):
        with st.spinner(f"Processing '{uploaded_file.name}'..."):
            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.session_state.current_pdf_path = temp_pdf_path
            st.session_state.uploaded_file_id = uploaded_file.file_id
            st.session_state.messages = []
            st.session_state.agent = initialize_agent() # Re-initialize agent for new book
            
            welcome_message = f"PDF '{uploaded_file.name}' loaded. What would you like to know?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
            st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept and process user input
if prompt := st.chat_input("Ask a question about the book..."):
    if not st.session_state.current_pdf_path:
        st.warning("Please upload a PDF file first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                agent_input = BookQAAgentInputSchema(
                    chat_message=prompt,
                    pdf_file_path=st.session_state.current_pdf_path
                )
                
                response_generator = st.session_state.agent.run_async(agent_input)
                
                # Use st.write_stream to display the async generator's output
                full_response = st.write_stream(response_generator)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})