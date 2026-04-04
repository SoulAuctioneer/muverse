"""REST routes for the paper pipeline."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.paper_schema import PaperOutline, Section, SectionStatus

router = APIRouter()

_paper: PaperOutline | None = None


def _get_paper() -> PaperOutline:
    global _paper
    if _paper is None:
        _paper = _build_default_outline()
    return _paper


def _build_default_outline() -> PaperOutline:
    """Create the default paper outline for Thermodynamic Darwinism."""
    sections = [
        Section(
            number="1",
            title="Introduction",
            outline_points=[
                "MWI context and the branching multiverse",
                "The Born rule problem in Everettian QM",
                "Motivation: finite energy as a selection mechanism",
                "Structure of the paper",
            ],
            related_axioms=["A1"],
        ),
        Section(
            number="2",
            title="Background",
            outline_points=[
                "Quantum Darwinism and einselection (Zurek)",
                "Wick rotation and Euclidean path integrals",
                "Jarzynski equality and non-equilibrium thermodynamics",
                "Free Energy Principle (Friston)",
                "SGD as Langevin dynamics: the NN-QM bridge",
            ],
            related_axioms=["A3", "A4", "A7"],
        ),
        Section(
            number="3",
            title="The Thermodynamic Darwinism Framework",
            outline_points=[
                "Axiom A1: Unitary evolution (standard MWI)",
                "Axiom A2: Finite Euclidean action (energy constraint)",
                "Axiom A3: Wick-rotated branch weights",
                "Axiom A4: Jarzynski preservation under decoherence",
                "Axiom A5: Emergent Born rule",
                "Axiom A6: Landauer cost of branching",
                "Axiom A7: SGD-Gibbs equivalence",
                "Axiom A8: Free-energy branch selection",
            ],
            related_axioms=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
            related_derivations=["D1", "D2", "D3"],
        ),
        Section(
            number="4",
            title="Derivations",
            outline_points=[
                "D1: Born rule from Gibbs weighting via Wick rotation",
                "D2: Free-energy selection from Landauer + Wick rotation",
                "D3: The QM → SGD deductive chain",
            ],
            related_derivations=["D1", "D2", "D3"],
        ),
        Section(
            number="5",
            title="Predictions",
            outline_points=[
                "P1: Temperature-dependent Born rule deviations",
                "P2: Free-energy selection of physical constants",
                "P3: NN analog test of Gibbs statistics",
                "Experimental design for P1",
            ],
        ),
        Section(
            number="6",
            title="Computational Results",
            outline_points=[
                "Sim 1: Branch ensemble under Boltzmann constraint",
                "Sim 2: Neural network analog model",
                "Sim 3: Quantum Langevin dynamics",
                "Summary of discriminating signals",
            ],
            related_simulations=["sim1", "sim2", "sim3"],
        ),
        Section(
            number="7",
            title="Discussion",
            outline_points=[
                "Interpretation and relation to existing frameworks",
                "Limitations: the A2 justification gap",
                "Comparison with other Born rule derivations",
                "Implications for cosmology and the arrow of time",
            ],
        ),
        Section(
            number="8",
            title="Conclusion",
            outline_points=[
                "Summary of the framework and key results",
                "Experimental outlook: what would confirm or falsify P1",
                "Open problems and future work",
            ],
        ),
    ]

    return PaperOutline(sections=sections)


@router.get("/outline", response_model=PaperOutline)
async def get_outline():
    return _get_paper()


@router.get("/sections", response_model=list[Section])
async def get_sections():
    return _get_paper().sections


@router.get("/sections/{number}", response_model=Section)
async def get_section(number: str):
    paper = _get_paper()
    for s in paper.sections:
        if s.number == number:
            return s
    return Section(title="Not found", number=number)


@router.get("/completeness")
async def get_completeness():
    paper = _get_paper()
    return {
        "completeness": paper.completeness(),
        "total_sections": len(paper.sections),
        "final_sections": sum(1 for s in paper.sections if s.status == SectionStatus.FINAL),
        "sections": [
            {"number": s.number, "title": s.title, "status": s.status.value}
            for s in paper.sections
        ],
    }


class SectionUpdate(BaseModel):
    body_latex: str = ""
    status: str = "drafted"
    review_notes: str | None = None


@router.put("/sections/{number}")
async def update_section(number: str, update: SectionUpdate):
    paper = _get_paper()
    for s in paper.sections:
        if s.number == number:
            if update.body_latex:
                s.body_latex = update.body_latex
            s.status = SectionStatus(update.status)
            if update.review_notes is not None:
                s.review_notes = update.review_notes
            return {"status": "updated", "section": number}
    return {"status": "not_found"}
