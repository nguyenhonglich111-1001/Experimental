# LangChain File Processor Documentation

## Overview

The LangChain File Processor is a standalone Streamlit application that enables users to upload PDF documents and ask questions about their content. It leverages the LangChain framework to create a retrieval-augmented generation (RAG) pipeline, providing answers that are grounded in the document's text.

This tool is designed for quick analysis and information retrieval from single documents without the need for a complex setup or persistent database.

## Features

-   **Simple Web Interface:** Built with Streamlit for ease of use.
-   **PDF Document Support:** Directly upload and process PDF files.
-   **Retrieval-Augmented Generation (RAG):** Uses a sophisticated pipeline to ensure answers are relevant to the uploaded document.
-   **Source Verification:** Displays the exact text chunks from the source document that were used to generate the answer, allowing for easy verification.
-   **Flexible API Key Support:** Works with either a `GOOGLE_API_KEY` or an `OPENROUTER_API_KEY`.
-   **In-Memory Processing:** The entire process, from file reading to vector storage, runs in memory for speed and simplicity.

## Technical Workflow

1.  **Initialization:** The app loads API keys from a `.env` file.
2.  **File Upload:** The user uploads a PDF via the Streamlit `file_uploader`.
3.  **Document Loading:** The file is temporarily saved, and its content is loaded using `PyPDFLoader`.
4.  **Text Splitting:** The loaded text is split into smaller, overlapping chunks by `RecursiveCharacterTextSplitter` to prepare it for embedding.
5.  **Embedding:** Each text chunk is converted into a vector embedding using `GoogleGenerativeAIEmbeddings`.
6.  **Vector Storage:** The embeddings are stored in a `FAISS` (Facebook AI Similarity Search) index, which allows for fast and efficient similarity searches. This index is held in the Streamlit session state.
7.  **Question Answering:**
    -   When a user asks a question, the app's retriever searches the FAISS index for the most semantically similar document chunks.
    -   The question and the retrieved chunks are passed to a `RetrievalQA` chain.
    -   The `ChatGoogleGenerativeAI` model (Gemini Pro) generates an answer based on the provided context.
8.  **Cleanup:** The temporary file is automatically removed after processing.

## TODOs & Future Enhancements

-   [ ] **Support More File Types:** Extend functionality to support `.docx`, `.txt`, and `.md` files.
-   [ ] **Chat History:** Implement a feature to remember previous questions and answers in the same session for conversational follow-ups.
-   [ ] **Persistent Vector Store:** Add an option to save the FAISS index to disk, allowing users to query a previously uploaded document without reprocessing it.
-   [ ] **UI/UX Improvements:** Enhance the interface with better loading indicators, formatted source documents, and the ability to clear the session/upload a new file.
-   [ ] **Configurable Models:** Allow users to select different language or embedding models from a dropdown menu.