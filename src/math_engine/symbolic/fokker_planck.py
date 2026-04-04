"""Fokker-Planck equation and its connection to quantum mechanics.

The FP equation governs probability density evolution in stochastic systems.
Under Wick rotation it is structurally identical to the Schrödinger equation.
The steady-state solution is the Gibbs distribution — the same distribution
that governs SGD weight convergence and (in our theory) MWI branch weights.
"""

from __future__ import annotations

import sympy as sp
from sympy import Derivative, Function, Symbol, exp, symbols

x = Symbol("x")
t = Symbol("t", positive=True)
D = Symbol("D", positive=True)  # diffusion coefficient
gamma = Symbol(r"\gamma", positive=True)  # friction / drift coefficient
T_temp = Symbol("T", positive=True)  # temperature
k_B = Symbol("k_B", positive=True)
hbar = Symbol(r"\hbar", positive=True)
m = Symbol("m", positive=True)

V = Function("V")  # potential function
P = Function("P")  # probability density


def fokker_planck_equation(
    potential: sp.Expr | None = None,
) -> sp.Eq:
    """General Fokker-Planck equation for overdamped Langevin dynamics.

    ∂P/∂t = ∂/∂x [V'(x)P/γ] + D ∂²P/∂x²

    where D = k_BT/γ (Einstein relation).
    """
    Pxt = P(x, t)
    if potential is None:
        potential = V(x)

    drift = sp.diff(sp.diff(potential, x) * Pxt / gamma, x)
    diffusion = D * sp.diff(Pxt, x, 2)
    return sp.Eq(sp.diff(Pxt, t), drift + diffusion)


def steady_state_gibbs(potential: sp.Expr | None = None) -> sp.Expr:
    """Steady-state solution of FP equation: Gibbs distribution.

    P_ss(x) ∝ exp(−V(x)/k_BT)

    This is the key result: the same Gibbs form governs:
    - Thermal equilibrium in statistical mechanics
    - SGD steady state in neural networks
    - Branch weights in energy-constrained MWI (our claim)
    """
    if potential is None:
        potential = V(x)
    return exp(-potential / (k_B * T_temp))


def schrodinger_comparison() -> dict[str, sp.Expr]:
    """Show the formal equivalence between FP and Schrödinger equations.

    Fokker-Planck:   ∂P/∂t = D ∂²P/∂x² + (1/γ) ∂(V'P)/∂x
    Schrödinger:     iℏ ∂ψ/∂t = −(ℏ²/2m) ∂²ψ/∂x² + V(x)ψ

    Under Wick rotation (t → −iτ) and identification D = ℏ/(2m),
    the FP equation maps to the imaginary-time Schrödinger equation.
    """
    psi = Function(r"\psi")
    psi_xt = psi(x, t)

    schrodinger = sp.Eq(
        sp.I * hbar * sp.diff(psi_xt, t),
        -hbar**2 / (2 * m) * sp.diff(psi_xt, x, 2) + V(x) * psi_xt,
    )

    fp = fokker_planck_equation()

    return {
        "fokker_planck": fp,
        "schrodinger": schrodinger,
        "identification": {
            "diffusion_coefficient": sp.Eq(D, hbar / (2 * m)),
            "temperature_planck": sp.Eq(k_B * T_temp, hbar),
        },
        "interpretation": (
            "Under Wick rotation, the diffusion coefficient D plays the role of ℏ/2m, "
            "and the FP temperature maps to ℏ. This makes the FP steady state "
            "(Gibbs distribution) equivalent to the ground-state wavefunction squared."
        ),
    }


def sgd_temperature(learning_rate: sp.Expr, batch_size: sp.Expr) -> sp.Expr:
    """Effective temperature of SGD noise.

    T_eff ∝ η/B, where η is the learning rate and B is the batch size.
    This sets the width of the Gibbs distribution over weight-space.
    """
    eta = learning_rate
    B = batch_size
    return eta / B


def sgd_gibbs_steady_state(
    loss: sp.Expr,
    learning_rate: sp.Expr,
    batch_size: sp.Expr,
) -> sp.Expr:
    """Steady-state weight distribution of SGD: Gibbs form.

    p_ss(w) ∝ exp(−L(w) / T_eff), where T_eff = η/B.
    """
    T_eff = sgd_temperature(learning_rate, batch_size)
    return exp(-loss / T_eff)
