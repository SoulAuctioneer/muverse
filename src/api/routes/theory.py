"""REST routes for theory CRUD operations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.core.seed_theory import build_seed_theory
from src.core.theory_schema import (
    Axiom,
    AxiomStatus,
    Critique,
    Derivation,
    Prediction,
    TheoryState,
)
from src.storage.database import load_latest_theory, save_theory_version

router = APIRouter()

_current_theory: TheoryState | None = None


def _get_theory() -> TheoryState:
    global _current_theory
    if _current_theory is None:
        _current_theory = build_seed_theory()
    return _current_theory


@router.get("/", response_model=TheoryState)
async def get_theory():
    """Get the current theory state."""
    return _get_theory()


@router.post("/seed", response_model=TheoryState)
async def seed_theory():
    """Reset theory to the initial seed state."""
    global _current_theory
    _current_theory = build_seed_theory()
    await save_theory_version(_current_theory)
    return _current_theory


@router.get("/axioms", response_model=list[Axiom])
async def get_axioms():
    return _get_theory().axioms


@router.get("/axioms/{label}", response_model=Axiom)
async def get_axiom(label: str):
    axiom = _get_theory().get_axiom(label)
    if not axiom:
        raise HTTPException(status_code=404, detail=f"Axiom {label} not found")
    return axiom


@router.get("/derivations", response_model=list[Derivation])
async def get_derivations():
    return _get_theory().derivations


@router.get("/predictions", response_model=list[Prediction])
async def get_predictions():
    return _get_theory().predictions


@router.get("/critiques", response_model=list[Critique])
async def get_critiques():
    return _get_theory().critiques


@router.get("/graph")
async def get_theory_graph():
    """Return the theory as a node-link graph for visualization."""
    theory = _get_theory()
    nodes = []
    edges = []

    for a in theory.axioms:
        nodes.append({
            "id": a.label,
            "type": "axiom",
            "label": a.label,
            "statement": a.statement[:100],
            "status": a.status.value,
        })

    for d in theory.derivations:
        nodes.append({
            "id": d.label,
            "type": "derivation",
            "label": d.label,
            "status": d.verification_status.value,
        })
        for premise in d.premises:
            edges.append({"source": premise, "target": d.label, "type": "premise"})
        edges.append({"source": d.label, "target": d.conclusion, "type": "conclusion"})

    for p in theory.predictions:
        nodes.append({
            "id": p.label,
            "type": "prediction",
            "label": p.label,
            "statement": p.statement[:100],
            "testable": p.testable,
        })
        for d_label in p.derived_from:
            edges.append({"source": d_label, "target": p.label, "type": "derives"})

    for c in theory.critiques:
        cid = f"C-{c.target_label}-{c.critique_type.value[:4]}"
        nodes.append({
            "id": cid,
            "type": "critique",
            "label": cid,
            "severity": c.severity.value,
            "status": c.resolution_status.value,
        })
        edges.append({"source": cid, "target": c.target_label, "type": "critiques"})

    return {"nodes": nodes, "edges": edges}


@router.get("/labels")
async def get_labels():
    return _get_theory().labels()
