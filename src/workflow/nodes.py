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

# Analysis agents
from ..agents.analysis.financial_analyst import run_financial_analyst
from ..agents.analysis.risk_assessor import run_risk_assessor
from ..agents.analysis.tech_evaluator import run_tech_evaluator
from ..agents.analysis.legal_reviewer import run_legal_reviewer


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
    """
    Validate research completeness.

    Check if we have enough data to proceed with analysis.
    """
    print("\nValidating research completeness...")

    research_outputs = state.get("research_outputs", [])

    # Count successful research agents
    success_count = sum(
        1 for r in research_outputs
        if r.get("success", False)
    )
    total_count = len(research_outputs)

    errors = []

    # We need at least 50% success rate to continue
    if total_count > 0 and success_count / total_count < 0.5:
        errors.append(
            f"CRITICAL: Only {success_count}/{total_count} research agents succeeded"
        )
        print(f"CRITICAL: Only {success_count}/{total_count} succeeded")
    else:
        print(f"Validation passed: {success_count}/{total_count} succeeded")

    return {
        "current_stage": "research_validated",
        "errors": errors
    }


def _get_agent_output(outputs: List[Dict], agent_name: str) -> Any:
    """Extract a specific agent's output from the outputs list."""
    for output in outputs:
        if output.get("agent") == agent_name and output.get("success"):
            return output.get("output")
    return None

async def analysis_node(state: DueDiligenceState) -> Dict[str, Any]:
    """
    Run analysis agents.

    Some run in parallel, but risk assessor needs other outputs first.
    """
    print("\n" + "=" * 60)
    print("STAGE 3: ANALYSIS (4 agents)")
    print("=" * 60)

    startup_name = state["startup_name"]
    startup_description = state["startup_description"]
    research_outputs = state.get("research_outputs", [])

    # Extract specific research outputs for analysis
    company_profile = _get_agent_output(research_outputs, "company_profiler")
    market_analysis = _get_agent_output(research_outputs, "market_researcher")
    team_analysis = _get_agent_output(research_outputs, "team_investigator")

    print("  Starting: financial_analyst, tech_evaluator, legal_reviewer (parallel)")
    start_time = time.time()

    # Run first batch in parallel
    first_batch = await asyncio.gather(
        run_financial_analyst(
            company_profile=company_profile,
            market_analysis=market_analysis,
            startup_name=startup_name,
            startup_description=startup_description
        ),
        run_tech_evaluator(
            startup_name=startup_name,
            startup_description=startup_description,
            team_analysis=team_analysis
        ),
        run_legal_reviewer(
            startup_name=startup_name,
            market_analysis=market_analysis
        ),
        return_exceptions=True
    )

    analysis_outputs = []
    errors = []

    # Process first batch
    first_batch_names = ["financial_analyst", "tech_evaluator", "legal_reviewer"]
    for i, result in enumerate(first_batch):
        agent_name = first_batch_names[i]
        if isinstance(result, Exception):
            errors.append(f"{agent_name}: {str(result)}")
            analysis_outputs.append({
                "agent": agent_name, "output": None,
                "success": False, "error": str(result)
            })
            print(f"  FAILED: {agent_name}")
        elif not result.success:
            errors.append(f"{agent_name}: {result.error}")
            analysis_outputs.append({
                "agent": agent_name, "output": None,
                "success": False, "error": result.error
            })
            print(f"  FAILED: {agent_name}")
        else:
            analysis_outputs.append({
                "agent": agent_name,
                "output": result.output,
                "raw_output": result.raw_output,
                "success": True,
                "execution_time_ms": result.execution_time_ms
            })
            print(f"  DONE: {agent_name} ({result.execution_time_ms/1000:.1f}s)")

    # Now run risk assessor with ALL outputs
    print("  Starting: risk_assessor (needs other analysis)")
    risk_result = await run_risk_assessor(
        research_outputs=research_outputs,
        analysis_outputs=analysis_outputs,
        startup_name=startup_name
    )

    if isinstance(risk_result, Exception) or not risk_result.success:
        error_msg = str(risk_result) if isinstance(risk_result, Exception) else risk_result.error
        errors.append(f"risk_assessor: {error_msg}")
        analysis_outputs.append({
            "agent": "risk_assessor", "output": None,
            "success": False, "error": error_msg
        })
        print(f"  FAILED: risk_assessor")
    else:
        analysis_outputs.append({
            "agent": "risk_assessor",
            "output": risk_result.output,
            "raw_output": risk_result.raw_output,
            "success": True,
            "execution_time_ms": risk_result.execution_time_ms
        })
        print(f"  DONE: risk_assessor ({risk_result.execution_time_ms/1000:.1f}s)")

    elapsed = time.time() - start_time
    success_count = sum(1 for r in analysis_outputs if r.get("success"))
    print(f"\nAnalysis complete: {success_count}/4 agents in {elapsed:.1f}s")

    return {
        "analysis_outputs": analysis_outputs,
        "errors": errors,
        "current_stage": "analysis_complete"
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
