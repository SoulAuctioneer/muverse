"""Simulation 4: Born Rule Deviation Test (P1 Discriminator).

The critical test that distinguishes Thermodynamic Darwinism from standard QM.

Setup: A quantum system prepared in a KNOWN PURE STATE |ψ⟩.
Three competing predictions for measurement probabilities:

  1. Standard QM (Born rule): P_i = |⟨i|ψ⟩|²   [temperature-independent]
  2. Standard QM + thermal bath: P_i = Tr(ρ_thermal · |i⟩⟨i|)  [state changes]
  3. Thermodynamic Darwinism: P_i(T) = exp(−S_{E,i}/(ℏ·f(T))) / Z(T)  [rule changes]

The residual between predictions 2 and 3 is the distinguishing signal.
If nonzero, P1 is experimentally testable.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class Sim4Config:
    n_levels: int = 4
    energy_scale: float = 1.0
    n_temperature_points: int = 40
    temp_min: float = 0.01
    temp_max: float = 5.0
    asymmetry: float = 0.3
    seed: int = 42


@dataclass
class Sim4Result:
    temperatures: NDArray[np.float64]
    born_probs: NDArray[np.float64]           # (n_levels,) -- constant
    thermal_state_probs: NDArray[np.float64]  # (n_temps, n_levels) -- standard QM
    td_probs: NDArray[np.float64]             # (n_temps, n_levels) -- Thermo Darwinism
    residual: NDArray[np.float64]             # (n_temps, n_levels) -- td - thermal
    residual_norm: NDArray[np.float64]        # (n_temps,) -- L2 norm of residual
    td_born_residual_norm: NDArray[np.float64]  # (n_temps,) -- TD deviation from Born
    energies: NDArray[np.float64]
    euclidean_actions: NDArray[np.float64]


def run_simulation(config: Sim4Config | None = None) -> Sim4Result:
    """Execute the Born rule deviation test."""
    config = config or Sim4Config()
    rng = np.random.default_rng(config.seed)

    n = config.n_levels
    temps = np.logspace(
        np.log10(config.temp_min),
        np.log10(config.temp_max),
        config.n_temperature_points,
    )

    # Energy levels with controlled asymmetry
    energies = np.arange(n, dtype=float) * config.energy_scale
    energies += rng.uniform(-config.asymmetry, config.asymmetry, n) * config.energy_scale
    energies -= energies.min()  # ground state at 0
    energies = np.sort(energies)

    # Initial pure state: asymmetric superposition (NOT a thermal state)
    amplitudes = rng.uniform(0.3, 1.0, n)
    amplitudes /= np.sqrt(np.sum(amplitudes**2))

    # Euclidean actions derived from the HAMILTONIAN via WKB tunneling formula.
    # For transitions between energy levels separated by barrier height ΔE,
    # the WKB tunneling action is S_E ~ √(2m) ∫ √(V-E) dx ∝ E^(3/2) for
    # a generic potential.  In ℏ=1 units with characteristic length a₀=1:
    #   S_E,i = c · (E_i)^(3/2)   for excited states
    #   S_E,0 = 0                   for ground state (no barrier)
    # The constant c sets the WKB regime scale.
    wkb_scale = 1.0 / config.energy_scale
    euclidean_actions = np.zeros(n)
    euclidean_actions[1:] = wkb_scale * energies[1:] ** 1.5

    # Born rule probabilities from the initial state (independent of S_E)
    born_probs = amplitudes**2

    # --- Prediction 2: Standard QM with thermal bath ---
    # The SYSTEM thermalizes. The density matrix becomes ρ = exp(−βH)/Z.
    # This is what standard QM predicts when you couple to a bath.
    thermal_state_probs = np.zeros((len(temps), n))
    for i, T in enumerate(temps):
        beta = 1.0 / max(T, 1e-15)
        boltzmann = np.exp(-beta * energies)
        thermal_state_probs[i] = boltzmann / boltzmann.sum()

    # --- Prediction 3: Thermodynamic Darwinism ---
    # TD claims that the probability of measuring branch i is NOT |ψ_i|²
    # but instead depends on the Euclidean action of the branch:
    #   P_i(T) = exp(−β_eff(T) · S_{E,i}) / Z(T)
    #
    # At T=0:  β_eff → ∞, lowest-action branch dominates (ground state)
    # At T=∞:  β_eff → 0, all branches equiprobable (uniform)
    # At finite T: Boltzmann-weighted by action, NOT by energy
    #
    # The phenomenological broadening: β_eff(T) = 2/(ℏ(1 + k_BT/(2ℏ)))
    # Motivation: at ℏ=1, the WKB regime sets β₀=2. Coupling to a bath
    # at temperature T introduces thermal fluctuations that reduce the
    # effective inverse temperature. The specific form is an ansatz;
    # a full derivation requires solving the open-system WKB problem.
    td_probs = np.zeros((len(temps), n))
    for i, T in enumerate(temps):
        beta_eff = 2.0 / (1.0 + T / 2.0)
        weights = np.exp(-beta_eff * euclidean_actions)
        td_probs[i] = weights / weights.sum()

    # --- Residuals: distinguishing signals ---
    residual = td_probs - thermal_state_probs
    residual_norm = np.sqrt(np.sum(residual**2, axis=1))

    # TD deviation from Born rule (the broadening effect unique to TD)
    td_born_residual = td_probs - born_probs[np.newaxis, :]
    td_born_residual_norm = np.sqrt(np.sum(td_born_residual**2, axis=1))

    return Sim4Result(
        temperatures=temps,
        born_probs=born_probs,
        thermal_state_probs=thermal_state_probs,
        td_probs=td_probs,
        residual=residual,
        residual_norm=residual_norm,
        td_born_residual_norm=td_born_residual_norm,
        energies=energies,
        euclidean_actions=euclidean_actions,
    )
