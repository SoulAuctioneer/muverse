"""Writer Agent: produces publication-quality paper sections.

Translates formalized theory, simulation results, and literature
into a coherent LaTeX paper suitable for physics journal submission.
"""

from __future__ import annotations

from src.agents.base import (
    AgentState,
    build_theory_context,
    load_system_prompt,
    make_messages,
)
from src.llm.provider import complete


async def run_writer(state: AgentState) -> AgentState:
    """Execute the Writer agent on the current state."""
    system_prompt = load_system_prompt("writer")
    theory_ctx = build_theory_context(state)

    sim_results = state.agent_outputs.get("simulator", "No simulation results yet.")
    lit_context = state.agent_outputs.get("literature", "No literature review yet.")

    extended_ctx = (
        f"{theory_ctx}\n\n"
        f"## Simulation Results\n{sim_results}\n\n"
        f"## Literature Notes\n{lit_context}"
    )

    task = state.current_task or _default_task(state)

    messages = make_messages(system_prompt, extended_ctx, task, state.messages)
    response = await complete(messages, role="writer", temperature=0.5, max_tokens=8192)

    state.agent_outputs["writer"] = response.content
    state.messages.append({"role": "assistant", "content": f"[Writer] {response.content}"})
    return state


def _default_task(state: AgentState) -> str:
    if state.phase == "write":
        return (
            "Draft the following paper sections in LaTeX:\n\n"
            "1. **Abstract** (150 words max): Framework summary, key prediction P1, "
            "simulation highlights.\n"
            "2. **Introduction**: MWI context, Born rule problem, why thermodynamic "
            "constraints are the natural next step.\n"
            "3. **The Framework**: Present axioms A1–A8 and derivations D1–D3 "
            "with full mathematical detail.\n\n"
            "Use REVTeX formatting. Number all equations. Cite all claims."
        )
    if state.phase == "review":
        critic_review = state.agent_outputs.get("critic", "")
        return (
            f"The Critic has reviewed the draft and provided feedback:\n\n"
            f"{critic_review}\n\n"
            "Revise the affected sections to address each point. "
            "Do not remove honest acknowledgments of limitations."
        )
    return "Prepare an outline of the paper with section-level summaries."
