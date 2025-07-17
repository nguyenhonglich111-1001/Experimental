import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import asyncio

from openai import OpenAI
import instructor

from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory

from .book_qa_agent import BookQAAgent, BookQAAgentInputSchema

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Atomic PDF Q&A", layout="wide", initial_sidebar_state="expanded")

# --- Styling ---
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .st-emotion-cache-1c7y2kd {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    """Initializes and caches the Gemini client."""
    return instructor.from_openai(
        OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

def initialize_agent():
    """Initializes the BookQAAgent and stores it in session state."""
    client = get_gemini_client()
    agent_config = BaseAgentConfig(
        client=client,
        model="gemini-2.0-flash-exp",
        memory=AgentMemory()
    )
    st.session_state.agent = BookQAAgent(config=agent_config)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    initialize_agent()
if "current_pdf_path" not in st.session_state:
    st.session_state.current_pdf_path = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

# --- Sidebar for File Upload and Controls ---
with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload a PDF book", type=["pdf"])
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Interface ---
st.title("📚 Atomic PDF Book Q&A")
st.write("Upload a PDF and ask questions about its content.")

# Handle new file upload
if uploaded_file is not None:
    if uploaded_file.name != os.path.basename(st.session_state.get("current_pdf_path", "")):
        with st.spinner(f"Processing '{uploaded_file.name}'..."):
            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.session_state.current_pdf_path = temp_pdf_path
            st.session_state.pdf_processed = False
            st.session_state.messages = []
            initialize_agent() # Re-initialize agent for new book
            st.success(f"PDF '{uploaded_file.name}' uploaded. Ready to answer your questions!")

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
            response_placeholder = st.empty()
            
            try:
                # Define the input for the agent
                agent_input = BookQAAgentInputSchema(
                    chat_message=prompt,
                    pdf_file_path=st.session_state.current_pdf_path
                )
                
                # Run the agent and stream the response
                response_generator = st.session_state.agent._run(agent_input)
                
                # Use an async function to handle the streaming
                async def stream_response():
                    full_response_content = ""
                    async for chunk in response_generator:
                        full_response_content += chunk
                        response_placeholder.markdown(full_response_content + "▌")
                    response_placeholder.markdown(full_response_content)
                    return full_response_content

                # Run the async function and get the final response
                full_response = asyncio.run(stream_response())
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.pdf_processed = True # Mark PDF as processed after first question
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})