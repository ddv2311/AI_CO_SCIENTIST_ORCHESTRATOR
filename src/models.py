from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- Input Models ---
class ResearchQuery(BaseModel):
    """Schema for the initial user request, validating user input."""
    topic: str = Field(description="The scientific topic or hypothesis to be investigated.")
    target_output: str = Field(description="The desired deliverable (e.g., 'Draft full experimental protocol').")
    keywords: List[str] = Field(description="List of core keywords for literature search.")

# --- Intermediate Tool Models ---
class ToolExecutionRequest(BaseModel):
    """Schema for a single tool request within the Multi-Execute call."""
    tool_slug: str = Field(description="The unique slug for the Composio tool (e.g., arxiv_search_tool_slug).")
    arguments: Dict[str, Any] = Field(description="Key-value arguments required by the tool's API.")

# --- Final Output Model (The official deliverable schema) ---
class FinalSynthesis(BaseModel):
    """Schema for the final published scientific report, enforcing structured output."""
    hypothesis: str = Field(description="The finalized, testable scientific hypothesis.")
    protocol_summary: str = Field(description="A brief summary of the proposed experimental steps.")
    analysis_findings: str = Field(description="The core metrics and conclusions from the remote data analysis.")
    prior_art_reference_links: List[str] = Field(description="List of URLs or Workbench Keys for key prior art documents.")
    next_steps: str = Field(description="Recommended next steps for human researchers (e.g., in-vitro testing).")
