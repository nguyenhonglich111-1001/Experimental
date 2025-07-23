from abc import ABC, abstractmethod
from typing import List, Dict

class BaseRetriever(ABC):
    """
    Abstract base class for a RAG retriever.
    Defines the interface that all concrete retriever implementations must follow.
    Each query is self-contained with its own set of source documents.
    """
    @abstractmethod
    def retrieve(self, query: str, source_documents: List[str]) -> Dict:
        """
        Takes a query and a list of source documents, performs retrieval,
        and returns a dictionary containing:
        - 'retrieved_docs': A list of document identifiers.
        - 'latency_ms': The time taken for the retrieval step.
        """
        pass

    @abstractmethod
    def retrieve_and_generate(self, query: str, source_documents: List[str]) -> Dict:
        """
        Takes a query and a list of source documents, performs the full RAG pipeline,
        and returns a dictionary containing:
        - 'generated_answer': The final answer string.
        - 'full_latency_ms': The time taken for the entire pipeline.
        """
        pass