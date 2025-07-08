# Gemini API Chatbot with Context Retrieval

## Task Overview

This document outlines the implementation and usage of the Gemini API Chatbot, which now includes functionality for uploading documents, generating embeddings, storing them in MongoDB, and retrieving relevant context to enhance chat responses.

## Features Implemented

*   **File Upload:** Users can upload `.txt` or `.md` files via a Streamlit file uploader.
*   **Embedding Generation:** Uploaded file content is embedded using the VoyageAI API (`voyage-lite-02-instruct` model).
*   **MongoDB Storage:** The original file content and its corresponding embedding are stored in a MongoDB collection (`gemini_chatbot_db.documents`).
*   **Context Retrieval:** When a user sends a chat message, an embedding of the query is generated. A placeholder for vector similarity search is implemented (currently fetches the most recent document). In a production environment, this would be replaced with a proper MongoDB Atlas Vector Search.
*   **Enriched Chat Responses:** The retrieved context is prepended to the user's query before being sent to the Gemini API, allowing the model to generate more informed responses.

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
    *   **Database and Collection:** The application uses `gemini_chatbot_db` database and `documents` collection.
    *   **Vector Search Index (Recommended for Production):** To enable efficient similarity search, create a Vector Search Index on the `embedding` field in your `documents` collection. Here's an example index definition (adjust as per your needs):

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

3.  **Install Dependencies:**
    *   Ensure you have the required Python packages installed. Navigate to the project root (`D:/LichNH/coding/Experimental/`) and run:
        ```bash
        pip install -r requirements.txt
        ```

## How to Run

1.  Ensure all setup steps (environment variables, MongoDB, dependencies) are completed.
2.  Navigate to the `nlp/tools/gemini-api/` directory:
    ```bash
    cd D:/LichNH/coding/Experimental/nlp/tools/gemini-api/
    ```
3.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```

## Todos

*   Implement robust error handling for various file types (e.g., PDF, DOCX) during upload and processing.
*   Replace the placeholder vector search with a proper MongoDB Atlas Vector Search aggregation pipeline.
*   Add more advanced context management strategies (e.g., chunking large documents, summarizing retrieved context).
*   Implement a UI for managing uploaded documents (view, delete).
*   Add unit tests for the new functionalities.
