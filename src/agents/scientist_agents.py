import os
from crewai import Agent
from groq import Groq
from langchain_groq import ChatGroq
from src.tools.custom_tools import SCIENTIST_TOOLS
from dotenv import load_dotenv

load_dotenv()

# --- LLM Setup ---
# Using Groq client initialized via LangChain for cost-effective, high-speed execution.
llm_model = ChatGroq(
    temperature=0.1,
    client=Groq(api_key=os.getenv("GROQ_API_KEY")),
    model_name="llama3-8b-8192" # Fast, powerful, and free-to-use open model
)

class ScientistAgents:
    """
    Defines the roles and responsibilities for the AI Co-Scientist Crew.
    """
    def __init__(self):
        self.llm = llm_model
        # All agents share the same set of tools for maximum flexibility, 
        # but their roles guide which tools they primarily use.

    def hypothesis_planner(self):
        return Agent(
            role="Hypothesis Planner and Workflow Orchestrator",
            goal="Analyze the user's research query, define a novel hypothesis, and create the multi-step execution plan using the Composio meta-tool.",
            backstory="You are the Lead Principal Investigator. Your job is to transform vague scientific ideas into concrete, testable plans. You MUST use the 'CreateWorkflowPlan' tool FIRST to start the process and get a session ID.",
            verbose=True,
            allow_delegation=False,
            tools=[t for t in SCIENTIST_TOOLS if t.name == "CreateWorkflowPlan"],
            llm=self.llm
        )

    def literature_and_data_acquisition_agent(self):
        return Agent(
            role="Literature Review and Data Acquisition Specialist",
            goal="Execute parallel searches for prior art and relevant data (Arxiv, PubChem) and ensure all raw, large data payloads are stored in the Composio Workbench.",
            backstory="You are the Lab Technician responsible for gathering information. Your critical function is running simultaneous, high-throughput data collection using the 'ExecuteParallelResearch' tool.",
            verbose=True,
            allow_delegation=False,
            # This agent must have access to the parallel execution tool
            tools=[t for t in SCIENTIST_TOOLS if t.name == "ExecuteParallelResearch"],
            llm=self.llm
        )

    def analysis_and_protocol_agent(self):
        return Agent(
            role="Data Analysis and Experimental Protocol Designer",
            goal="Retrieve raw data keys from the Workbench, execute custom Python scripts for data cleaning/analysis using the Remote Bash tool, and draft the final experimental protocol based on findings.",
            backstory="You are the Computational Biologist. You specialize in retrieving large datasets from remote storage (Workbench) and executing complex scripts via the 'RunRemoteDataAnalysis' tool to produce validated findings.",
            verbose=True,
            allow_delegation=True, # Can delegate the final reporting task
            # This agent needs both the analysis tool and the documentation tool for drafting the protocol.
            tools=[t for t in SCIENTIST_TOOLS if t.name in ["RunRemoteDataAnalysis", "PublishFinalReport"]],
            llm=self.llm
        )

    def synthesis_and_reporting_agent(self):
        return Agent(
            role="Final Synthesis and Publication Editor",
            goal="Take the finalized hypothesis, protocol draft, and analysis results to generate a comprehensive FinalSynthesis report and publish it using the appropriate meta-tool.",
            backstory="You are the Journal Editor. You enforce structured Pydantic output and ensure the report is auditable, well-cited, and ready for publication using the 'PublishFinalReport' tool.",
            verbose=True,
            allow_delegation=False,
            # This agent only needs the final publishing tool
            tools=[t for t in SCIENTIST_TOOLS if t.name == "PublishFinalReport"],
            llm=self.llm
        )
