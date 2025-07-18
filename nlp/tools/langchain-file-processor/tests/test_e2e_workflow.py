import os
import shutil
from unittest.mock import patch

import pytest
from langchain_community.embeddings import FakeEmbeddings

from app.config import PERSIST_DIRECTORY
from app.langchain_logic import (build_retriever, build_vector_store,
                                   get_indexed_files)
from app.utils import load_and_split_docs

# --- Test Setup ---

# Use a known, existing file for the test
TEST_FILE_PATH = r"C:\Users\MGUser\Downloads\The Hidden Costs of LangChain, CrewAI, PydanticAI and Others_ Why Popular AI Frameworks Are Failing Production Teams _ by Kenny Vaneetvelde _ Jul, 2025 _ AI Advances.pdf"
TEST_FILE_NAME = os.path.basename(TEST_FILE_PATH)

@pytest.fixture(scope="module")
def test_environment():
    """
    Sets up the test environment by clearing any old database
    and yields the path to the test file.
    """
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
    
    # Ensure the test file exists before running tests
    if not os.path.exists(TEST_FILE_PATH):
        pytest.fail(f"Test file not found at: {TEST_FILE_PATH}")
        
    yield TEST_FILE_PATH
    
    # Teardown: clean up the created database
    if os.path.exists(PERSIST_DIRECTORY):
        try:
            shutil.rmtree(PERSIST_DIRECTORY)
        except PermissionError:
            print(f"Warning: Could not remove {PERSIST_DIRECTORY} on teardown due to a PermissionError, likely on Windows.")

# --- Unit Test ---

@patch('app.langchain_logic.get_embeddings')
def test_file_upload_and_listing(mock_get_embeddings, test_environment):
    """
    Tests the end-to-end logic of processing a file and then listing it.
    This simulates the core workflow of uploading a file and verifying its presence.
    """
    # --- 1. Setup ---
    
    # Mock the embeddings to avoid real API calls
    mock_get_embeddings.return_value = FakeEmbeddings(size=768)
    
    # Get the embeddings instance (it will be the mocked one)
    embeddings = mock_get_embeddings()
    
    # --- 2. Execution ---
    
    # Step 1: Load the document (same as in server.py)
    # We call the original function wrapped by the decorator
    docs = load_and_split_docs.__wrapped__(test_environment)
    assert docs is not None
    assert len(docs) > 0

    # Step 2: Build the vector store and retriever
    vectorstore = build_vector_store(embeddings)
    retriever = build_retriever(vectorstore, docs)
    assert retriever is not None

    # Step 3: Get the list of indexed files
    indexed_files = get_indexed_files(vectorstore)

    # --- 3. Assertion ---
    
    assert indexed_files is not None
    assert isinstance(indexed_files, list)
    assert len(indexed_files) == 1
    
    # Check if the basename of the uploaded file is in the list
    assert os.path.basename(indexed_files[0]) == TEST_FILE_NAME