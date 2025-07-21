import os
import re
from typing import List, Optional

import PyPDF2
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

@st.cache_data
def load_and_split_by_chapter(file_path: str) -> List[Document]:
    """
    Loads a PDF, splits it by chapters, and creates Document objects with chapter metadata.
    """
    with open(file_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        full_text = "".join(page.extract_text() for page in pdf_reader.pages)

    # Split the text by chapters. This regex looks for "Chapter X" or "CHAPTER X"
    # and keeps the delimiter.
    chapters = re.split(r"(Chapter \d+|CHAPTER \d+)", full_text)
    
    # The first element is the text before Chapter 1, which we can often discard.
    # Then, we group the chapter title with its content.
    if chapters[0].strip() == "":
        chapters.pop(0)

    documents = []
    for i in range(0, len(chapters), 2):
        chapter_title = chapters[i]
        chapter_content = chapters[i+1] if (i+1) < len(chapters) else ""
        
        # Extract chapter number for metadata
        chapter_num_match = re.search(r"\d+", chapter_title)
        chapter_num = int(chapter_num_match.group(0)) if chapter_num_match else i // 2 + 1

        documents.append(
            Document(
                page_content=f"{chapter_title}\n\n{chapter_content}",
                metadata={
                    "source": os.path.basename(file_path),
                    "chapter": chapter_num,
                },
            )
        )
    
    return documents
