"""Paper outline manager.

Maintains the structured outline, tracks section completeness,
and maps theory elements to paper sections.

The outline follows the v2 narrative: original framework, negative results
(A3 falsification), and the surviving information-theoretic direction.
"""

from __future__ import annotations

from src.core.paper_schema import PaperOutline, Section, SectionStatus


def create_default_outline() -> PaperOutline:
    """Build the v2 outline for the Thermodynamic Darwinism paper.

    Structure:
      1. Introduction
      2. Background
      3. The Original Framework  (axioms, derivations, original predictions)
      4. Initial Computational Results  (sims 1-4)
      5. Negative Results: Falsification of A3  (sims 5-6)
      6. Discussion: What Survives  (Phase A, sims 7-8)
      7. Conclusion
    """
    sections = [
        Section(
            number="1",
            title="Introduction",
            outline_points=[
                "MWI context and the branching multiverse",
                "The Born rule problem in Everettian QM",
                "Motivation: finite energy as a selection mechanism",
                "Structure: original framework, negative results, revised direction",
            ],
            related_axioms=["A1"],
        ),
        Section(
            number="2",
            title="Background",
            outline_points=[
                "Quantum Darwinism and einselection (Zurek)",
                "Wick rotation and Euclidean path integrals",
                "Feynman-Vernon influence functional",
                "Jarzynski equality and non-equilibrium thermodynamics",
                "SGD as Langevin dynamics: the NN-QM bridge",
                "Landauer bound and Bekenstein bound",
            ],
            related_axioms=["A4", "A6", "A7"],
        ),
        Section(
            number="3",
            title="The Original Framework",
            outline_points=[
                "Axioms A1-A9 with current status",
                "Derivations D1-D4 with verification status and caveats",
                "Original predictions P1-P3",
            ],
            related_axioms=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"],
            related_derivations=["D1", "D2", "D3", "D4"],
        ),
        Section(
            number="4",
            title="Initial Computational Results",
            outline_points=[
                "Sim 1: Branch ensemble under Boltzmann constraint",
                "Sim 2: Neural network analog model",
                "Sim 3: Quantum Langevin dynamics",
                "Sim 4: Born rule deviation test",
            ],
            related_simulations=["sim1", "sim2", "sim3", "sim4"],
        ),
        Section(
            number="5",
            title="Negative Results: Falsification of A3",
            outline_points=[
                "Influence functional analysis: decoherence depends on path "
                "differences and bath correlations, not Euclidean action",
                "Sim 5: Lindblad steady state = Gibbs(E), not Gibbs(S_E)",
                "Sim 6: HEOM non-Markovian corrections point away from TD",
                "Direction cosine metric confirms anti-correlation with TD",
                "Conclusion: A3 falsified, D1-D3 broken",
            ],
            related_simulations=["sim5", "sim6"],
            related_axioms=["A3"],
        ),
        Section(
            number="6",
            title="Discussion: What Survives",
            outline_points=[
                "Landauer cost of branching (A6) -- established physics",
                "Bekenstein bound on environment information capacity",
                "SGD/Gibbs analogy (A7) -- valid independently of A3",
                "Information-constrained pointer-state selection (Phase A)",
                "D4: non-circular derivation via conditional von Neumann entropy",
                "New predictions P4, P5 from information bounds",
                "Sim 7: Landauer pointer-state test",
                "Sim 8: Jarzynski double-stochasticity test",
            ],
            related_simulations=["sim7", "sim8"],
            related_axioms=["A6", "A7", "A8", "A9"],
            related_derivations=["D4"],
        ),
        Section(
            number="7",
            title="Conclusion",
            outline_points=[
                "Honest account: tested and partially falsified",
                "Scientific value of negative results",
                "Information-theoretic direction for future work",
            ],
        ),
    ]

    return PaperOutline(
        title=(
            "Thermodynamic Darwinism: Testing Born-Rule Emergence from "
            "Energy-Constrained Many-Worlds"
        ),
        sections=sections,
    )


def section_completeness_report(outline: PaperOutline) -> dict:
    """Generate a completeness report for each section."""
    report: dict = {
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
