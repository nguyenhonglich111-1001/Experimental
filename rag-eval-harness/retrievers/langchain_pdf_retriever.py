import os
import sys
import time

# Add the parent project directory to the Python path
# This allows us to import modules from the 'langchain-file-processor'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base import BaseRetriever
from nlp.tools.langchain_file_processor.app.langchain_logic import (
    get_llm, get_fast_llm, get_embeddings, build_vector_store, build_retriever,
    generate_sub_queries, extract_chapter_from_query, handle_rag_query
)
from nlp.tools.langchain_file_processor.app.utils import load_and_split_by_chapter

# This is a bit of a hack to make sure we can get the API key.
# In a real app, this would be handled by a more robust config system.
from dotenv import load_dotenv
load_dotenv()


class LangchainPdfRetriever(BaseRetriever):
    """
    Concrete implementation of BaseRetriever for our LangChain PDF chatter.
    """
    def __init__(self):
        self.retriever = None
        self.llm = None
        self.fast_llm = None
        self.embeddings = None
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.fast_llm = get_fast_llm(google_api_key)
        self.embeddings = get_embeddings(google_api_key)

    def setup(self, document_path: str):
        """
        Loads, processes, and indexes the document.
        """
        print(f"Setting up LangchainPdfRetriever with document: {document_path}")
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found at: {document_path}")

        print("Loading and splitting document by chapter...")
        docs = load_and_split_by_chapter(document_path)
        
        print("Building vector store...")
        vector_store = build_vector_store(self.embeddings)
        
        print("Building retriever...")
        self.retriever = build_retriever(vector_store, docs)
        print("Setup complete.")

    def retrieve(self, query: str, chat_history: list) -> dict:
        """
        Performs the retrieval step and returns retrieved doc IDs and latency.
        """
        if not self.retriever:
            raise RuntimeError("Retriever is not set up. Please call 'setup' first.")

        start_time = time.perf_counter()

        sub_queries = generate_sub_queries(self.llm, query, chat_history)
        
        all_retrieved_docs = []
        for q in sub_queries:
            chapter_num = extract_chapter_from_query(self.fast_llm, q)
            
            search_kwargs = {}
            if chapter_num is not None:
                search_kwargs = {"filter": {"chapter": chapter_num}}

            retrieved = self.retriever.get_relevant_documents(q, search_kwargs=search_kwargs)
            all_retrieved_docs.extend(retrieved)
        
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())
        
        # Extract just the chapter number for evaluation
        retrieved_chapters = [doc.metadata.get('chapter') for doc in unique_docs]
        # Filter out None values
        retrieved_chapters = [ch for ch in retrieved_chapters if ch is not None]


        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        return {
            "retrieved_docs": retrieved_chapters,
            "latency_ms": latency_ms
        }

    def retrieve_and_generate(self, query: str, chat_history: list) -> dict:
        """
        Performs the full RAG pipeline and returns the generated answer and latency.
        """
        if not self.retriever:
            raise RuntimeError("Retriever is not set up. Please call 'setup' first.")

        start_time = time.perf_counter()
        
        # We can reuse the full handle_rag_query function, but we need to adapt it
        # to not use Streamlit features like st.spinner or st.expander
        # For now, we will replicate the logic here without the UI calls.
        
        sub_queries = generate_sub_queries(self.llm, query, chat_history)
        
        all_retrieved_docs = []
        for q in sub_queries:
            chapter_num = extract_chapter_from_query(self.fast_llm, q)
            search_kwargs = {}
            if chapter_num is not None:
                search_kwargs = {"filter": {"chapter": chapter_num}}
            retrieved = self.retriever.get_relevant_documents(q, search_kwargs=search_kwargs)
            all_retrieved_docs.extend(retrieved)
            
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())

        if not unique_docs:
            answer = "I couldn't find any relevant information in the document to answer your question."
        else:
            # The re-ranking and final answer generation logic is inside handle_rag_query
            # For simplicity, we'll call a simplified version of it here.
            # In a real scenario, you'd refactor handle_rag_query to separate logic from UI.
            from langchain.chains import RetrievalQA
            from nlp.tools.langchain-file-processor.app.langchain_logic import CITATION_PROMPT, rerank_documents
            
            reranked_docs = rerank_documents(self.llm, query, unique_docs)
            top_docs = reranked_docs[:4]
            
            contextual_vectorstore = build_vector_store(self.embeddings)
            contextual_vectorstore.add_documents(top_docs)

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