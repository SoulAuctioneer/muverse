"""Critic Agent: adversarial quality gate for the theory.

Operates in three modes:
1. Internal consistency — circularity, hidden assumptions, independence
2. External conflict — empirical contradictions, prior art overlap
3. Alternative explanation — strongest counter-arguments
"""

from __future__ import annotations

from src.agents.base import (
    AgentState,
    build_theory_context,
    load_system_prompt,
    make_messages,
)
from src.llm.provider import complete


async def run_critic(state: AgentState) -> AgentState:
    """Execute the Critic agent on the current state."""
    system_prompt = load_system_prompt("critic")
    theory_ctx = build_theory_context(state)

    task = state.current_task or _default_task(state)

    messages = make_messages(system_prompt, theory_ctx, task, state.messages)
    response = await complete(messages, role="critic", temperature=0.5, max_tokens=8192)

    state.agent_outputs["critic"] = response.content
    state.messages.append({"role": "assistant", "content": f"[Critic] {response.content}"})
    return state


def _default_task(state: AgentState) -> str:
    if state.phase == "formalize":
        return (
            "Perform a full internal consistency audit of the theory:\n"
            "1. Check each derivation (D1–D3) for circular reasoning.\n"
            "2. Verify that axioms are independent — can any be derived from the others?\n"
            "3. Check dimensional consistency of all formal expressions.\n"
            "4. Identify the single most critical weakness in the current formulation.\n"
            "5. For Derivation D1 specifically: does the T→0 limit step assume |ψ|²?"
        )
    if state.phase == "simulate":
        return (
            "Review the simulation designs and results. For each simulation:\n"
            "1. Is the null hypothesis (standard MWI prediction) correctly stated?\n"
            "2. Are there hidden assumptions in the simulation setup that bias results?\n"
            "3. Could the results be explained without invoking the new framework?\n"
            "4. Are the statistical claims justified by the error bars?"
        )
    if state.phase == "write" or state.phase == "review":
        return (
            "Review the paper draft with a referee's eye:\n"
            "1. Does every claim have a supporting axiom, derivation, simulation, or citation?\n"
            "2. Are limitations honestly presented?\n"
            "3. What would the strongest reviewer objection be?"
        )
    return (
        "Identify the three most critical weaknesses in the current theory. "
        "For each, state the specific axiom/derivation affected, the type of issue, "
        "severity, and what would resolve it."
    )
