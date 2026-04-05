"""Structured data models for the Thermodynamic Darwinism theory.

Every element of the theory — axioms, derivations, predictions, critiques — is
represented as a Pydantic model so that agents can query, mutate, and verify
the theory programmatically.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _id() -> str:
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AxiomStatus(str, Enum):
    POSTULATED = "postulated"
    DERIVED = "derived"
    CONTESTED = "contested"
    FALSIFIED = "falsified"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    SYMBOLICALLY_VERIFIED = "symbolically_verified"
    NUMERICALLY_CONFIRMED = "numerically_confirmed"
    CRITIQUED = "critiqued"


class CritiqueType(str, Enum):
    LOGICAL_GAP = "logical_gap"
    CIRCULAR_REASONING = "circular_reasoning"
    EMPIRICAL_CONFLICT = "empirical_conflict"
    ALTERNATIVE_EXPLANATION = "alternative_explanation"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, Enum):
    OPEN = "open"
    ADDRESSED = "addressed"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"


# ---------------------------------------------------------------------------
# Core theory objects
# ---------------------------------------------------------------------------

class Axiom(BaseModel):
    id: str = Field(default_factory=_id)
    label: str = Field(..., description="Short identifier like A1, A2, …")
    statement: str = Field(..., description="Natural-language statement")
    formal_expression: Optional[str] = Field(
        None, description="LaTeX or SymPy-parseable expression"
    )
    status: AxiomStatus = AxiomStatus.POSTULATED
    source_document: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)


class DerivationStep(BaseModel):
    description: str
    expression: Optional[str] = None  # LaTeX


class Derivation(BaseModel):
    id: str = Field(default_factory=_id)
    label: str = Field(..., description="Short identifier like D1, D2, …")
    premises: list[str] = Field(..., description="List of Axiom labels used")
    conclusion: str = Field(..., description="Axiom label produced")
    steps: list[DerivationStep] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    agent_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Prediction(BaseModel):
    id: str = Field(default_factory=_id)
    label: str = Field(..., description="Short identifier like P1, P2, …")
    derived_from: list[str] = Field(
        default_factory=list, description="Derivation labels"
    )
    statement: str
    quantitative_formula: Optional[str] = None  # LaTeX
    testable: bool = True
    experimental_design: Optional[str] = None
    discriminating_power: Optional[str] = Field(
        None,
        description="What alternative theories this prediction rules out",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Critique(BaseModel):
    id: str = Field(default_factory=_id)
    target_label: str = Field(..., description="Label of the Axiom/Derivation/Prediction")
    critique_type: CritiqueType
    severity: Severity = Severity.MEDIUM
    description: str
    counter_argument: Optional[str] = None
    resolution_status: ResolutionStatus = ResolutionStatus.OPEN
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Aggregate: the full theory state at a point in time
# ---------------------------------------------------------------------------

class TheoryState(BaseModel):
    """Snapshot of the entire theory — axioms, derivations, predictions, critiques."""

    version: int = 1
    name: str = "Thermodynamic Darwinism"
    axioms: list[Axiom] = Field(default_factory=list)
    derivations: list[Derivation] = Field(default_factory=list)
    predictions: list[Prediction] = Field(default_factory=list)
    critiques: list[Critique] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_axiom(self, label: str) -> Optional[Axiom]:
        return next((a for a in self.axioms if a.label == label), None)

    def get_derivation(self, label: str) -> Optional[Derivation]:
        return next((d for d in self.derivations if d.label == label), None)

    def get_prediction(self, label: str) -> Optional[Prediction]:
        return next((p for p in self.predictions if p.label == label), None)

    def labels(self) -> dict[str, list[str]]:
        return {
            "axioms": [a.label for a in self.axioms],
            "derivations": [d.label for d in self.derivations],
            "predictions": [p.label for p in self.predictions],
            "critiques": [c.id for c in self.critiques],
        }
