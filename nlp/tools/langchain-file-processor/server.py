"""
A Streamlit application for processing and chatting with uploaded files using LangChain.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)

# Define the path for the persistent Chroma database relative to the script file
PERSIST_DIRECTORY = Path(__file__).parent / ".chroma_db"


def get_google_api_key() -> Optional[str]:
    """
    Fetches the Google API key from environment variables.

    Checks for GOOGLE_API_KEY first, then falls back to OPENROUTER_API_KEY.

    Returns:
        Optional[str]: The API key if found, otherwise None.
    """
    return os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")


def initialize_session_state(embeddings: GoogleGenerativeAIEmbeddings):
    """Initializes the Streamlit session state."""
    if "vector_store" not in st.session_state:
        if PERSIST_DIRECTORY.exists():
            st.write("Loading existing vector store...")
            st.session_state.vector_store = Chroma(
                persist_directory=str(PERSIST_DIRECTORY),
                embedding_function=embeddings,
            )
            st.write("Vector store loaded.")
        else:
            st.session_state.vector_store = None
    if "processed_file_id" not in st.session_state:
        st.session_state.processed_file_id = None


def process_uploaded_file(uploaded_file, embeddings: GoogleGenerativeAIEmbeddings):
    """
    Processes the uploaded PDF file, creates a vector store, and updates the session state.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        st.write(f"Processing `{uploaded_file.name}`...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. Load the document
        status_text.text("Loading PDF...")
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        progress_bar.progress(25)

        # 2. Split the document into chunks
        status_text.text(f"Splitting {len(documents)} pages into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
            separators=["\n\n", "\n", " ", ""],
        )
        texts: list[Document] = text_splitter.split_documents(documents)
        progress_bar.progress(50)

        # 3. Create embeddings and vector store
        status_text.text(f"Creating embeddings for {len(texts)} chunks...")
        st.session_state.vector_store = Chroma.from_documents(
            texts, embeddings, persist_directory=str(PERSIST_DIRECTORY)
        )
        progress_bar.progress(100)
        status_text.text("Processing complete!")
        st.success("File processed and vector store created/updated successfully!")
        st.session_state.processed_file_id = uploaded_file.file_id

    except Exception as e:
        st.error(f"An error occurred during file processing: {e}")
    finally:
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


def handle_question_answering(google_api_key: str, vector_store: VectorStore):
    """Handles the user input and the QA process."""
    st.header("Ask a question about the document")
    user_question = st.text_input("Your question:")

    if user_question:
        try:
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-1.5-flash-latest",
                google_api_key=google_api_key,
                temperature=0.7,
            )
            retriever = vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 3}
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
            )

            with st.spinner("Finding the answer..."):
                response = qa_chain.invoke({"query": user_question})
                st.write("### Answer")
                st.write(response["result"])

                with st.expander("Show source documents"):
                    st.write(response["source_documents"])

        except Exception as e:
            st.error(f"An error occurred while answering the question: {e}")


def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Chat with your PDF", layout="wide")
    st.title("📚 Chat with Your Book")

    load_dotenv()
    google_api_key = get_google_api_key()

    if not google_api_key:
        st.error(
            "API key not found. Please set GOOGLE_API_KEY or OPENROUTER_API_KEY in your .env file."
        )
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=google_api_key
    )

    initialize_session_state(embeddings)

    uploaded_file = st.file_uploader(
        "Upload your PDF book to create or update the vector store", type="pdf"
    )

    if uploaded_file and uploaded_file.file_id != st.session_state.get(
        "processed_file_id"
    ):
        process_uploaded_file(uploaded_file, embeddings)

    if st.session_state.get("vector_store"):
        handle_question_answering(google_api_key, st.session_state.vector_store)


if __name__ == "__main__":
    main()