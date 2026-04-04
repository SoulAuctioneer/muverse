"""Decoherence simulation for quantum branch selection.

Models environment-induced decoherence that transforms quantum
superpositions into classical-like branch mixtures. Tracks the
energy cost of decoherence events (Landauer bound) and tests
whether Jarzynski double stochasticity is preserved.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class DecoherenceResult:
    initial_state: NDArray[np.complex128]
    final_density_matrix: NDArray[np.complex128]
    branch_probabilities: NDArray[np.float64]
    coherence_measure: float
    energy_dissipated: float
    jarzynski_preserved: bool


def pure_state_density_matrix(psi: NDArray[np.complex128]) -> NDArray[np.complex128]:
    """|ψ⟩⟨ψ| from a state vector."""
    return np.outer(psi, np.conj(psi))


def partial_decoherence(
    rho: NDArray[np.complex128],
    decoherence_rate: float,
    dt: float = 0.1,
) -> NDArray[np.complex128]:
    """Apply partial decoherence: off-diagonal elements decay exponentially.

    ρ_ij(t+dt) = ρ_ij(t) · exp(−γ dt)  for i ≠ j
    ρ_ii(t+dt) = ρ_ii(t)               (populations preserved)

    This models the Lindblad decoherence channel in the pointer basis.
    """
    n = rho.shape[0]
    rho_new = rho.copy()
    decay = np.exp(-decoherence_rate * dt)
    for i in range(n):
        for j in range(n):
            if i != j:
                rho_new[i, j] *= decay
    return rho_new


def full_decoherence(rho: NDArray[np.complex128]) -> NDArray[np.complex128]:
    """Complete decoherence: remove all off-diagonal elements."""
    return np.diag(np.diag(rho))


def coherence_measure(rho: NDArray[np.complex128]) -> float:
    """l1-norm of coherence: sum of absolute values of off-diagonal elements."""
    n = rho.shape[0]
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i != j:
                total += abs(rho[i, j])
    return float(total)


def landauer_cost(n_bits: int, temperature: float, k_B: float = 1.0) -> float:
    """Minimum energy dissipated per Landauer's principle: Q = n · k_BT ln 2."""
    return n_bits * k_B * temperature * np.log(2)


def simulate_branching_decoherence(
    psi: NDArray[np.complex128],
    hamiltonian: NDArray[np.complex128],
    decoherence_rate: float,
    n_steps: int = 100,
    dt: float = 0.01,
    temperature: float = 1.0,
) -> DecoherenceResult:
    """Simulate unitary evolution + decoherence of a quantum state.

    Alternates Hamiltonian evolution with decoherence channel, tracking
    the energy cost of information loss.
    """
    n = len(psi)
    rho = pure_state_density_matrix(psi)
    total_energy_dissipated = 0.0

    U = np.eye(n, dtype=complex) - 1j * hamiltonian * dt

    for _ in range(n_steps):
        rho = U @ rho @ np.conj(U.T)

        coherence_before = coherence_measure(rho)
        rho = partial_decoherence(rho, decoherence_rate, dt)
        coherence_after = coherence_measure(rho)

        bits_lost = max(0, (coherence_before - coherence_after) / coherence_before) if coherence_before > 0 else 0
        total_energy_dissipated += landauer_cost(
            int(np.ceil(bits_lost * np.log2(n))), temperature
        )

    branch_probs = np.real(np.diag(rho))
    branch_probs = np.maximum(branch_probs, 0)
    if branch_probs.sum() > 0:
        branch_probs /= branch_probs.sum()

    final_coherence = coherence_measure(rho)

    transition_matrix = np.abs(U) ** 2
    row_sums = transition_matrix.sum(axis=1)
    col_sums = transition_matrix.sum(axis=0)
    doubly_stochastic = (
        np.allclose(row_sums, 1.0, atol=0.1) and np.allclose(col_sums, 1.0, atol=0.1)
    )

    return DecoherenceResult(
        initial_state=psi,
        final_density_matrix=rho,
        branch_probabilities=branch_probs,
        coherence_measure=final_coherence,
        energy_dissipated=total_energy_dissipated,
        jarzynski_preserved=doubly_stochastic,
    )
