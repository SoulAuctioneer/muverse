"""Simulator Agent: designs, runs, and interprets computational experiments.

Interfaces with the math engine and simulation modules to execute
the three core simulations and any ad-hoc experiments proposed
during the research process.
"""

from __future__ import annotations

from src.agents.base import (
    AgentState,
    build_theory_context,
    load_system_prompt,
    make_messages,
)
from src.llm.provider import complete


async def run_simulator(state: AgentState) -> AgentState:
    """Execute the Simulator agent on the current state."""
    system_prompt = load_system_prompt("simulator")
    theory_ctx = build_theory_context(state)

    task = state.current_task or _default_task(state)

    messages = make_messages(system_prompt, theory_ctx, task, state.messages)
    response = await complete(messages, role="simulator", temperature=0.3, max_tokens=8192)

    state.agent_outputs["simulator"] = response.content
    state.messages.append({"role": "assistant", "content": f"[Simulator] {response.content}"})
    return state


def _default_task(state: AgentState) -> str:
    return (
        "Design and describe the execution plan for all three core simulations:\n\n"
        "**Simulation 1: Branch Ensemble under Boltzmann Constraint**\n"
        "- Define the branching model parameters (n_branches, action distribution, branching factor)\n"
        "- Specify the null hypothesis (equal-weight MWI) and alternative (Gibbs weighting)\n"
        "- Plan the temperature sweep and KL divergence measurement\n\n"
        "**Simulation 2: Neural Network Analog Model**\n"
        "- Define the hierarchical branching loss landscape architecture\n"
        "- Specify the temperature sweep (learning rate / batch size variations)\n"
        "- Plan the comparison of weight distributions to Born rule predictions\n\n"
        "**Simulation 3: Quantum Langevin Dynamics**\n"
        "- Define the quantum system and Hamiltonian\n"
        "- Specify the thermal bath coupling and temperature range\n"
        "- Plan the measurement of branch probabilities vs temperature\n\n"
        "For each simulation, state the expected result under both the null and "
        "alternative hypotheses, and the statistical test you will use."
    )
