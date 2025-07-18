## Overview
A personal laboratory for rapid experimentation with AI, focusing on Natural Language Processing (NLP), Generative AI, and supporting technologies. The goal is to build a collection of independent, runnable tools and minimal use cases for future development and reference.

## Scope
- Each tool is self-contained and runnable (Most of the time is Streamlit)
- Organized by theme (NLP, GenAI, Tech Enhancements)
- Designed for easy extension and reuse
- Not intended for production, but for learning, prototyping, and inspiration

## Goals
- Quickly prototype and test AI ideas
- Build a reusable library of minimal, runnable AI tools
- Document experiments and learnings for future reference

## Technical Requirements
- Programming language: Python
- Store variables in `.env` file
- AI frameworks/libraries: LangGraph, CrewAI, LangChain, Google Generative AI (google-generativeai), Docling, EasyOCR, VoyageAI
- API Integrations: OpenRouter AI API, Google Gemini API, Serper API
- Supports Agent-to-Agent (A2A) protocol for AI agents to communicate with each others ("Supervisor" architecture)
- Supports Model Context Protocol (MCP) servers integration (for AI agents to use tool call)
- Expose API for frontend (Next.js) interaction (support streaming request)
- Database: PostgreSQL, MongoDB, ChromaDB (for vector store), In-memory JSON file (for Smart Notes App)
- Cloud storage: Cloudflare R2 bucket
- UI Frameworks: Streamlit
- Other: Text splitting (RecursiveCharacterTextSplitter), PDF processing (PyPDFLoader)

## Environment Variables (Development Environment / localhost)

```
DATABASE_URL=""
OPENROUTER_API_KEY=""
MONGO_URI=""
VOYAGE_API_KEY=""
...
```

## Documentations & References
* https://docs.crewai.com/en
* https://github.com/BrainBlend-AI/atomic-agents

## Instructions
* always follow the `python_rules.md` for Python coding standards overall
* always use `instruction_rules.md` in each inner project as a reference for coding and project management
* always store relevent data, application's states, user's states,... in database (PostgreSQL)
* always create/update `PROJECT_OVERVIEW.md` after every task with:
    * features
    * dependencies
    * api routes
    * changelog
* always check `PROJECT_OVERVIEW.md` before starting a new task
* always create/update `docs/<feature_name>.md` after every feature implementation with task overview and todos
* always use `context7` MCP tool to study dependencies/plugins/frameworks' docs carefully while implementing them
* always implement error catching handler
* always implement user-friendly flows
* always follow security best practices
* always use the model "gemini-2.5-flash-lite-preview-06-17" when using the Gemini API
* always commit your code after finishing fixing a bug or implementing a feature completely (DO NOT commit `.env` file)
* **Commit Workflow:**
    1.  **Write to File:** Always first write the complete, multi-line commit message to a temporary file named `.git_commit_message.txt` in the project root.
    2.  **Commit from File:** Always execute the commit using the command `git commit -F .git_commit_message.txt`.
    3.  **Do Not Delete:** The `.git_commit_message.txt` file should not be deleted after the commit to allow for reuse.
* always commit your code, but let the user (you) handle the `git push` operation manually
* always run the development environment in another process and export logs to `./server.log` (view this file to check the logs and debug)
* always name the main application file of each project `server.py`
* always investigate all requirements.txt in smaller project and make the final requirements.txt in main directory contain all of them without duplicate library after creating or updating an inner project.
