"""REST routes for the mathematical derivation chain."""

from __future__ import annotations

import sympy as sp
from fastapi import APIRouter

router = APIRouter()


def _latex(expr: sp.Expr) -> str:
    """Convert a SymPy expression to LaTeX string with corrected symbols."""
    raw = sp.latex(expr)
    raw = raw.replace(r"\bar{\h}", r"\hbar")
    raw = raw.replace(r"\bar{h}", r"\hbar")
    return raw


def _build_derivation_chain() -> list[dict]:
    """Build the five-step derivation chain with LaTeX from the symbolic engine."""
    steps: list[dict] = []

    # --- Step 1: Path Integrals ---
    from src.math_engine.symbolic.path_integrals import (
        discrete_path_sum,
        born_rule_weight,
        partition_function_from_actions,
    )

    S1, S2, S3 = sp.symbols("S_1 S_2 S_3", positive=True)
    hbar = sp.Symbol(r"\hbar", positive=True)
    psi = sp.Symbol(r"\psi")

    minkowski_sum = discrete_path_sum([S1, S2, S3], "minkowski")
    euclidean_sum = discrete_path_sum([S1, S2, S3], "euclidean")
    born = born_rule_weight(psi)

    steps.append({
        "id": "path_integrals",
        "title": "Path Integrals",
        "subtitle": "Sum over histories",
        "description": (
            "In Feynman's path integral formulation, the quantum amplitude is a sum "
            "over all possible histories, each weighted by a phase factor exp(iS/ℏ). "
            "In MWI, every branch contributes to this sum. The Born rule gives the "
            "probability as |ψ|², but the path integral sums complex amplitudes."
        ),
        "equations": [
            {
                "label": "Minkowski path sum",
                "latex": r"K = \sum_{\text{paths}} e^{iS/\hbar} = " + _latex(minkowski_sum),
            },
            {
                "label": "Born rule",
                "latex": r"P = |\psi|^2 = " + _latex(born),
            },
        ],
    })

    # --- Step 2: Wick Rotation ---
    from src.math_engine.symbolic.wick_rotation import (
        demonstrate_equivalence,
        minkowski_weight,
        euclidean_weight,
        thermal_weight,
    )

    equiv = demonstrate_equivalence()
    E_n = sp.Symbol("E_n", positive=True)
    beta = sp.Symbol(r"\beta", positive=True)

    steps.append({
        "id": "wick_rotation",
        "title": "Wick Rotation",
        "subtitle": "Phase → Boltzmann",
        "description": (
            "The Wick rotation t → −iτ transforms the oscillatory Minkowski path integral "
            "into a real-valued Euclidean integral. Phase weights exp(iS/ℏ) become "
            "Boltzmann weights exp(−S_E/ℏ). This is the mathematical bridge: the quantum "
            "propagator becomes a statistical partition function."
        ),
        "equations": [
            {
                "label": "Minkowski weight",
                "latex": r"w_M = e^{iS/\hbar}",
            },
            {
                "label": "Euclidean weight (after Wick rotation)",
                "latex": r"w_E = e^{-S_E/\hbar}",
            },
            {
                "label": "Thermal operator",
                "latex": r"\hat{U} = " + _latex(equiv["thermal_operator"]),
            },
            {
                "label": "Partition function element",
                "latex": _latex(equiv["partition_function_element"]),
            },
        ],
    })

    # --- Step 3: Partition Function ---
    from src.math_engine.symbolic.partition_functions import (
        canonical_partition_function,
        gibbs_probability,
        helmholtz_free_energy,
    )

    E1, E2, E3 = sp.symbols("E_1 E_2 E_3", positive=True)
    Z = canonical_partition_function([E1, E2, E3])
    p_gibbs = gibbs_probability(E1, Z)
    F = helmholtz_free_energy(Z)

    steps.append({
        "id": "partition_function",
        "title": "Partition Function",
        "subtitle": "Branch ensemble thermodynamics",
        "description": (
            "Treating branches as a statistical ensemble, we define a partition function "
            "Z = Σ exp(−βE_i). The probability of each branch follows the Gibbs distribution "
            "P_i = exp(−βE_i)/Z. The free energy F = −(1/β)ln Z governs which macro-branches "
            "persist. This is the core of Thermodynamic Darwinism."
        ),
        "equations": [
            {
                "label": "Partition function",
                "latex": r"Z = \sum_i e^{-\beta E_i} = " + _latex(Z),
            },
            {
                "label": "Gibbs probability",
                "latex": r"P_i = \frac{e^{-\beta E_i}}{Z} = " + _latex(p_gibbs),
            },
            {
                "label": "Helmholtz free energy",
                "latex": r"F = -\frac{1}{\beta}\ln Z = " + _latex(F),
            },
        ],
    })

    # --- Step 4: Fokker-Planck ---
    from src.math_engine.symbolic.fokker_planck import (
        fokker_planck_equation,
        steady_state_gibbs,
        schrodinger_comparison,
    )

    fp_eq = fokker_planck_equation()
    gibbs_ss = steady_state_gibbs()
    comparison = schrodinger_comparison()

    steps.append({
        "id": "fokker_planck",
        "title": "Fokker-Planck Equation",
        "subtitle": "Diffusion → Gibbs steady state",
        "description": (
            "The Fokker-Planck equation describes probability flow in stochastic systems. "
            "Its steady-state solution is the Gibbs distribution P_ss ∝ exp(−V/k_BT). "
            "Under Wick rotation, the FP equation maps to the imaginary-time Schrödinger equation, "
            "establishing a deep structural link between quantum mechanics and thermodynamics."
        ),
        "equations": [
            {
                "label": "Fokker-Planck equation",
                "latex": r"\frac{\partial P}{\partial t} = \frac{\partial}{\partial x}\!\left[\frac{1}{\gamma}\frac{\partial V}{\partial x}P + D\frac{\partial P}{\partial x}\right]",
            },
            {
                "label": "Steady-state Gibbs distribution",
                "latex": r"P_{\text{ss}}(x) \propto " + _latex(gibbs_ss),
            },
            {
                "label": "Schrödinger equation",
                "latex": _latex(comparison["schrodinger"]),
            },
        ],
    })

    # --- Step 5: SGD Connection ---
    from src.math_engine.symbolic.fokker_planck import (
        sgd_temperature,
        sgd_gibbs_steady_state,
    )

    eta = sp.Symbol(r"\eta", positive=True)
    B = sp.Symbol("B", positive=True)
    L = sp.Function("L")
    w = sp.Symbol("w")

    T_eff = sgd_temperature(eta, B)
    p_sgd = sgd_gibbs_steady_state(L(w), eta, B)

    steps.append({
        "id": "sgd_connection",
        "title": "SGD Connection",
        "subtitle": "Neural networks ↔ quantum selection",
        "description": (
            "Stochastic gradient descent (SGD) in neural networks is an overdamped Langevin process. "
            "Its effective temperature T_eff = η/B (learning rate / batch size) sets the width of "
            "exploration. The steady-state weight distribution is Gibbs: p(w) ∝ exp(−L(w)/T_eff). "
            "This is the same mathematical structure as branch selection, completing the chain: "
            "path integrals → Wick rotation → partition function → Fokker-Planck → SGD."
        ),
        "equations": [
            {
                "label": "Effective temperature",
                "latex": r"T_{\text{eff}} = " + _latex(T_eff),
            },
            {
                "label": "SGD steady-state distribution",
                "latex": r"p_{\text{ss}}(w) \propto " + _latex(p_sgd),
            },
        ],
    })

    # --- Step 6: WKB Semiclassical Derivation ---
    from src.math_engine.symbolic.wkb_semiclassical import (
        wkb_wavefunction_tunneling,
        born_gibbs_equivalence,
        finite_temperature_deviation,
    )

    tunnel = wkb_wavefunction_tunneling()
    bg_equiv = born_gibbs_equivalence()
    deviation = finite_temperature_deviation()

    steps.append({
        "id": "wkb_semiclassical",
        "title": "WKB Derivation",
        "subtitle": "Born rule derived, not assumed",
        "description": (
            "In the semiclassical (WKB) regime, the tunneling wavefunction is "
            "ψ ~ exp(−S_E/ℏ) where S_E is the Euclidean action through the "
            "classically forbidden region. Therefore |ψ|² = exp(−2S_E/ℏ), "
            "which has the form of a Boltzmann weight at effective β = 2/ℏ. "
            "Normalizing gives P_i = exp(−2S_{E,i}/ℏ)/Z — the Born rule as a "
            "derived consequence of path integral weighting, not a postulate. "
            "This derivation is exact in the semiclassical limit (S_E ≫ ℏ); "
            "corrections of order ℏ/S_E arise beyond WKB."
        ),
        "equations": [
            {
                "label": "Tunneling wavefunction (WKB)",
                "latex": r"\psi_{\text{tunnel}}(x) \sim e^{-S_E/\hbar}",
            },
            {
                "label": "Action–amplitude relation",
                "latex": r"|\psi|^2 = " + _latex(tunnel["action_amplitude_rhs"]),
            },
            {
                "label": "Effective inverse temperature",
                "latex": r"\beta_{\text{eff}} = " + _latex(bg_equiv["effective_inverse_temperature"]),
            },
            {
                "label": "Gibbs–Born equivalence",
                "latex": r"P_i = \frac{e^{-2S_{E,i}/\hbar}}{Z} = \frac{|\psi_i|^2}{\sum_j |\psi_j|^2}",
            },
        ],
    })

    # --- Step 7: Finite Temperature Prediction (P1) ---
    steps.append({
        "id": "temperature_prediction",
        "title": "Temperature Prediction",
        "subtitle": "Testable deviation from Born rule",
        "description": (
            "At T > 0, thermal fluctuations reduce the effective inverse temperature. "
            "The phenomenological ansatz f(T) = 1 + k_BT/(2ℏ) captures the leading "
            "correction: at low T the Born rule holds exactly; at higher T the "
            "distribution broadens. A first-principles derivation of f(T) requires "
            "solving the open-system WKB problem (open problem). Standard QM predicts "
            "the state changes (ρ thermalizes) but the rule |ψ|² is sacrosanct. "
            "Here the rule itself is temperature-dependent. The difference ΔP is "
            "the experimentally measurable residual — vanishingly small when S_E ≫ ℏ "
            "(macroscopic systems) but potentially detectable in mesoscopic regimes."
        ),
        "equations": [
            {
                "label": "Thermal broadening factor",
                "latex": r"f(T) = 1 + \frac{k_BT}{2\hbar}",
            },
            {
                "label": "Temperature-dependent probability",
                "latex": r"P_i(T) = \frac{e^{-2S_{E,i}/(\hbar \cdot f(T))}}{Z(T)}",
            },
            {
                "label": "Born rule (T → 0 limit)",
                "latex": r"\lim_{T \to 0} P_i(T) = \frac{|\psi_i|^2}{\sum_j|\psi_j|^2}",
            },
            {
                "label": "Deviation from standard QM",
                "latex": r"\Delta P_i = P_i^{\text{TD}}(T) - \text{Tr}(\rho_{\text{thermal}} |i\rangle\langle i|)",
            },
        ],
    })

    # --- Step 8: Jarzynski & Branch Suppression ---
    from src.math_engine.symbolic.jarzynski import (
        jarzynski_equality,
        branch_suppression_theorem,
    )

    jarzynski = jarzynski_equality()
    suppression = branch_suppression_theorem()

    steps.append({
        "id": "jarzynski_suppression",
        "title": "Branch Suppression",
        "subtitle": "Dissipative branches eliminated",
        "description": (
            "The Jarzynski equality ⟨exp(−βW)⟩ = exp(−βΔF) holds for any "
            "process. Decoherent branching is double-stochastic (unitary + "
            "partial trace), so it satisfies Jarzynski with W_diss = 0. "
            "Dissipative branching requires W_diss > 0, increasing the total "
            "Euclidean action by W_diss. Under Gibbs weighting, these branches "
            "are suppressed by exp(−W_diss/ℏ) — exponentially punished for "
            "thermodynamic waste. This converts axiom A4 into a theorem."
        ),
        "equations": [
            {
                "label": "Jarzynski equality",
                "latex": r"\langle e^{-\beta W} \rangle = e^{-\beta \Delta F}",
            },
            {
                "label": "Second law",
                "latex": r"W_{\text{diss}} = W - \Delta F \geq 0",
            },
            {
                "label": "Decoherent branch weight",
                "latex": r"w_{\text{dec}} = " + _latex(suppression["decoherent_weight"]),
            },
            {
                "label": "Dissipative branch weight",
                "latex": r"w_{\text{diss}} = " + _latex(suppression["dissipative_weight"]),
            },
            {
                "label": "Suppression factor",
                "latex": r"\frac{w_{\text{diss}}}{w_{\text{dec}}} = " + _latex(suppression["suppression_simplified"]),
            },
        ],
    })

    return steps


@router.get("/derivations")
async def get_derivations():
    """Return the eight-step derivation chain with LaTeX-rendered equations."""
    return {"steps": _build_derivation_chain()}
