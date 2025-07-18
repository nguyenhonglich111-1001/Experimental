# System Patterns

## Architecture
- Monorepo structure with top-level themes (nlp, genai, tech-enhancements)
- Each tool is a self-contained folder with its own code and documentation
- Shared utilities live in the utils/ directory
- Documentation and project context are managed in memory-bank/

## Key Technical Decisions
- Use Streamlit for rapid prototyping and UI
- Use HuggingFace Transformers and other popular AI libraries
- Keep each tool minimal and independent

## Design Patterns
- Modular: Each tool is independent and can be run or extended without affecting others
- Documentation-first: Every tool and experiment is documented
- Reusability: Shared code is placed in utils/ 