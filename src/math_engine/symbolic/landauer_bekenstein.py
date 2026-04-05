"""Information-theoretic bounds on branching: Landauer and Bekenstein.

After the falsification of A3 (Wick rotation = decoherence), the surviving
foundation for Thermodynamic Darwinism rests on established results in
quantum thermodynamics and information theory:

  1. Landauer's principle: erasing one bit costs at least k_B T ln 2
  2. Bekenstein bound: maximum entropy of a region is S <= 2π k_B R E / (ℏc)
  3. Quantum Darwinism: pointer states are selected by environmental redundancy

Combining these: if each redundant copy of a pointer state costs energy
(Landauer), and the environment has finite information capacity (Bekenstein),
then pointer-state selection is constrained by information-theoretic costs.
States requiring fewer bits per copy achieve higher redundancy and are more
classically robust.

CRITICAL: The information content I_i of each pointer state must be defined
as the conditional von Neumann entropy S(rho_{E_k|i}) — determined by the
system-environment Hamiltonian — NOT as -log2(p_i) (Born surprisal), which
would be circular.

References:
  Landauer, IBM J. Res. Dev. 5, 183 (1961)
  Bekenstein, Phys. Rev. D 23, 287 (1981)
  Zurek, Nat. Phys. 5, 181 (2009) [Quantum Darwinism]
"""

from __future__ import annotations

import sympy as sp
from sympy import (
    Function,
    Rational,
    Symbol,
    ceiling,
    exp,
    floor,
    log,
    oo,
    pi,
    sqrt,
    symbols,
)

k_B = Symbol("k_B", positive=True)
T_phys = Symbol("T", positive=True)
hbar = Symbol(r"\hbar", positive=True)
c = Symbol("c", positive=True)


def landauer_erasure_cost() -> dict[str, sp.Expr | str]:
    r"""Landauer's principle: minimum energy to erase one bit.

    Any logically irreversible operation (e.g., creating a record of a
    measurement outcome) must dissipate at least k_B T ln 2 of energy
    into the environment. This is a theorem of statistical mechanics,
    not a conjecture.

    For quantum branching: each decoherence event that creates a record
    of "which branch" in the environment is a logically irreversible
    operation. The minimum energy cost per branching event that creates
    n_bits of which-branch information is n_bits × k_B T ln 2.
    """
    n_bits = Symbol("n", positive=True, integer=True)

    Q_min_per_bit = k_B * T_phys * log(2)
    Q_branch = n_bits * Q_min_per_bit

    return {
        "Q_min_per_bit": Q_min_per_bit,
        "Q_branch": Q_branch,
        "latex_per_bit": r"Q_{\min} = k_B T \ln 2",
        "latex_branch": r"Q_{\text{branch}} = n \cdot k_B T \ln 2",
        "physical_content": (
            "Landauer's principle (1961): any logically irreversible computation "
            "must dissipate at least k_B T ln 2 per bit erased. Experimentally "
            "confirmed to the Landauer limit in nanoscale systems (Berut et al., "
            "Nature 2012). For quantum branching, each record of 'which outcome' "
            "created in the environment is an irreversible bit."
        ),
    }


def bekenstein_bound() -> dict[str, sp.Expr | str]:
    r"""Bekenstein bound: maximum entropy of a finite region.

    The Bekenstein bound states that the maximum entropy (information
    content) of a system enclosed in a sphere of radius R with total
    energy E is:

        S_max ≤ 2π k_B R E / (ℏc)

    This is a fundamental result linking gravity, thermodynamics, and
    information. It bounds the total number of distinguishable quantum
    states — and hence the total number of distinguishable branches —
    in any finite region.
    """
    R = Symbol("R", positive=True)
    E = Symbol("E", positive=True)

    S_max = 2 * pi * k_B * R * E / (hbar * c)
    I_max_bits = S_max / (k_B * log(2))
    N_max_states = exp(S_max / k_B)

    return {
        "S_max": S_max,
        "I_max_bits": I_max_bits,
        "N_max_states": N_max_states,
        "latex_bound": r"S_{\max} \leq \frac{2\pi k_B R E}{\hbar c}",
        "latex_bits": r"I_{\max} = \frac{S_{\max}}{k_B \ln 2} = \frac{2\pi R E}{\hbar c \ln 2}",
        "physical_content": (
            "Bekenstein bound (1981): the maximum information content of a region "
            "is proportional to its surface area times energy. This is the tightest "
            "known bound on information density in physics. For the environment of a "
            "quantum system, it limits the total number of distinguishable pointer-state "
            "records the environment can hold."
        ),
    }


def pointer_state_redundancy_cost() -> dict[str, sp.Expr | str]:
    r"""Cost of redundant pointer-state encoding (Quantum Darwinism).

    Quantum Darwinism (Zurek 2009) explains classicality via redundancy:
    a pointer state becomes "objective" when N independent fragments of
    the environment each carry a copy of the system's state information.

    Each copy requires I_state bits to encode (the von Neumann entropy of
    the pointer state's record in one environment fragment). By Landauer's
    principle, creating each copy dissipates at least:

        Q_copy = I_state × k_B T ln 2

    The total energy for N redundant copies:

        Q_total = N × I_state × k_B T ln 2

    The maximum achievable redundancy given available energy E_avail:

        N_max = E_avail / (I_state × k_B T ln 2)

    States with lower I_state (fewer bits per copy) can achieve higher N
    and are thus more "classically robust."
    """
    I_state = Symbol("I_s", positive=True)
    N_copies = Symbol("N", positive=True, integer=True)
    E_avail = Symbol("E_{\\text{avail}}", positive=True)

    Q_per_copy = I_state * k_B * T_phys * log(2)
    Q_total = N_copies * Q_per_copy
    N_max = E_avail / (I_state * k_B * T_phys * log(2))

    return {
        "Q_per_copy": Q_per_copy,
        "Q_total": Q_total,
        "N_max": N_max,
        "latex_cost": r"Q_{\text{copy}} = I_s \cdot k_B T \ln 2",
        "latex_total": r"Q_{\text{total}} = N \cdot I_s \cdot k_B T \ln 2",
        "latex_Nmax": r"N_{\max} = \frac{E_{\text{avail}}}{I_s \cdot k_B T \ln 2}",
        "physical_content": (
            "Quantum Darwinism requires N >> 1 redundant copies for objectivity. "
            "Each copy has an irreducible Landauer cost. The maximum redundancy is "
            "set by the energy budget divided by the per-copy cost. This creates a "
            "genuine selection pressure: pointer states that require fewer bits per "
            "copy (simpler states) can achieve higher redundancy and thus appear "
            "more 'classical' to observers."
        ),
    }


def information_budget_selection() -> dict[str, sp.Expr | str]:
    r"""Selection mechanism from information-budget constraints.

    If the environment has finite energy E_env and each pointer state i
    requires I_i bits to encode in one environment fragment, then:

        N_i = E_env / (I_i × k_B T ln 2)

    is the maximum redundancy for state i.

    CRITICAL: I_i is defined as the von Neumann entropy of the conditional
    environment fragment state:

        I_i = S(ρ_{E_k|i})

    where ρ_{E_k|i} is the reduced state of environment fragment k given
    that the system is in pointer state |i⟩. This is determined entirely
    by the system-environment Hamiltonian H_SE — no reference to Born
    probabilities. The previous definition I_i = -log₂(p_i) was CIRCULAR
    because it used Born weights to define the quantity that was meant to
    be independent of them.

    The information-selected probability is:

        P_i^{info} = N_i / Σ_j N_j = (1/I_i) / Σ_j (1/I_j)

    which weights states inversely by their Hamiltonian-determined
    encoding cost.
    """
    I_i = Symbol("I_i", positive=True)
    E_env = Symbol("E_{\\text{env}}", positive=True)

    N_i = E_env / (I_i * k_B * T_phys * log(2))

    I_vals = symbols("I_1 I_2 I_3", positive=True)
    N_vals = [E_env / (I_v * k_B * T_phys * log(2)) for I_v in I_vals]
    Z_info = sum(N_vals)
    P_1 = N_vals[0] / Z_info

    P_1_simplified = sp.simplify(P_1)

    return {
        "N_i": N_i,
        "P_info_example": P_1_simplified,
        "latex_Ni": r"N_i = \frac{E_{\text{env}}}{I_i \cdot k_B T \ln 2}",
        "latex_P_info": r"P_i^{\text{info}} = \frac{1/I_i}{\sum_j 1/I_j}",
        "latex_I_def": r"I_i \equiv S(\rho_{E_k | i}) = -\text{Tr}[\rho_{E_k|i} \log_2 \rho_{E_k|i}]",
        "key_insight": (
            "I_i = S(ρ_{E_k|i}) is the von Neumann entropy of the conditional "
            "environment fragment — determined by the system-environment Hamiltonian "
            "H_SE alone, with NO reference to Born probabilities. Energy and "
            "temperature cancel in the probability ratio, so the selection depends "
            "only on the relative Hamiltonian-determined encoding costs."
        ),
        "circularity_note": (
            "IMPORTANT: The previous formulation defined I_i = -log₂(p_i) where "
            "p_i = |⟨i|ψ⟩|² (Born surprisal). This was circular — it used the "
            "Born rule to define the information content that was supposed to "
            "predict an alternative to the Born rule. The correct, non-circular "
            "definition is I_i = S(ρ_{E_k|i}), computable from the Hamiltonian."
        ),
    }


def compare_with_born() -> dict[str, sp.Expr | str]:
    r"""Quantify the difference between Hamiltonian-derived and Born predictions.

    The information-budget distribution P_i^info = (1/I_i) / Σ(1/I_j) uses
    I_i = S(ρ_{E_k|i}), the Hamiltonian-determined encoding cost. The Born
    distribution uses p_i = |⟨i|ψ⟩|². These are INDEPENDENT quantities —
    one comes from the coupling structure, the other from state amplitudes.

    The discrepancy is:

        Δ P_i = p_i^Born − P_i^info

    which is nonzero whenever the Hamiltonian-determined encoding costs
    are not proportional to the Born weights.

    For illustration, in the special (circular) case where I_i = -log₂(p_i),
    the discrepancy for a two-level system is shown below. But the actual
    testable prediction uses I_i from the simulation dynamics, not from
    Born probabilities.
    """
    p = Symbol("p", positive=True)

    I_1 = -log(p, 2)
    I_2 = -log(1 - p, 2)

    P_info_1 = (1 / I_1) / (1 / I_1 + 1 / I_2)

    Delta_P = sp.simplify(p - P_info_1)

    return {
        "P_info_1_twostate_illustrative": P_info_1,
        "Delta_P_twostate_illustrative": Delta_P,
        "latex_discrepancy": (
            r"\Delta P_i = p_i^{\text{Born}} - P_i^{\text{info}}"
            r" = |\langle i|\psi\rangle|^2 - \frac{1/I_i}{\sum_j 1/I_j}"
            r", \quad I_i = S(\rho_{E_k|i})"
        ),
        "testable_regime": (
            "Maximum discrepancy occurs when the Hamiltonian couples some "
            "pointer states more strongly to the environment than others, "
            "creating asymmetric encoding costs. Sim7 computes I_i directly "
            "from the evolved density matrix (non-circular)."
        ),
        "experimental_signature": (
            "In an engineered quantum system with a small, controlled environment "
            "(few qubits), measure the pointer-state statistics as a function of "
            "environment size. As the environment shrinks, information constraints "
            "tighten and pointer-state statistics should deviate from Born toward "
            "the Hamiltonian-determined prediction P_i^info."
        ),
    }
