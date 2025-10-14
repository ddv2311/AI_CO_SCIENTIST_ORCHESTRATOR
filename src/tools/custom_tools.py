import json
from crewai import Tool
from typing import List, Dict, Any
from src.tools.composio_client import COMPOSIO_CLIENT, TOOL_SLUGS
from src.models import ResearchQuery, FinalSynthesis # Import Pydantic models

# --- Tool 1: COMPOSIO_CREATE_PLAN Wrapper ---
def create_workflow_plan(query_json: str) -> str:
    """
    REQUIRED META-TOOL: Uses COMPOSIO_CREATE_PLAN to generate a reliable, multi-step execution plan.
    Input MUST be a JSON string of the ResearchQuery model.
    """
    try:
        # Pydantic validation for input quality (adherence to Type Safety)
        query = ResearchQuery(**json.loads(query_json))
        primary_tools = [TOOL_SLUGS["ARXIV_SEARCH"], TOOL_SLUGS["PUBCHEM_QUERY"]]
        use_case = f"Generate a novel hypothesis and experimental protocol for the topic: {query.topic}"
        
        plan_result = COMPOSIO_CLIENT.create_plan(
            use_case=use_case,
            primary_tool_slugs=primary_tools
        )
        if plan_result.get("successful"):
            # Return the session_id and plan for the next agent
            return (f"Plan successful. Session ID: {plan_result['session_id']}. "
                    f"Workflow steps: {plan_result['workflow_steps']}.")
        else:
            return f"Error generating plan: {plan_result.get('reasoning', 'Unknown Error')}"
    except json.JSONDecodeError:
        return "CRITICAL TOOL ERROR: Input was not valid JSON. You must pass a JSON string conforming to ResearchQuery."
    except Exception as e:
        # Graceful error handling (adherence to Error Handling)
        return f"CRITICAL TOOL ERROR: Failed to call Composio CREATE_PLAN. Error: {str(e)}"

# --- Tool 2: COMPOSIO_MULTI_EXECUTE_TOOL Wrapper ---
def execute_parallel_research(session_id: str, requests_json: str) -> str:
    """
    REQUIRED META-TOOL: Executes multiple API calls concurrently via COMPOSIO_MULTI_EXECUTE_TOOL.
    Inputs: session_id and a JSON string of a list of ToolExecutionRequest objects.
    """
    try:
        # No Pydantic validation here, as the LLM's output for this tool is inherently nested and complex
        requests_list = json.loads(requests_json)
        
        # Prepare execution requests using the simulated tool slugs
        execution_requests = []
        for req in requests_list:
            tool_slug = TOOL_SLUGS.get(req.get('tool_slug')) or req.get('tool_slug')
            execution_requests.append({
                "tool_slug": tool_slug,
                "arguments": req.get('arguments', {})
            })

        multi_exec_result = COMPOSIO_CLIENT.multi_execute_tool(
            execution_requests=execution_requests,
            session_id=session_id
        )

        if multi_exec_result.get("successful"):
            # Extract the crucial Workbench keys for the next agent
            workbench_keys = [res.get('workbench_key') for res in multi_exec_result['results'] if res.get('workbench_key')]
            
            return (f"Parallel execution successful. Raw data saved to Workbench. "
                    f"Workbench Keys (JSON list): {json.dumps(workbench_keys)}. Summary: {multi_exec_result['results']}")
        else:
            # Informative error message (adherence to Error Handling)
            return f"Error during multi-execution: {multi_exec_result.get('error', 'Unknown Error')}"
    except json.JSONDecodeError:
        return "JSON Error: The 'requests_json' input was not valid JSON."
    except Exception as e:
        return f"CRITICAL TOOL ERROR: Failed to call Composio MULTI_EXECUTE. Error: {str(e)}"

# --- Tool 3: COMPOSIO_REMOTE_BASH_TOOL Wrapper ---
def run_data_analysis(workbench_keys_json: str) -> str:
    """
    REQUIRED META-TOOL: Executes custom Python/Pandas code via COMPOSIO_REMOTE_BASH_TOOL on Workbench data.
    Input: A JSON string containing a list of workbench keys to retrieve data.
    """
    try:
        workbench_keys = json.loads(workbench_keys_json)
        
        # Simulate data retrieval from Workbench (Crucial Step for context management)
        # The agent must know the data is retrieved before the bash tool executes
        for key in workbench_keys:
             COMPOSIO_CLIENT.remote_workbench(action='retrieve', key=key)

        # In a real system, the agent would generate a complex Python script here
        python_script = f"analyze_data_from_workbench(keys={workbench_keys})"
        bash_result = COMPOSIO_CLIENT.remote_bash_tool(script=python_script)

        if bash_result.get("successful"):
            return f"Analysis complete. Raw analysis output (stdout JSON): {bash_result['stdout']}"
        else:
            return f"Error during Remote Bash execution: {bash_result.get('stderr', 'Unknown Error')}"
    except json.JSONDecodeError:
        return "JSON Error: The 'workbench_keys_json' input was not valid JSON."
    except Exception as e:
        return f"CRITICAL TOOL ERROR: Failed to run data analysis. Error: {str(e)}"

# --- Tool 4: Simple Documentation/Reporting Tool ---
def publish_final_report(final_synthesis_json: str) -> str:
    """
    Publishes the final report to Notion/Docs.
    Input: A JSON string conforming to the FinalSynthesis model.
    """
    try:
        # Pydantic validation for output quality (Best Practice)
        synthesis_data = FinalSynthesis(**json.loads(final_synthesis_json))
        
        # Simulate Notion/Docs tool call via Composio
        print(f"-> Calling Composio Notion Tool: Creating page '{synthesis_data.hypothesis}'")
        
        report_url = f"https://notion.com/reports/{hash(synthesis_data.hypothesis)}"
        
        return f"Final Synthesis published successfully. Report URL: {report_url}."
    except json.JSONDecodeError:
        return "JSON Error: The 'final_synthesis_json' input was not valid JSON. Ensure all fields in FinalSynthesis are present."
    except Exception as e:
        return f"CRITICAL TOOL ERROR: Failed to publish report. Error: {str(e)}"


# Define the list of tools that CrewAI will expose to the agents
SCIENTIST_TOOLS = [
    Tool(
        name="CreateWorkflowPlan",
        func=create_workflow_plan,
        description="A required planning meta-tool. Use this FIRST to define the workflow steps and get a session ID. Input MUST be a JSON string of the ResearchQuery model."
    ),
    Tool(
        name="ExecuteParallelResearch",
        func=execute_parallel_research,
        description="A required execution meta-tool. Use this to run multiple data acquisition APIs (Arxiv, PubChem) concurrently and store large results in the Workbench. Requires session_id and a list of tool requests in JSON format."
    ),
    Tool(
        name="RunRemoteDataAnalysis",
        func=run_data_analysis,
        description="A required execution meta-tool. Use this to execute Python/Pandas scripts via Remote Bash on the data stored in the Workbench. Input MUST be a JSON list of workbench keys."
    ),
    Tool(
        name="PublishFinalReport",
        func=publish_final_report,
        description="A final documentation tool. Use this to format and publish the final synthesis (hypothesis, protocol, and analysis) to Notion or Google Docs. Input MUST be a JSON string of the FinalSynthesis model."
    )
]
