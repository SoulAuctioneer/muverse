"""Symbolic path integral formulation using SymPy.

Provides tools for:
- Constructing discrete path integral sums
- Computing amplitudes for branching histories
- Converting between Minkowski and Euclidean signatures
"""

from __future__ import annotations

import sympy as sp
from sympy import (
    Function,
    I,
    Rational,
    Symbol,
    conjugate,
    exp,
    oo,
    pi,
    sqrt,
    symbols,
)

hbar, m, omega, t, T_phys = symbols(r"\hbar m \omega t T", positive=True)
k_B = Symbol("k_B", positive=True)
beta = Symbol(r"\beta", positive=True)
S_E = Symbol("S_E", positive=True)


def free_particle_propagator(x_f: Symbol, x_i: Symbol, t_val: Symbol) -> sp.Expr:
    """Exact Feynman propagator for a free particle: K(x_f, t | x_i, 0)."""
    return sqrt(m / (2 * pi * I * hbar * t_val)) * exp(
        I * m * (x_f - x_i) ** 2 / (2 * hbar * t_val)
    )


def harmonic_propagator(x_f: Symbol, x_i: Symbol, t_val: Symbol) -> sp.Expr:
    """Exact propagator for the quantum harmonic oscillator."""
    return sqrt(m * omega / (2 * pi * I * hbar * sp.sin(omega * t_val))) * exp(
        I
        * m
        * omega
        / (2 * hbar * sp.sin(omega * t_val))
        * (
            (x_f**2 + x_i**2) * sp.cos(omega * t_val)
            - 2 * x_f * x_i
        )
    )


def discrete_path_sum(
    action_values: list[sp.Expr],
    signature: str = "minkowski",
) -> sp.Expr:
    """Sum over discrete set of histories weighted by exp(iS/hbar) or exp(-S_E/hbar).

    Parameters
    ----------
    action_values : list of SymPy expressions
        The action S (Minkowski) or S_E (Euclidean) for each path/branch.
    signature : "minkowski" or "euclidean"
    """
    if signature == "minkowski":
        weights = [exp(I * S / hbar) for S in action_values]
    elif signature == "euclidean":
        weights = [exp(-S / hbar) for S in action_values]
    else:
        raise ValueError(f"Unknown signature: {signature}")

    return sum(weights)


def branch_amplitude_squared(action_val: sp.Expr, partition_fn: sp.Expr) -> sp.Expr:
    """Probability of a branch in the Euclidean ensemble: exp(-S_E/hbar) / Z."""
    return exp(-action_val / hbar) / partition_fn


def born_rule_weight(psi: sp.Expr) -> sp.Expr:
    """Standard Born rule: |psi|^2."""
    return conjugate(psi) * psi


def partition_function_from_actions(action_values: list[sp.Expr]) -> sp.Expr:
    """Z = sum_i exp(-S_{E,i} / hbar)."""
    return sum(exp(-S / hbar) for S in action_values)


def verify_born_rule_limit(
    action_values: list[sp.Expr],
    psi_amplitudes: list[sp.Expr],
) -> list[tuple[sp.Expr, sp.Expr, sp.Expr]]:
    """Compare Gibbs weights to Born rule weights for a set of branches.

    Returns list of (Gibbs_weight, Born_weight, difference) tuples.
    """
    Z = partition_function_from_actions(action_values)
    results = []
    for S_val, psi in zip(action_values, psi_amplitudes):
        gibbs = branch_amplitude_squared(S_val, Z)
        born = born_rule_weight(psi)
        results.append((gibbs, born, sp.simplify(gibbs - born)))
    return results
