"""ODE/PDE solvers for Fokker-Planck and related equations.

Numerical integration of the Fokker-Planck equation to verify
that the steady state converges to the Gibbs distribution.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp


@dataclass
class FPSolution:
    x_grid: NDArray[np.float64]
    t_grid: NDArray[np.float64]
    density: NDArray[np.float64]  # shape (n_t, n_x)
    steady_state: NDArray[np.float64]


def solve_fokker_planck_1d(
    potential_fn: callable,
    x_min: float = -5.0,
    x_max: float = 5.0,
    n_x: int = 200,
    t_max: float = 10.0,
    n_t: int = 100,
    diffusion: float = 1.0,
    friction: float = 1.0,
    initial_density: NDArray[np.float64] | None = None,
) -> FPSolution:
    """Solve the 1D Fokker-Planck equation via method of lines.

    ∂P/∂t = (D/γ) ∂²P/∂x² + (1/γ) ∂[V'(x) P]/∂x

    Parameters
    ----------
    potential_fn : callable
        V(x) — the potential function.
    """
    x = np.linspace(x_min, x_max, n_x)
    dx = x[1] - x[0]
    D = diffusion
    gam = friction

    V_prime = np.gradient(potential_fn(x), dx)

    if initial_density is None:
        initial_density = np.exp(-0.5 * (x - 0) ** 2)
        initial_density /= np.trapezoid(initial_density, x)

    def rhs(t_val: float, P: NDArray) -> NDArray:
        dP = np.zeros_like(P)
        dPdx = np.gradient(P, dx)
        d2Pdx2 = np.gradient(dPdx, dx)

        drift_flux = V_prime * P / gam
        drift_term = np.gradient(drift_flux, dx)
        diffusion_term = (D / gam) * d2Pdx2

        dP = drift_term + diffusion_term

        dP[0] = 0
        dP[-1] = 0
        return dP

    t_eval = np.linspace(0, t_max, n_t)
    sol = solve_ivp(
        rhs,
        (0, t_max),
        initial_density,
        t_eval=t_eval,
        method="RK45",
        max_step=dx**2 / (4 * D),
    )

    density = sol.y.T  # shape (n_t, n_x)
    steady_state = density[-1]
    steady_state = np.maximum(steady_state, 0)
    norm = np.trapezoid(steady_state, x)
    if norm > 0:
        steady_state /= norm

    return FPSolution(
        x_grid=x,
        t_grid=t_eval,
        density=density,
        steady_state=steady_state,
    )


def gibbs_distribution_1d(
    potential_fn: callable,
    x: NDArray[np.float64],
    temperature: float,
) -> NDArray[np.float64]:
    """Analytical Gibbs distribution for comparison: P(x) ∝ exp(−V(x)/T)."""
    V = potential_fn(x)
    log_p = -V / temperature
    log_p -= np.max(log_p)
    p = np.exp(log_p)
    p /= np.trapezoid(p, x)
    return p


def verify_fp_gibbs_convergence(
    potential_fn: callable,
    temperature: float = 1.0,
    **kwargs,
) -> dict[str, float]:
    """Run FP solver and compare steady state to analytical Gibbs distribution."""
    sol = solve_fokker_planck_1d(
        potential_fn, diffusion=temperature, **kwargs
    )
    gibbs = gibbs_distribution_1d(potential_fn, sol.x_grid, temperature)

    from src.math_engine.numerical.monte_carlo import kl_divergence

    mask = (sol.steady_state > 1e-10) & (gibbs > 1e-10)
    p = sol.steady_state[mask]
    q = gibbs[mask]
    p /= p.sum()
    q /= q.sum()
    kl = kl_divergence(p, q)

    l2_error = float(np.sqrt(np.trapezoid(
        (sol.steady_state - gibbs) ** 2, sol.x_grid
    )))

    return {
        "kl_divergence": kl,
        "l2_error": l2_error,
        "max_abs_error": float(np.max(np.abs(sol.steady_state - gibbs))),
    }
