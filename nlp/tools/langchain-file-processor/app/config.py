from pathlib import Path

# --- Configuration ---
PERSIST_DIRECTORY = Path(__file__).parent.parent / ".chroma_db"
PARENT_CHUNK_SIZE = 2000
CHILD_CHUNK_SIZE = 400
LLM_MODEL = "gemini-2.5-flash-lite-preview-06-17"
EMBEDDINGS_MODEL = "models/embedding-001"
