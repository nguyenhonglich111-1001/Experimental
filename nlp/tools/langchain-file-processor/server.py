import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from app.langchain_logic import (build_retriever, build_vector_store,
                                 get_embeddings, get_llm)
from app.ui import display_chat_interface
from app.utils import get_google_api_key, load_and_split_docs


def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Chat with Gemini", layout="wide")
    st.title("📚 Universal Chat")
    
    load_dotenv()

    # Initialize session state variables
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None

    # --- API Key and Model Initialization ---
    google_api_key = get_google_api_key()
    if not google_api_key:
        st.error(
            "API key not found. Please set GOOGLE_API_KEY or OPENROUTER_API_KEY in your .env file."
        )
        return
    
    llm = get_llm(google_api_key)
    embeddings = get_embeddings(google_api_key)
    
    # Build or load the vector store
    if st.session_state.vectorstore is None:
        st.session_state.vectorstore = build_vector_store(embeddings)

    # --- Sidebar for PDF Upload ---
    with st.sidebar:
        st.header("Add Context")
        st.markdown(
            "Upload a PDF to chat with its content. "
            "Each upload starts a new, fresh knowledge base."
        )
        uploaded_file = st.file_uploader("Upload your PDF", type="pdf", key="file_uploader")

        if uploaded_file:
            with st.spinner("Processing your document..."):
                try:
                    # Reset the vector store for a fresh start
                    st.session_state.vectorstore = build_vector_store(embeddings)
                    st.session_state.retriever = None

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_file_path = tmp_file.name
                    
                    # Add the original filename to the metadata
                    docs = load_and_split_docs(tmp_file_path)
                    for doc in docs:
                        doc.metadata["source"] = uploaded_file.name

                    st.session_state.retriever = build_retriever(st.session_state.vectorstore, docs)
                    st.success("Document processed! The chat will now use its content.")
                
                except Exception as e:
                    st.error(f"An error occurred during file processing: {e}")
                finally:
                    if "tmp_file_path" in locals() and os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)
        
        if st.session_state.retriever:
            st.success("A document is loaded and ready.")

    # --- Main Chat Interface ---
    display_chat_interface(llm, st.session_state.retriever, st.session_state.vectorstore, embeddings)


if __name__ == "__main__":
    main()

