import os
from typing import List
from crewai import Crew
from dotenv import load_dotenv
from src.agents.scientist_agents import ScientistAgents
from src.tasks import ScientistTasks
from src.models import ResearchQuery
from src.tools.custom_tools import SCIENTIST_TOOLS # Import the custom tools list

# Load environment variables (API keys)
load_dotenv()

def run_co_scientist_crew(user_topic: str, desired_output: str, keywords: List[str]):
    """
    Orchestrates the AI Co-Scientist crew to execute the end-to-end workflow.
    """
    print("--- Starting AI Co-Scientist Lab Orchestration ---")

    # 1. Instantiate Agents
    scientist_agents = ScientistAgents()
    hypothesis_agent = scientist_agents.hypothesis_planner()
    review_agent = scientist_agents.literature_and_data_acquisition_agent()
    analysis_agent = scientist_agents.analysis_and_protocol_agent()
    reporting_agent = scientist_agents.synthesis_and_reporting_agent()

    # 2. Define the Research Query (Validated Input)
    research_query = ResearchQuery(
        topic=user_topic,
        target_output=desired_output,
        keywords=keywords
    )

    # 3. Instantiate Tasks
    scientist_tasks = ScientistTasks(research_query=research_query)

    # Note: We use the methods from the tasks class to get the instances of Task objects
    plan_task = scientist_tasks.plan_workflow_task(hypothesis_agent)
    research_task = scientist_tasks.parallel_research_task(review_agent)
    analysis_task = scientist_tasks.data_analysis_task(analysis_agent)
    report_task = scientist_tasks.final_reporting_task(reporting_agent)

    # 4. Define the Crew (Orchestration)
    # CRITICAL: Pass the entire list of SCIENTIST_TOOLS to the crew.
    scientific_crew = Crew(
        agents=[
            hypothesis_agent,
            review_agent,
            analysis_agent,
            reporting_agent
        ],
        tasks=[
            plan_task,
            research_task,
            analysis_task,
            report_task
        ],
        tools=SCIENTIST_TOOLS, # Make all custom tools available
        verbose=2, # Shows detailed reasoning and tool usage
        process='sequential' 
    )

    # 5. Execute the Workflow
    print("\n\n--- Initiating Autonomous Workflow Execution ---")
    
    try:
        # CrewAI automatically handles passing the output of one task as input to the next.
        result = scientific_crew.kickoff()
        
        print("\n\n#############################################")
        print("  AI CO-SCIENTIST WORKFLOW COMPLETE! ")
        print("#############################################")
        print(f"\nFinal Result:\n{result}")
        print("\nCheck the final_scientific_report.txt file for the published URL.")

    except Exception as e:
        print(f"\n--- CRITICAL WORKFLOW FAILURE ---")
        print(f"Error during crew execution: {e}")
        print("Ensure GROQ_API_KEY and COMPOSIO_API_KEY are set.")


if __name__ == "__main__":
    # Example User Input for the Hackathon Demo
    example_topic = "A novel application of graphene quantum dots for localized drug delivery."
    example_output = "Drafting a full hypothesis, protocol summary, and prior art matrix."
    example_keywords = ["graphene quantum dots", "localized delivery", "biocompatibility", "nanomedicine"]
    
    if not os.getenv("GROQ_API_KEY") or not os.getenv("COMPOSIO_API_KEY"):
        print("\nFATAL ERROR: Please set GROQ_API_KEY and COMPOSIO_API_KEY in your .env file.")
    else:
        run_co_scientist_crew(example_topic, example_output, example_keywords)