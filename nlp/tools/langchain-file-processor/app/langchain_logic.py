from typing import List, Tuple

import chromadb
import streamlit as st
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)

from .config import (CHILD_CHUNK_SIZE, EMBEDDINGS_MODEL, LLM_MODEL,
                    PARENT_CHUNK_SIZE, PERSIST_DIRECTORY)

@st.cache_resource
def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    """Initializes and caches the LLM."""
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=api_key,
        temperature=0.7,
    )

@st.cache_resource
def get_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Initializes and caches the embeddings model."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDINGS_MODEL, google_api_key=api_key
    )

def build_vector_store(
    embeddings: GoogleGenerativeAIEmbeddings,
) -> Chroma:
    """Builds and caches the Chroma vector store."""
    return Chroma(
        collection_name="split_parents",
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIRECTORY),
        client_settings=chromadb.Settings(allow_reset=True),
    )

def build_retriever(
    vectorstore: Chroma, docs: List[Document]
) -> ParentDocumentRetriever:
    """Builds the ParentDocumentRetriever and adds documents to it."""
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=PARENT_CHUNK_SIZE)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=CHILD_CHUNK_SIZE)
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    
    retriever.add_documents(docs, ids=None)
    return retriever

def get_indexed_files(vectorstore: Chroma) -> List[str]:
    """Retrieves the list of unique source file names from the vector store."""
    if not vectorstore:
        return []
    
    try:
        all_docs = vectorstore.get()
        if not all_docs or not all_docs.get("metadatas"):
            return []
        
        unique_sources = set()
        for metadata in all_docs["metadatas"]:
            if "source" in metadata:
                unique_sources.add(metadata["source"])
        
        return list(unique_sources)
    except Exception:
        # This can happen if the collection doesn't exist yet
        return []

@st.cache_data
def classify_intent(_llm: ChatGoogleGenerativeAI, query: str) -> str:
    """Uses an LLM to classify the user's intent."""
    system_message = """
    You are an intent classifier. Your job is to determine the user's intent based on their message.
    There are three possible intents:
    1. "conversational": For greetings, farewells, thank yous, or other general chat.
    2. "list_files": For when the user explicitly asks to see the list of loaded files.
    3. "question_about_document": For any question that should be answered from the loaded document.

    Respond with ONLY one of the three intent names.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{question}"),
        ]
    )
    
    chain = prompt | _llm | StrOutputParser()
    result = chain.invoke({"question": query})
    return result.strip()

@st.cache_data
def generate_sub_queries(_llm: ChatGoogleGenerativeAI, query: str) -> List[str]:
    """Uses an LLM to break down a complex query into simpler sub-queries."""
    system_message = """
    You are an expert at converting user questions into a set of simple, self-contained sub-queries.
    Your goal is to break down the user's query into a series of questions that a semantic search system can effectively answer.

    - For broad requests (e.g., "list all...", "summarize..."), first generate a query to find the general context, then generate queries to extract the specific details.
    - Each sub-query should be on a new line.
    - Do not number the sub-queries.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{question}"),
        ]
    )
    
    chain = prompt | _llm | StrOutputParser()
    result = chain.invoke({"question": query})
    return [q.strip() for q in result.split("\n") if q.strip()]