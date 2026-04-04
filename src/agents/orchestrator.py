"""Orchestrator: LangGraph state machine coordinating the agent workflow.

Workflow phases:
  Formalize → Critique → Refine → Simulate → Analyze →
  Critique → Write → Review → Refine → Write → [done]

The orchestrator routes between agents based on the current phase
and the results of previous agent runs.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from src.agents.base import AgentState
from src.agents.critic import run_critic
from src.agents.literature import run_literature
from src.agents.simulator import run_simulator
from src.agents.theorist import run_theorist
from src.agents.writer import run_writer
from src.core.seed_theory import build_seed_theory

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10


# ---------------------------------------------------------------------------
# Node wrappers (adapt async agent functions to graph nodes)
# ---------------------------------------------------------------------------

async def formalize_node(state: AgentState) -> AgentState:
    """Phase 1: Theorist extracts and refines axioms."""
    state.phase = "formalize"
    state.current_task = ""
    state = await run_theorist(state)
    state = await run_literature(state)
    return state


async def critique_node(state: AgentState) -> AgentState:
    """Critic reviews current theory state."""
    state.phase = "critique"
    state.current_task = ""
    state = await run_critic(state)
    return state


async def refine_node(state: AgentState) -> AgentState:
    """Theorist addresses critique."""
    state.current_task = ""
    state = await run_theorist(state)
    state.iteration += 1
    return state


async def simulate_node(state: AgentState) -> AgentState:
    """Simulator designs and runs experiments."""
    state.phase = "simulate"
    state.current_task = ""
    state = await run_simulator(state)
    return state


async def write_node(state: AgentState) -> AgentState:
    """Writer drafts paper sections."""
    state.phase = "write"
    state.current_task = ""
    state = await run_writer(state)
    return state


async def review_node(state: AgentState) -> AgentState:
    """Critic reviews paper draft."""
    state.phase = "review"
    state.current_task = ""
    state = await run_critic(state)
    return state


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def _ensure_state(state: AgentState | dict) -> AgentState:
    return AgentState(**state) if isinstance(state, dict) else state


def should_continue_refining(state: AgentState | dict) -> Literal["refine", "simulate"]:
    """After critique: refine if critical issues remain, else move to simulation."""
    s = _ensure_state(state)
    critical = [
        c for c in s.theory.critiques
        if c.severity.value == "critical" and c.resolution_status.value == "open"
    ]
    if critical and s.iteration < MAX_ITERATIONS:
        return "refine"
    return "simulate"


def should_continue_writing(state: AgentState | dict) -> Literal["refine_paper", "done"]:
    """After review: iterate on paper if issues remain, else finish."""
    s = _ensure_state(state)
    if s.iteration < MAX_ITERATIONS and s.phase == "review":
        return "refine_paper"
    return "done"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_workflow() -> StateGraph:
    """Construct the full orchestrator graph.

    Flow:
      formalize → critique → [refine ↔ critique] → simulate →
      critique → write → review → [refine_paper ↔ review] → END
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("formalize", formalize_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("simulate", simulate_node)
    workflow.add_node("write", write_node)
    workflow.add_node("review", review_node)

    workflow.set_entry_point("formalize")

    workflow.add_edge("formalize", "critique")

    workflow.add_conditional_edges(
        "critique",
        should_continue_refining,
        {"refine": "refine", "simulate": "simulate"},
    )

    workflow.add_edge("refine", "critique")
    workflow.add_edge("simulate", "write")

    workflow.add_edge("write", "review")

    workflow.add_conditional_edges(
        "review",
        should_continue_writing,
        {"refine_paper": "write", "done": END},
    )

    return workflow


def create_initial_state() -> AgentState:
    """Create the starting state seeded with the Thermodynamic Darwinism theory."""
    theory = build_seed_theory()
    return AgentState(
        theory=theory,
        messages=[],
        current_task="",
        agent_outputs={},
        iteration=0,
        phase="formalize",
    )


async def run_full_pipeline() -> AgentState:
    """Execute the complete orchestrator pipeline end-to-end."""
    workflow = build_workflow()
    graph = workflow.compile()
    state = create_initial_state()

    logger.info("Starting Muverse orchestrator pipeline")
    raw = await graph.ainvoke(state)

    if isinstance(raw, dict):
        final_state = AgentState(**raw)
    else:
        final_state = raw

    logger.info("Pipeline complete after %d iterations", final_state.iteration)
    return final_state
