from typing import Literal

from ..state.schema import DueDiligenceState

# Why Literal? Using Literal types for return values ensures routing functions
# return only valid path names, catching typos at type-check time rather than
# silently routing to a nonexistent node at runtime.


def check_init_success(
    state: DueDiligenceState,
) -> Literal["success", "failed"]:
    """
    Check if initialization succeeded.

    Returns:
        - "success": Inputs valid, proceed
        - "failed": Missing required inputs
    """
    errors = state.get("errors", [])
    critical_errors = [e for e in errors if "required" in e.lower()]

    if critical_errors:
        return "failed"
    return "success"


def check_research_completeness(
    state: DueDiligenceState,
) -> Literal["complete", "incomplete", "failed"]:
    """
    Check if research phase completed successfully.

    Returns:
        - "complete": Enough data to proceed
        - "incomplete": Should retry research
        - "failed": Too many failures, abort
    """
    research_outputs = state.get("research_outputs", [])
    retry_count = state.get("retry_count", 0)

    if not research_outputs:
        if retry_count < 2:
            return "incomplete"
        return "failed"

    success_count = sum(
        1 for r in research_outputs
        if r.get("success", False)
    )
    total_count = len(research_outputs)

    if total_count == 0:
        return "failed"

    success_rate = success_count / total_count

    if success_rate >= 0.5:
        return "complete"

    if retry_count < 2:
        return "incomplete"

    return "complete"  # Proceed with what we have
