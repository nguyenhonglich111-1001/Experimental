# PROJECT OVERVIEW

This document provides a comprehensive overview of the "Experimental" project, including its structure, features, and technical components, as of 2025-07-15.

## Project Structure

```
.
├── .envGrab.py
├── .gitignore
├── GEMINI.md
├── PROJECT_OVERVIEW.md
├── README.md
├── requirements.txt
├── docs/
│   ├── file_upload_docling.md
│   ├── gemini-api-chatbot.md
│   ├── generalized_research_crew.md
│   ├── langchain-file-processor.md
│   └── workflow-rules.md
├── genai/
│   ├── README.md
│   └── tools/
│       └── crewai/
├── nlp/
│   ├── README.md
│   └── tools/
│       ├── docling-file-processor/
│       ├── gemini-api/
│       └── langchain-file-processor/
├── utils/
│   └── README.md
└── xnotes/
    ├── custom-agents.md
    └── project-idea-prompt.md
```

### Directory Explanations:

-   **docs/:** Contains detailed documentation for each feature and workflow within the project.
-   **genai/:** Houses tools and components related to Generative AI. Includes a `crewai` integration for multi-agent systems.
-   **nlp/:** Contains Natural Language Processing tools.
    -   `nlp/tools/docling-file-processor/`: A Streamlit app for general file processing.
    -   `nlp/tools/gemini-api/`: A tool for interacting with the Gemini API.
    -   `nlp/tools/langchain-file-processor/`: A Streamlit app for asking questions about an uploaded PDF.
-   **utils/:** Contains utility scripts and helper modules for the project.
-   **xnotes/:** Stores miscellaneous development notes, prompts, and ideas.

## Features

*   **LangChain-Powered File Q&A:**
    *   **File Type:** PDF
    *   **Functionality:** Allows users to upload a PDF and ask questions about its content.
    *   **Technology:** Uses LangChain for document loading, `FAISS` for in-memory vector search, and Google's Gemini model for question answering. The interface is built with Streamlit.
*   **Generalized Research Crew:**
    *   **Functionality:** A flexible CrewAI setup for comprehensive data research, analysis, and quality assurance.
    *   **Technology:** CrewAI, LangGraph.
*   **File Upload and Docling Processing:**
    *   **Functionality:** A basic Streamlit application for uploading and processing various file formats.
    *   **Technology:** Streamlit, Docling.

## Dependencies

*   **Programming Language:** Python
*   **Primary AI Frameworks:** LangChain, LangGraph, CrewAI
*   **LLM APIs:** Google Generative AI, OpenRouter
*   **Vector Stores / Search:** FAISS (in-memory)
*   **PDF/Document Parsing:** PyPDF
*   **Frontend/UI:** Streamlit
*   **Database:** PostgreSQL (planned)
*   **Cloud Storage:** Cloudflare R2 (planned)

## Changelog

*   **2025-07-15:** Detailed and documented the `langchain-file-processor` tool. Created documentation and updated the project overview.
*   **2025-07-09:** Enforced `server.py` naming convention for main application files.
*   **2025-07-09:** Added Streamlit-based File Upload and Docling Processing project.
*   **2025-07-08:** Initial creation of `PROJECT_OVERVIEW.md`.
