# Gemini API Chatbot with Context Retrieval

## Task Overview

This document outlines the implementation and usage of the Gemini API Chatbot, which now includes functionality for uploading documents, generating embeddings, storing them in MongoDB, and retrieving relevant context to enhance chat responses.

## Features Implemented

*   **File Upload and Chunking:** Users can upload `.txt` or `.md` files via a Streamlit file uploader. Large files are automatically split into smaller, overlapping chunks using `langchain-text-splitters`.
*   **Embedding Generation:** Each chunk of the uploaded file content is embedded using the VoyageAI API (`voyage-lite-02-instruct` model).
*   **MongoDB Storage:** Each chunk, along with its original file name, chunk index, and corresponding embedding, is stored in a MongoDB collection (`gemini_chatbot_db.document_chunks`).
*   **Context Retrieval:** When a user sends a chat message, an embedding of the query is generated. A placeholder for vector similarity search is implemented (currently fetches a few most recent chunks). In a production environment, this would be replaced with a proper MongoDB Atlas Vector Search to retrieve the most relevant chunks based on the query.
*   **Enriched Chat Responses:** The retrieved relevant chunks are combined and prepended to the user's query before being sent to the Gemini API, allowing the model to generate more informed responses.

## Setup and Configuration

To run this feature, you need to set up the following:

1.  **Environment Variables:**
    *   Create a `.env` file in the project root (`D:/LichNH/coding/Experimental/`).
    *   Add the following variables:
        ```
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        MONGO_URI="YOUR_MONGODB_CONNECTION_STRING"
        VOYAGE_API_KEY="YOUR_VOYAGE_API_KEY"
        ```
    *   Replace the placeholder values with your actual API keys and MongoDB connection string.

2.  **MongoDB Setup (for full vector search capability):**
    *   **MongoDB Instance:** You need a MongoDB instance. MongoDB Atlas is recommended for its built-in Vector Search capabilities.
    *   **Database and Collection:** The application uses `gemini_chatbot_db` database and `document_chunks` collection.
    *   **Vector Search Index (Recommended for Production):** To enable efficient similarity search, create a Vector Search Index on the `embedding` field in your `document_chunks` collection. Here's an example index definition (adjust as per your needs):

        ```json
        {
          "fields": [
            {
              "type": "vector",
              "path": "embedding",
              "numDimensions": 1024, // Adjust based on your VoyageAI model's embedding dimension
              "similarity": "cosine"
            }
          ]
        }
        ```
        *Note: The `voyage-lite-02-instruct` model produces 1024-dimensional embeddings.* 

3.  **Set up and Install Dependencies:**
    *   **Create a Virtual Environment:**
        Navigate to the `nlp/tools/gemini-api/` directory:
        ```bash
        cd D:/LichNH/coding/Experimental/nlp/tools/gemini-api/
        ```
        Create a virtual environment (if you haven't already):
        ```bash
        python -m venv venv-gemini-api
        ```
    *   **Activate the Virtual Environment:**
        On Windows:
        ```bash
        .\venv-gemini-api\Scripts\activate
        ```
        On Linux/macOS:
        ```bash
        source venv-gemini-api/bin/activate
        ```
    *   **Install Dependencies:**
        With the virtual environment activated, install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

## How to Run

1.  Ensure all setup steps (environment variables, MongoDB, and dependency installation) are completed.
2.  Navigate to the `nlp/tools/gemini-api/` directory:
    ```bash
    cd D:/LichNH/coding/Experimental/nlp/tools/gemini-api/
    ```
3.  **Activate the virtual environment:**
    On Windows:
    ```bash
    .\venv-gemini-api\Scripts\activate
    ```
    On Linux/macOS:
    ```bash
    source venv-gemini-api/bin/activate
    ```
4.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```

## Todos

*   Implement robust error handling for various file types (e.g., PDF, DOCX) during upload and processing.
*   Replace the placeholder vector search with a proper MongoDB Atlas Vector Search aggregation pipeline.
*   Add more advanced context management strategies (e.g., chunking large documents, summarizing retrieved context).
*   Implement a UI for managing uploaded documents (view, delete).
*   Add unit tests for the new functionalities.
