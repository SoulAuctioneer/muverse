"""Theorist Agent: develops and refines mathematical formulations.

Responsibilities:
- Extract axioms from source documents
- Develop formal derivation chains
- Fill logical gaps identified by the Critic
- Propose new axioms when needed
"""

from __future__ import annotations

from src.agents.base import (
    AgentState,
    build_theory_context,
    load_system_prompt,
    make_messages,
)
from src.llm.provider import Message, complete


async def run_theorist(state: AgentState) -> AgentState:
    """Execute the Theorist agent on the current state."""
    system_prompt = load_system_prompt("theorist")
    theory_ctx = build_theory_context(state)

    task = state.current_task or _default_task(state)

    messages = make_messages(system_prompt, theory_ctx, task, state.messages)
    response = await complete(messages, role="theorist", temperature=0.4, max_tokens=8192)

    state.agent_outputs["theorist"] = response.content
    state.messages.append({"role": "assistant", "content": f"[Theorist] {response.content}"})
    return state


def _default_task(state: AgentState) -> str:
    if state.phase == "formalize":
        return (
            "Review the current axioms A1–A8 and derivations D1–D3. "
            "For each derivation, verify that every step is explicit and "
            "mathematically justified. Identify any steps that rely on "
            "unstated assumptions or hand-waving. Propose corrections."
        )
    if state.phase == "critique":
        open_critiques = [
            c for c in state.theory.critiques
            if c.resolution_status.value == "open"
        ]
        if open_critiques:
            targets = ", ".join(c.target_label for c in open_critiques)
            return (
                f"The Critic has raised open issues on: {targets}. "
                "Address each critique with a formal mathematical response. "
                "If a derivation step is circular, propose an alternative derivation. "
                "If an axiom is unjustified, either derive it or explain why it must be postulated."
            )
    return "Continue developing the mathematical framework. Focus on the weakest derivation."
