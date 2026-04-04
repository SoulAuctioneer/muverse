"""Paper outline manager.

Maintains the structured outline, tracks section completeness,
and maps theory elements to paper sections.
"""

from __future__ import annotations

from src.core.paper_schema import Figure, PaperOutline, Section, SectionStatus


def create_default_outline() -> PaperOutline:
    """Build the standard outline for the Thermodynamic Darwinism paper."""
    sections = [
        Section(
            number="1",
            title="Introduction",
            outline_points=[
                "The Many-Worlds Interpretation and the branching multiverse",
                "The Born rule as MWI's deepest embarrassment",
                "Finite energy as a natural selection mechanism for branches",
                "Contributions and structure of this paper",
            ],
            related_axioms=["A1"],
        ),
        Section(
            number="2",
            title="Background and Related Work",
            outline_points=[
                "Quantum Darwinism: einselection and pointer states (Zurek 2003)",
                "Cosmological Natural Selection (Smolin 1992)",
                "Wick rotation: from quantum to statistical path integrals",
                "Jarzynski equality and non-equilibrium thermodynamics",
                "Free Energy Principle and active inference (Friston)",
                "SGD as Langevin dynamics: the neural network connection",
                "Dissipative adaptation (England)",
            ],
            related_axioms=["A3", "A4", "A6", "A7"],
        ),
        Section(
            number="3",
            title="The Thermodynamic Darwinism Framework",
            outline_points=[
                "Axiom A1: Unitary evolution of the universal wavefunction",
                "Axiom A2: Finite total Euclidean action (energy budget)",
                "Axiom A3: Wick rotation yields Gibbs-weighted branch ensemble",
                "Axiom A4: Jarzynski preservation under decoherence",
                "Axiom A5: Born rule as emergent Gibbs weight",
                "Axiom A6: Landauer cost of branching",
                "Axiom A7: SGD–Gibbs formal equivalence",
                "Axiom A8: Free-energy branch selection",
            ],
            related_axioms=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
        ),
        Section(
            number="4",
            title="Derivations",
            outline_points=[
                "D1: Born rule from Wick-rotated partition function under finite action",
                "D2: Free-energy selection from Landauer + partition function",
                "D3: The deductive chain from quantum path integrals to SGD",
            ],
            related_derivations=["D1", "D2", "D3"],
        ),
        Section(
            number="5",
            title="Predictions and Experimental Tests",
            outline_points=[
                "P1: Temperature-dependent Born rule deviations exp(−S_E/k_BT)",
                "P2: Free-energy selection of cosmological constants",
                "P3: Neural network analog test",
                "Experimental protocol: superconducting qubit thermodynamics",
                "Comparison with other Born rule derivation attempts",
            ],
        ),
        Section(
            number="6",
            title="Computational Results",
            outline_points=[
                "Simulation 1: Branch ensemble under Boltzmann constraint",
                "Simulation 2: Neural network analog model",
                "Simulation 3: Quantum Langevin dynamics",
                "Summary: discriminating signals and statistical significance",
            ],
            related_simulations=["sim1", "sim2", "sim3"],
        ),
        Section(
            number="7",
            title="Discussion",
            outline_points=[
                "Interpretation and philosophical implications",
                "Relation to Quantum Darwinism, CNS, FEP, and dissipative adaptation",
                "The A2 gap: justifying finite Euclidean action",
                "Wick rotation as physical vs. mathematical transformation",
                "Implications for the arrow of time and cosmological evolution",
            ],
        ),
        Section(
            number="8",
            title="Conclusion",
            outline_points=[
                "Summary of the framework, derivations, and predictions",
                "The key experimental test: temperature-dependent Born rule",
                "Open problems and future directions",
            ],
        ),
    ]

    return PaperOutline(sections=sections)


def section_completeness_report(outline: PaperOutline) -> dict:
    """Generate a completeness report for each section."""
    report = {
        "total": len(outline.sections),
        "final": 0,
        "reviewed": 0,
        "drafted": 0,
        "outline": 0,
        "sections": [],
    }
    for s in outline.sections:
        status = s.status.value
        report[status] = report.get(status, 0) + 1
        report["sections"].append({
            "number": s.number,
            "title": s.title,
            "status": status,
            "has_content": bool(s.body_latex),
            "n_outline_points": len(s.outline_points),
            "n_figures": len(s.figures),
        })
    report["overall_completeness"] = outline.completeness()
    return report
