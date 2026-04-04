"""Base agent infrastructure shared by all specialized agents.

Each agent is a callable that processes a TheoryState and conversation
history, returning an updated state and response.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.core.theory_schema import TheoryState
from src.llm.provider import Message

PROMPTS_DIR = Path(__file__).parent.parent / "llm" / "prompts"


class AgentState(BaseModel):
    """Shared state passed through the LangGraph workflow."""

    theory: TheoryState
    messages: list[dict[str, str]] = Field(default_factory=list)
    current_task: str = ""
    agent_outputs: dict[str, str] = Field(default_factory=dict)
    iteration: int = 0
    phase: str = "formalize"  # formalize | critique | simulate | write | review


def load_system_prompt(agent_name: str) -> str:
    """Load the system prompt for an agent from its markdown file."""
    path = PROMPTS_DIR / f"{agent_name}.md"
    return path.read_text()


def build_theory_context(state: AgentState) -> str:
    """Serialize current theory state as context for the LLM."""
    theory = state.theory
    parts = [f"# Current Theory State (v{theory.version})\n"]

    parts.append("## Axioms")
    for a in theory.axioms:
        parts.append(f"- **{a.label}** [{a.status.value}]: {a.statement}")
        if a.formal_expression:
            parts.append(f"  Formula: `{a.formal_expression}`")

    parts.append("\n## Derivations")
    for d in theory.derivations:
        parts.append(
            f"- **{d.label}** [{d.verification_status.value}]: "
            f"{' + '.join(d.premises)} → {d.conclusion}"
        )
        for i, step in enumerate(d.steps, 1):
            parts.append(f"  Step {i}: {step.description}")

    parts.append("\n## Predictions")
    for p in theory.predictions:
        parts.append(f"- **{p.label}**: {p.statement}")
        if p.quantitative_formula:
            parts.append(f"  Formula: `{p.quantitative_formula}`")

    parts.append("\n## Open Critiques")
    for c in theory.critiques:
        if c.resolution_status.value in ("open", "addressed"):
            parts.append(
                f"- [{c.severity.value.upper()}] on {c.target_label}: {c.description}"
            )

    return "\n".join(parts)


def make_messages(
    system_prompt: str,
    theory_context: str,
    task: str,
    history: list[dict[str, str]] | None = None,
) -> list[Message]:
    """Assemble the message list for an LLM call."""
    msgs = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=f"{theory_context}\n\n---\n\n**Task:** {task}"),
    ]
    if history:
        for h in history[-10:]:  # keep last 10 exchanges for context window
            msgs.append(Message(role=h.get("role", "user"), content=h.get("content", "")))
    return msgs
