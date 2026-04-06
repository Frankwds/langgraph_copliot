from langgraph.graph import StateGraph, END

from ..state.schema import DueDiligenceState
from .nodes import (
    init_node,
    research_node,
    validate_research_node,
    analysis_node,
    synthesis_node,
    output_node,
)


# Why StateGraph with TypedDict? The StateGraph constructor takes our state type
# as a parameter, telling LangGraph how to handle state updates and enabling
# type checking across all nodes.
def create_due_diligence_graph() -> StateGraph:
    """
    Create the due diligence workflow graph.

    Returns:
        StateGraph ready for node and edge definitions
    """
    # Create the graph with our state type
    workflow = StateGraph(DueDiligenceState)

    # Add nodes to the graph
    workflow.add_node("init", init_node)
    workflow.add_node("research", research_node)
    workflow.add_node("validate_research", validate_research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("output", output_node)

    # Set the entry point of the workflow
    workflow.set_entry_point("init")
    
    # Define edges between nodes to establish workflow order
    

    return workflow
