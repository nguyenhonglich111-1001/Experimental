import os
import shutil
import tempfile

import streamlit as st
from dotenv import load_dotenv

from app.components import display_chat_history
from app.config import PERSIST_DIRECTORY
from app.langchain_logic import (build_retriever, build_vector_store,
                                 classify_intent, generate_sub_queries,
                                 get_embeddings, get_llm, handle_direct_llm_query,
                                 handle_rag_query, rerank_documents)
from app.state import (cancel_file_deletion, confirm_file_deletion,
                       initialize_session_state)
from app.utils import get_google_api_key, load_and_split_by_chapter

def reset_knowledge_base():
    """Deletes the vector store and resets the session state."""
    # First, release the resources by setting them to None
    st.session_state.retriever = None
    st.session_state.vectorstore = None
    st.session_state.messages = []
    st.session_state.file_to_delete = None

    # Now, delete the physical storage
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
    
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    
    st.success("Knowledge base has been reset.")


def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Chat with Gemini", layout="wide")
    st.title("📚 Universal Chat")

    load_dotenv()
    initialize_session_state()

    # --- API Key and Model Initialization ---
    google_api_key = get_google_api_key()
    if not google_api_key:
        st.error("API key not found. Please set GOOGLE_API_KEY or OPENROUTER_API_KEY.")
        return

    llm = get_llm(google_api_key)
    embeddings = get_embeddings(google_api_key)

    # Build or load the vector store and retriever from session state
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = build_vector_store(embeddings)
    if "retriever" not in st.session_state:
        st.session_state.retriever = None

    # --- Sidebar for PDF Upload ---
    with st.sidebar:
        st.header("Add Context")
        st.markdown("Upload a PDF to chat with its content.")
        uploaded_file = st.file_uploader("Upload your PDF", type="pdf", key="file_uploader")

        if uploaded_file:
            with st.spinner("Processing your document..."):
                try:
                    # Define the permanent path for the uploaded file
                    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    
                    permanent_path = os.path.join(upload_dir, uploaded_file.name)
                    
                    # Save the file to the permanent location
                    with open(permanent_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    docs = load_and_split_by_chapter(permanent_path)
                    for doc in docs:
                        # The source in metadata is now the permanent path
                        doc.metadata["source"] = permanent_path

                    st.session_state.vectorstore = build_vector_store(embeddings)
                    st.session_state.retriever = build_retriever(st.session_state.vectorstore, docs)
                    st.success("Document processed! The chat will now use its content.")
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        
        if st.session_state.retriever:
            st.success("A document is loaded and ready.")

        st.divider()
        if st.button("Reset Knowledge Base"):
            reset_knowledge_base()
            st.rerun()

    # --- Main Chat and Deletion Confirmation UI ---
    display_chat_history(st.session_state.vectorstore)

    if st.session_state.file_to_delete:
        file_path = st.session_state.file_to_delete
        st.warning(f"Are you sure you want to delete `{os.path.basename(file_path)}`? This is irreversible.")
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            st.button("Yes, Delete", on_click=confirm_file_deletion, args=(st.session_state.vectorstore,))
        with col2:
            st.button("Cancel", on_click=cancel_file_deletion)

    # --- Handle new user input ---
    if prompt := st.chat_input("What would you like to ask?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            intent = classify_intent(llm, prompt)

            if intent == "list_files":
                st.session_state.messages.append({"role": "assistant", "type": "file_list"})
                st.rerun()

            elif intent == "question_about_document" and st.session_state.retriever:
                # Pass the last 4 messages for conversational context
                response = handle_rag_query(
                    prompt, 
                    llm, 
                    st.session_state.retriever, 
                    embeddings, 
                    st.session_state.messages[-4:]
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            else:
                response = handle_direct_llm_query(prompt, llm)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()

