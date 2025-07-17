# Atomic Agents-Powered PDF Book Q&A (Streamlit)

## Task Overview

This document outlines the implementation of a Streamlit-based web application that enables users to upload PDF books and interact with an AI agent to ask questions about the book's content. The core of the AI functionality is built using the `atomic-agents` framework, leveraging Google Gemini (via OpenAI-compatible API with `instructor`) for natural language understanding and generation, and `PyPDF2` for PDF text extraction.

## Features Implemented

*   **Streamlit User Interface:** A responsive and interactive web interface for file uploads and chat interactions.
*   **PDF Upload and Processing:** Users can upload PDF files, which are then processed to extract their text content.
*   **Atomic Agent Integration:** A `BookQAAgent` is implemented using `atomic-agents` to manage the conversation flow and interact with the LLM.
*   **Custom PDF Tool:** A `PDFReaderTool` (inheriting from `atomic-agents`' `BaseTool`) is created to encapsulate PDF text extraction logic.
*   **Google Gemini Integration:** The `BookQAAgent` is configured to use Google Gemini (via `openai` and `instructor`) for its language model capabilities.
*   **Streaming Responses:** The AI agent's responses are streamed to the Streamlit UI for a better user experience.
*   **Conversation Memory:** The agent maintains a memory of the conversation, allowing for follow-up questions based on the previously loaded PDF content.

## Technical Details

### Project Structure

```
nlp/tools/atomic-pdf-qa-streamlit/
├── .env_example
├── README.md
├── requirements.txt
├── server.py
├── pdf_tool.py
└── book_qa_agent.py
```

*   `server.py`: The main Streamlit application file, handling UI, file uploads, and orchestrating interactions with the `BookQAAgent`.
*   `pdf_tool.py`: Defines the `PDFReaderTool` for extracting text from PDF files.
*   `book_qa_agent.py`: Defines the `BookQAAgent`, which uses the `PDFReaderTool` and interacts with the Google Gemini LLM to answer questions based on PDF content.
*   `requirements.txt`: Lists all Python dependencies specific to this project.
*   `.env_example`: Provides an example for setting up the `GEMINI_API_KEY` environment variable.
*   `README.md`: Provides setup, installation, and usage instructions for the project.

### Key Components and Interactions

1.  **`server.py` (Streamlit App):**
    *   Uses `st.file_uploader` to accept PDF files.
    *   Saves uploaded PDFs to a temporary directory.
    *   Initializes the `BookQAAgent` (cached with `@st.cache_resource`) and passes the PDF file path to it.
    *   Manages chat history using `st.session_state`.
    *   Uses `st.chat_input` for user questions and `st.chat_message` to display conversation turns.
    *   Calls the `BookQAAgent`'s `_run` method (which is an `async generator`) and streams its output to `st.markdown`.

2.  **`pdf_tool.py` (`PDFReaderTool`):**
    *   A custom `atomic-agents` `BaseTool`.
    *   Takes a `file_path` as input.
    *   Uses `PyPDF2.PdfReader` to extract text from the PDF.
    *   Returns the extracted text content.

3.  **`book_qa_agent.py` (`BookQAAgent`):**
    *   An `atomic-agents` `BaseAgent`.
    *   Configured with an `OpenAI` client (patched by `instructor`) pointing to the Google Gemini API.
    *   Maintains `AgentMemory` for conversational context.
    *   Its `_run` method: 
        *   If a new PDF path is provided, it uses the `PDFReaderTool` to read the content and adds it to the agent's system prompt/memory.
        *   Constructs a prompt for the LLM, including the PDF content and the user's question.
        *   Interacts with the Gemini LLM, enabling streaming (`stream=True`).
        *   **Yields** chunks of the LLM's response, allowing `server.py` to display them in real-time.
        *   Adds the complete LLM response to its `AgentMemory` for subsequent turns.

## Todos / Future Enhancements

*   **Large PDF Handling (Chunking & Vector Store):** For very large PDFs, passing the entire content to the LLM's context window is inefficient and can hit token limits. Implement a proper RAG (Retrieval Augmented Generation) system:
    *   Integrate a text splitter (e.g., `RecursiveCharacterTextSplitter`) to break down PDF content into smaller, semantically meaningful chunks.
    *   Utilize a vector database (e.g., ChromaDB, already in the project's dependencies) to store embeddings of these chunks.
    *   Modify `BookQAAgent` to perform a similarity search against the vector store based on the user's query, retrieving only the most relevant chunks to pass to the LLM.
*   **Error Handling & User Feedback:** Enhance error messages and provide more robust feedback to the user for issues like invalid PDF files, API key problems, or LLM errors.
*   **Temporary File Cleanup:** Implement a more robust mechanism for cleaning up temporary PDF files after they are processed or when the Streamlit session ends.
*   **UI Enhancements:** Add a loading indicator during PDF processing and response generation.
*   **Multi-turn Conversation with Contextual Retrieval:** Refine how the agent uses its memory and retrieves context from the PDF for complex, multi-turn conversations.
*   **Cost Monitoring:** Integrate a mechanism to track token usage and estimated costs for LLM interactions.
