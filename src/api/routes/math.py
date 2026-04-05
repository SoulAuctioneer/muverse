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
    """Build the derivation chain with LaTeX from the symbolic engine.

    v2: Steps 1-5 are mathematically valid. Steps 6-8 assumed the now-falsified
    A3 (Wick rotation). Step 9 presents the refutation. Steps 10+ present the
    new Phase A direction (information-theoretic bounds).
    """
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
        "subtitle": "Born rule from semiclassical limit [CAVEAT: assumed A3]",
        "description": (
            "In the semiclassical (WKB) regime, the tunneling wavefunction is "
            "ψ ~ exp(−S_E/ℏ) where S_E is the Euclidean action through the "
            "classically forbidden region. Therefore |ψ|² = exp(−2S_E/ℏ), "
            "which has the form of a Boltzmann weight at effective β = 2/ℏ. "
            "CAVEAT: This step implicitly assumes A3 — that the Euclidean action "
            "is the physically relevant quantity for branch weighting. The WKB "
            "amplitude relationship |ψ|² ∝ exp(−2S_E/ℏ) is mathematically "
            "correct but does NOT imply that thermal baths weight states by S_E. "
            "Sim5 and Sim6 show they weight by energy E instead."
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
        "subtitle": "Proposed deviation from Born rule [UNDERMINED: A3 falsified]",
        "description": (
            "UNDERMINED BY PHASE B: This prediction assumed A3 (Wick rotation = "
            "decoherence). The specific mechanism proposed — deviations scaling with "
            "exp(−S_E/k_BT) — is no longer viable because decoherence does not "
            "produce Euclidean-action-weighted distributions. "
            "The phenomenological ansatz f(T) = 1 + k_BT/(2ℏ) was a placeholder. "
            "A first-principles derivation via the influence functional (Step 9) "
            "shows the actual steady state is Gibbs(E), not Gibbs(S_E). "
            "The math below is preserved for historical reference."
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
        "subtitle": "Dissipative branches eliminated [CAVEAT: assumed A3]",
        "description": (
            "The Jarzynski equality ⟨exp(−βW)⟩ = exp(−βΔF) holds for any "
            "process — this is mathematically rigorous. However, the claim "
            "that dissipative branches are suppressed by exp(−W_diss/ℏ) "
            "assumed Gibbs weighting over Euclidean actions (A3), which is "
            "falsified. The Jarzynski equality itself survives and applies to "
            "real thermodynamic processes, but the connection to branch selection "
            "via Euclidean action is broken. The surviving content: dissipation "
            "is energetically costly (second law), which constrains branching "
            "via Landauer bounds (Phase A)."
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

    # --- Step 9: Influence Functional (Replaces Wick Rotation) ---
    from src.math_engine.symbolic.influence_functional import (
        drude_lorentz_spectral_density,
        bath_correlation_function,
        influence_functional_phase,
        high_T_ohmic_limit,
        mean_force_gibbs_state,
    )

    sd = drude_lorentz_spectral_density()
    ht = high_T_ohmic_limit()
    mfg = mean_force_gibbs_state()

    steps.append({
        "id": "influence_functional",
        "title": "The Refutation",
        "subtitle": "Influence functional falsifies A3",
        "description": (
            "The Feynman-Vernon influence functional is the correct, first-principles "
            "description of how a thermal bath suppresses quantum paths. For a system "
            "coupled to a Drude-Lorentz bath, the suppression factor depends on the "
            "PATH DIFFERENCE Δ(t) = x(t) − x′(t) and the bath correlation C(t) — "
            "NOT on the Euclidean action S_E of individual paths. "
            "At high T, Γ = 2mγk_BT/ℏ² (no S_E dependence). "
            "The dissipative part drives the system toward Gibbs(E), not Gibbs(S_E). "
            "Sim5 (Lindblad): steady state = Gibbs(E) to machine precision. "
            "Sim6 (HEOM): non-Markovian corrections point AWAY from Gibbs(S_E). "
            "VERDICT: A3 is falsified. Decoherence ≠ Wick rotation."
        ),
        "equations": [
            {
                "label": "Drude-Lorentz spectral density",
                "latex": sd["description"],
            },
            {
                "label": "Influence functional phase",
                "latex": (
                    r"\Phi[x,x'] = \frac{1}{\hbar}\int_0^t\!\!ds\int_0^s\!\!ds'\,"
                    r"\Delta(s)\!\left[C_{\mathrm{re}}(s\!-\!s')\Delta(s') "
                    r"+ iC_{\mathrm{im}}(s\!-\!s')\Sigma(s')\right]"
                ),
            },
            {
                "label": "High-T decoherence rate (Caldeira-Leggett)",
                "latex": ht["description"],
            },
            {
                "label": "Mean-force Gibbs state (exact at any coupling)",
                "latex": mfg["description"],
            },
            {
                "label": "Weak coupling limit (confirmed by Sim5)",
                "latex": mfg["weak_coupling_limit"],
            },
        ],
    })

    # --- Step 10: Landauer Bound on Pointer States (Phase A) ---
    from src.math_engine.symbolic.landauer_bekenstein import (
        landauer_erasure_cost,
        pointer_state_redundancy_cost,
        information_budget_selection,
    )

    lec = landauer_erasure_cost()
    prc = pointer_state_redundancy_cost()
    ibs = information_budget_selection()

    steps.append({
        "id": "landauer_pointer",
        "title": "Landauer Bound on Pointer States",
        "subtitle": "Phase A: information-theoretic selection (non-circular)",
        "description": (
            "With A3 falsified, the surviving foundation is information-theoretic. "
            "Landauer's principle (1961): any irreversible computation dissipates "
            "at least k_B T ln 2 per bit. Quantum Darwinism requires N redundant "
            "copies of a pointer state, each carrying I_i bits. CRITICAL: I_i is "
            "defined as S(ρ_{E_k|i}), the conditional von Neumann entropy of the "
            "environment fragment — determined by the Hamiltonian H_SE, NOT by "
            "Born probabilities. The previous definition I_i = -log₂(p_i) was "
            "circular. Given energy budget E_env, maximum redundancy is "
            "N_max = E_env / (I_i k_B T ln 2)."
        ),
        "equations": [
            {"label": "Landauer minimum per bit", "latex": lec["latex_per_bit"]},
            {"label": "Encoding cost (Hamiltonian-determined)",
             "latex": ibs["latex_I_def"]},
            {"label": "Total cost of N redundant copies", "latex": prc["latex_total"]},
            {"label": "Maximum redundancy", "latex": prc["latex_Nmax"]},
        ],
    })

    # --- Step 11: Information-Budget Selection (Phase A) ---
    from src.math_engine.symbolic.landauer_bekenstein import (
        bekenstein_bound,
        compare_with_born,
    )

    bb = bekenstein_bound()
    cwb = compare_with_born()

    steps.append({
        "id": "info_budget_selection",
        "title": "Information-Budget Selection",
        "subtitle": "Phase A: Bekenstein-limited branching (non-circular)",
        "description": (
            "The Bekenstein bound limits total information in any finite region: "
            "S_max ≤ 2π k_B R E / (ℏc). Combined with Landauer costs, this bounds "
            "the total number of pointer-state copies the environment can hold. "
            "The information-selected probability P_i^info = (1/I_i) / Σ(1/I_j) "
            "weights states inversely by their Hamiltonian-determined encoding "
            "cost I_i = S(ρ_{E_k|i}). Energy and temperature cancel in the ratio. "
            "This is genuinely independent of Born probabilities — the I_i come "
            "from the coupling structure, not from |⟨i|ψ⟩|². Simulation 7 "
            "computes I_i from the actual evolved density matrix."
        ),
        "equations": [
            {"label": "Bekenstein bound", "latex": bb["latex_bound"]},
            {"label": "Maximum information (bits)", "latex": bb["latex_bits"]},
            {"label": "Information-budget selection", "latex": ibs["latex_P_info"]},
            {"label": "Discrepancy with Born rule", "latex": cwb["latex_discrepancy"]},
        ],
    })

    return steps


@router.get("/derivations")
async def get_derivations():
    """Return the derivation chain with LaTeX-rendered equations."""
    return {"steps": _build_derivation_chain()}
