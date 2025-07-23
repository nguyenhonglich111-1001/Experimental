import os
import sys
import time
from typing import List, Dict

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from nlp.rag.core.base import BaseRAG
from nlp.tools.langchain_file_processor.app.langchain_logic import get_llm, get_embeddings, CITATION_PROMPT
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

class MMRSummaryRAG(BaseRAG):
    """
    A RAG implementation that uses Maximal Marginal Relevance (MMR) search.
    This is well-suited for summarization tasks where a diverse set of
    relevant chunks is desirable.
    """
    def __init__(self, config: Dict = {}):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.embeddings = get_embeddings(google_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.retriever = None

    def ingest(self, documents: List[Dict[str, str]]):
        """Processes and indexes documents using an in-memory vector store."""
        print("Ingesting documents for MMRSummaryRAG...")
        docs_to_chunk = []
        for doc in documents:
            # Each chunk inherits the ID of its parent document
            chunks = self.text_splitter.split_text(doc['text'])
            for chunk in chunks:
                docs_to_chunk.append(Document(page_content=chunk, metadata={"source": doc['id']}))
        
        if not docs_to_chunk:
            print("No text to ingest.")
            self.retriever = None
            return

        # Create a true in-memory vector store
        vector_store = Chroma.from_documents(docs_to_chunk, self.embeddings)
        
        # Use Maximal Marginal Relevance search
        self.retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 5, 'fetch_k': 20}
        )
        print("Ingestion complete.")

    def query(self, prompt: str, chat_history: List[Dict]) -> Dict:
        """Performs the full RAG pipeline using the MMR strategy."""
        start_time = time.perf_counter()

        if not self.retriever:
            return {
                "answer": "I have no documents to search. Please upload a file first.",
                "sources": [],
                "latency_ms": 0
            }

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": CITATION_PROMPT},
            return_source_documents=True,
        )
        
        response = qa_chain.invoke({"query": prompt})
        answer = response.get("result", "Sorry, I couldn't find an answer.")
        sources = response.get("source_documents", [])

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        return {
            "answer": answer,
            "sources": sources,
            "latency_ms": latency_ms
        }
