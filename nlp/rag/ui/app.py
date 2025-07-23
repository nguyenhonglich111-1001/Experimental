import streamlit as st
import os
import sys
import importlib
from typing import Dict

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from nlp.rag.core.base import BaseRAG
from langchain_core.messages import AIMessage, HumanMessage

# --- Helper Functions ---

def find_rag_implementations() -> Dict[str, BaseRAG]:
    """Scans the 'implementations' directory to find all BaseRAG subclasses."""
    implementations = {}
    impl_dir = os.path.join(os.path.dirname(__file__), '..', 'implementations')
    for filename in os.listdir(impl_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"nlp.rag.implementations.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseRAG) and attr is not BaseRAG:
                        # Use a user-friendly name for the dropdown
                        friendly_name = attr.__name__.replace("RAG", " RAG").replace("_", " ")
                        implementations[friendly_name] = attr
            except Exception as e:
                st.error(f"Could not load {module_name}: {e}")
    return implementations

@st.cache_resource
def get_rag_instance(rag_class) -> BaseRAG:
    """Creates and caches an instance of the selected RAG class."""
    return rag_class()

# --- Main Streamlit App ---

st.set_page_config(page_title="Modular RAG Chat", layout="wide")
st.title("Modular RAG Framework")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_instance" not in st.session_state:
    st.session_state.rag_instance = None

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")
    
    available_rags = find_rag_implementations()
    if not available_rags:
        st.error("No RAG implementations found!")
        st.stop()

    selected_rag_name = st.selectbox(
        "Choose a RAG Strategy",
        options=list(available_rags.keys())
    )
    
    RagClass = available_rags[selected_rag_name]
    st.session_state.rag_instance = get_rag_instance(RagClass)

    st.info(f"**Current Strategy:** `{selected_rag_name}`")

    uploaded_file = st.file_uploader("Upload a document to chat with", type=['txt', 'pdf'])

    if st.button("Ingest Document"):
        if uploaded_file and st.session_state.rag_instance:
            with st.spinner(f"Ingesting '{uploaded_file.name}'..."):
                # For simplicity, we'll read the whole file as text.
                # A real app would handle PDFs and other formats more robustly.
                file_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                documents = [{"id": uploaded_file.name, "text": file_text}]
                st.session_state.rag_instance.ingest(documents)
                st.success("Ingestion complete! You can now ask questions.")
        else:
            st.warning("Please upload a file and select a RAG strategy first.")

# --- Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Handle new user input
if prompt := st.chat_input("Ask a question about the document..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.rag_instance:
            with st.spinner("Thinking..."):
                response_dict = st.session_state.rag_instance.query(prompt, []) # History not yet implemented
                st.markdown(response_dict['answer'])
                
                with st.expander("Sources"):
                    for source in response_dict['sources']:
                        st.write(f"**Source:** `{source.metadata.get('source', 'N/A')}`")
                        st.write(source.page_content)

            st.session_state.messages.append(AIMessage(content=response_dict['answer']))
        else:
            st.warning("The RAG system is not initialized. Please configure it in the sidebar.")
