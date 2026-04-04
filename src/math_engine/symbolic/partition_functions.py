"""Partition functions and statistical mechanics of branch ensembles.

Provides tools for computing canonical partition functions, Gibbs
distributions, free energies, and entropy — the core thermodynamic
quantities that govern branch weighting in the theory.
"""

from __future__ import annotations

from typing import Sequence

import sympy as sp
from sympy import Function, Rational, Symbol, exp, log, oo, symbols, summation

beta = Symbol(r"\beta", positive=True)
k_B = Symbol("k_B", positive=True)
T = Symbol("T", positive=True)
hbar = Symbol(r"\hbar", positive=True)
n = Symbol("n", integer=True, nonneg=True)


def canonical_partition_function(energies: Sequence[sp.Expr]) -> sp.Expr:
    """Z = Σ_i exp(−β E_i) for a discrete set of energy levels."""
    return sum(exp(-beta * E) for E in energies)


def gibbs_probability(energy: sp.Expr, Z: sp.Expr) -> sp.Expr:
    """P_i = exp(−β E_i) / Z — probability of state i in Gibbs ensemble."""
    return exp(-beta * energy) / Z


def helmholtz_free_energy(Z: sp.Expr) -> sp.Expr:
    """F = −k_B T ln Z = −(1/β) ln Z."""
    return -log(Z) / beta


def mean_energy(energies: Sequence[sp.Expr], Z: sp.Expr) -> sp.Expr:
    """<E> = Σ_i E_i P_i = −∂(ln Z)/∂β."""
    return sum(E * gibbs_probability(E, Z) for E in energies)


def entropy_from_partition(Z: sp.Expr) -> sp.Expr:
    """S = k_B (ln Z + β <E>) = −∂F/∂T.

    Uses S = k_B(ln Z + β ∂ln Z/∂β) but expressed as β·<E> + ln Z.
    """
    ln_Z = log(Z)
    return k_B * (ln_Z - beta * sp.diff(ln_Z, beta))


def branch_ensemble_partition(
    action_values: Sequence[sp.Expr],
) -> dict[str, sp.Expr]:
    """Compute the full thermodynamic state of a branch ensemble.

    Parameters
    ----------
    action_values : sequence of SymPy expressions
        Euclidean action S_{E,i} for each branch.

    Returns
    -------
    dict with keys: Z, probabilities, F, S_entropy, mean_action
    """
    Z = sum(exp(-S / hbar) for S in action_values)
    probs = [exp(-S / hbar) / Z for S in action_values]

    beta_eff = 1 / hbar  # effective inverse temperature in action units

    F = -hbar * log(Z)

    return {
        "Z": Z,
        "probabilities": probs,
        "F_free_energy": F,
        "branch_count": len(action_values),
    }


def harmonic_oscillator_Z() -> sp.Expr:
    """Partition function for the quantum harmonic oscillator.

    Z = 1 / (2 sinh(βℏω/2)) — standard textbook result, useful as
    a verification target.
    """
    omega = Symbol(r"\omega", positive=True)
    return 1 / (2 * sp.sinh(beta * hbar * omega / 2))


def two_level_system_Z(epsilon: sp.Expr) -> sp.Expr:
    """Partition function for a two-level system with gap ε.

    Z = 1 + exp(−βε) — simplest non-trivial example for testing
    Born rule emergence.
    """
    return 1 + exp(-beta * epsilon)
