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
                "FALSIFIED. Originally postulated that under Wick rotation (it = ℏβ), "
                "the MWI path integral transforms from phase weights exp(iS/ℏ) to "
                "Boltzmann weights exp(−S_E/ℏ), yielding a thermal partition function "
                "over branch-space. Disproven by the Feynman-Vernon influence functional "
                "analysis: decoherence depends on path differences and bath correlations, "
                "not on Euclidean action. Confirmed numerically by Sim5 (Lindblad steady "
                "state = Gibbs(E), not Gibbs(S_E)) and Sim6 (HEOM non-Markovian "
                "corrections point away from the TD prediction)."
            ),
            formal_expression=(
                r"\sum_{\text{branches}} e^{iS/\hbar} "
                r"\xrightarrow{\text{Wick}} "
                r"\sum_{\text{branches}} e^{-S_E/\hbar}"
                r"\quad\textbf{[FALSIFIED]}"
            ),
            status=AxiomStatus.FALSIFIED,
            source_document=SOURCE_CONV,
            tags=["Wick rotation", "partition function", "Gibbs", "falsified"],
        ),
        Axiom(
            label="A4",
            statement=(
                "CONTESTED. Claims (a) and (b) verified by Sim8; claim (c) broken. "
                "(a) Decoherence-induced branching (unitary + partial trace) preserves "
                "double stochasticity — confirmed as an instance of Birkhoff's theorem. "
                "(b) Dissipative branching breaks double stochasticity — confirmed "
                "numerically. (c) Jarzynski-violating branches are suppressed under the "
                "energy-constrained partition function — this claim depends on the "
                "Gibbs(S_E) weighting from falsified A3 and has no surviving derivation."
            ),
            formal_expression=(
                r"\langle e^{-\beta W} \rangle = e^{-\beta \Delta F} "
                r"\quad\text{(Jarzynski equality)}"
                r"\quad\textbf{[CONTESTED — (c) depends on A3]}"
            ),
            status=AxiomStatus.CONTESTED,
            source_document=SOURCE_CONV,
            tags=["Jarzynski", "decoherence", "dissipation", "non-equilibrium",
                  "partially verified", "contested"],
        ),
        Axiom(
            label="A5",
            statement=(
                "CONTESTED. Originally claimed the Born rule |ψ|² emerges as the "
                "squared Euclidean amplitude in the thermal ensemble at zero temperature. "
                "The derivation via Wick rotation (D1) is broken because its premise A3 "
                "is falsified. The Born rule's emergence from thermodynamic constraints "
                "remains an open question requiring a new derivation path — possibly "
                "through information-theoretic bounds on pointer-state redundancy."
            ),
            formal_expression=(
                r"P(\text{branch}_i) = \frac{e^{-S_{E,i}/\hbar}}{Z} "
                r"\xrightarrow{T \to 0} |\psi_i|^2"
                r"\quad\textbf{[CONTESTED — derivation broken]}"
            ),
            status=AxiomStatus.CONTESTED,
            source_document=SOURCE_CONV,
            tags=["Born rule", "emergent", "Gibbs", "contested"],
        ),
        Axiom(
            label="A6",
            statement=(
                "Branching is not informationally free. Each branching event incurs a "
                "thermodynamic cost bounded below by Landauer's limit: kT ln 2 per bit "
                "of new information created. This is an established theorem of "
                "statistical mechanics, experimentally confirmed to the Landauer limit "
                "(Berut et al., Nature 2012)."
            ),
            formal_expression=r"Q_{\min} = k_B T \ln 2 \quad\text{per bit}",
            status=AxiomStatus.DERIVED,
            source_document=SOURCE_REPORT,
            tags=["Landauer", "information", "thermodynamic cost", "established"],
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
                "CONTESTED. Branches that persist most robustly are not lowest-energy "
                "but those with the best free-energy balance F = E − TS: energetically "
                "viable AND internally self-consistent (high entropy). This parallels "
                "SGD converging to wide flat minima, not the global minimum. The only "
                "derivation (D2) depends on falsified A3; the free-energy selection "
                "mechanism has no surviving derivation path from first principles."
            ),
            formal_expression=(
                r"F = E - TS, \quad \text{branch weight} \propto e^{-F/k_B T}"
                r"\quad\textbf{[CONTESTED — D2 broken]}"
            ),
            status=AxiomStatus.CONTESTED,
            source_document=SOURCE_CONV,
            tags=["free energy", "entropy", "flat minima", "selection", "contested"],
        ),
        Axiom(
            label="A9",
            statement=(
                "The number of redundant pointer-state copies that an environment "
                "can support is bounded by the Bekenstein bound on the environment's "
                "information capacity and the Landauer cost of each copy. The "
                "encoding cost per copy I_i = S(ρ_{E_k|i}) is the von Neumann "
                "entropy of the environment fragment conditioned on pointer state "
                "|i⟩ — determined by the system-environment Hamiltonian H_SE, not "
                "by Born probabilities. Pointer states with lower I_i achieve "
                "higher redundancy. The information-selected probability is "
                "P_i^info = (1/I_i) / Σ_j(1/I_j)."
            ),
            formal_expression=(
                r"I_i = S(\rho_{E_k|i}), \quad "
                r"N_{\max,i} = \frac{E_{\text{env}}}{I_i \cdot k_B T \ln 2}, \quad "
                r"P_i^{\text{info}} = \frac{1/I_i}{\sum_j 1/I_j}"
            ),
            status=AxiomStatus.POSTULATED,
            source_document="Phase A derivation",
            tags=["Landauer", "Bekenstein", "Quantum Darwinism", "pointer states",
                  "information", "Phase A", "non-circular"],
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
            verification_status=VerificationStatus.CRITIQUED,
            agent_notes=(
                "BROKEN: Premise A3 (Wick rotation = decoherence) has been falsified "
                "by the influence functional analysis and Sim5/Sim6. The Feynman-Vernon "
                "formalism shows that decoherence suppresses path *differences* via bath "
                "correlations, not individual paths via Euclidean action. This derivation "
                "chain is invalid as stated. A new path to the Born rule is needed."
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
            verification_status=VerificationStatus.CRITIQUED,
            agent_notes=(
                "BROKEN: Depends on falsified A3. The Euclidean action weighting that "
                "connects branching cost to the partition function is invalid. However, "
                "the Landauer cost component (A6) survives independently and may support "
                "a revised version of free-energy selection via information-theoretic "
                "constraints rather than Wick-rotated action."
            ),
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
            verification_status=VerificationStatus.CRITIQUED,
            agent_notes=(
                "PARTIALLY BROKEN: The FP → SGD Gibbs equivalence is mathematically "
                "valid and independent of A3 — it relies only on the structure of "
                "stochastic dynamics. But the first step (branch evolution via Wick "
                "rotation) invokes A3, which is falsified. The SGD analogy survives "
                "as a mathematical fact about Fokker-Planck steady states, but the "
                "claimed *physical* bridge from quantum branching is broken."
            ),
        ),
        Derivation(
            label="D4",
            premises=["A1", "A6", "A9"],
            conclusion="A9",
            steps=[
                DerivationStep(
                    description=(
                        "Quantum Darwinism (Zurek 2009): a pointer state becomes "
                        "'objective' when N independent environment fragments each "
                        "carry a copy of the system's state information."
                    ),
                    expression=r"R_\delta = \text{max } k \text{ s.t. } I(S:E_k) \geq (1-\delta) H(S)",
                ),
                DerivationStep(
                    description=(
                        "The encoding cost per pointer-state copy is "
                        "I_i = S(ρ_{E_k|i}), the conditional von Neumann entropy "
                        "of the environment fragment — determined by the "
                        "Hamiltonian H_SE, not by Born probabilities."
                    ),
                    expression=r"I_i = S(\rho_{E_k|i}) = -\text{Tr}[\rho_{E_k|i} \log_2 \rho_{E_k|i}]",
                ),
                DerivationStep(
                    description=(
                        "By Landauer's principle (A6), creating each copy dissipates "
                        "at least I_i × k_B T ln 2 of energy. Given available "
                        "energy E_env, maximum redundancy is "
                        "N_max,i = E_env / (I_i k_B T ln 2)."
                    ),
                    expression=r"N_{\max,i} = \frac{E_{\text{env}}}{I_i \cdot k_B T \ln 2}",
                ),
                DerivationStep(
                    description=(
                        "The information-selected probability P_i^info = (1/I_i) / "
                        "Σ_j(1/I_j) is determined solely by relative "
                        "Hamiltonian-determined encoding costs — energy and "
                        "temperature cancel in the ratio."
                    ),
                    expression=r"P_i^{\text{info}} = \frac{1/I_i}{\sum_j 1/I_j}",
                ),
            ],
            verification_status=VerificationStatus.UNVERIFIED,
            agent_notes=(
                "Phase A derivation (non-circular formulation). I_i is computed "
                "as S(ρ_{E_k|i}) from the system-environment Hamiltonian, not "
                "from Born probabilities. Uses only established results (Landauer "
                "bound, Quantum Darwinism redundancy). Simulation 7 tests this "
                "numerically with the non-circular I_i."
            ),
        ),
    ]

    predictions = [
        Prediction(
            label="P1",
            derived_from=["D1"],
            statement=(
                "UNDERMINED. Branch probabilities are temperature-dependent: |ψ|² "
                "statistics are recovered exactly only in the zero-temperature (maximum "
                "coherence) limit, with measurable deviations at finite temperature "
                "scaling as exp(−S_E/k_BT). This prediction's derivation (D1) depends "
                "on falsified A3; the specific mechanism proposed (Gibbs weighting over "
                "Euclidean actions) is no longer viable."
            ),
            quantitative_formula=(
                r"\Delta P \sim e^{-S_E / k_B T} - |\psi|^2"
                r"\quad\textbf{[UNDERMINED — D1 broken]}"
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
                "temperature dependence is evidence for thermodynamic weighting. "
                "NOTE: The derivation path for this prediction is broken."
            ),
        ),
        Prediction(
            label="P2",
            derived_from=["D2"],
            statement=(
                "UNDERMINED. Physical laws that survive across cosmic time are those "
                "with the best free-energy balance (not lowest energy), analogous to "
                "SGD converging to wide flat minima rather than the global minimum. "
                "This prediction's derivation (D2) depends on falsified A3; the "
                "free-energy selection mechanism has no surviving derivation path."
            ),
            testable=False,
            discriminating_power=(
                "Distinguishes from pure anthropic reasoning: laws are selected for "
                "thermodynamic efficiency, not merely observer-compatibility. "
                "NOTE: The derivation path for this prediction is broken."
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
        Prediction(
            label="P4",
            derived_from=["D4"],
            statement=(
                "In systems where the environment has finite information capacity "
                "(near the Bekenstein bound), the standard Quantum Darwinism "
                "redundancy plateau should be modified. States requiring more bits "
                "per pointer-state copy (higher I_i = S(ρ_{E_k|i})) should show "
                "reduced redundancy compared to the Born-rule prediction. The "
                "pointer-state statistics should interpolate between Born "
                "(P_i = |ψ_i|²) and the information-budget prediction "
                "(P_i^info ∝ 1/I_i) as the environment shrinks."
            ),
            quantitative_formula=(
                r"P_i^{\text{info}} = \frac{1/I_i}{\sum_j 1/I_j}, \quad "
                r"I_i = S(\rho_{E_k|i})"
            ),
            testable=True,
            experimental_design=(
                "Engineer a quantum system (e.g., transmon qubit) coupled to a "
                "small, controlled environment (few ancilla qubits). Measure "
                "pointer-state redundancy R_δ as a function of environment size. "
                "Compare the redundancy ranking with Born probabilities and with "
                "the Hamiltonian-determined information-budget prediction."
            ),
            discriminating_power=(
                "Born rule predicts redundancy proportional to |ψ_i|². Information "
                "budget predicts redundancy proportional to 1/I_i where I_i is the "
                "Hamiltonian-determined encoding cost S(ρ_{E_k|i}). These are "
                "independent quantities — one from state amplitudes, one from the "
                "coupling structure. Discrepancy depends on the specific H_SE."
            ),
        ),
        Prediction(
            label="P5",
            derived_from=["D4"],
            statement=(
                "The Landauer cost of pointer-state creation sets a minimum "
                "decoherence energy scale. Below this energy, branching is "
                "thermodynamically forbidden: the environment cannot create even "
                "one copy of the pointer-state record. This predicts a sharp "
                "energy threshold for the quantum-to-classical transition at "
                "E_threshold = I_state × k_B T ln 2."
            ),
            quantitative_formula=(
                r"E_{\text{threshold}} = I_s \cdot k_B T \ln 2"
            ),
            testable=True,
            experimental_design=(
                "Cool a mesoscopic quantum system to progressively lower "
                "temperatures while monitoring decoherence rates and pointer-state "
                "formation. The prediction is a threshold below which the "
                "environment lacks the energy to create pointer-state records, "
                "manifesting as anomalously slow decoherence."
            ),
            discriminating_power=(
                "Standard decoherence theory predicts a smooth temperature "
                "dependence (Γ ∝ T for ohmic baths). This prediction adds a "
                "sharp cutoff from the Landauer bound — a qualitatively different "
                "feature that would be unambiguous evidence for information-theoretic "
                "constraints on the quantum-to-classical transition."
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
            resolution_status=ResolutionStatus.ADDRESSED,
            resolution_notes=(
                "Superseded: D1 is now broken for a more fundamental reason — its "
                "premise A3 has been falsified. The circularity concern is moot."
            ),
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
            resolution_status=ResolutionStatus.RESOLVED,
            resolution_notes=(
                "Resolved by falsification. The Feynman-Vernon influence functional "
                "shows that decoherence depends on path differences Δ(t) = x(t) − x'(t) "
                "and bath correlation C(t), NOT on the Euclidean action S_E of individual "
                "paths. Sim5 (Lindblad) confirmed that Markovian steady state = Gibbs(E) "
                "to machine precision. Sim6 (HEOM) showed non-Markovian corrections point "
                "AWAY from Gibbs(S_E) (negative direction cosine). A3 is definitively false."
            ),
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
            resolution_status=ResolutionStatus.ADDRESSED,
            resolution_notes=(
                "P1 as originally stated (deviations scaling with exp(−S_E/k_BT)) is "
                "undermined by the falsification of A3. The specific mechanism proposed "
                "for temperature-dependent Born rule deviations is no longer viable."
            ),
        ),
        Critique(
            target_label="D1",
            critique_type=CritiqueType.EMPIRICAL_CONFLICT,
            severity=Severity.CRITICAL,
            description=(
                "D1 derives A5 from premises A1+A2+A3. Premise A3 has been falsified "
                "by the Feynman-Vernon influence functional analysis and confirmed by "
                "Sim5 (Lindblad) and Sim6 (HEOM). The derivation chain is broken: "
                "one cannot derive the Born rule from a Gibbs distribution over "
                "Euclidean actions because decoherence does not produce such a "
                "distribution."
            ),
            resolution_status=ResolutionStatus.OPEN,
            resolution_notes=(
                "A new derivation of the Born rule (or a revised prediction) is "
                "needed. Phase A explores information-theoretic constraints as a "
                "replacement mechanism."
            ),
        ),
        Critique(
            target_label="A5",
            critique_type=CritiqueType.LOGICAL_GAP,
            severity=Severity.HIGH,
            description=(
                "With A3 falsified, A5 has no surviving derivation path. The claim "
                "that the Born rule emerges as a thermodynamic consequence of "
                "Euclidean-action weighting is unsupported. The Born rule's emergence "
                "from within MWI remains an open question, now requiring a fundamentally "
                "different mechanism."
            ),
            resolution_status=ResolutionStatus.OPEN,
        ),
        Critique(
            target_label="A4",
            critique_type=CritiqueType.LOGICAL_GAP,
            severity=Severity.HIGH,
            description=(
                "A4 conflates established physics with a novel claim. Claims (a) "
                "(unitary preserves DS) and (b) (dissipation breaks DS) are "
                "restatements of Birkhoff's theorem, verified by Sim8. Claim (c) "
                "(Jarzynski-violating branches are exponentially suppressed via "
                "Gibbs(S_E) weighting) depends on the Euclidean action partition "
                "function from falsified A3. The branch_suppression_theorem in "
                "jarzynski.py explicitly uses exp(-S_E/hbar), which is invalid. "
                "The suppression mechanism needs reformulation without A3."
            ),
            resolution_status=ResolutionStatus.OPEN,
            resolution_notes=(
                "Claims (a) and (b) confirmed by Sim8. Claim (c) requires a new "
                "suppression mechanism not dependent on Euclidean action weighting."
            ),
        ),
    ]

    return TheoryState(
        version=2,
        name="Thermodynamic Darwinism",
        axioms=axioms,
        derivations=derivations,
        predictions=predictions,
        critiques=critiques,
    )
