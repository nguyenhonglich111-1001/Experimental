## Overview
A personal laboratory for rapid experimentation with AI, focusing on Natural Language Processing (NLP), Generative AI, and supporting technologies. The goal is to build a collection of independent, runnable tools and minimal use cases for future development and reference.

## Scope
- Each tool is self-contained and runnable (preferably via Streamlit)
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
- AI framework: LangGraph (with OpenRouter AI API)
- Supports Agent-to-Agent (A2A) protocol for AI agents to communicate with each others ("Supervisor" architecture)
- Supports Model Context Protocol (MCP) servers integration (for AI agents to use tool call)
- Expose API for frontend (nextjs) interaction (support streaming request)
- Database: PostgreSQL
- Cloud storage: Cloudflare R2 bucket

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
* https://langchain-ai.github.io/langgraph/concepts/multi_agent/
* https://github.com/langchain-ai/langgraph
* https://github.com/a2aproject/A2A/tree/main
* https://openrouter.ai/docs/quickstart
* https://www.relari.ai/blog/ai-agent-framework-comparison-langgraph-crewai-openai-swarm
* https://langchain-ai.github.io/langgraph/agents/mcp/
* https://modelcontextprotocol.io/introduction
* https://github.com/modelcontextprotocol/python-sdk

## Instructions
* always store relevent data, application's states, user's states,... in database (PostgreSQL)
* always create/update `PROJECT_OVERVIEW.md` after every task with:
    * project structure (use `tree -L 3 -I 'node_modules|.git|.next'` to generate, then explain the directories briefly)
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
* always commit your code after finishing fixing a bug or implementing a feature completely (DO NOT commit `.env` file)
* always run the development environment in another process and export logs to `./server.log` (view this file to check the logs and debug)
* always name the main application file of each project `server.py`