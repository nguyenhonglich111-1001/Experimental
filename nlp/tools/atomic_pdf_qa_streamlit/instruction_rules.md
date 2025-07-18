Please adapt the globs depending on your project structure. Here are the best practices for each major library/framework found in your dependencies:

---
name: streamlit-best-practices.mdc
description: Best practices for Streamlit applications
globs: **/*.py
---

- Use caching to improve performance with `@st.cache_data` for expensive computations.
- Organize your app into functions to enhance readability and maintainability.
- Utilize session state to manage user interactions and data across reruns.
- Implement layout components (e.g., columns, sidebar) for better user experience.

---
name: atomic-agents-best-practices.mdc
description: Best practices for Atomic Agents framework
globs: **/*.py
---

- Define clear interfaces for agents to ensure modularity and reusability.
- Use environment variables for configuration to enhance security and flexibility.
- Implement logging for better debugging and monitoring of agent behavior.
- Regularly update agent models to adapt to changing environments.

---
name: pypdf2-best-practices.mdc
description: Best practices for working with PyPDF2
globs: **/*.py
---

- Always check for file integrity before processing PDFs to avoid errors.
- Use context managers when opening files to ensure proper resource management.
- Handle exceptions gracefully to manage issues with corrupted or unsupported PDF files.
- Optimize PDF merging and splitting by processing in batches when dealing with large documents.

---
name: python-dotenv-best-practices.mdc
description: Best practices for using python-dotenv for environment variables
globs: **/*.py
---

- Store sensitive information in a `.env` file and add it to `.gitignore`.
- Use `dotenv.load_dotenv()` at the start of your application to load environment variables.
- Validate environment variables to ensure required configurations are set.
- Keep the `.env` file organized and well-documented for easier maintenance.

---
name: instructor-best-practices.mdc
description: Best practices for using the Instructor library
globs: **/*.py
---

- Structure your training data clearly to facilitate easier model training.
- Use version control for your models and datasets to track changes over time.
- Implement logging to monitor training progress and performance metrics.
- Regularly evaluate and fine-tune models based on feedback and performance data.

---
name: openai-best-practices.mdc
description: Best practices for integrating OpenAI API
globs: **/*.py
---

- Use API keys securely by storing them in environment variables.
- Implement rate limiting and error handling to manage API usage effectively.
- Optimize prompt design to improve response quality and relevance.
- Monitor usage and costs regularly to avoid unexpected charges.