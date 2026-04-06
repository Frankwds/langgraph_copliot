"""
State schema for the Startup Due Diligence workflow.
"""

from typing import TypedDict, List, Optional, Annotated
from operator import add


class DueDiligenceState(TypedDict):
    """
    Central state object that flows through the LangGraph workflow.
    All agents read from and write to this state.
    """

    # INPUT
    startup_name: str
    startup_description: str
    funding_stage: Optional[str]

    # RESEARCH
    # Why Annotated[..., add]? When agents run in parallel and both write to this
    # list, the default "last write wins" would drop results. The add reducer
    # merges lists instead: add([1,2], [3,4]) = [1,2,3,4].
    research_outputs: Annotated[List[dict], add]

    # ANALYSIS
    analysis_outputs: Annotated[List[dict], add]

    # SYNTHESIS
    full_report: Optional[str]
    investment_decision: Optional[dict]

    # METADATA
    current_stage: str
    errors: Annotated[List[str], add]  # also parallel-safe, same reason as above
    retry_count: int


# Why create_initial_state? Every workflow run needs proper defaults — empty
# lists, zero counters, None for optional outputs. Centralizing this prevents
# callers from forgetting a field or setting a wrong default.
def create_initial_state(
    startup_name: str,
    startup_description: str,
    funding_stage: Optional[str] = None,
) -> DueDiligenceState:
    """Create a fresh state object with required inputs and defaults."""
    return DueDiligenceState(
        startup_name=startup_name,
        startup_description=startup_description,
        funding_stage=funding_stage,
        research_outputs=[],
        analysis_outputs=[],
        full_report=None,
        investment_decision=None,
        current_stage="init",
        errors=[],
        retry_count=0,
    )
