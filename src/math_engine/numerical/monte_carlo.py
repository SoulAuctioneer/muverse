"""Monte Carlo methods for branch ensemble simulation.

Provides Metropolis-Hastings sampling over branch configurations
weighted by Boltzmann/Gibbs factors, plus utilities for computing
ensemble averages, KL divergence, and error estimates.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class MCResult:
    samples: NDArray[np.float64]
    acceptance_rate: float
    energies: NDArray[np.float64]
    weights: NDArray[np.float64]


def boltzmann_weight(action: float | NDArray, beta: float) -> NDArray[np.float64]:
    """Compute Boltzmann weights exp(−β S_E) for given actions."""
    return np.exp(-beta * np.asarray(action))


def gibbs_probabilities(actions: NDArray[np.float64], beta: float) -> NDArray[np.float64]:
    """Normalized Gibbs probabilities from a set of Euclidean actions."""
    log_weights = -beta * actions
    log_weights -= np.max(log_weights)  # numerical stability
    weights = np.exp(log_weights)
    return weights / weights.sum()


def born_rule_probabilities(amplitudes: NDArray[np.complex128]) -> NDArray[np.float64]:
    """Standard Born rule: P_i = |ψ_i|²."""
    probs = np.abs(amplitudes) ** 2
    return probs / probs.sum()


def kl_divergence(p: NDArray[np.float64], q: NDArray[np.float64]) -> float:
    """KL divergence D_KL(P || Q). Returns inf if Q has zeros where P doesn't."""
    mask = p > 0
    if np.any(q[mask] <= 0):
        return float("inf")
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def metropolis_hastings(
    action_fn: callable,
    x0: NDArray[np.float64],
    beta: float,
    n_steps: int = 10_000,
    step_size: float = 0.1,
    rng: np.random.Generator | None = None,
) -> MCResult:
    """Metropolis-Hastings sampling with Boltzmann acceptance.

    Parameters
    ----------
    action_fn : callable
        Maps configuration x → Euclidean action S_E(x).
    x0 : initial configuration
    beta : inverse temperature (1/k_BT in natural units)
    n_steps : number of MC steps
    step_size : proposal distribution width
    """
    rng = rng or np.random.default_rng()
    dim = x0.shape[0] if x0.ndim > 0 else 1
    x = np.copy(x0)
    S_current = action_fn(x)

    samples = np.empty((n_steps, dim) if dim > 1 else (n_steps,))
    energies = np.empty(n_steps)
    accepted = 0

    for i in range(n_steps):
        proposal = x + rng.normal(0, step_size, size=x.shape)
        S_proposal = action_fn(proposal)
        delta_S = S_proposal - S_current

        if delta_S < 0 or rng.random() < np.exp(-beta * delta_S):
            x = proposal
            S_current = S_proposal
            accepted += 1

        samples[i] = x
        energies[i] = S_current

    weights = boltzmann_weight(energies, beta)
    return MCResult(
        samples=samples,
        acceptance_rate=accepted / n_steps,
        energies=energies,
        weights=weights / weights.sum(),
    )


def temperature_sweep(
    actions: NDArray[np.float64],
    born_probs: NDArray[np.float64],
    betas: NDArray[np.float64],
) -> dict[str, NDArray[np.float64]]:
    """Sweep inverse temperature and compute KL divergence from Born rule.

    This is the core numerical test for prediction P1: at low T (high β),
    Gibbs weights should match Born rule; at high T (low β), they diverge.

    Returns dict with keys: betas, kl_divergences, gibbs_probs_per_beta.
    """
    kl_values = np.empty(len(betas))
    all_probs = np.empty((len(betas), len(actions)))

    for i, b in enumerate(betas):
        g_probs = gibbs_probabilities(actions, b)
        all_probs[i] = g_probs
        kl_values[i] = kl_divergence(born_probs, g_probs)

    return {
        "betas": betas,
        "kl_divergences": kl_values,
        "gibbs_probs_per_beta": all_probs,
    }
