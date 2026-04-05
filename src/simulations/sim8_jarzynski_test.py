"""Simulation 8: Jarzynski Double Stochasticity Test.

PURPOSE
-------
Test Axiom A4's three claims:
  (a) Decoherent branching (unitary + partial trace) preserves double stochasticity
  (b) Dissipative branching breaks double stochasticity
  (c) Jarzynski-violating branches are suppressed under energy-constrained weighting

Claims (a) and (b) are established physics (Birkhoff's theorem for unitaries).
Claim (c) depends on the Gibbs(S_E) weighting from falsified A3.

PHYSICAL SETUP
--------------
A d-level quantum system coupled to a bath of n_env qubits.
1. Build unitary evolution U = exp(-iHt) for the composite system.
2. Compute transition matrix T_nm by tracing out the bath (maximally mixed).
3. Check double stochasticity: row sums = col sums = 1.
4. Add Lindblad dissipation and check if DS breaks.
5. Compute Jarzynski ratio: <e^{-beta W}> / e^{-beta Delta_F}.

KEY METRICS
-----------
- ds_distance: Frobenius norm of deviation from doubly stochastic constraints
- jarzynski_ratio: should be 1.0 for unitary, deviate for dissipative
- row_sum_dev / col_sum_dev: separate tracking of stochastic vs doubly-stochastic

References:
  Birkhoff, Tres observaciones sobre el algebra lineal (1946)
  Campisi, Hanggi, Talkner, Rev. Mod. Phys. 83, 771 (2011)
  Manzano, Horowitz, Parrondo, Phys. Rev. X 8, 031037 (2018)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm


@dataclass
class Sim8Config:
    d_system: int = 4
    n_env_qubits: int = 3
    coupling_strength: float = 0.5
    dissipation_rates: list[float] = field(
        default_factory=lambda: [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    )
    temperature: float = 1.0
    t_final: float = 5.0
    n_time_steps: int = 300
    seed: int = 42


@dataclass
class Sim8Result:
    dissipation_rates: NDArray[np.float64]
    ds_distance: NDArray[np.float64]
    jarzynski_ratio: NDArray[np.float64]
    row_sum_dev: NDArray[np.float64]
    col_sum_dev: NDArray[np.float64]
    a4_verified_unitary: bool
    a4_broken_dissipative: bool
    temperature: float
    system_energies: NDArray[np.float64]


def _build_hamiltonian(
    d_sys: int, n_env: int, coupling: float, rng: np.random.Generator,
) -> tuple[NDArray, NDArray]:
    """Build system + bath + interaction Hamiltonian.

    Returns (H_total, system_energies).
    """
    d_bath = 2 ** n_env
    d_total = d_sys * d_bath

    E_sys = np.arange(d_sys, dtype=float)
    H = np.zeros((d_total, d_total), dtype=complex)

    bath_energies = rng.standard_normal(n_env) * 0.5
    for env_state in range(d_bath):
        e_bath = 0.0
        for q in range(n_env):
            bit = (env_state >> q) & 1
            e_bath += bath_energies[q] * (2 * bit - 1)
        for s in range(d_sys):
            idx = s * d_bath + env_state
            H[idx, idx] = E_sys[s] + e_bath

    for s in range(d_sys):
        fields = rng.standard_normal(n_env) * coupling * (s + 1)
        for env_state in range(d_bath):
            e_int = 0.0
            for q in range(n_env):
                bit = (env_state >> q) & 1
                e_int += fields[q] * (2 * bit - 1)
            idx = s * d_bath + env_state
            H[idx, idx] += e_int

    return H, E_sys


def _transition_matrix_unitary(
    U: NDArray, d_sys: int, d_bath: int,
) -> NDArray:
    """Transition matrix from unitary evolution with maximally mixed bath.

    T_nm = (1/d_bath) sum_{e,e'} |U_{n,e';m,e}|^2

    Birkhoff's theorem guarantees this is doubly stochastic.
    """
    T = np.zeros((d_sys, d_sys))
    for m in range(d_sys):
        for n in range(d_sys):
            val = 0.0
            for e_init in range(d_bath):
                for e_final in range(d_bath):
                    i_init = m * d_bath + e_init
                    i_final = n * d_bath + e_final
                    val += abs(U[i_final, i_init]) ** 2
            T[n, m] = val / d_bath
    return T


def _transition_matrix_lindblad(
    H: NDArray,
    collapse_ops: list[NDArray],
    d_sys: int,
    d_bath: int,
    gamma: float,
    t_final: float,
    n_steps: int,
) -> NDArray:
    """Transition matrix from Lindblad evolution with maximally mixed bath.

    For each initial system state |m>, evolve rho = |m><m| x rho_bath
    under the Lindblad master equation, then read off system populations.
    """
    d_total = d_sys * d_bath
    dt = t_final / n_steps
    T = np.zeros((d_sys, d_sys))
    rho_bath = np.eye(d_bath, dtype=complex) / d_bath

    for m in range(d_sys):
        rho_sys_init = np.zeros((d_sys, d_sys), dtype=complex)
        rho_sys_init[m, m] = 1.0
        rho = np.kron(rho_sys_init, rho_bath)

        for _ in range(n_steps):
            drho = -1j * (H @ rho - rho @ H)
            for L in collapse_ops:
                Ld = L.conj().T
                LdL = Ld @ L
                drho += gamma * (L @ rho @ Ld - 0.5 * (LdL @ rho + rho @ LdL))
            rho = rho + drho * dt
            rho = 0.5 * (rho + rho.conj().T)
            trace_val = np.real(np.trace(rho))
            if trace_val > 1e-15:
                rho /= trace_val

        for n in range(d_sys):
            pop = 0.0
            for e in range(d_bath):
                idx = n * d_bath + e
                pop += np.real(rho[idx, idx])
            T[n, m] = max(0.0, pop)

    for m in range(d_sys):
        col_sum = T[:, m].sum()
        if col_sum > 1e-15:
            T[:, m] /= col_sum

    return T


def _ds_distance(T: NDArray) -> float:
    """Frobenius distance from doubly stochastic constraints."""
    row_dev = T.sum(axis=1) - 1.0
    col_dev = T.sum(axis=0) - 1.0
    return float(np.sqrt(np.sum(row_dev ** 2) + np.sum(col_dev ** 2)))


def _jarzynski_ratio(T: NDArray, energies: NDArray, beta: float) -> float:
    """Compute <e^{-beta W}> for same-Hamiltonian process.

    For same initial and final Hamiltonian, Delta_F = 0, so the Jarzynski
    equality predicts <e^{-beta W}> = 1 iff T is doubly stochastic.
    """
    d = len(energies)
    boltz = np.exp(-beta * energies)
    Z = boltz.sum()
    p_init = boltz / Z

    ratio = 0.0
    for m in range(d):
        for n in range(d):
            W = energies[n] - energies[m]
            ratio += p_init[m] * T[n, m] * np.exp(-beta * W)
    return float(ratio)


def run_simulation(config: Sim8Config | None = None) -> Sim8Result:
    """Execute the Jarzynski double stochasticity test."""
    cfg = config or Sim8Config()
    rng = np.random.default_rng(cfg.seed)

    d_sys = cfg.d_system
    d_bath = 2 ** cfg.n_env_qubits
    beta = 1.0 / cfg.temperature

    H, E_sys = _build_hamiltonian(d_sys, cfg.n_env_qubits, cfg.coupling_strength, rng)

    I_bath = np.eye(d_bath, dtype=complex)
    collapse_ops: list[NDArray] = []
    for k in range(d_sys - 1):
        L_sys = np.zeros((d_sys, d_sys), dtype=complex)
        L_sys[k, k + 1] = 1.0
        collapse_ops.append(np.kron(L_sys, I_bath))

    U = expm(-1j * H * cfg.t_final)

    gammas = np.array(cfg.dissipation_rates)
    n_gamma = len(gammas)

    ds_dist = np.zeros(n_gamma)
    j_ratio = np.zeros(n_gamma)
    row_dev = np.zeros(n_gamma)
    col_dev = np.zeros(n_gamma)

    for idx, gamma in enumerate(gammas):
        if gamma < 1e-12:
            T = _transition_matrix_unitary(U, d_sys, d_bath)
        else:
            T = _transition_matrix_lindblad(
                H, collapse_ops, d_sys, d_bath,
                gamma, cfg.t_final, cfg.n_time_steps,
            )

        ds_dist[idx] = _ds_distance(T)
        j_ratio[idx] = _jarzynski_ratio(T, E_sys, beta)
        row_dev[idx] = float(np.max(np.abs(T.sum(axis=1) - 1.0)))
        col_dev[idx] = float(np.max(np.abs(T.sum(axis=0) - 1.0)))

    unitary_ds = bool(
        len(gammas) > 0 and gammas[0] < 1e-12 and ds_dist[0] < 0.01
    )
    diss_indices = [i for i, g in enumerate(gammas) if g > 0.1]
    diss_broken = bool(any(ds_dist[i] > 0.05 for i in diss_indices))

    return Sim8Result(
        dissipation_rates=gammas,
        ds_distance=ds_dist,
        jarzynski_ratio=j_ratio,
        row_sum_dev=row_dev,
        col_sum_dev=col_dev,
        a4_verified_unitary=unitary_ds,
        a4_broken_dissipative=diss_broken,
        temperature=cfg.temperature,
        system_energies=E_sys,
    )
