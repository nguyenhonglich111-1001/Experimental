# PROJECT OVERVIEW

This document provides a comprehensive overview of the "Experimental" project, including its structure, features, and technical components, as of 2025-07-17.

## Project Structure
```
.
├── GEMINI.md
├── PROJECT_OVERVIEW.md
├── README.md
├── data.json
├── docs
│   ├── ...
│   └── octomind-testing-experiment.md
├── genai
│   └── ...
├── memory-bank
│   └── ...
├── nlp
│   ├── ...
│   └── tools/
│       └── atomic-pdf-qa-streamlit/
├── tech-enhancements
│   └── tools
│       └── smart-notes-app
├── requirements.txt
├── ...
```

### Directory Explanations:

-   **docs/:** Contains detailed documentation for each feature and workflow within the project.
-   **genai/:** Houses tools and components related to Generative AI.
-   **memory-bank/:** Stores context and memory files for the AI agent.
-   **nlp/:** Contains Natural Language Processing tools.
    -   `nlp/tools/atomic-pdf-qa-streamlit/`: A Streamlit application for PDF book Q&A using Atomic Agents.
-   **tech-enhancements/:** Contains tools and infrastructure to enhance AI development, such as testing tools.
    -   `tech-enhancements/tools/smart-notes-app/`: A web app for the Octomind testing experiment.
-   **utils/:** Contains utility scripts and helper modules for the project.
-   **xnotes/:** Stores miscellaneous development notes, prompts, and ideas.

## Features

*   **Atomic Agents-Powered PDF Book Q&A (Streamlit):**
    *   **Functionality:** A Streamlit web application that allows users to upload a PDF book and ask questions about its content, receiving intelligent, streaming answers.
    *   **Technology:** Streamlit, Atomic Agents, PyPDF2, Google Gemini API (via OpenAI-compatible API with Instructor).
*   **Smart Notes Web App & Octomind Experiment:**
    *   **Functionality:** A simple web application for creating, managing, and summarizing notes. This app serves as the testbed for experimenting with the Octomind AI-powered testing tool.
    *   **Technology:** Flask, Bootstrap, Google Gemini API.
*   **LangChain-Powered Book Q&A:**
    *   **File Type:** PDF
    *   **Functionality:** Allows users to upload a PDF book and ask questions about its content.
    *   **Technology:** LangChain, Chroma, Streamlit, Google Gemini.
*   **Generalized Research Crew:**
    *   **Functionality:** A flexible CrewAI setup for comprehensive data research, analysis, and quality assurance.
    *   **Technology:** CrewAI, LangGraph.
*   **File Upload and Docling Processing:**
    *   **Functionality:** A basic Streamlit application for uploading and processing various file formats.
    *   **Technology:** Streamlit, Docling.

## Dependencies

*   **Programming Language:** Python
*   **Primary AI Frameworks:** LangChain, LangGraph, CrewAI, Atomic Agents
*   **LLM APIs:** Google Generative AI (Gemini API), OpenRouter
*   **Vector Stores / Search:** Chroma (persistent)
*   **Web Frameworks:** Flask
*   **Frontend/UI:** Streamlit, Bootstrap
*   **Database:** PostgreSQL (planned)
*   **Cloud Storage:** Cloudflare R2 (planned)

## Changelog

*   **2025-07-17:** Implemented the "Atomic Agents-Powered PDF Book Q&A (Streamlit)" feature, including `pdf_tool.py`, `book_qa_agent.py`, and `server.py`. Updated `requirements.txt` and project overview.
*   **2025-07-17:** Initial project setup and documentation.
*   **2025-07-17:** Reconstructed Technical Requirements in GEMINI.md based on inner project scans.
*   **2025-07-16:** Prevented redundant PDF reprocessing on chat interactions in the `langchain-file-processor` tool.
*   **2025-07-16:** Implemented smarter chunking with metadata extraction and a progress bar for the book Q&A tool.
*   **2025-07-16:** Updated `ChatGoogleGenerativeAI` and `RecursiveCharacterTextSplitter` to use best practices.
*   **2025-07-16:** Replaced FAISS with Chroma in the `langchain-file-processor` tool.
*   **2025-07-16:** Updated project structure in `PROJECT_OVERVIEW.md`.
*   **2025-07-15:** Detailed and documented the `langchain-file-processor` tool. Created documentation and updated the project overview.
*   **2025-07-09:** Enforced `server.py` naming convention for main application files.
*   **2025-07-09:** Added Streamlit-based File Upload and Docling Processing project.
*   **2025-07-08:** Initial creation of `PROJECT_OVERVIEW.md`.
