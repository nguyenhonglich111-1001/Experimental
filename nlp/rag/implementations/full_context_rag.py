import os
import sys
import time
from typing import List, Dict

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from nlp.rag.core.base import BaseRAG
from nlp.tools.langchain_file_processor.app.langchain_logic import get_llm
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()

class FullContextRAG(BaseRAG):
    """
    A RAG implementation that stuffs the entire document content into the
    system prompt. This relies on the LLM's large context window to find
    relevant information without an explicit retrieval step.
    """
    def __init__(self, config: Dict = {}):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.llm = get_llm(google_api_key)
        self.full_context = None
        self.source_id = "N/A"
        self.chat_history = []

    def ingest(self, documents: List[Dict[str, str]]):
        """
        Loads the full text of the first document provided into the system prompt.
        """
        print("Ingesting document for FullContextRAG...")
        if not documents:
            self.full_context = None
            self.source_id = "N/A"
            print("No documents provided for ingestion.")
            return

        # This strategy only considers the first document
        first_doc = documents[0]
        self.full_context = first_doc['text']
        self.source_id = first_doc['id']
        
        system_prompt = (
            "You are a helpful assistant. Answer questions based on the provided document content. "
            "If the answer isn't in the document, say so.\n\n"
            f"--- DOCUMENT CONTENT ---\n{self.full_context}"
        )
        
        # Reset and initialize chat history with the new system prompt
        self.chat_history = [SystemMessage(content=system_prompt)]
        print(f"Ingestion complete. Context length: {len(self.full_context)} characters.")

    def query(self, prompt: str, chat_history: List[Dict]) -> Dict:
        """
        Queries the LLM with the full document context and conversation history.
        """
        start_time = time.perf_counter()

        if not self.full_context:
            return {
                "answer": "I have no document to search. Please upload a file first.",
                "sources": [],
                "latency_ms": 0
            }

        # Add the current user prompt to our internal history
        self.chat_history.append(HumanMessage(content=prompt))

        # Create the prompt template for the LLM call
        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="history")
        ])
        
        chain = prompt_template | self.llm | StrOutputParser()
        
        response_text = chain.invoke({"history": self.chat_history})
        
        # Add the AI's response to our internal history for future context
        self.chat_history.append(AIMessage(content=response_text))

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # For this strategy, the "source" is the entire document
        source_doc = Document(
            page_content=self.full_context[:500] + "...", # Truncate for display
            metadata={"source": self.source_id}
        )

        return {
            "answer": response_text,
            "sources": [source_doc],
            "latency_ms": latency_ms
        }