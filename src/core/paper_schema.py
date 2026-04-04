"""Data models for the paper generation pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _id() -> str:
    return uuid.uuid4().hex[:12]


class SectionStatus(str, Enum):
    OUTLINE = "outline"
    DRAFTED = "drafted"
    REVIEWED = "reviewed"
    FINAL = "final"


class Citation(BaseModel):
    id: str = Field(default_factory=_id)
    bibtex_key: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    url: Optional[str] = None
    bibtex: Optional[str] = None


class Figure(BaseModel):
    id: str = Field(default_factory=_id)
    caption: str
    file_path: str
    simulation_id: Optional[str] = None
    latex_label: str = ""


class Section(BaseModel):
    id: str = Field(default_factory=_id)
    number: str = ""
    title: str
    status: SectionStatus = SectionStatus.OUTLINE
    outline_points: list[str] = Field(default_factory=list)
    body_latex: str = ""
    related_axioms: list[str] = Field(default_factory=list)
    related_derivations: list[str] = Field(default_factory=list)
    related_simulations: list[str] = Field(default_factory=list)
    citations_used: list[str] = Field(default_factory=list)
    figures: list[Figure] = Field(default_factory=list)
    review_notes: Optional[str] = None


class PaperOutline(BaseModel):
    id: str = Field(default_factory=_id)
    title: str = "Thermodynamic Darwinism: Born Rule as Emergent Gibbs Weighting in Energy-Constrained MWI"
    abstract: str = ""
    sections: list[Section] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def completeness(self) -> float:
        if not self.sections:
            return 0.0
        done = sum(1 for s in self.sections if s.status == SectionStatus.FINAL)
        return done / len(self.sections)
