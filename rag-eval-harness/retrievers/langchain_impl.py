import os
import sys
import time
from typing import List, Dict

# Add the parent project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base import BaseRetriever
from nlp.tools.langchain_file_processor.app.langchain_logic import (
    get_llm, get_fast_llm, get_embeddings, build_retriever,
    generate_sub_queries, rerank_documents, CITATION_PROMPT
)
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma

from dotenv import load_dotenv
load_dotenv()

class LangchainImpl(BaseRetriever):
    """
    Concrete implementation of BaseRetriever using our LangChain logic.
    This implementation performs in-memory indexing for each query.
    """
    def __init__(self):
        self.llm = None
        self.fast_llm = None
        self.embeddings = None
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.fast_llm = get_fast_llm(google_api_key)
        self.embeddings = get_embeddings(google_api_key)

    def _create_docs_with_ids(self, source_documents: List[str], doc_ids: List[str]) -> List[Document]:
        """Helper to create LangChain Document objects with metadata."""
        docs = []
        for i, doc_text in enumerate(source_documents):
            doc = Document(page_content=doc_text, metadata={"source": doc_ids[i]})
            docs.append(doc)
        return docs

    def retrieve(self, query: str, source_documents: List[str], doc_ids: List[str]) -> Dict:
        """
        Performs the retrieval step for a given query and documents.
        """
        start_time = time.perf_counter()

        docs = self._create_docs_with_ids(source_documents, doc_ids)
        
        # Create a true in-memory vector store for this specific query
        vector_store = Chroma.from_documents(docs, self.embeddings)
        retriever = build_retriever(vector_store, docs)

        sub_queries = generate_sub_queries(self.llm, query, [])
        
        all_retrieved_docs = []
        for q in sub_queries:
            retrieved = retriever.get_relevant_documents(q)
            all_retrieved_docs.extend(retrieved)
        
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())
        
        retrieved_doc_ids = [doc.metadata.get('source') for doc in unique_docs]
        retrieved_doc_ids = [doc_id for doc_id in retrieved_doc_ids if doc_id is not None]

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        return {
            "retrieved_docs": retrieved_doc_ids,
            "latency_ms": latency_ms
        }

    def retrieve_and_generate(self, query: str, source_documents: List[str], doc_ids: List[str]) -> Dict:
        """
        Performs the full RAG pipeline for a given query and documents.
        """
        start_time = time.perf_counter()

        docs = self._create_docs_with_ids(source_documents, doc_ids)
        
        # Create a true in-memory vector store for this specific query
        vector_store = Chroma.from_documents(docs, self.embeddings)
        retriever = build_retriever(vector_store, docs)

        sub_queries = generate_sub_queries(self.llm, query, [])
        
        all_retrieved_docs = []
        for q in sub_queries:
            retrieved = retriever.get_relevant_documents(q)
            all_retrieved_docs.extend(retrieved)
            
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())

        if not unique_docs:
            answer = "I couldn't find any relevant information in the document to answer your question."
        else:
            reranked_docs = rerank_documents(self.llm, query, unique_docs)
            top_docs = reranked_docs[:4]
            
            # Create a new in-memory vector store for the final QA chain
            contextual_vectorstore = Chroma.from_documents(top_docs, self.embeddings)

            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=contextual_vectorstore.as_retriever(),
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