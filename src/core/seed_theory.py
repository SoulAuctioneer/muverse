"""Seed the initial TheoryState from the two source documents.

Extracts the core axioms, derivations, predictions, and known critiques
identified in ThermoDynamicDarwinism.md and the MWI research report.
"""

from src.core.theory_schema import (
    Axiom,
    AxiomStatus,
    Critique,
    CritiqueType,
    Derivation,
    DerivationStep,
    Prediction,
    ResolutionStatus,
    Severity,
    TheoryState,
    VerificationStatus,
)

SOURCE_CONV = "ThermoDynamicDarwinism.md"
SOURCE_REPORT = "MWI, Evolution, and Energy Constraints.txt"


def build_seed_theory() -> TheoryState:
    axioms = [
        Axiom(
            label="A1",
            statement=(
                "The universal wavefunction evolves unitarily via the Schrödinger equation; "
                "all possible outcomes of quantum interactions are physically realized in "
                "distinct branches (standard MWI)."
            ),
            formal_expression=r"i\hbar \frac{\partial}{\partial t}|\Psi\rangle = \hat{H}|\Psi\rangle",
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_REPORT,
            tags=["MWI", "unitarity", "Everett"],
        ),
        Axiom(
            label="A2",
            statement=(
                "The total Euclidean action S_E of the universal wavefunction is bounded "
                "(finite energy budget). The multiverse as a whole has finite energy."
            ),
            formal_expression=r"S_E = \int \mathcal{L}_E \, d^4x < \infty",
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_CONV,
            tags=["energy constraint", "cosmological boundary", "Hartle-Hawking"],
        ),
        Axiom(
            label="A3",
            statement=(
                "Under Wick rotation (it = ℏβ), the MWI path integral over branches "
                "transforms from phase weights exp(iS/ℏ) to Boltzmann weights exp(−S_E/ℏ), "
                "yielding a thermal partition function over branch-space."
            ),
            formal_expression=(
                r"\sum_{\text{branches}} e^{iS/\hbar} "
                r"\xrightarrow{\text{Wick}} "
                r"\sum_{\text{branches}} e^{-S_E/\hbar}"
            ),
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_CONV,
            tags=["Wick rotation", "partition function", "Gibbs"],
        ),
        Axiom(
            label="A4",
            statement=(
                "Decoherence-induced branching preserves the Jarzynski double stochasticity "
                "condition, while energetically dissipative branching violates it. Branches "
                "that violate Jarzynski symmetry are exactly those suppressed under the "
                "energy-constrained partition function."
            ),
            formal_expression=(
                r"\langle e^{-\beta W} \rangle = e^{-\beta \Delta F} "
                r"\quad\text{(Jarzynski equality)}"
            ),
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_CONV,
            tags=["Jarzynski", "decoherence", "dissipation", "non-equilibrium"],
        ),
        Axiom(
            label="A5",
            statement=(
                "The Born rule |ψ|² emerges as the squared Euclidean amplitude in the "
                "thermal ensemble at zero temperature, not as an independent axiom. "
                "It is a thermodynamic consequence of finite-energy branch weighting."
            ),
            formal_expression=(
                r"P(\text{branch}_i) = \frac{e^{-S_{E,i}/\hbar}}{Z} "
                r"\xrightarrow{T \to 0} |\psi_i|^2"
            ),
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_CONV,
            tags=["Born rule", "emergent", "Gibbs"],
        ),
        Axiom(
            label="A6",
            statement=(
                "Branching is not informationally free. Each branching event incurs a "
                "thermodynamic cost bounded below by Landauer's limit: kT ln 2 per bit "
                "of new information created."
            ),
            formal_expression=r"Q_{\min} = k_B T \ln 2 \quad\text{per bit}",
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_REPORT,
            tags=["Landauer", "information", "thermodynamic cost"],
        ),
        Axiom(
            label="A7",
            statement=(
                "The steady-state distribution of the SGD process over neural network "
                "weights converges to a Gibbs distribution exp(−Φ(x)/T), making NN "
                "training a finite-compute-budget analogue of energy-constrained branch "
                "selection. This is a formal equivalence, not a metaphor."
            ),
            formal_expression=(
                r"p_{\text{ss}}(x) \propto e^{-\Phi(x)/T}, \quad "
                r"T = \frac{\eta}{B} \cdot \text{(noise scale)}"
            ),
            status=AxiomStatus.DERIVED,
            source_document=SOURCE_CONV,
            tags=["SGD", "neural network", "Fokker-Planck", "Gibbs"],
        ),
        Axiom(
            label="A8",
            statement=(
                "Branches that persist most robustly are not lowest-energy but those with "
                "the best free-energy balance F = E − TS: energetically viable AND "
                "internally self-consistent (high entropy). This parallels SGD converging "
                "to wide flat minima, not the global minimum."
            ),
            formal_expression=r"F = E - TS, \quad \text{branch weight} \propto e^{-F/k_B T}",
            status=AxiomStatus.POSTULATED,
            source_document=SOURCE_CONV,
            tags=["free energy", "entropy", "flat minima", "selection"],
        ),
    ]

    derivations = [
        Derivation(
            label="D1",
            premises=["A1", "A2", "A3"],
            conclusion="A5",
            steps=[
                DerivationStep(
                    description=(
                        "Start with the MWI path integral: sum over all histories "
                        "weighted by exp(iS/ℏ)."
                    ),
                    expression=r"\Psi = \int \mathcal{D}[\phi]\, e^{iS[\phi]/\hbar}",
                ),
                DerivationStep(
                    description=(
                        "Apply Wick rotation it = ℏβ to convert to Euclidean signature. "
                        "Phase weight becomes Boltzmann weight."
                    ),
                    expression=(
                        r"Z = \int \mathcal{D}[\phi]\, e^{-S_E[\phi]/\hbar}"
                    ),
                ),
                DerivationStep(
                    description=(
                        "Under finite total action (A2), the branch distribution at "
                        "steady state is a Gibbs distribution with effective temperature "
                        "T* = ℏ/(βk_B)."
                    ),
                    expression=(
                        r"P(\text{branch}_i) = \frac{e^{-S_{E,i}/\hbar}}{Z}"
                    ),
                ),
                DerivationStep(
                    description=(
                        "In the zero-temperature limit (maximum coherence), the Gibbs "
                        "weight reduces to the Born rule |ψ|²."
                    ),
                    expression=(
                        r"\lim_{T \to 0} P_i = |\psi_i|^2"
                    ),
                ),
            ],
            verification_status=VerificationStatus.UNVERIFIED,
            agent_notes=(
                "The T→0 limit step requires showing that the squared Euclidean "
                "amplitude equals |ψ|². This is the key step to verify for circularity."
            ),
        ),
        Derivation(
            label="D2",
            premises=["A3", "A6"],
            conclusion="A8",
            steps=[
                DerivationStep(
                    description=(
                        "Each branching event has informational cost (Landauer). "
                        "Total branch cost = Euclidean action + informational entropy cost."
                    ),
                ),
                DerivationStep(
                    description=(
                        "Branches with high action AND low entropy are doubly suppressed. "
                        "Branches with moderate action and high entropy (many similar "
                        "nearby configurations) are favored: F = E − TS is minimized."
                    ),
                    expression=r"\text{weight} \propto e^{-(E - TS)/k_B T} = e^{-F/k_B T}",
                ),
            ],
            verification_status=VerificationStatus.UNVERIFIED,
        ),
        Derivation(
            label="D3",
            premises=["A1", "A3", "A7"],
            conclusion="A7",
            steps=[
                DerivationStep(
                    description=(
                        "The Fokker-Planck equation governing branch-space evolution "
                        "under constrained MWI is structurally identical to the "
                        "Schrödinger equation under Wick rotation."
                    ),
                ),
                DerivationStep(
                    description=(
                        "SGD viewed as overdamped Langevin dynamics has the same "
                        "Fokker-Planck steady state: a Gibbs distribution with "
                        "temperature set by learning rate and batch size."
                    ),
                ),
                DerivationStep(
                    description=(
                        "Therefore the chain Quantum path integral → Partition function "
                        "→ Fokker-Planck → Langevin → SGD is deductive, not analogical."
                    ),
                ),
            ],
            verification_status=VerificationStatus.UNVERIFIED,
            agent_notes="Establishes the NN-QM equivalence as the formal bridge for Simulation 2.",
        ),
    ]

    predictions = [
        Prediction(
            label="P1",
            derived_from=["D1"],
            statement=(
                "Branch probabilities are temperature-dependent: |ψ|² statistics are "
                "recovered exactly only in the zero-temperature (maximum coherence) limit, "
                "with measurable deviations at finite temperature scaling as exp(−S_E/k_BT). "
                "No other Born rule derivation makes this temperature-dependent prediction."
            ),
            quantitative_formula=(
                r"\Delta P \sim e^{-S_E / k_B T} - |\psi|^2"
            ),
            testable=True,
            experimental_design=(
                "Prepare quantum superposition at multiple effective temperatures via "
                "coupling to thermal baths (superconducting qubit thermodynamics). "
                "Measure whether effective branch probabilities shift with temperature."
            ),
            discriminating_power=(
                "Standard MWI predicts temperature-independent Born rule statistics. "
                "Carroll/Sebens, Deutsch/Wallace, Zurek envariance, and Saunders branch "
                "counting make no temperature-dependent prediction. Any observed "
                "temperature dependence is evidence for thermodynamic weighting."
            ),
        ),
        Prediction(
            label="P2",
            derived_from=["D2"],
            statement=(
                "Physical laws that survive across cosmic time are those with the best "
                "free-energy balance (not lowest energy), analogous to SGD converging "
                "to wide flat minima rather than the global minimum."
            ),
            testable=False,
            discriminating_power=(
                "Distinguishes from pure anthropic reasoning: laws are selected for "
                "thermodynamic efficiency, not merely observer-compatibility."
            ),
        ),
        Prediction(
            label="P3",
            derived_from=["D3"],
            statement=(
                "In a neural network with branching loss landscape, Born rule statistics "
                "should emerge at low effective temperature (low learning rate) and "
                "deviate measurably at high temperature. Standard MWI has no "
                "temperature-dependent prediction."
            ),
            quantitative_formula=(
                r"p_{\text{branch}} \propto e^{-L_{\text{branch}}/T_{\text{eff}}}"
            ),
            testable=True,
            experimental_design=(
                "Design NN with hierarchical branching loss landscape. Train at "
                "multiple effective temperatures (varying learning rate/batch size). "
                "Compare weight distributions to Born rule predictions."
            ),
            discriminating_power=(
                "Clean discriminating signal: if weight distributions follow Gibbs "
                "statistics at branch points, the formal equivalence is confirmed "
                "experimentally."
            ),
        ),
    ]

    critiques = [
        Critique(
            target_label="A2",
            critique_type=CritiqueType.LOGICAL_GAP,
            severity=Severity.CRITICAL,
            description=(
                "The finite Euclidean action assumption is the theory's weakest link. "
                "Whether the MWI total wavefunction admits a well-defined finite "
                "Euclidean action requires cosmological boundary conditions that remain "
                "contested. The Hartle-Hawking no-boundary proposal is the most developed "
                "attempt but its interpretation is disputed."
            ),
            resolution_status=ResolutionStatus.OPEN,
        ),
        Critique(
            target_label="D1",
            critique_type=CritiqueType.CIRCULAR_REASONING,
            severity=Severity.HIGH,
            description=(
                "The derivation of the Born rule from Gibbs weighting must be verified "
                "to not smuggle in |ψ|² as a hidden assumption. The T→0 limit step "
                "is the key point to audit: does equating the squared Euclidean amplitude "
                "with |ψ|² presuppose the Born rule?"
            ),
            resolution_status=ResolutionStatus.OPEN,
        ),
        Critique(
            target_label="A3",
            critique_type=CritiqueType.LOGICAL_GAP,
            severity=Severity.HIGH,
            description=(
                "Wick rotation is a mathematical technique for evaluating path integrals, "
                "not necessarily a physical transformation. Interpreting the Euclidean "
                "path integral as physically real (branches ARE Boltzmann-weighted) "
                "rather than as a calculational tool requires additional justification."
            ),
            resolution_status=ResolutionStatus.OPEN,
        ),
        Critique(
            target_label="P1",
            critique_type=CritiqueType.EMPIRICAL_CONFLICT,
            severity=Severity.MEDIUM,
            description=(
                "Must verify that no existing experiments already constrain "
                "temperature-dependent deviations from Born rule statistics. If such "
                "constraints exist and are tight, P1 may already be falsified or "
                "pushed to unobservably small regimes."
            ),
            resolution_status=ResolutionStatus.OPEN,
        ),
    ]

    return TheoryState(
        version=1,
        name="Thermodynamic Darwinism",
        axioms=axioms,
        derivations=derivations,
        predictions=predictions,
        critiques=critiques,
    )
