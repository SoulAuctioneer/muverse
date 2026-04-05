"""REST routes for the paper pipeline.

Serves the paper outline, section CRUD, completeness metrics, and
full LaTeX generation.  All content is generated from the unified
pipeline (seed_theory + outline + optional sim results) rather than
hardcoded LaTeX blobs.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.core.paper_schema import PaperOutline, Section, SectionStatus

router = APIRouter()
logger = logging.getLogger(__name__)

_paper: PaperOutline | None = None

PIPELINE_OUTPUT = Path("pipeline_output.json")


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def _get_paper() -> PaperOutline:
    global _paper
    if _paper is None:
        from src.paper.outline import create_default_outline
        _paper = create_default_outline()
        _populate_from_pipeline(_paper)
    return _paper


# ---------------------------------------------------------------------------
# Optional population from legacy pipeline_output.json
# ---------------------------------------------------------------------------

def _extract_latex_from_writer(writer_output: str) -> str:
    """Pull the LaTeX source from the writer agent's markdown-wrapped output."""
    match = re.search(r"```latex\s*\n(.*?)```", writer_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    if r"\begin{document}" in writer_output:
        start = writer_output.index(r"\documentclass")
        end = writer_output.rindex(r"\end{document}") + len(r"\end{document}")
        return writer_output[start:end].strip()
    return ""


def _extract_section_bodies(full_latex: str) -> dict[str, str]:
    """Split full LaTeX into section bodies keyed by section title fragment."""
    section_pattern = re.compile(
        r"\\section\{([^}]+)\}.*?\n(.*?)(?=\\section\{|\\begin\{thebibliography\}|\\end\{document\})",
        re.DOTALL,
    )
    sections: dict[str, str] = {}
    for match in section_pattern.finditer(full_latex):
        title = match.group(1).strip()
        body = match.group(2).strip()
        body = re.sub(r"\\label\{[^}]*\}\s*", "", body, count=1).strip()
        sections[title.lower()] = body
    return sections


def _populate_from_pipeline(paper: PaperOutline) -> None:
    """Load writer output from pipeline_output.json and fill section bodies."""
    if not PIPELINE_OUTPUT.exists():
        logger.info("No pipeline_output.json found, sections remain empty")
        return

    try:
        data = json.loads(PIPELINE_OUTPUT.read_text())
    except Exception as e:
        logger.warning("Failed to parse pipeline_output.json: %s", e)
        return

    writer_output = data.get("agent_outputs", {}).get("writer", "")
    if not writer_output:
        return

    full_latex = _extract_latex_from_writer(writer_output)
    if not full_latex:
        logger.warning("Could not extract LaTeX from writer output")
        return

    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", full_latex, re.DOTALL
    )
    if abstract_match:
        paper.abstract = abstract_match.group(1).strip()

    section_bodies = _extract_section_bodies(full_latex)
    logger.info("Extracted %d sections from writer output", len(section_bodies))

    for section in paper.sections:
        key = section.title.lower()
        for extracted_title, body in section_bodies.items():
            if key in extracted_title or extracted_title in key:
                if body and not section.body_latex:
                    section.body_latex = body
                    section.status = SectionStatus.DRAFTED
                    break


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

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
        "drafted_sections": sum(
            1
            for s in paper.sections
            if s.status in (SectionStatus.DRAFTED, SectionStatus.REVIEWED, SectionStatus.FINAL)
        ),
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


@router.get("/full-latex")
async def get_full_latex():
    """Return the full paper LaTeX source, generated from the unified pipeline.

    The generation order is:
    1. If pipeline_output.json has a writer-generated LaTeX document and the
       paper outline sections have been populated from it, prefer that.
    2. Otherwise, generate the paper from the current seed theory + outline
       using ``generate_full_paper``.
    """
    paper = _get_paper()

    if PIPELINE_OUTPUT.exists():
        try:
            data = json.loads(PIPELINE_OUTPUT.read_text())
            writer_output = data.get("agent_outputs", {}).get("writer", "")
            full = _extract_latex_from_writer(writer_output)
            if full:
                return PlainTextResponse(full, media_type="text/plain")
        except Exception:
            pass

    try:
        from src.core.seed_theory import build_seed_theory
        from src.paper.latex_generator import generate_full_paper

        theory = build_seed_theory()
        latex = generate_full_paper(theory, paper)
        return PlainTextResponse(latex, media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}
