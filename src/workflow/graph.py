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
from .routing import check_init_success, check_research_completeness


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
    workflow.add_conditional_edges(
        "init",
        check_init_success,
        {"success": "research", "failed": END},
    )
    workflow.add_conditional_edges(
        "research",
        check_research_completeness,
        {"complete": "validate_research", "incomplete": "research", "failed": END},
    )
    workflow.add_edge("validate_research", "analysis")
    workflow.add_edge("analysis", "synthesis")
    workflow.add_edge("synthesis", "output")
    workflow.add_edge("output", END)

    return workflow

def compile_workflow():
    """
    Create and compile the workflow graph.

    Returns:
        Compiled graph ready for invocation
    """
    graph = create_due_diligence_graph()
    return graph.compile()


# Why singleton? Compilation is expensive. This ensures we only compile once,
# then reuse the compiled graph for multiple invocations.
compiled_graph = None


def get_compiled_graph():
    """
    Get the compiled workflow graph (singleton).

    Returns:
        Compiled graph instance
    """
    global compiled_graph
    if compiled_graph is None:
        compiled_graph = compile_workflow()
    return compiled_graph


async def run_due_diligence(
    startup_name: str,
    startup_description: str,
    funding_stage: str = None,
) -> DueDiligenceState:
    """
    Run the complete due diligence workflow.

    Args:
        startup_name: Name of the startup to analyze
        startup_description: Description of the startup's business
        funding_stage: Optional funding stage

    Returns:
        Final state containing all outputs
    """
    from ..state.schema import create_initial_state

    initial_state = create_initial_state(
        startup_name=startup_name,
        startup_description=startup_description,
        funding_stage=funding_stage,
    )

    graph = get_compiled_graph()
    final_state = await graph.ainvoke(initial_state)

    return final_state
