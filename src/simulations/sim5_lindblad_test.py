"""Simulation 5: Lindblad Master Equation — The Small Provable Step.

PURPOSE
-------
Test the core claim of Thermodynamic Darwinism against actual open-quantum
dynamics.  Standard QM (Lindblad master equation with detailed balance)
predicts that a system coupled to a thermal bath relaxes to the Gibbs state
ρ_ss = exp(−βH)/Z.  The TD hypothesis predicts Gibbs weighting over
Euclidean actions instead of energies.

This simulation solves the Lindblad equation for a concrete double-well
potential and compares the steady-state populations to both predictions.

SYSTEM
------
Quartic double-well: V(x) = a·(x² − x₀²)²
Energy levels below and above the barrier have WKB tunneling actions S_E
that are *nonlinearly* related to energies E — precisely the regime where
Gibbs(E) and Gibbs(S_E) give different predictions.

EXPECTED RESULT
---------------
The Lindblad equation satisfies detailed balance, so the steady state is
*guaranteed* to be Gibbs(E).  Any deviation would be a bug, not new physics.
The scientific value is in QUANTIFYING:
  • How different Gibbs(E) and Gibbs(S_E) are for this system
  • What measurement precision would distinguish them
  • In what parameter regime the predictions diverge most
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import trapezoid


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Sim5Config:
    n_grid: int = 200
    x_max: float = 5.0
    barrier_height: float = 6.0
    well_separation: float = 1.8
    asymmetry: float = 0.15
    n_levels: int = 8
    bath_temps: list[float] = field(default_factory=lambda: [0.5, 1.0, 2.0, 4.0, 8.0])
    gamma_0: float = 0.01
    t_max: float = 300.0
    n_time_steps: int = 400
    seed: int = 42


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class Sim5Result:
    energies: NDArray[np.float64]
    wkb_actions: NDArray[np.float64]
    barrier_top: float

    bath_temps: NDArray[np.float64]

    # (n_temps, n_levels): populations from the Lindblad steady state
    lindblad_pops: NDArray[np.float64]

    # (n_temps, n_levels): standard QM prediction — Gibbs over energies
    gibbs_energy_pops: NDArray[np.float64]

    # (n_temps, n_levels): TD prediction — Gibbs over WKB actions
    gibbs_action_pops: NDArray[np.float64]

    # (n_levels,): Born-rule prediction from the initial state
    born_pops: NDArray[np.float64]

    # (n_temps,): L2 residual between Lindblad and Gibbs(E) — should be ~0
    residual_lindblad_vs_gibbs_e: NDArray[np.float64]

    # (n_temps,): L2 residual between Gibbs(E) and Gibbs(S_E) — the gap
    residual_gibbs_e_vs_gibbs_s: NDArray[np.float64]

    # potential profile for plotting
    x_grid: NDArray[np.float64]
    potential: NDArray[np.float64]

    # time-evolution trace at one temperature (for dynamics plot)
    trace_temp_idx: int
    trace_times: NDArray[np.float64]
    trace_pops: NDArray[np.float64]  # (n_times, n_levels)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_hamiltonian(cfg: Sim5Config):
    """Build double-well Hamiltonian on a position grid and diagonalise."""
    dx = 2 * cfg.x_max / (cfg.n_grid - 1)
    x = np.linspace(-cfg.x_max, cfg.x_max, cfg.n_grid)

    x0 = cfg.well_separation
    a = cfg.barrier_height / x0 ** 4
    V = a * (x ** 2 - x0 ** 2) ** 2 + cfg.asymmetry * x

    barrier_top = cfg.barrier_height + cfg.asymmetry * 0  # at x=0

    # Kinetic energy via 3-point finite difference: T = -ℏ²/(2m) d²/dx²
    diag_main = np.full(cfg.n_grid, 1.0 / dx ** 2)
    diag_off = np.full(cfg.n_grid - 1, -0.5 / dx ** 2)
    T_mat = np.diag(diag_main) + np.diag(diag_off, 1) + np.diag(diag_off, -1)

    H = T_mat + np.diag(V)
    eigenvalues, eigenvectors = np.linalg.eigh(H)

    return eigenvalues, eigenvectors, x, V, barrier_top


def _wkb_actions(
    energies: NDArray, x: NDArray, V: NDArray, n_levels: int,
    well_sep: float,
) -> NDArray:
    """Compute WKB tunneling action through the CENTRAL barrier only.

    S_E,n = ∫_{central barrier} √(2·(V(x) − E_n)) dx

    Only the barrier between the two wells matters for tunneling.
    The outer walls are confinement boundaries, not tunneling barriers.
    For above-barrier states, S_E = 0.
    """
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


def _gibbs_distribution(quantities: NDArray, beta: float) -> NDArray:
    """Compute normalised Gibbs distribution: P_i = exp(-β·q_i) / Z."""
    log_weights = -beta * quantities
    log_weights -= log_weights.max()  # numerical stability
    weights = np.exp(log_weights)
    return weights / weights.sum()


def _position_matrix_elements(
    eigvecs: NDArray, x: NDArray, n_levels: int
) -> NDArray:
    """Compute ⟨m|x|n⟩ in the energy eigenbasis.

    The eigenvectors from eigh satisfy Σ|v_i|²=1. The physical wavefunction
    is ψ(x_i) = v(i)/√dx, so ⟨m|x|n⟩ = Σ v_m(i)·x_i·v_n(i) (no extra dx).
    """
    X = np.zeros((n_levels, n_levels))
    for m in range(n_levels):
        for n in range(n_levels):
            X[m, n] = np.sum(eigvecs[:, m] * x * eigvecs[:, n])
    return X


# ---------------------------------------------------------------------------
# Lindblad dynamics (using QuTiP)
# ---------------------------------------------------------------------------

def _build_lindblad_ops(
    energies: NDArray,
    X_mn: NDArray,
    T_bath: float,
    gamma_0: float,
    n_levels: int,
):
    """Build Lindblad collapse operators for a thermal bath.

    Rates satisfy detailed balance:
      γ_{m→n} / γ_{n→m} = exp(−(E_n − E_m)/T)
    which guarantees the unique steady state is ρ_ss = exp(−H/T)/Z.
    """
    import qutip as qt

    c_ops = []
    for m in range(n_levels):
        for n in range(n_levels):
            if m == n:
                continue
            omega = energies[m] - energies[n]
            coupling = abs(X_mn[n, m]) ** 2

            if omega > 0:
                n_bar = 1.0 / (np.exp(omega / max(T_bath, 1e-15)) - 1) if T_bath > 0.01 else 0.0
                rate = gamma_0 * coupling * (n_bar + 1)
            else:
                omega_abs = abs(omega)
                n_bar = 1.0 / (np.exp(omega_abs / max(T_bath, 1e-15)) - 1) if T_bath > 0.01 else 0.0
                rate = gamma_0 * coupling * n_bar

            if rate > 1e-20:
                op = np.zeros((n_levels, n_levels))
                op[n, m] = np.sqrt(rate)
                c_ops.append(qt.Qobj(op))

    return c_ops


def _solve_steady_state(energies, X_mn, T_bath, gamma_0, n_levels):
    """Find the exact Lindblad steady state (no time evolution needed)."""
    import qutip as qt

    H_q = qt.Qobj(np.diag(energies[:n_levels]))
    c_ops = _build_lindblad_ops(energies, X_mn, T_bath, gamma_0, n_levels)

    if not c_ops:
        return np.ones(n_levels) / n_levels

    rho_ss = qt.steadystate(H_q, c_ops)
    return np.real(np.diag(rho_ss.full()))


def _solve_dynamics(energies, X_mn, initial_dm, T_bath, gamma_0, t_max, n_steps, n_levels):
    """Solve the time evolution for the dynamics trace plot."""
    import qutip as qt

    H_q = qt.Qobj(np.diag(energies[:n_levels]))
    c_ops = _build_lindblad_ops(energies, X_mn, T_bath, gamma_0, n_levels)
    tlist = np.linspace(0, t_max, n_steps)

    result = qt.mesolve(H_q, initial_dm, tlist, c_ops, [])

    pops_vs_time = np.zeros((n_steps, n_levels))
    for t_idx in range(n_steps):
        rho_t = result.states[t_idx].full()
        pops_vs_time[t_idx] = np.real(np.diag(rho_t))

    return tlist, pops_vs_time


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_simulation(config: Sim5Config | None = None) -> Sim5Result:
    """Execute the Lindblad test."""
    import qutip as qt

    cfg = config or Sim5Config()
    rng = np.random.default_rng(cfg.seed)

    # 1. Build system
    all_E, all_vecs, x_grid, V_grid, barrier_top = _build_hamiltonian(cfg)
    dx = x_grid[1] - x_grid[0]

    energies = all_E[: cfg.n_levels]
    energies -= energies[0]  # shift ground state to 0

    # 2. WKB tunneling actions (central barrier only)
    wkb_actions = _wkb_actions(all_E, x_grid, V_grid, cfg.n_levels, cfg.well_separation)

    # 3. Position matrix elements (for bath coupling)
    X_mn = _position_matrix_elements(all_vecs, x_grid, cfg.n_levels)

    # 4. Initial state: asymmetric superposition in the energy eigenbasis
    amplitudes = rng.uniform(0.2, 1.0, cfg.n_levels)
    amplitudes /= np.linalg.norm(amplitudes)
    born_pops = amplitudes ** 2

    psi0 = np.zeros(cfg.n_levels, dtype=complex)
    psi0[:] = amplitudes
    rho0 = qt.ket2dm(qt.Qobj(psi0))

    # 5. Solve at each bath temperature
    temps = np.array(cfg.bath_temps)
    n_temps = len(temps)

    lindblad_pops = np.zeros((n_temps, cfg.n_levels))
    gibbs_e_pops = np.zeros((n_temps, cfg.n_levels))
    gibbs_s_pops = np.zeros((n_temps, cfg.n_levels))

    trace_temp_idx = n_temps // 2
    trace_times = None
    trace_pops = None

    for i, T_bath in enumerate(temps):
        beta = 1.0 / max(T_bath, 1e-15)

        # Lindblad EXACT steady state (no time truncation)
        lindblad_pops[i] = _solve_steady_state(
            all_E, X_mn, T_bath, cfg.gamma_0, cfg.n_levels,
        )

        # Standard QM prediction: Gibbs over energies
        gibbs_e_pops[i] = _gibbs_distribution(energies, beta)

        # TD prediction: Gibbs over WKB actions
        if np.all(wkb_actions == 0):
            gibbs_s_pops[i] = np.ones(cfg.n_levels) / cfg.n_levels
        else:
            beta_eff = 2.0 / (1.0 + T_bath / 2.0)
            gibbs_s_pops[i] = _gibbs_distribution(wkb_actions, beta_eff)

        # Time-evolution trace for one temperature (dynamics plot)
        if i == trace_temp_idx:
            trace_times, trace_pops = _solve_dynamics(
                all_E, X_mn, rho0, T_bath, cfg.gamma_0,
                cfg.t_max, cfg.n_time_steps, cfg.n_levels,
            )

    # 6. Residuals
    res_lindblad_gibbs_e = np.sqrt(
        np.sum((lindblad_pops - gibbs_e_pops) ** 2, axis=1)
    )
    res_gibbs_e_gibbs_s = np.sqrt(
        np.sum((gibbs_e_pops - gibbs_s_pops) ** 2, axis=1)
    )

    barrier_top_shifted = barrier_top - all_E[0]

    return Sim5Result(
        energies=energies,
        wkb_actions=wkb_actions,
        barrier_top=barrier_top_shifted,
        bath_temps=temps,
        lindblad_pops=lindblad_pops,
        gibbs_energy_pops=gibbs_e_pops,
        gibbs_action_pops=gibbs_s_pops,
        born_pops=born_pops,
        residual_lindblad_vs_gibbs_e=res_lindblad_gibbs_e,
        residual_gibbs_e_vs_gibbs_s=res_gibbs_e_gibbs_s,
        x_grid=x_grid,
        potential=V_grid - all_E[0],
        trace_temp_idx=trace_temp_idx,
        trace_times=trace_times if trace_times is not None else np.array([]),
        trace_pops=trace_pops if trace_pops is not None else np.array([[]]),
    )
