"""Simulation 3: Quantum Langevin Dynamics.

Tests whether branch probability distributions in a quantum system
coupled to a thermal bath shift with temperature in a way consistent
with Boltzmann weighting, as predicted by the Thermodynamic Darwinism
framework.

Null hypothesis (H0): Branch probabilities are temperature-independent (standard QM)
Alternative (H1): Branch probabilities follow Gibbs distribution with bath temperature

The system: an N-level quantum system (representing branch structure) coupled
to a thermal bath at tunable temperature T. We measure the steady-state
populations and compare to both Born rule and Gibbs predictions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.math_engine.quantum.langevin import (
    QLangevinResult,
    simulate_quantum_langevin,
    thermal_occupation,
)


@dataclass
class Sim3Config:
    n_levels: int = 6
    energy_scale: float = 1.0
    coupling_strength: float = 0.1
    temperatures: list[float] | None = None
    t_max: float = 100.0
    dt: float = 0.02
    n_trials: int = 5
    seed: int = 42

    def __post_init__(self):
        if self.temperatures is None:
            self.temperatures = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]


@dataclass
class Sim3Result:
    temperatures: NDArray[np.float64]
    steady_state_pops: NDArray[np.float64]  # (n_temps, n_levels)
    gibbs_predictions: NDArray[np.float64]  # (n_temps, n_levels)
    born_predictions: NDArray[np.float64]  # (n_levels,)
    kl_from_gibbs: NDArray[np.float64]  # (n_temps,)
    kl_from_born: NDArray[np.float64]  # (n_temps,)
    convergence_times: NDArray[np.float64]
    energies: NDArray[np.float64]
    population_histories: list[NDArray[np.float64]]


def build_hamiltonian(
    n_levels: int,
    energy_scale: float,
    seed: int = 42,
) -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
    """Build a Hamiltonian with specified level structure and an initial superposition state.

    Returns (H, psi_0) where H is the Hamiltonian and psi_0 is an
    equal superposition over all levels (maximum uncertainty initial state).
    """
    rng = np.random.default_rng(seed)

    energies = np.sort(rng.exponential(energy_scale, n_levels))
    energies[0] = 0.0  # ground state at zero

    U = np.linalg.qr(rng.standard_normal((n_levels, n_levels)))[0]
    H = U @ np.diag(energies) @ np.conj(U.T)

    psi_0 = np.ones(n_levels, dtype=complex) / np.sqrt(n_levels)

    return H, psi_0


def run_simulation(config: Sim3Config | None = None) -> Sim3Result:
    """Execute the full Simulation 3: Quantum Langevin temperature sweep."""
    config = config or Sim3Config()

    H, psi_0 = build_hamiltonian(config.n_levels, config.energy_scale, config.seed)
    energies = np.real(np.sort(np.linalg.eigvalsh(H)))

    born_probs = np.abs(psi_0) ** 2

    temps = np.array(config.temperatures)
    n_temps = len(temps)
    n_levels = config.n_levels

    steady_pops = np.zeros((n_temps, n_levels))
    gibbs_preds = np.zeros((n_temps, n_levels))
    kl_gibbs = np.zeros(n_temps)
    kl_born = np.zeros(n_temps)
    conv_times = np.zeros(n_temps)
    pop_histories = []

    from src.math_engine.numerical.monte_carlo import kl_divergence

    for i, temp in enumerate(temps):
        trial_pops = np.zeros((config.n_trials, n_levels))

        for j in range(config.n_trials):
            rng = np.random.default_rng(config.seed + i * 100 + j)
            phase = rng.uniform(0, 2 * np.pi, n_levels)
            init = np.abs(psi_0) * np.exp(1j * phase)
            init /= np.sqrt(np.sum(np.abs(init) ** 2))

            result = simulate_quantum_langevin(
                H=H,
                initial_state=init,
                temperature=temp,
                coupling_strength=config.coupling_strength,
                t_max=config.t_max,
                dt=config.dt,
            )
            trial_pops[j] = result.steady_state_populations

        steady_pops[i] = np.mean(trial_pops, axis=0)
        gibbs_preds[i] = thermal_occupation(energies, temp)

        if i == len(temps) // 2:
            pop_histories.append(result.populations_history)

        p_s = steady_pops[i] + 1e-10
        p_s /= p_s.sum()
        p_g = gibbs_preds[i] + 1e-10
        p_g /= p_g.sum()
        p_b = born_probs + 1e-10
        p_b /= p_b.sum()

        kl_gibbs[i] = kl_divergence(p_s, p_g)
        kl_born[i] = kl_divergence(p_s, p_b)
        conv_times[i] = result.convergence_time

    return Sim3Result(
        temperatures=temps,
        steady_state_pops=steady_pops,
        gibbs_predictions=gibbs_preds,
        born_predictions=born_probs,
        kl_from_gibbs=kl_gibbs,
        kl_from_born=kl_born,
        convergence_times=conv_times,
        energies=energies,
        population_histories=pop_histories,
    )
