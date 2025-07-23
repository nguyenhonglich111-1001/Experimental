from abc import ABC, abstractmethod
from typing import List, Dict

class BaseRAG(ABC):
    """
    Abstract base class for a RAG (Retrieval-Augmented Generation) pipeline.
    Defines the standard interface for all RAG implementations.
    """
    @abstractmethod
    def __init__(self, config: Dict = {}):
        """
        Initializes the RAG pipeline with necessary configurations.
        e.g., API keys, model names, etc.
        """
        pass

    @abstractmethod
    def ingest(self, documents: List[Dict[str, str]]):
        """
        Processes and indexes a list of source documents.
        Each document is a dictionary with 'id' and 'text' keys.
        This method should build the retriever.
        """
        pass

    @abstractmethod
    def query(self, prompt: str, chat_history: List[Dict]) -> Dict:
        """
        Takes a user prompt and chat history, performs the full RAG process,
        and returns a dictionary containing:
        - 'answer': The final generated answer string.
        - 'sources': A list of source document chunks used for the answer.
        - 'latency_ms': The time taken for the entire query process.
        """
        pass
