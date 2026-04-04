"""REST routes for simulation control and results."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

_sim_state: dict[str, Any] = {}


class SimRequest(BaseModel):
    simulation: str  # sim1 | sim2 | sim3
    parameters: dict[str, Any] = {}


class SimStatusResponse(BaseModel):
    simulation: str
    status: str
    metrics: dict[str, Any] = {}
    error: str | None = None


def _run_sim(name: str, params: dict):
    """Execute a simulation synchronously (called from background task)."""
    try:
        _sim_state[name] = {"status": "running", "metrics": {}, "error": None}

        if name == "sim1":
            from src.simulations.sim1_branch_boltzmann import Sim1Config, run_simulation
            config = Sim1Config(**{k: v for k, v in params.items() if hasattr(Sim1Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "best_kl_constrained": float(min(result.kl_constrained)),
                    "best_kl_unconstrained": float(min(result.kl_unconstrained)),
                    "n_beta_points": len(result.betas),
                    "kl_constrained": result.kl_constrained.tolist(),
                    "kl_unconstrained": result.kl_unconstrained.tolist(),
                    "betas": result.betas.tolist(),
                },
                "error": None,
            }

        elif name == "sim2":
            from src.simulations.sim2_nn_analog import Sim2Config, run_simulation
            config = Sim2Config(**{k: v for k, v in params.items() if hasattr(Sim2Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "temperatures": result.temperatures.tolist(),
                    "kl_from_born": result.kl_from_born.tolist(),
                    "kl_from_gibbs": result.kl_from_gibbs.tolist(),
                    "branch_energies": result.branch_energies.tolist(),
                },
                "error": None,
            }

        elif name == "sim3":
            from src.simulations.sim3_quantum_langevin import Sim3Config, run_simulation
            config = Sim3Config(**{k: v for k, v in params.items() if hasattr(Sim3Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "temperatures": result.temperatures.tolist(),
                    "kl_from_gibbs": result.kl_from_gibbs.tolist(),
                    "kl_from_born": result.kl_from_born.tolist(),
                    "convergence_times": result.convergence_times.tolist(),
                    "energies": result.energies.tolist(),
                },
                "error": None,
            }
        else:
            _sim_state[name] = {"status": "failed", "metrics": {}, "error": f"Unknown simulation: {name}"}

    except Exception as e:
        _sim_state[name] = {"status": "failed", "metrics": {}, "error": str(e)}


@router.post("/run", response_model=SimStatusResponse)
async def run_simulation(request: SimRequest, background_tasks: BackgroundTasks):
    """Launch a simulation in the background."""
    name = request.simulation
    if name in _sim_state and _sim_state[name].get("status") == "running":
        return SimStatusResponse(simulation=name, status="already_running")

    background_tasks.add_task(_run_sim, name, request.parameters)
    return SimStatusResponse(simulation=name, status="started")


@router.get("/status/{simulation}", response_model=SimStatusResponse)
async def get_simulation_status(simulation: str):
    """Get the status of a simulation."""
    if simulation not in _sim_state:
        return SimStatusResponse(simulation=simulation, status="not_started")
    state = _sim_state[simulation]
    return SimStatusResponse(
        simulation=simulation,
        status=state["status"],
        metrics=state.get("metrics", {}),
        error=state.get("error"),
    )


@router.get("/results/{simulation}")
async def get_simulation_results(simulation: str):
    """Get full results of a completed simulation."""
    if simulation not in _sim_state:
        return {"error": "Simulation not found"}
    return _sim_state[simulation]


@router.get("/list")
async def list_simulations():
    """List all available simulations and their current status."""
    sims = {
        "sim1": {
            "name": "Branch Ensemble under Boltzmann Constraint",
            "description": "Tests whether Gibbs weighting recovers Born rule statistics",
        },
        "sim2": {
            "name": "Neural Network Analog Model",
            "description": "Tests SGD-Gibbs equivalence at different effective temperatures",
        },
        "sim3": {
            "name": "Quantum Langevin Dynamics",
            "description": "Tests temperature-dependent branch probabilities",
        },
    }
    for key in sims:
        if key in _sim_state:
            sims[key]["status"] = _sim_state[key]["status"]
        else:
            sims[key]["status"] = "not_started"
    return sims
