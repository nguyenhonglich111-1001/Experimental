from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Ensure GOOGLE_API_KEY and SERPER_API_KEY are set in your .env file
# For example:
# SERPER_API_KEY="your_serper_api_key_here"
# GOOGLE_API_KEY="your_google_api_key_here"

# Get API Keys directly from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
if not serper_api_key:
    raise ValueError(
        "SERPER_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize Gemini LLM by explicitly passing the API key
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash-preview-04-17", 
    google_api_key=gemini_api_key
)

def test_llm_response():
    response = gemini_llm.call("Say hello and tell me your model name.")
    print("LLM Test Response:\n", response)


def run_genetic_crew(topic: str) -> str:
    """
    Runs a CrewAI workflow for genetic research and analysis.
    """
    # Initialize the search tool
    search_tool = SerperDevTool(api_key=serper_api_key)

    # Define specialized agents
    senior_research_specialist = Agent(
        role="Senior Research Specialist",
        goal=f"Gather comprehensive and up-to-date information on {topic}",
        backstory=(
            "You are a leading expert in research, highly skilled in "
            "finding relevant papers, studies, and breakthroughs "
            "related to any given topic. You use advanced search techniques "
            "to ensure accuracy and completeness."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
    )

    research_analyst = Agent(
        role="Research Analyst and Report Writer",
        goal=f"Analyze and synthesize research data on {topic} into actionable insights and comprehensive reports",
        backstory=(
            "You are a meticulous research analyst, proficient in interpreting "
            "complex information, identifying key patterns, and summarizing "
            "findings into clear, concise reports. You excel at extracting the "
            "most critical information for further study or application."
        ),
        verbose=True,
        llm=gemini_llm  # Assign Gemini LLM here
    )

    quality_assurance_reviewer = Agent(
        role="Quality Assurance Reviewer",
        goal=f"Ensure the research findings and analysis on {topic} are accurate, well-supported, and meet high standards of clarity and completeness",
        backstory=(
            "You are an experienced fact-checker and editor, meticulous in reviewing "
            "research outputs for accuracy, logical flow, and adherence to the "
            "research objectives. You ensure all information is credible and "
            "presented clearly."
        ),
        verbose=True,
        llm=gemini_llm # Assign Gemini LLM here
    )

    # Define tasks for each agent
    research_task = Task(
        description=f"Conduct a thorough search and gather all pertinent information about '{topic}'. "
        "Focus on recent discoveries, significant studies, and potential implications. "
        "Compile findings into detailed bullet points.",
        expected_output="A detailed bulleted list of recent research findings and studies on the given topic.",
        agent=senior_research_specialist
    )

    analysis_task = Task(
        description=f"Based on the research findings about '{topic}', analyze and synthesize the information. "
        "Identify the most important breakthroughs, potential applications, and any unresolved questions. "
        "Present a concise summary of the key insights and their significance.",
        expected_output="A concise summary (2-3 paragraphs) highlighting key breakthroughs, applications, and open questions related to the research topic.",
        agent=research_analyst,
        context=[research_task]
    )

    review_task = Task(
        description=f"Review the research analysis and summary on '{topic}' for accuracy, completeness, and clarity. "
        "Provide constructive feedback and suggest improvements if necessary. "
        "Ensure the final output is polished and ready for presentation.",
        expected_output="A reviewed and refined summary of the research findings, ensuring high quality and accuracy.",
        agent=quality_assurance_reviewer,
        context=[analysis_task]
    )

    # Create the crew
    research_crew = Crew(
        agents=[senior_research_specialist, research_analyst, quality_assurance_reviewer],
        tasks=[research_task, analysis_task, review_task],
        process=Process.sequential,
        verbose=True
    )

    # Kick off the crew
    result = genetic_crew.kickoff()
    return str(result)


if __name__ == '__main__':
    # Example usage (for testing the crew_logic directly)
    test_llm_response()
    print("Running general research crew for 'AI in healthcare'...")
    output = run_research_crew(topic="AI in healthcare")
    print("\n---" + " Crew Output ---\n")
    print(output)
