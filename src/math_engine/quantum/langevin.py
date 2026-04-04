"""Quantum Langevin dynamics simulation.

An open dissipative quantum system coupled to a thermal bath,
modeling the branch-selection process under thermodynamic constraints.
The system converges toward a steady state near the global minimum
with exponential convergence at low temperature.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class QLangevinResult:
    time_grid: NDArray[np.float64]
    density_matrices: list[NDArray[np.complex128]]
    populations_history: NDArray[np.float64]  # (n_steps, n_states)
    steady_state_populations: NDArray[np.float64]
    effective_temperature: float
    convergence_time: float


def thermal_occupation(energies: NDArray[np.float64], temperature: float) -> NDArray[np.float64]:
    """Boltzmann occupation probabilities: p_n = exp(−E_n/T) / Z."""
    if temperature <= 0:
        p = np.zeros_like(energies)
        p[np.argmin(energies)] = 1.0
        return p
    log_p = -energies / temperature
    log_p -= np.max(log_p)
    p = np.exp(log_p)
    return p / p.sum()


def lindblad_dissipator(
    rho: NDArray[np.complex128],
    L: NDArray[np.complex128],
) -> NDArray[np.complex128]:
    """Single Lindblad dissipator: D[L]ρ = LρL† − ½{L†L, ρ}."""
    Ld = np.conj(L.T)
    LdL = Ld @ L
    return L @ rho @ Ld - 0.5 * (LdL @ rho + rho @ LdL)


def quantum_langevin_step(
    rho: NDArray[np.complex128],
    H: NDArray[np.complex128],
    jump_ops: list[NDArray[np.complex128]],
    dt: float,
) -> NDArray[np.complex128]:
    """Single time step of Lindblad master equation.

    dρ/dt = −i[H, ρ] + Σ_k D[L_k]ρ
    """
    commutator = -1j * (H @ rho - rho @ H)
    dissipation = sum(lindblad_dissipator(rho, L) for L in jump_ops)
    rho_new = rho + dt * (commutator + dissipation)

    rho_new = 0.5 * (rho_new + np.conj(rho_new.T))
    trace = np.real(np.trace(rho_new))
    if trace > 0:
        rho_new /= trace
    return rho_new


def build_thermal_bath_operators(
    H: NDArray[np.complex128],
    temperature: float,
    coupling_strength: float = 0.1,
) -> list[NDArray[np.complex128]]:
    """Construct Lindblad jump operators for a thermal bath.

    For an N-level system with Hamiltonian H, the bath induces
    transitions between energy eigenstates at rates determined by
    the detailed balance condition.
    """
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    n = len(eigenvalues)
    jump_ops = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            delta_E = eigenvalues[j] - eigenvalues[i]

            if temperature > 0:
                if delta_E > 0:
                    rate = coupling_strength * np.exp(-delta_E / temperature)
                else:
                    rate = coupling_strength
            else:
                rate = coupling_strength if delta_E < 0 else 0.0

            if rate > 1e-12:
                L = np.sqrt(rate) * np.outer(eigenvectors[:, j], np.conj(eigenvectors[:, i]))
                jump_ops.append(L)

    return jump_ops


def simulate_quantum_langevin(
    H: NDArray[np.complex128],
    initial_state: NDArray[np.complex128],
    temperature: float,
    coupling_strength: float = 0.1,
    t_max: float = 50.0,
    dt: float = 0.05,
) -> QLangevinResult:
    """Full quantum Langevin simulation.

    Evolves a quantum system coupled to a thermal bath at given temperature,
    tracking the approach to thermal equilibrium (Gibbs state).
    """
    n_steps = int(t_max / dt)
    n = H.shape[0]

    if initial_state.ndim == 1:
        rho = np.outer(initial_state, np.conj(initial_state))
    else:
        rho = initial_state.copy()

    jump_ops = build_thermal_bath_operators(H, temperature, coupling_strength)

    time_grid = np.linspace(0, t_max, n_steps)
    populations = np.empty((n_steps, n))
    density_matrices = []

    for step in range(n_steps):
        pops = np.real(np.diag(rho))
        populations[step] = pops
        if step % max(1, n_steps // 20) == 0:
            density_matrices.append(rho.copy())
        rho = quantum_langevin_step(rho, H, jump_ops, dt)

    steady_pops = populations[-1]
    target_pops = thermal_occupation(np.real(np.diag(H)), temperature)

    diff_history = np.sum(np.abs(populations - target_pops[None, :]), axis=1)
    threshold = 0.05 * n
    converged_steps = np.where(diff_history < threshold)[0]
    convergence_time = float(time_grid[converged_steps[0]]) if len(converged_steps) > 0 else t_max

    return QLangevinResult(
        time_grid=time_grid,
        density_matrices=density_matrices,
        populations_history=populations,
        steady_state_populations=steady_pops,
        effective_temperature=temperature,
        convergence_time=convergence_time,
    )
