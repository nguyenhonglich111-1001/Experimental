import os
import sys
import time
from typing import List, Dict

# Add the parent project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base import BaseRetriever
from nlp.tools.langchain_file_processor.app.langchain_logic import (
    get_llm, get_embeddings, CITATION_PROMPT
)
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

class SimpleRetriever(BaseRetriever):
    """
    A simplified retriever that uses a direct vector search with MMR
    to get a diverse set of relevant documents.
    """
    def __init__(self):
        self.llm = None
        self.embeddings = None
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.embeddings = get_embeddings(google_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def _create_retriever_from_docs(self, source_documents: List[str], doc_ids: List[str]):
        """Helper to create an in-memory retriever with MMR search."""
        docs_with_ids = []
        for i, doc_text in enumerate(source_documents):
            # Split each source document into smaller chunks
            chunks = self.text_splitter.split_text(doc_text)
            for chunk in chunks:
                # Each chunk inherits the ID of its parent document
                docs_with_ids.append(Document(page_content=chunk, metadata={"source": doc_ids[i]}))
        
        if not docs_with_ids:
            return None

        # Create a true in-memory vector store for this specific query
        vector_store = Chroma.from_documents(docs_with_ids, self.embeddings)
        
        # Use Maximal Marginal Relevance search to balance relevance and diversity
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 5, 'fetch_k': 20} # Fetch more docs initially to give MMR a good selection
        )

    def retrieve(self, query: str, source_documents: List[str], doc_ids: List[str]) -> Dict:
        """
        Performs the retrieval step using the MMR strategy.
        """
        start_time = time.perf_counter()

        retriever = self._create_retriever_from_docs(source_documents, doc_ids)
        if not retriever:
            return {"retrieved_docs": [], "latency_ms": 0}

        retrieved_chunks = retriever.get_relevant_documents(query)
        
        # Deduplicate based on the parent document ID
        retrieved_parent_ids = list(set(doc.metadata.get('source') for doc in retrieved_chunks))
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        return {
            "retrieved_docs": retrieved_parent_ids,
            "latency_ms": latency_ms
        }

    def retrieve_and_generate(self, query: str, source_documents: List[str], doc_ids: List[str]) -> Dict:
        """
        Performs the full RAG pipeline using the MMR strategy.
        """
        start_time = time.perf_counter()

        retriever = self._create_retriever_from_docs(source_documents, doc_ids)
        if not retriever:
            return {"generated_answer": "No documents to process.", "full_latency_ms": 0}

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": CITATION_PROMPT},
            return_source_documents=False,
        )
        
        response = qa_chain.invoke({"query": query})
        answer = response.get("result", "Sorry, I couldn't find an answer.")

        end_time = time.perf_counter()
        full_latency_ms = (end_time - start_time) * 1000

        return {
            "generated_answer": answer,
            "full_latency_ms": full_latency_ms
        }