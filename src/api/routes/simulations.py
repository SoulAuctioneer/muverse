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

        elif name == "sim4":
            from src.simulations.sim4_born_deviation import Sim4Config, run_simulation
            config = Sim4Config(**{k: v for k, v in params.items() if hasattr(Sim4Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "temperatures": result.temperatures.tolist(),
                    "born_probs": result.born_probs.tolist(),
                    "thermal_state_probs": result.thermal_state_probs.tolist(),
                    "td_probs": result.td_probs.tolist(),
                    "residual_norm": result.residual_norm.tolist(),
                    "td_born_residual_norm": result.td_born_residual_norm.tolist(),
                    "energies": result.energies.tolist(),
                    "euclidean_actions": result.euclidean_actions.tolist(),
                },
                "error": None,
            }
        elif name == "sim5":
            from src.simulations.sim5_lindblad_test import Sim5Config, run_simulation
            config = Sim5Config(**{k: v for k, v in params.items() if hasattr(Sim5Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "energies": result.energies.tolist(),
                    "wkb_actions": result.wkb_actions.tolist(),
                    "barrier_top": float(result.barrier_top),
                    "bath_temps": result.bath_temps.tolist(),
                    "lindblad_pops": result.lindblad_pops.tolist(),
                    "gibbs_energy_pops": result.gibbs_energy_pops.tolist(),
                    "gibbs_action_pops": result.gibbs_action_pops.tolist(),
                    "born_pops": result.born_pops.tolist(),
                    "residual_lindblad_vs_gibbs_e": result.residual_lindblad_vs_gibbs_e.tolist(),
                    "residual_gibbs_e_vs_gibbs_s": result.residual_gibbs_e_vs_gibbs_s.tolist(),
                    "x_grid": result.x_grid.tolist(),
                    "potential": result.potential.tolist(),
                    "trace_temp_idx": result.trace_temp_idx,
                    "trace_times": result.trace_times.tolist() if result.trace_times is not None else [],
                    "trace_pops": result.trace_pops.tolist() if result.trace_pops is not None else [],
                },
                "error": None,
            }
        elif name == "sim6":
            from src.simulations.sim6_heom_nonmarkov import Sim6Config, run_simulation
            config = Sim6Config(**{k: v for k, v in params.items() if hasattr(Sim6Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "energies": result.energies.tolist(),
                    "wkb_actions": result.wkb_actions.tolist(),
                    "barrier_top": float(result.barrier_top),
                    "coupling_strengths": result.coupling_strengths.tolist(),
                    "heom_pops": result.heom_pops.tolist(),
                    "gibbs_energy_pops": result.gibbs_energy_pops.tolist(),
                    "gibbs_action_pops": result.gibbs_action_pops.tolist(),
                    "residual_heom_vs_gibbs_e": result.residual_heom_vs_gibbs_e.tolist(),
                    "residual_heom_vs_gibbs_s": result.residual_heom_vs_gibbs_s.tolist(),
                    "direction_cosine": result.direction_cosine.tolist(),
                    "bath_temp": result.bath_temp,
                    "bath_cutoff": result.bath_cutoff,
                },
                "error": None,
            }
        elif name == "sim7":
            from src.simulations.sim7_landauer_pointer import Sim7Config, run_simulation
            config = Sim7Config(**{k: v for k, v in params.items() if hasattr(Sim7Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "d_system": result.d_system,
                    "env_sizes": result.env_sizes.tolist(),
                    "born_probs": result.born_probs.tolist(),
                    "info_probs": result.info_probs.tolist(),
                    "redundancy_per_env": result.redundancy_per_env.tolist(),
                    "mutual_info_per_env": result.mutual_info_per_env.tolist(),
                    "kl_born_per_env": result.kl_born_per_env.tolist(),
                    "kl_info_per_env": result.kl_info_per_env.tolist(),
                    "landauer_efficiency": result.landauer_efficiency.tolist(),
                    "landauer_min_cost": result.landauer_min_cost.tolist(),
                    "actual_dissipation": result.actual_dissipation.tolist(),
                    "pointer_info_bits": result.pointer_info_bits.tolist(),
                    "temperature": result.temperature,
                },
                "error": None,
            }
        elif name == "sim8":
            from src.simulations.sim8_jarzynski_test import Sim8Config, run_simulation
            config = Sim8Config(**{k: v for k, v in params.items() if hasattr(Sim8Config, k)})
            result = run_simulation(config)
            _sim_state[name] = {
                "status": "completed",
                "metrics": {
                    "dissipation_rates": result.dissipation_rates.tolist(),
                    "ds_distance": result.ds_distance.tolist(),
                    "jarzynski_ratio": result.jarzynski_ratio.tolist(),
                    "row_sum_dev": result.row_sum_dev.tolist(),
                    "col_sum_dev": result.col_sum_dev.tolist(),
                    "a4_verified_unitary": result.a4_verified_unitary,
                    "a4_broken_dissipative": result.a4_broken_dissipative,
                    "temperature": result.temperature,
                    "system_energies": result.system_energies.tolist(),
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
            "configurable_params": {
                "n_initial_branches": {"default": 16, "type": "int", "label": "Initial branches"},
                "n_beta_points": {"default": 50, "type": "int", "label": "Beta points"},
                "beta_range_min": {"default": 0.01, "type": "float", "label": "Beta min"},
                "beta_range_max": {"default": 10.0, "type": "float", "label": "Beta max"},
                "n_trials": {"default": 20, "type": "int", "label": "Trials"},
            },
        },
        "sim2": {
            "name": "Neural Network Analog Model",
            "description": "Tests SGD-Gibbs equivalence at different effective temperatures",
            "configurable_params": {
                "n_branches": {"default": 8, "type": "int", "label": "Branches"},
                "n_epochs": {"default": 200, "type": "int", "label": "Epochs"},
                "n_trials": {"default": 10, "type": "int", "label": "Trials"},
                "hidden_dim": {"default": 32, "type": "int", "label": "Hidden dim"},
            },
        },
        "sim3": {
            "name": "Quantum Langevin Dynamics",
            "description": "Tests temperature-dependent branch probabilities",
            "configurable_params": {
                "n_levels": {"default": 6, "type": "int", "label": "Energy levels"},
                "coupling_strength": {"default": 0.1, "type": "float", "label": "Coupling strength"},
                "t_max": {"default": 100.0, "type": "float", "label": "Max time"},
                "n_trials": {"default": 5, "type": "int", "label": "Trials"},
            },
        },
        "sim4": {
            "name": "Born Rule Deviation Test (P1)",
            "description": "Distinguishes Thermodynamic Darwinism from standard QM predictions",
            "configurable_params": {
                "n_levels": {"default": 4, "type": "int", "label": "Energy levels"},
                "energy_scale": {"default": 1.0, "type": "float", "label": "Energy scale"},
                "n_temperature_points": {"default": 40, "type": "int", "label": "Temp points"},
                "asymmetry": {"default": 0.3, "type": "float", "label": "Asymmetry"},
            },
        },
        "sim5": {
            "name": "Lindblad Master Equation Test",
            "description": "Tests TD vs standard QM using exact open-quantum dynamics (double-well + thermal bath)",
            "configurable_params": {
                "n_levels": {"default": 8, "type": "int", "label": "Energy levels"},
                "barrier_height": {"default": 6.0, "type": "float", "label": "Barrier height"},
                "well_separation": {"default": 1.8, "type": "float", "label": "Well separation"},
                "asymmetry": {"default": 0.15, "type": "float", "label": "Asymmetry"},
            },
        },
        "sim6": {
            "name": "HEOM Non-Markovian Test (Beyond Lindblad)",
            "description": "Tests TD at strong coupling using exact non-Markovian HEOM dynamics (influence functional)",
            "configurable_params": {
                "n_levels": {"default": 6, "type": "int", "label": "Energy levels"},
                "bath_temp": {"default": 2.0, "type": "float", "label": "Bath temperature"},
                "bath_cutoff": {"default": 2.0, "type": "float", "label": "Bath cutoff γ"},
                "heom_depth": {"default": 5, "type": "int", "label": "HEOM depth"},
            },
        },
        "sim7": {
            "name": "Landauer Pointer-State Test (Phase A)",
            "description": "Tests information-constrained pointer-state selection: Landauer cost vs Born rule vs info-budget prediction",
            "configurable_params": {
                "d_system": {"default": 4, "type": "int", "label": "System dimension"},
                "coupling_strength": {"default": 0.3, "type": "float", "label": "Coupling strength"},
                "temperature": {"default": 1.0, "type": "float", "label": "Temperature"},
                "n_steps": {"default": 200, "type": "int", "label": "Time steps"},
            },
        },
        "sim8": {
            "name": "Jarzynski Double Stochasticity Test (A4)",
            "description": "Tests whether unitary branching preserves double stochasticity and Jarzynski equality, and whether dissipation breaks it",
            "configurable_params": {
                "d_system": {"default": 4, "type": "int", "label": "System dimension"},
                "n_env_qubits": {"default": 3, "type": "int", "label": "Bath qubits"},
                "coupling_strength": {"default": 0.5, "type": "float", "label": "Coupling strength"},
                "temperature": {"default": 1.0, "type": "float", "label": "Temperature"},
                "t_final": {"default": 5.0, "type": "float", "label": "Evolution time"},
                "n_time_steps": {"default": 300, "type": "int", "label": "Time steps"},
            },
        },
    }
    for key in sims:
        if key in _sim_state:
            sims[key]["status"] = _sim_state[key]["status"]
        else:
            sims[key]["status"] = "not_started"
    return sims
