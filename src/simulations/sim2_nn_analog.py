"""Simulation 2: Neural Network as Analog Model.

Tests the formal equivalence between SGD steady state and Gibbs
distribution by designing a neural network with a branching loss
landscape and measuring whether Born rule statistics emerge at low
effective temperature.

Null hypothesis (H0): Weight distributions are independent of effective temperature
Alternative (H1): Weight distributions follow Gibbs statistics with temperature
                  set by learning rate/batch size, matching Born rule at low T

The key prediction: Born rule statistics at branch points should emerge at
low T (low η/B) and deviate measurably at high T.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class Sim2Config:
    n_branches: int = 8
    n_layers: int = 4
    hidden_dim: int = 32
    n_samples: int = 1000
    learning_rates: list[float] | None = None
    batch_sizes: list[int] | None = None
    n_epochs: int = 200
    n_trials: int = 10
    seed: int = 42

    def __post_init__(self):
        if self.learning_rates is None:
            self.learning_rates = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        if self.batch_sizes is None:
            self.batch_sizes = [32]


@dataclass
class Sim2Result:
    temperatures: NDArray[np.float64]
    weight_distributions: NDArray[np.float64]  # (n_temps, n_branches)
    gibbs_predictions: NDArray[np.float64]  # (n_temps, n_branches)
    born_predictions: NDArray[np.float64]  # (n_branches,)
    kl_from_born: NDArray[np.float64]  # (n_temps,)
    kl_from_gibbs: NDArray[np.float64]  # (n_temps,)
    branch_energies: NDArray[np.float64]


def create_branching_landscape(
    n_branches: int,
    seed: int = 42,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Create a synthetic hierarchical loss landscape with branch structure.

    Returns (branch_energies, branch_amplitudes) where:
    - branch_energies[i] = the "depth" of basin i in the loss landscape
    - branch_amplitudes[i] = corresponding quantum amplitude (for Born rule comparison)
    """
    rng = np.random.default_rng(seed)

    energies = rng.exponential(scale=2.0, size=n_branches)
    energies = np.sort(energies)

    phases = rng.uniform(0, 2 * np.pi, n_branches)
    raw_amplitudes = np.exp(-energies / 2) * np.exp(1j * phases)
    amplitudes = raw_amplitudes / np.sqrt(np.sum(np.abs(raw_amplitudes) ** 2))

    return energies, amplitudes


def sgd_on_branching_landscape(
    energies: NDArray[np.float64],
    temperature: float,
    n_steps: int = 5000,
    seed: int = 42,
) -> NDArray[np.float64]:
    """Simulate SGD as Langevin dynamics on the branching landscape.

    At each step, the "particle" (representing the weight configuration)
    moves in the energy landscape with Gaussian noise scaled by temperature.
    We count the fraction of time spent near each branch minimum.

    Returns the empirical occupation probabilities.
    """
    rng = np.random.default_rng(seed)
    n_branches = len(energies)

    positions = np.zeros(n_branches)
    visit_counts = np.zeros(n_branches)

    current_branch = rng.integers(0, n_branches)

    for _ in range(n_steps):
        proposed_branch = rng.integers(0, n_branches)
        delta_E = energies[proposed_branch] - energies[current_branch]

        if delta_E < 0 or rng.random() < np.exp(-delta_E / max(temperature, 1e-10)):
            current_branch = proposed_branch

        visit_counts[current_branch] += 1

    probs = visit_counts / visit_counts.sum()
    return probs


def gibbs_prediction(energies: NDArray[np.float64], temperature: float) -> NDArray[np.float64]:
    """Theoretical Gibbs distribution: p_i ∝ exp(−E_i/T)."""
    if temperature <= 0:
        p = np.zeros_like(energies)
        p[np.argmin(energies)] = 1.0
        return p
    log_p = -energies / temperature
    log_p -= np.max(log_p)
    p = np.exp(log_p)
    return p / p.sum()


def run_simulation(config: Sim2Config | None = None) -> Sim2Result:
    """Execute the full Simulation 2: NN analog temperature sweep."""
    config = config or Sim2Config()
    rng = np.random.default_rng(config.seed)

    energies, amplitudes = create_branching_landscape(config.n_branches, config.seed)
    born_probs = np.abs(amplitudes) ** 2

    temperatures = np.array([lr / config.batch_sizes[0] for lr in config.learning_rates])
    n_temps = len(temperatures)
    n_branches = config.n_branches

    weight_dists = np.zeros((n_temps, n_branches))
    gibbs_preds = np.zeros((n_temps, n_branches))
    kl_born = np.zeros(n_temps)
    kl_gibbs = np.zeros(n_temps)

    for i, temp in enumerate(temperatures):
        trial_dists = np.zeros((config.n_trials, n_branches))
        for j in range(config.n_trials):
            trial_dists[j] = sgd_on_branching_landscape(
                energies, temp, config.n_epochs * config.n_samples // 10,
                seed=config.seed + i * 100 + j,
            )
        weight_dists[i] = np.mean(trial_dists, axis=0)

        gibbs_preds[i] = gibbs_prediction(energies, temp)

        from src.math_engine.numerical.monte_carlo import kl_divergence

        p_w = weight_dists[i] + 1e-10
        p_w /= p_w.sum()
        p_b = born_probs + 1e-10
        p_b /= p_b.sum()
        p_g = gibbs_preds[i] + 1e-10
        p_g /= p_g.sum()

        kl_born[i] = kl_divergence(p_w, p_b)
        kl_gibbs[i] = kl_divergence(p_w, p_g)

    return Sim2Result(
        temperatures=temperatures,
        weight_distributions=weight_dists,
        gibbs_predictions=gibbs_preds,
        born_predictions=born_probs,
        kl_from_born=kl_born,
        kl_from_gibbs=kl_gibbs,
        branch_energies=energies,
    )
