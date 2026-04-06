from langgraph.graph import StateGraph, END

from ..state.schema import DueDiligenceState


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

    # We'll add nodes and edges next

    return workflow
