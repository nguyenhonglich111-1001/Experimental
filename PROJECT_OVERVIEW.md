# PROJECT_OVERVIEW.md

## Project Structure

```
D:/LichNH/coding/Experimental/
├───.cursor/
│   ├───rules/
│   │   ├───core-rules/
│   │   ├───global-rules/
│   │   ├───tool-rules/
│   │   ├───ts-rules/
│   │   ├───ui-rules/
│   │   └───workflows/
│   │       ├───arch.mdc
│   │       ├───dev.mdc
│   │       ├───pm.mdc
│   │       └───workflow-agile-manual.mdc
│   ├───templates/
│   │   ├───mode-format.md
│   │   ├───template-arch.md
│   │   ├───template-prd.md
│   │   └───template-story.md
│   ├───mcp.json
│   └───modes.json
├───docs/
│   └───workflow-rules.md
├───genai/
│   ├───tool/
│   ├───tools/
│   │   └───crewai/
│   │       ├───__pycache__/
│   │       ├───venv_crewai/
│   │       ├───.env_example
│   │       ├───app.py
│   │       ├───crew_logic.py
│   │       ├───README.md
│   │       └───requirements.txt
│   └───README.md
├───memory-bank/
���   ├───.gitkeep
│   ├───activeContext.md
│   ├───productContext.md
│   ├───progress.md
│   ├───projectbrief.md
│   ├───systemPatterns.md
│   └───techContext.md
├───nlp/
│   ├───tools/
│   │   └───gemini-api/
│   │       ├───README.md
│   │       └───streamlit_app.py
│   ├───.gitkeep
│   └───README.md
├───tech-enhancements/
│   └───README.md
├───utils/
│   └───README.md
├───venv/
├───xnotes/
│   ├───custom-agents.md
│   └───project-idea-prompt.md
├───.cursorignore
├───.cursorindexingignore
├───.gitignore
├───GEMINI.md
├───README.md
├───requirements.txt
└───test.py
```

### Directory Explanations:
- **.cursor/:** Contains configuration files and rules for the Cursor editor, including core rules, global rules, tool-specific rules, TypeScript rules, UI rules, and workflow definitions. Also includes templates for various document formats.
- **docs/:** Stores project documentation, such as workflow rules.
- **genai/:** Houses components related to generative AI, including tools for AI agents, specifically a `crewai` integration with its application logic, environment examples, and dependencies.
- **memory-bank/:** Contains various markdown files for project context, progress tracking, product briefs, system patterns, and technical context.
- **nlp/:** Contains natural language processing related components, including tools for Gemini API integration.
- **tech-enhancements/:** Directory for technical enhancements and related documentation.
- **utils/:** Contains utility scripts or modules.
- **venv/:** Python virtual environment for the main project.
- **xnotes/:** Contains miscellaneous notes, such as custom agent definitions and project idea prompts.

## Features

*   Create & manage AI crews easily (with a default supervisor agent, add/remove AI agents)
*   Create & manage AI agents easily (add/remove MCP tools)
*   Create & manage MCP servers easily (supports Streamable HTTP transport only)
*   Create & manage conversations with AI crews / AI agents easily
*   Able to monitor all the activity logs of AI crews and AI agents easily
*   Expose API for frontend (nextjs) interaction (support streaming request)
*   Expose Swagger API Docs for frontend integration instructions

## Dependencies

*   **Programming language:** Python
*   **AI framework:** LangGraph (with OpenRouter AI API)
*   **Database:** PostgreSQL
*   **Cloud storage:** Cloudflare R2 bucket
*   **Protocols:** Agent-to-Agent (A2A) protocol, Model Context Protocol (MCP)

## API Routes

*   API for frontend (nextjs) interaction (support streaming request)
*   Swagger API Docs for frontend integration instructions

## Changelog

*   **2025-07-08:** Initial creation of `PROJECT_OVERVIEW.md` based on `GEMINI.md` and project structure analysis.