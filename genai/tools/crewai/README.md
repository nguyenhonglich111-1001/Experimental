# 🧬 Genetic Research with CrewAI

This is a minimal CrewAI application with a Streamlit user interface, designed to perform genetic research and analysis based on a user-provided topic.

## Project Structure

```
project-root/
│
├── app.py                # Streamlit UI entry point
├── crew_logic.py         # CrewAI agents, tasks, and crew definition
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Setup and Installation

1.  **Navigate to the project directory:**
    ```bash
    cd genai/tool/crewai
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up your Serper API Key (if you plan to use web search):**
    The `crew_logic.py` file uses `SerperDevTool` for web searching. You need to set your Serper API key as an environment variable.
    
    *   **Windows:**
        ```bash
        set SERPER_API_KEY=YOUR_SERPER_API_KEY
        ```
    *   **macOS/Linux:**
        ```bash
        export SERPER_API_KEY=YOUR_SERPER_API_KEY
        ```
    
    Replace `YOUR_SERPER_API_KEY` with your actual Serper API key. You can get one from [Serper](https://serper.dev/). If you don't set this, the `SerperDevTool` will not function.

## Running the Application

Once the setup is complete and your virtual environment is activated, run the Streamlit application:

```bash
streamlit run app.py
```

This command will open the Streamlit application in your web browser (usually at `http://localhost:8501`).

## How to Use

1.  Open the application in your browser.
2.  Enter a genetic research topic in the input box (e.g., "CRISPR gene editing", "mRNA vaccines", "human genome project advancements").
3.  Click the "Start Genetic Research" button.
4.  The CrewAI agents will then perform the research and analysis. A loading spinner will indicate progress.
5.  Once complete, the "Research Summary" will be displayed on the page.

## Customization

You can modify the `crew_logic.py` file to:

-   Adjust the roles and goals of the `Genetic Research Specialist` and `Genetic Data Analyst`.
-   Change the tasks `research_task` and `analysis_task` descriptions.
-   Integrate different tools for the agents by modifying the `tools` list in the agent definitions. You'll need to install the corresponding `crewai_tools`.

Remember to install any new tool dependencies in `requirements.txt`. 