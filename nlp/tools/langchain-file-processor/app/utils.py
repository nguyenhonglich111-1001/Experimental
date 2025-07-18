import os
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import streamlit as st

def get_google_api_key() -> Optional[str]:
    """
    Fetches the Google API key from environment variables.
    Checks for GOOGLE_API_KEY first, then falls back to OPENROUTER_API_KEY.
    """
    return os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")

@st.cache_data
def load_and_split_docs(file_path: str) -> List[Document]:
    """
    Loads a PDF and splits it into documents.
    Caches the result based on the file path.
    """
    loader = PyPDFLoader(file_path)
    return loader.load()
