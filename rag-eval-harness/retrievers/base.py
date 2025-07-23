from abc import ABC, abstractmethod

class BaseRetriever(ABC):
    """
    Abstract base class for a RAG retriever.
    Defines the interface that all concrete retriever implementations must follow.
    """
    @abstractmethod
    def setup(self, document_path: str):
        """
        Loads, processes, and indexes the document.
        This is the one-time setup cost.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, chat_history: list) -> dict:
        """
        Takes a query and returns a dictionary containing:
        - 'retrieved_docs': A list of document identifiers (e.g., chapter numbers, doc IDs).
        - 'latency_ms': The time taken for the retrieval step.
        """
        pass

    @abstractmethod
    def retrieve_and_generate(self, query: str, chat_history: list) -> dict:
        """
        Performs the full RAG pipeline and returns a dictionary containing:
        - 'generated_answer': The final answer string.
        - 'full_latency_ms': The time taken for the entire pipeline.
        """
        pass
