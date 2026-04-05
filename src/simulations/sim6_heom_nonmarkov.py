"""Simulation 6: HEOM Non-Markovian Dynamics — Beyond Lindblad.

PURPOSE
-------
Sim5 showed that the Lindblad (Markovian, weak-coupling) steady state is
Gibbs(E), not Gibbs(S_E). But Lindblad is an approximation. The exact
steady state at finite coupling is the mean-force Gibbs (MFG) state,
which deviates from bare Gibbs(E).

This simulation solves the Hierarchical Equations of Motion (HEOM) for
the same double-well system coupled to a Drude-Lorentz thermal bath at
various coupling strengths. HEOM is numerically exact for this class of
bath and captures all non-Markovian effects.

SCIENTIFIC QUESTION
-------------------
As coupling increases, the MFG steady state deviates from bare Gibbs(E).
Does this deviation point TOWARD Gibbs(S_E) (supporting the TD hypothesis)
or in an unrelated direction (further constraining it)?

The "direction cosine" metric:
  cos(θ) = (v_HEOM · v_TD) / (|v_HEOM| |v_TD|)

where v_HEOM = ρ_HEOM − ρ_Gibbs(E) and v_TD = ρ_Gibbs(S_E) − ρ_Gibbs(E).
  cos(θ) ≈ +1: deviation aligns with TD prediction
  cos(θ) ≈  0: deviation is orthogonal (unrelated)
  cos(θ) ≈ −1: deviation is opposite to TD
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import trapezoid


@dataclass
class Sim6Config:
    n_grid: int = 200
    x_max: float = 5.0
    barrier_height: float = 6.0
    well_separation: float = 1.8
    asymmetry: float = 0.15
    n_levels: int = 6
    bath_temp: float = 2.0
    coupling_strengths: list[float] = field(
        default_factory=lambda: [0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0]
    )
    bath_cutoff: float = 2.0  # gamma: bath memory cutoff frequency
    heom_depth: int = 5
    n_matsubara: int = 3
    seed: int = 42


@dataclass
class Sim6Result:
    energies: NDArray[np.float64]
    wkb_actions: NDArray[np.float64]
    barrier_top: float

    coupling_strengths: NDArray[np.float64]

    # (n_couplings, n_levels): HEOM exact steady-state populations
    heom_pops: NDArray[np.float64]

    # (n_levels,): bare Gibbs(E) — the weak-coupling prediction
    gibbs_energy_pops: NDArray[np.float64]

    # (n_levels,): Gibbs(S_E) — the TD prediction
    gibbs_action_pops: NDArray[np.float64]

    # (n_couplings,): ||HEOM - Gibbs(E)|| — deviation from standard QM
    residual_heom_vs_gibbs_e: NDArray[np.float64]

    # (n_couplings,): ||HEOM - Gibbs(S_E)|| — deviation from TD
    residual_heom_vs_gibbs_s: NDArray[np.float64]

    # (n_couplings,): cos(angle) between (HEOM-Gibbs(E)) and (Gibbs(S_E)-Gibbs(E))
    direction_cosine: NDArray[np.float64]

    bath_temp: float
    bath_cutoff: float


def _build_hamiltonian(cfg: Sim6Config):
    """Build double-well Hamiltonian on a position grid and diagonalise."""
    dx = 2 * cfg.x_max / (cfg.n_grid - 1)
    x = np.linspace(-cfg.x_max, cfg.x_max, cfg.n_grid)

    x0 = cfg.well_separation
    a = cfg.barrier_height / x0 ** 4
    V = a * (x ** 2 - x0 ** 2) ** 2 + cfg.asymmetry * x

    barrier_top = cfg.barrier_height

    diag_main = np.full(cfg.n_grid, 1.0 / dx ** 2)
    diag_off = np.full(cfg.n_grid - 1, -0.5 / dx ** 2)
    T_mat = np.diag(diag_main) + np.diag(diag_off, 1) + np.diag(diag_off, -1)

    H = T_mat + np.diag(V)
    eigenvalues, eigenvectors = np.linalg.eigh(H)

    return eigenvalues, eigenvectors, x, V, barrier_top


def _wkb_actions(
    energies: NDArray, x: NDArray, V: NDArray, n_levels: int, well_sep: float,
) -> NDArray:
    """Compute WKB tunneling action through the central barrier."""
    actions = np.zeros(n_levels)
    central = np.abs(x) < well_sep * 1.1
    for n in range(n_levels):
        E_n = energies[n]
        forbidden = (V > E_n) & central
        if not np.any(forbidden):
            continue
        integrand = np.sqrt(2.0 * np.maximum(V[forbidden] - E_n, 0.0))
        actions[n] = trapezoid(integrand, x[forbidden])
    return actions


def _position_matrix_elements(eigvecs: NDArray, x: NDArray, n_levels: int) -> NDArray:
    """Compute <m|x|n> in the energy eigenbasis."""
    X = np.zeros((n_levels, n_levels))
    for i in range(n_levels):
        for j in range(n_levels):
            X[i, j] = np.sum(eigvecs[:, i] * x * eigvecs[:, j])
    return X


def _gibbs_distribution(quantities: NDArray, beta: float) -> NDArray:
    log_weights = -beta * quantities
    log_weights -= log_weights.max()
    weights = np.exp(log_weights)
    return weights / weights.sum()


def _solve_heom_steady_state(
    energies: NDArray,
    X_mn: NDArray,
    n_levels: int,
    lam: float,
    gamma: float,
    T_bath: float,
    max_depth: int,
    Nk: int,
):
    """Solve for the exact non-Markovian steady state using HEOM."""
    import qutip as qt
    from qutip.solver.heom import DrudeLorentzBath, HEOMSolver

    H_q = qt.Qobj(np.diag(energies[:n_levels]))

    Q_op = qt.Qobj(X_mn)

    bath = DrudeLorentzBath(Q_op, lam=lam, gamma=gamma, T=T_bath, Nk=Nk)

    solver = HEOMSolver(H_q, bath, max_depth=max_depth)
    result = solver.steady_state(use_mkl=False)

    if isinstance(result, tuple):
        rho_ss = result[0]
    else:
        rho_ss = result

    return np.real(np.diag(rho_ss.full()))


def run_simulation(config: Sim6Config | None = None) -> Sim6Result:
    """Execute the HEOM non-Markovian test."""
    cfg = config or Sim6Config()

    all_E, all_vecs, x_grid, V_grid, barrier_top = _build_hamiltonian(cfg)

    energies = all_E[: cfg.n_levels]
    energies_shifted = energies - energies[0]

    wkb_actions = _wkb_actions(all_E, x_grid, V_grid, cfg.n_levels, cfg.well_separation)

    X_mn = _position_matrix_elements(all_vecs, x_grid, cfg.n_levels)

    beta = 1.0 / max(cfg.bath_temp, 1e-15)

    gibbs_e = _gibbs_distribution(energies_shifted, beta)

    if np.all(wkb_actions == 0):
        gibbs_s = np.ones(cfg.n_levels) / cfg.n_levels
    else:
        beta_eff = 2.0 / (1.0 + cfg.bath_temp / 2.0)
        gibbs_s = _gibbs_distribution(wkb_actions, beta_eff)

    couplings = np.array(cfg.coupling_strengths)
    n_couplings = len(couplings)

    heom_pops = np.zeros((n_couplings, cfg.n_levels))
    res_he = np.zeros(n_couplings)
    res_hs = np.zeros(n_couplings)
    dir_cos = np.zeros(n_couplings)

    v_td = gibbs_s - gibbs_e
    v_td_norm = np.linalg.norm(v_td)

    for i, lam_val in enumerate(couplings):
        pops = _solve_heom_steady_state(
            all_E, X_mn, cfg.n_levels,
            lam=lam_val,
            gamma=cfg.bath_cutoff,
            T_bath=cfg.bath_temp,
            max_depth=cfg.heom_depth,
            Nk=cfg.n_matsubara,
        )
        heom_pops[i] = pops

        res_he[i] = np.linalg.norm(pops - gibbs_e)
        res_hs[i] = np.linalg.norm(pops - gibbs_s)

        v_heom = pops - gibbs_e
        v_heom_norm = np.linalg.norm(v_heom)

        if v_heom_norm > 1e-10 and v_td_norm > 1e-10:
            dir_cos[i] = np.dot(v_heom, v_td) / (v_heom_norm * v_td_norm)
        else:
            dir_cos[i] = 0.0

    barrier_shifted = barrier_top - all_E[0]

    return Sim6Result(
        energies=energies_shifted,
        wkb_actions=wkb_actions,
        barrier_top=barrier_shifted,
        coupling_strengths=couplings,
        heom_pops=heom_pops,
        gibbs_energy_pops=gibbs_e,
        gibbs_action_pops=gibbs_s,
        residual_heom_vs_gibbs_e=res_he,
        residual_heom_vs_gibbs_s=res_hs,
        direction_cosine=dir_cos,
        bath_temp=cfg.bath_temp,
        bath_cutoff=cfg.bath_cutoff,
    )
