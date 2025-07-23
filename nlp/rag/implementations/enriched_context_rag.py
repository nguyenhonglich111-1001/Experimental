import os
import sys
import time
from typing import List, Dict
import instructor
from pydantic import BaseModel, Field
from tqdm import tqdm

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from nlp.rag.core.base import BaseRAG
from nlp.tools.langchain_file_processor.app.langchain_logic import get_llm, get_fast_llm, get_embeddings, CITATION_PROMPT
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

# Pydantic model to parse the XML output from the enrichment LLM
class EnrichedChunk(BaseModel):
    summary: str = Field(..., description="A concise summary of the chunk.")
    hypothetical_question: str = Field(..., description="A hypothetical question the chunk answers.")

class EnrichedContextRAG(BaseRAG):
    """
    A RAG implementation that uses a fast LLM to enrich document chunks
    at ingestion time with a summary and a hypothetical question.
    """
    def __init__(self, config: Dict = {}):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.fast_llm = get_fast_llm(google_api_key)
        self.embeddings = get_embeddings(google_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        self.retriever = None

    def ingest(self, documents: List[Dict[str, str]]):
        """Processes, enriches, and indexes documents."""
        print("Ingesting and enriching documents for EnrichedContextRAG...")
        
        # 1. Chunk all documents
        all_chunks = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['text'])
            for chunk_text in chunks:
                all_chunks.append({"text": chunk_text, "source_id": doc['id']})

        # 2. Enrich each chunk using the fast LLM
        enriched_docs_for_indexing = []
        
        enrichment_prompt_template = self._get_enrichment_prompt()
        # Patch the client with instructor for Pydantic parsing
        instructor_client = instructor.from_openai(self.fast_llm)

        for chunk_info in tqdm(all_chunks, desc="Enriching Chunks"):
            try:
                enriched_data = instructor_client.chat.completions.create(
                    model="gemini-1.0-flash-lite", # Using the fast model
                    response_model=EnrichedChunk,
                    messages=[{"role": "user", "content": enrichment_prompt_template.format(chunk=chunk_info['text'])}]
                )
                
                combined_text = (
                    f"Question: {enriched_data.hypothetical_question}\n\n"
                    f"Summary: {enriched_data.summary}\n\n"
                    f"Content: {chunk_info['text']}"
                )
                
                doc = Document(
                    page_content=combined_text,
                    metadata={
                        "source": chunk_info['source_id'],
                        "original_content": chunk_info['text'] # Store original for final answer
                    }
                )
                enriched_docs_for_indexing.append(doc)

            except Exception as e:
                print(f"Warning: Could not enrich chunk. Skipping. Error: {e}")
                # Fallback: index the original chunk without enrichment
                doc = Document(
                    page_content=chunk_info['text'],
                    metadata={
                        "source": chunk_info['source_id'],
                        "original_content": chunk_info['text']
                    }
                )
                enriched_docs_for_indexing.append(doc)

        # 3. Index the enriched documents
        if not enriched_docs_for_indexing:
            print("No text to ingest.")
            self.retriever = None
            return

        vector_store = Chroma.from_documents(enriched_docs_for_indexing, self.embeddings)
        self.retriever = vector_store.as_retriever(search_kwargs={'k': 5})
        print("Ingestion complete.")

    def query(self, prompt: str, chat_history: List[Dict]) -> Dict:
        """Performs retrieval against enriched documents and generates an answer."""
        start_time = time.perf_counter()

        if not self.retriever:
            return {"answer": "Please ingest a document first.", "sources": [], "latency_ms": 0}

        # The retriever will find the enriched docs, but the QA chain needs the original content.
        # We need a custom chain to handle this. For simplicity, we'll do it manually.
        
        # 1. Retrieve enriched docs
        retrieved_docs = self.retriever.get_relevant_documents(prompt)
        
        # 2. Reconstruct the context for the generator using the *original* content
        source_documents_for_generator = []
        for doc in retrieved_docs:
            original_doc = Document(
                page_content=doc.metadata['original_content'],
                metadata={'source': doc.metadata['source']}
            )
            source_documents_for_generator.append(original_doc)
        
        # 3. Build a temporary QA chain with the original content
        if not source_documents_for_generator:
             return {"answer": "Could not find relevant information.", "sources": [], "latency_ms": 0}

        contextual_vectorstore = Chroma.from_documents(source_documents_for_generator, self.embeddings)
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=contextual_vectorstore.as_retriever(),
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

    def _get_enrichment_prompt(self) -> str:
        return """
        You are an AI assistant tasked with enriching text chunks for a Retrieval-Augmented Generation (RAG) system. For the given text chunk, you will generate two distinct, complementary pieces of text.
        
        <chunk>
        {chunk}
        </chunk>
        
        Please generate the following two items based on the chunk provided:
        1.  **A concise summary:** In 2-3 sentences, capture the high-level gist of the chunk. This summary will be used to answer broad, topic-level queries.
        2.  **A hypothetical question:** Generate a single, specific question that the chunk directly answers.
        
        Respond in **strict XML format** as shown in the example:
        
        <summary>This section outlines the core benefits of solar energy, emphasizing cost savings and environmental impact.</summary>
        <hypothetical_question>What are the main benefits of using solar energy?</hypothetical_question>
        """