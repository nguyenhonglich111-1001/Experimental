# Atomic PDF Book Q&A (Streamlit)

This project implements a Streamlit web application that allows users to upload a PDF book and ask questions about its content. It leverages the `atomic-agents` framework for building the AI agent, `PyPDF2` for PDF text extraction, and Google Gemini (via `openai` and `instructor`) for generating intelligent responses.

## Features

*   **PDF Upload:** Easily upload PDF documents through a user-friendly interface.
*   **AI-Powered Q&A:** Ask natural language questions about the content of the uploaded PDF.
*   **Streaming Responses:** Get real-time, word-by-word responses from the AI agent.
*   **Conversation Memory:** The agent maintains conversation context for follow-up questions.

## Technologies Used

*   **Streamlit:** For building the interactive web user interface.
*   **Atomic Agents:** The core framework for orchestrating the AI agent logic.
*   **PyPDF2:** For efficient extraction of text from PDF documents.
*   **Google Gemini API:** (Accessed via `openai` and `instructor` libraries) For large language model capabilities.
*   **Python-dotenv:** For managing environment variables securely.

## Setup and Installation

1.  **Navigate to the project directory:**

    ```bash
    cd nlp/tools/atomic-pdf-qa-streamlit
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **On Windows:**

        ```bash
        .\venv\Scripts\activate
        ```

    *   **On macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure your API Key:**

    Create a `.env` file in the `nlp/tools/atomic-pdf-qa-streamlit` directory (the same directory as `server.py`) and add your Google Gemini API key:

    ```
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

    Replace `your_gemini_api_key_here` with your actual API key.

## How to Run

1.  **Ensure your virtual environment is activated** (as per setup steps).

2.  **Navigate to the project directory:**

    ```bash
    cd nlp/tools/atomic-pdf-qa-streamlit
    ```

3.  **Run the Streamlit application:**

    ```bash
    streamlit run server.py
    ```

    This will open the application in your web browser.

## Usage

1.  **Upload a PDF file** using the file uploader on the sidebar.
2.  Once the PDF is processed, you can **type your questions** in the chat input box at the bottom.
3.  The AI agent will respond based on the content of the uploaded PDF.

## Project Structure

```
nlp/tools/atomic-pdf-qa-streamlit/
├── .env_example
├── README.md
├── requirements.txt
├── server.py
├── pdf_tool.py
└── book_qa_agent.py
```
