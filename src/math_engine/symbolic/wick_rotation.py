"""Wick rotation: the bridge between quantum mechanics and statistical mechanics.

The transformation it → −τ (or equivalently 1/k_BT ↔ it/ℏ) converts:
  - Minkowski path integral  →  Euclidean path integral
  - Phase weights exp(iS/ℏ)  →  Boltzmann weights exp(−S_E/ℏ)
  - Quantum propagator       →  Statistical partition function
"""

from __future__ import annotations

import sympy as sp
from sympy import I, Symbol, exp, symbols

hbar = Symbol(r"\hbar", positive=True)
k_B = Symbol("k_B", positive=True)
beta = Symbol(r"\beta", positive=True)
tau = Symbol(r"\tau", positive=True)  # Euclidean time
t = Symbol("t")  # Minkowski time


def wick_rotate_time(expr: sp.Expr) -> sp.Expr:
    """Apply Wick rotation: replace t → −iτ in a symbolic expression."""
    return expr.subs(t, -I * tau)


def wick_rotate_action(minkowski_action: sp.Expr) -> sp.Expr:
    """Convert Minkowski action S to Euclidean action S_E.

    Under Wick rotation, S_M → iS_E, so the phase factor
    exp(iS_M/ℏ) → exp(−S_E/ℏ).
    """
    rotated = wick_rotate_time(minkowski_action)
    euclidean_action = sp.simplify(-I * rotated)
    return euclidean_action


def minkowski_weight(action: sp.Expr) -> sp.Expr:
    """Phase weight in Minkowski signature: exp(iS/ℏ)."""
    return exp(I * action / hbar)


def euclidean_weight(euclidean_action: sp.Expr) -> sp.Expr:
    """Boltzmann weight in Euclidean signature: exp(−S_E/ℏ)."""
    return exp(-euclidean_action / hbar)


def thermal_weight(energy: sp.Expr) -> sp.Expr:
    """Canonical Boltzmann factor: exp(−βE) = exp(−E/k_BT)."""
    return exp(-beta * energy)


def demonstrate_equivalence() -> dict[str, sp.Expr]:
    """Show that Wick-rotated propagator equals thermal partition function.

    For a system with energy eigenvalues E_n, the quantum propagator
    trace at imaginary time β = it/ℏ equals the thermal partition function:
        Tr[exp(−iHt/ℏ)] → Tr[exp(−βH)] = Z(β)
    """
    H = Symbol("H")  # Hamiltonian operator (symbolic placeholder)
    E_n = Symbol("E_n", positive=True)

    quantum_propagator = exp(-I * H * t / hbar)
    rotated = quantum_propagator.subs(t, -I * hbar * beta)
    thermal_operator = sp.simplify(rotated)

    return {
        "quantum_propagator": quantum_propagator,
        "wick_rotation_substitution": f"t → −iℏβ, where β = 1/k_BT",
        "thermal_operator": thermal_operator,  # Should be exp(-βH)
        "partition_function_element": exp(-beta * E_n),
        "interpretation": (
            "The trace of the thermal operator over energy eigenstates "
            "gives Z = Σ_n exp(−βE_n), the canonical partition function."
        ),
    }


def branch_temperature(total_energy_budget: sp.Expr) -> sp.Expr:
    """Effective temperature T* of the branch ensemble.

    If the total Euclidean action is bounded by S_max, the effective
    inverse temperature is β* = S_max / ℏ, giving T* = ℏ / (k_B · S_max).
    """
    S_max = total_energy_budget
    return hbar / (k_B * S_max)
