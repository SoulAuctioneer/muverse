"""REST routes for agent interaction."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.agents.base import AgentState
from src.agents.critic import run_critic
from src.agents.literature import run_literature
from src.agents.orchestrator import create_initial_state, run_full_pipeline
from src.agents.simulator import run_simulator
from src.agents.theorist import run_theorist
from src.agents.writer import run_writer
from src.storage.database import save_agent_output

router = APIRouter()

_pipeline_state: dict[str, Any] = {"running": False, "state": None, "error": None}


class AgentRequest(BaseModel):
    agent: str  # theorist | critic | literature | simulator | writer
    task: str = ""
    phase: str = "formalize"


class AgentResponse(BaseModel):
    agent: str
    output: str
    phase: str
    iteration: int


AGENT_MAP = {
    "theorist": run_theorist,
    "critic": run_critic,
    "literature": run_literature,
    "simulator": run_simulator,
    "writer": run_writer,
}


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """Run a single agent with a custom task."""
    if request.agent not in AGENT_MAP:
        return AgentResponse(
            agent=request.agent,
            output=f"Unknown agent: {request.agent}",
            phase=request.phase,
            iteration=0,
        )

    state = create_initial_state()
    state.current_task = request.task
    state.phase = request.phase

    agent_fn = AGENT_MAP[request.agent]
    state = await agent_fn(state)

    output = state.agent_outputs.get(request.agent, "No output produced.")

    await save_agent_output(
        agent_name=request.agent,
        phase=request.phase,
        output_text=output,
        task=request.task,
        theory_version=state.theory.version,
        iteration=state.iteration,
    )

    return AgentResponse(
        agent=request.agent,
        output=output,
        phase=state.phase,
        iteration=state.iteration,
    )


async def _run_pipeline():
    """Background task: run the full orchestrator pipeline."""
    global _pipeline_state
    _pipeline_state["running"] = True
    _pipeline_state["error"] = None
    try:
        final_state = await run_full_pipeline()
        _pipeline_state["state"] = final_state.model_dump(mode="json")
    except Exception as e:
        _pipeline_state["error"] = str(e)
    finally:
        _pipeline_state["running"] = False


@router.post("/pipeline/start")
async def start_pipeline(background_tasks: BackgroundTasks):
    """Start the full orchestrator pipeline in the background."""
    if _pipeline_state["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_run_pipeline)
    return {"status": "started"}


@router.get("/pipeline/status")
async def pipeline_status():
    """Check the status of the running pipeline."""
    return {
        "running": _pipeline_state["running"],
        "has_result": _pipeline_state["state"] is not None,
        "error": _pipeline_state["error"],
    }
