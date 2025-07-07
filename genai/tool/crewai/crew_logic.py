from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Ensure these are set in your .env file
# For example:
# OPENAI_API_KEY="your_openai_api_key_here"
# SERPER_API_KEY="your_serper_api_key_here"
# GOOGLE_API_KEY="your_google_api_key_here"

# It's good practice to set them if they are not already set in the environment
# but for passing to ChatGoogleGenerativeAI, we will directly use os.getenv
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") # Keep if other parts rely on it
# os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY") # Keep if other parts rely on it

# Get Google API Key directly from environment
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize Gemini LLM by explicitly passing the API key
gemini_llm = ChatGoogleGenerativeAI(model="google/gemini-pro", google_api_key=google_api_key) # Changed model to "google/gemini-pro"

def run_genetic_crew(topic: str) -> str:
    """
    Runs a CrewAI workflow for genetic research and analysis.
    """
    # Initialize the search tool
    search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY")) # Ensure Serper API key is also passed explicitly if needed

    # Define specialized agents
    genetic_researcher = Agent(
        role="Genetic Research Specialist",
        goal=f"Gather comprehensive and up-to-date information on {topic} in genetics",
        backstory=(
            "You are a leading expert in genetic research, highly skilled in "
            "finding relevant scientific papers, studies, and breakthroughs "
            "related to specific genetic topics. You use advanced search techniques "
            "to ensure accuracy and completeness."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=gemini_llm # Assign Gemini LLM here
    )

    genetic_analyst = Agent(
        role="Genetic Data Analyst",
        goal=f"Analyze and synthesize genetic research data on {topic} into actionable insights",
        backstory=(
            "You are a meticulous genetic data analyst, proficient in interpreting "
            "complex genetic information, identifying key patterns, and summarizing "
            "findings into clear, concise reports. You excel at extracting the "
            "most critical information for further study or application."
        ),
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm # Assign Gemini LLM here
    )

    # Define tasks for each agent
    research_task = Task(
        description=f"Conduct a thorough search and gather all pertinent information about '{topic}' in genetic research. "
                    "Focus on recent discoveries, significant studies, and potential implications. "
                    "Compile findings into detailed bullet points.",
        expected_output="A detailed bulleted list of recent genetic research findings and studies on the given topic.",
        agent=genetic_researcher
    )

    analysis_task = Task(
        description=f"Based on the research findings about '{topic}', analyze and synthesize the information. "
                    "Identify the most important breakthroughs, potential applications, and any unresolved questions. "
                    "Present a concise summary of the key insights and their significance.",
        expected_output="A concise summary (2-3 paragraphs) highlighting key breakthroughs, applications, and open questions related to the genetic research topic.",
        agent=genetic_analyst,
        context=[research_task]
    )

    # Create the crew
    genetic_crew = Crew(
        agents=[genetic_researcher, genetic_analyst],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )

    # Kick off the crew
    result = genetic_crew.kickoff()
    return str(result)

if __name__ == '__main__':
    # Example usage (for testing the crew_logic directly)
    print("Running genetic research crew for 'CRISPR gene editing'...")
    output = run_genetic_crew(topic="CRISPR gene editing")
    print("\n---" + " Crew Output ---\n")
    print(output) 