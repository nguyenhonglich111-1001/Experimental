"""
A Streamlit application for processing and chatting with uploaded files using LangChain.
This version incorporates best practices for Streamlit apps, including:
- Caching for expensive resources (@st.cache_resource) and data processing (@st.cache_data).
- Modularity and separation of concerns for better readability and maintenance.
- Advanced RAG techniques: ParentDocumentRetriever and LLM-based re-ranking.
"""
import os
import tempfile
from pathlib import Path
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.retrievers import (ContextualCompressionRetriever,
                                  ParentDocumentRetriever)
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)

# --- Configuration ---
PERSIST_DIRECTORY = Path(__file__).parent / ".chroma_db"
PARENT_CHUNK_SIZE = 2000
CHILD_CHUNK_SIZE = 400

# --- Helper Functions ---

def get_google_api_key() -> Optional[str]:
    """
    Fetches the Google API key from environment variables.
    Checks for GOOGLE_API_KEY first, then falls back to OPENROUTER_API_KEY.
    """
    return os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")

# --- Caching Functions for Expensive Resources ---

@st.cache_resource
def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    """Initializes and caches the LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite-preview-06-17",
        google_api_key=api_key,
        temperature=0.7,
    )

@st.cache_resource
def get_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Initializes and caches the embeddings model."""
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=api_key
    )

@st.cache_data
def load_and_split_docs(file_path: str) -> List[Document]:
    """
    Loads a PDF and splits it into documents.
    Caches the result based on the file path.
    """
    loader = PyPDFLoader(file_path)
    return loader.load()

@st.cache_resource
def build_retriever(
    _docs: List[Document], embeddings: GoogleGenerativeAIEmbeddings
) -> ParentDocumentRetriever:
    """
    Builds and caches the advanced ParentDocumentRetriever.
    The '_docs' argument is used for caching purposes but the function
    relies on the documents being passed to retriever.add_documents.
    """
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=PARENT_CHUNK_SIZE)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=CHILD_CHUNK_SIZE)
    
    vectorstore = Chroma(
        collection_name="split_parents",
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIRECTORY),
    )
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    # This part is crucial and will run only when the documents change
    retriever.add_documents(_docs, ids=None)
    return retriever

# --- Main Application Logic ---

def handle_question_answering(llm: ChatGoogleGenerativeAI, retriever):
    """Handles the user input and the QA process with re-ranking."""
    st.header("Ask a question about the document")
    user_question = st.text_input("Your question:")

    if user_question:
        with st.spinner("Retrieving, re-ranking, and finding the answer..."):
            try:
                # 1. Set up the re-ranking compressor
                compressor = LLMChainExtractor.from_llm(llm)
                compression_retriever = ContextualCompressionRetriever(
                    base_compressor=compressor, base_retriever=retriever
                )

                # 2. Set up the QA chain
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=compression_retriever,
                    return_source_documents=True,
                )

                # 3. Invoke the chain and display the response
                response = qa_chain.invoke({"query": user_question})
                st.write("### Answer")
                st.write(response["result"])

                with st.expander("Show source documents"):
                    st.write(response["source_documents"])

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Chat with your PDF", layout="wide")
    st.title("📚 Advanced Chat with Your Book")
    st.markdown(
        "This app uses advanced RAG techniques for more accurate answers. "
        "Upload a PDF to get started."
    )

    load_dotenv()
    google_api_key = get_google_api_key()

    if not google_api_key:
        st.error(
            "API key not found. Please set GOOGLE_API_KEY or OPENROUTER_API_KEY in your .env file."
        )
        return

    # Initialize LLM and Embeddings using cached functions
    llm = get_llm(google_api_key)
    embeddings = get_embeddings(google_api_key)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your PDF book to create the retriever", type="pdf"
    )

    if uploaded_file:
        try:
            # Use a temporary file to get a stable path for caching
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name
            
            # Load, split, and build the retriever using cached functions
            with st.spinner("Processing your document... This may take a moment."):
                docs = load_and_split_docs(tmp_file_path)
                retriever = build_retriever(docs, embeddings)

            st.success("Document processed successfully! You can now ask questions.")
            
            # Handle the QA logic
            handle_question_answering(llm, retriever)

        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
            st.exception(e)
        finally:
            # Clean up the temporary file
            if "tmp_file_path" in locals() and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    else:
        st.info("Please upload a PDF file to begin.")


if __name__ == "__main__":
    main()
