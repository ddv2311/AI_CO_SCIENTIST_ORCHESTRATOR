import json
from crewai import Task
from src.tools.custom_tools import SCIENTIST_TOOLS
from src.models import ResearchQuery, ToolExecutionRequest

class ScientistTasks:
    """
    Defines the sequential tasks that drive the AI Co-Scientist workflow.
    Each task's expected output becomes the input for the next.
    """
    def __init__(self, research_query: ResearchQuery):
        self.query = research_query

    def plan_workflow_task(self, agent) -> Task:
        """
        Task 1: Hypothesis Agent. 
        ACTION: Use the CreateWorkflowPlan tool to initiate the workflow and get a session ID.
        """
        query_json = self.query.json()
        return Task(
            description=(
                f"Formalize the request (Topic: {self.query.topic}, Output: {self.query.target_output}) into a novel hypothesis. "
                f"CRITICAL: You MUST use the 'CreateWorkflowPlan' tool with the following JSON input: {query_json}. "
                "The output must be the full plan result, including the Composio session_id."
            ),
            expected_output="The full structured workflow plan and the Composio session_id.",
            agent=agent,
            tools=[t for t in SCIENTIST_TOOLS if t.name == "CreateWorkflowPlan"],
        )

    def parallel_research_task(self, agent) -> Task:
        """
        Task 2: Literature Agent. 
        ACTION: Use the ExecuteParallelResearch tool for concurrent data collection and Workbench storage.
        """
        # Example JSON structure to guide the LLM's tool call argument
        example_requests = [
            ToolExecutionRequest(
                tool_slug="ARXIV_SEARCH", 
                arguments={"query": f"{self.query.topic} prior art", "max_results": 5}
            ),
            ToolExecutionRequest(
                tool_slug="PUBCHEM_QUERY", 
                arguments={"keywords": self.query.keywords, "compound_type": "delivery vehicle"}
            )
        ]
        requests_json = json.dumps([req.dict() for req in example_requests], indent=2)

        return Task(
            description=(
                "Obtain the session_id from the previous task's result. "
                "CRITICAL: You MUST use the 'ExecuteParallelResearch' tool. "
                f"Pass the session_id and a JSON list of requests similar to this structure: {requests_json}. "
                "This step showcases parallel execution and Workbench storage."
            ),
            expected_output="A summary of the parallel execution results, including the list of Workbench Keys (JSON list of strings) for the raw data.",
            agent=agent,
            tools=[t for t in SCIENTIST_TOOLS if t.name == "ExecuteParallelResearch"],
        )

    def data_analysis_task(self, agent) -> Task:
        """
        Task 3: Analysis Agent. 
        ACTION: Use the RunRemoteDataAnalysis tool (Remote Bash) to process Workbench data.
        """
        return Task(
            description=(
                "Retrieve the JSON list of Workbench Keys from the previous task's output. "
                "CRITICAL: You MUST use the 'RunRemoteDataAnalysis' tool, passing the JSON list of keys. "
                "This action simulates retrieval from the Workbench and execution of custom analysis code (data cleaning and risk filtering)."
            ),
            expected_output="The final structured analysis output (JSON string) from the remote execution, including 'final_clean_compounds' and 'summary'.",
            agent=agent,
            tools=[t for t in SCIENTIST_TOOLS if t.name == "RunRemoteDataAnalysis"],
        )

    def final_reporting_task(self, agent) -> Task:
        """
        Task 4: Reporting Agent. 
        ACTION: Synthesize all findings into the FinalSynthesis model and publish.
        """
        return Task(
            description=(
                "Synthesize the initial hypothesis, the parallel research summary, and the structured analysis result. "
                "Draft a detailed experimental protocol based on the consolidated data. "
                "CRITICAL: You MUST output a JSON string that conforms exactly to the 'FinalSynthesis' Pydantic model. "
                "You MUST then use the 'PublishFinalReport' tool, passing this FinalSynthesis JSON string."
            ),
            expected_output="The URL and confirmation message of the published, finalized report.",
            agent=agent,
            tools=[t for t in SCIENTIST_TOOLS if t.name == "PublishFinalReport"],
            output_file="final_scientific_report.txt"
        )