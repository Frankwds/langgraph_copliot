import asyncio
import time
from typing import Dict, Any, List

from ..state.schema import DueDiligenceState

# Research agents
from ..agents.research.company_profiler import run_company_profiler
from ..agents.research.market_researcher import run_market_researcher
from ..agents.research.competitor_scout import run_competitor_scout
from ..agents.research.team_investigator import run_team_investigator
from ..agents.research.news_monitor import run_news_monitor


async def init_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Initialize the workflow."""
    print("Running: init_node")
    print(f"  Startup: {state.get('startup_name')}")
    return {"current_stage": "init_complete"}


async def research_node(state: DueDiligenceState) -> Dict[str, Any]:
    """
    Run all research agents in parallel.

    This is the main data gathering phase where we collect information
    about the company, market, competitors, team, and news.
    """
    print("\n" + "=" * 60)
    print("STAGE 2: RESEARCH (5 agents in parallel)")
    print("=" * 60)

    startup_name = state["startup_name"]
    startup_description = state["startup_description"]

    agent_names = [
        "company_profiler",
        "market_researcher",
        "competitor_scout",
        "team_investigator",
        "news_monitor"
    ]

    for name in agent_names:
        print(f"  Starting: {name}")

    start_time = time.time()

    # Run all research agents in parallel
    tasks = [
        run_company_profiler(startup_name, startup_description),
        run_market_researcher(startup_name, startup_description),
        run_competitor_scout(startup_name, startup_description),
        run_team_investigator(startup_name),
        run_news_monitor(startup_name),
    ]

    # Gather results - don't fail on individual agent failures
    results = await asyncio.gather(*tasks, return_exceptions=True)

    research_outputs = []
    errors = []

    for i, result in enumerate(results):
        agent_name = agent_names[i]

        if isinstance(result, Exception):
            # Agent raised an exception
            errors.append(f"{agent_name}: {str(result)}")
            research_outputs.append({
                "agent": agent_name,
                "output": None,
                "success": False,
                "error": str(result)
            })
            print(f"  FAILED: {agent_name} - {str(result)[:50]}")

        elif not result.success:
            # Agent returned but reported failure
            errors.append(f"{agent_name}: {result.error}")
            research_outputs.append({
                "agent": agent_name,
                "output": None,
                "success": False,
                "error": result.error
            })
            print(f"  FAILED: {agent_name} - {result.error[:50] if result.error else 'Unknown'}")

        else:
            # Success!
            research_outputs.append({
                "agent": agent_name,
                "output": result.output,
                "raw_output": result.raw_output,
                "success": True,
                "execution_time_ms": result.execution_time_ms
            })
            print(f"  DONE: {agent_name} ({result.execution_time_ms/1000:.1f}s)")

    elapsed = time.time() - start_time
    success_count = sum(1 for r in research_outputs if r.get("success"))
    print(f"\nResearch complete: {success_count}/5 agents in {elapsed:.1f}s")

    return {
        "research_outputs": research_outputs,
        "errors": errors,
        "current_stage": "research_complete"
    }

async def validate_research_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Validate that research outputs are complete and sufficient."""
    print("Running: validate_research_node")
    return {"current_stage": "research_validated"}


async def analysis_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Run all analysis agents in parallel to interpret research data."""
    print("Running: analysis_node")
    print("Would run 4 analysis agents here...")
    return {
        "analysis_outputs": [{"agent": "stub", "success": True}],
        "current_stage": "analysis_complete",
    }


async def synthesis_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Generate the final report and investment decision from analysis outputs."""
    print("Running: synthesis_node")
    return {
        "full_report": "Stub report",
        "investment_decision": {"recommendation": "hold"},
        "current_stage": "synthesis_complete",
    }


async def output_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Finalize and present the workflow output."""
    print("Running: output_node")
    print("Workflow complete!")
    return {"current_stage": "complete"}
