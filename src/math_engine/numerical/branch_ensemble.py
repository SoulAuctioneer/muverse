"""Branch ensemble dynamics under energy constraints.

Simulates the evolution of a population of MWI-like branches
where each branch has an associated Euclidean action cost and
the total energy budget is finite.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class Branch:
    action: float
    amplitude: complex
    depth: int = 0
    parent_id: int = -1


@dataclass
class BranchEnsemble:
    branches: list[Branch] = field(default_factory=list)
    total_budget: float = 100.0
    generation: int = 0

    @property
    def actions(self) -> NDArray[np.float64]:
        return np.array([b.action for b in self.branches])

    @property
    def amplitudes(self) -> NDArray[np.complex128]:
        return np.array([b.amplitude for b in self.branches])


def initialize_ensemble(
    n_branches: int,
    action_scale: float = 1.0,
    rng: np.random.Generator | None = None,
) -> BranchEnsemble:
    """Create initial branch ensemble with random actions and unit amplitudes."""
    rng = rng or np.random.default_rng(42)
    branches = []
    for i in range(n_branches):
        action = rng.exponential(action_scale)
        phase = rng.uniform(0, 2 * np.pi)
        amplitude = np.exp(1j * phase) / np.sqrt(n_branches)
        branches.append(Branch(action=action, amplitude=amplitude, depth=0, parent_id=-1))
    return BranchEnsemble(branches=branches)


def evolve_unconstrained(
    ensemble: BranchEnsemble,
    branching_factor: int = 2,
    action_noise: float = 0.3,
    rng: np.random.Generator | None = None,
) -> BranchEnsemble:
    """Standard MWI branching: all branches split equally (no selection).

    Each branch splits into `branching_factor` children with slightly
    mutated actions. Amplitudes are divided equally (no weighting).
    """
    rng = rng or np.random.default_rng()
    new_branches = []
    for i, parent in enumerate(ensemble.branches):
        for _ in range(branching_factor):
            child_action = max(0, parent.action + rng.normal(0, action_noise))
            child_amplitude = parent.amplitude / np.sqrt(branching_factor)
            new_branches.append(Branch(
                action=child_action,
                amplitude=child_amplitude,
                depth=parent.depth + 1,
                parent_id=i,
            ))
    return BranchEnsemble(
        branches=new_branches,
        total_budget=ensemble.total_budget,
        generation=ensemble.generation + 1,
    )


def evolve_constrained(
    ensemble: BranchEnsemble,
    branching_factor: int = 2,
    action_noise: float = 0.3,
    beta: float = 1.0,
    rng: np.random.Generator | None = None,
) -> BranchEnsemble:
    """Energy-constrained branching: branches weighted by Gibbs factor.

    Each branch splits, but child amplitudes are weighted by
    exp(−β S_E) / Z, redistributing the "energy budget" toward
    low-action (thermodynamically favored) configurations.
    """
    rng = rng or np.random.default_rng()
    new_branches = []
    for i, parent in enumerate(ensemble.branches):
        children_actions = []
        for _ in range(branching_factor):
            child_action = max(0, parent.action + rng.normal(0, action_noise))
            children_actions.append(child_action)

        log_weights = -beta * np.array(children_actions)
        log_weights -= np.max(log_weights)
        weights = np.exp(log_weights)
        weights /= weights.sum()

        for j, child_action in enumerate(children_actions):
            child_amplitude = parent.amplitude * np.sqrt(weights[j])
            new_branches.append(Branch(
                action=child_action,
                amplitude=child_amplitude,
                depth=parent.depth + 1,
                parent_id=i,
            ))

    return BranchEnsemble(
        branches=new_branches,
        total_budget=ensemble.total_budget,
        generation=ensemble.generation + 1,
    )


def measure_born_rule_adherence(ensemble: BranchEnsemble, beta: float) -> dict[str, float]:
    """Compare ensemble statistics to Born rule predictions.

    Returns KL divergences and correlation metrics.
    """
    from src.math_engine.numerical.monte_carlo import (
        born_rule_probabilities,
        gibbs_probabilities,
        kl_divergence,
    )

    actions = ensemble.actions
    amplitudes = ensemble.amplitudes

    born_probs = born_rule_probabilities(amplitudes)
    gibbs_probs = gibbs_probabilities(actions, beta)

    amplitude_probs = np.abs(amplitudes) ** 2
    amplitude_probs /= amplitude_probs.sum()

    return {
        "kl_born_vs_gibbs": kl_divergence(born_probs, gibbs_probs),
        "kl_gibbs_vs_born": kl_divergence(gibbs_probs, born_probs),
        "mean_action": float(np.mean(actions)),
        "std_action": float(np.std(actions)),
        "n_branches": len(ensemble.branches),
        "generation": ensemble.generation,
    }
