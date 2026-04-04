"""Literature Agent: searches and synthesizes relevant scientific literature.

Ensures all claims are properly cited, identifies prior art,
discovers connections, and maintains the BibTeX database.
"""

from __future__ import annotations

from src.agents.base import (
    AgentState,
    build_theory_context,
    load_system_prompt,
    make_messages,
)
from src.llm.provider import complete


async def run_literature(state: AgentState) -> AgentState:
    """Execute the Literature agent on the current state."""
    system_prompt = load_system_prompt("literature")
    theory_ctx = build_theory_context(state)

    task = state.current_task or _default_task(state)

    messages = make_messages(system_prompt, theory_ctx, task, state.messages)
    response = await complete(messages, role="literature", temperature=0.3, max_tokens=8192)

    state.agent_outputs["literature"] = response.content
    state.messages.append({"role": "assistant", "content": f"[Literature] {response.content}"})
    return state


def _default_task(state: AgentState) -> str:
    if state.phase == "formalize":
        return (
            "For each axiom A1–A8, identify the key supporting references:\n"
            "1. A1 (standard MWI) — Everett, DeWitt, Wallace\n"
            "2. A2 (finite action) — Hartle-Hawking, cosmological boundary conditions\n"
            "3. A3 (Wick rotation) — Standard QFT textbooks, Euclidean path integrals\n"
            "4. A4 (Jarzynski) — Jarzynski 1997, Crooks fluctuation theorem, quantum extensions\n"
            "5. A5 (Born rule emergence) — Carroll/Sebens, Deutsch/Wallace, Zurek\n"
            "6. A6 (Landauer) — Landauer 1961, Bennett, recent experimental confirmations\n"
            "7. A7 (SGD-Gibbs) — Mandt et al., Smith & Le, Chaudhari et al.\n"
            "8. A8 (free energy selection) — Friston FEP, England dissipative adaptation\n\n"
            "For each, provide: authors, year, journal, DOI if available. "
            "Flag any axiom that lacks adequate literature support."
        )
    return (
        "Search for any recent publications (2023–2026) that may overlap with or "
        "contradict the Thermodynamic Darwinism framework. Focus on:\n"
        "- New Born rule derivation attempts\n"
        "- Energy cost of decoherence experiments\n"
        "- Extensions of Quantum Darwinism to thermodynamic systems"
    )
