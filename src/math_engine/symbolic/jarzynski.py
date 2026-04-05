"""Jarzynski equality and double-stochasticity for branch selection.

Converts A4 from an axiom to a derived consequence:
  1. Decoherent branching (unitary + partial trace) is double-stochastic.
  2. Double-stochastic processes satisfy the Jarzynski equality.
  3. Dissipative branching violates double-stochasticity.
  4. Jarzynski-violating branches have excess action ΔS_E = W_diss > 0.
  5. Under Gibbs weighting, these branches are exponentially suppressed
     by a factor exp(−W_diss/ℏ).

References:
  - Campisi, Hänggi, Talkner, Rev. Mod. Phys. 83, 771 (2011)
  - Manzano, Horowitz, Parrondo, Phys. Rev. X 8, 031037 (2018)
"""

from __future__ import annotations

import sympy as sp
from sympy import Symbol, exp, log, symbols

hbar = Symbol(r"\hbar", positive=True)
k_B = Symbol("k_B", positive=True)
beta = Symbol(r"\beta", positive=True)


def jarzynski_equality() -> dict[str, sp.Expr]:
    """The quantum Jarzynski equality: ⟨exp(−βW)⟩ = exp(−βΔF).

    W is the work done on the system during a non-equilibrium process.
    ΔF is the equilibrium free energy difference between initial and final states.
    """
    W = Symbol("W")
    Delta_F = Symbol(r"\Delta F")

    lhs = sp.Symbol(r"\langle e^{-\beta W} \rangle")
    rhs = exp(-beta * Delta_F)

    W_diss = W - Delta_F

    return {
        "jarzynski_equality": sp.Eq(lhs, rhs),
        "dissipated_work": W_diss,
        "second_law": sp.Ge(W_diss, 0),
        "interpretation": (
            "The Jarzynski equality is exact for any process, equilibrium or not. "
            "The dissipated work W_diss = W − ΔF ≥ 0 (second law). "
            "Equality holds iff the process is thermodynamically reversible."
        ),
    }


def double_stochasticity_condition() -> dict[str, sp.Expr]:
    """Double stochasticity: the condition for Jarzynski to hold.

    A transition matrix T_{mn} is doubly stochastic iff:
      Σ_m T_{mn} = 1  (columns sum to 1, standard stochasticity)
      Σ_n T_{mn} = 1  (rows sum to 1, double stochasticity)

    Unitary evolution is automatically double-stochastic.
    Decoherence (partial trace over environment) preserves this.
    Energy dissipation breaks it.
    """
    T_mn = Symbol("T_{mn}")

    return {
        "column_sum": sp.Eq(sp.Symbol(r"\sum_m T_{mn}"), 1),
        "row_sum": sp.Eq(sp.Symbol(r"\sum_n T_{mn}"), 1),
        "unitary_preserves": True,
        "decoherence_preserves": True,
        "dissipation_breaks": True,
        "interpretation": (
            "Unitary evolution: |U_{mn}|² is doubly stochastic (Birkhoff). "
            "Decoherence adds noise but preserves the trace condition. "
            "Dissipation (irreversible energy loss) breaks row normalization "
            "because probability leaks to unmeasured environmental degrees."
        ),
    }


def branch_suppression_theorem() -> dict[str, sp.Expr]:
    """Theorem: Dissipative branches are exponentially suppressed.

    CAVEAT: This derivation depends on falsified A3. The Gibbs weighting
    exp(-S_E/hbar) over Euclidean actions is not produced by decoherence
    (shown by the influence functional analysis, Sim5, and Sim6). The
    suppression factor exp(-W_diss/hbar) is formally correct within the
    A3 framework but the framework itself is invalid. A new suppression
    mechanism is needed.

    For a branch that requires dissipated work W_diss:
      1. Its total action increases: S_E → S_E + W_diss
      2. Its Gibbs weight decreases: exp(−S_E/ℏ) → exp(−(S_E + W_diss)/ℏ)
      3. Suppression factor: exp(−W_diss/ℏ)

    This converts A4 from an axiom to a derived consequence of A3 + thermodynamics.
    A3 is now FALSIFIED, so this derivation is invalid as stated.
    """
    S_E = Symbol("S_E", positive=True)
    W_diss = Symbol("W_{diss}", positive=True)

    weight_decoherent = exp(-S_E / hbar)
    weight_dissipative = exp(-(S_E + W_diss) / hbar)
    suppression = weight_dissipative / weight_decoherent

    return {
        "decoherent_weight": weight_decoherent,
        "dissipative_weight": weight_dissipative,
        "suppression_factor": suppression,
        "suppression_simplified": exp(-W_diss / hbar),
        "interpretation": (
            "Branches requiring dissipation W_diss are suppressed by "
            "exp(−W_diss/ℏ) relative to purely decoherent branches. "
            "For W_diss >> ℏ, suppression is exponential. "
            "This provides the selection pressure: energetically wasteful "
            "branches are thermodynamically disfavored."
        ),
    }
