"""Simulation 1: Branch Ensemble under Boltzmann Constraint.

Tests the core premise: does Gibbs weighting of MWI branches recover
Born rule statistics while equal-weight branching does not?

Null hypothesis (H0): Equal-weight MWI — all branches have identical weight
Alternative (H1): Gibbs-weighted MWI — branches weighted by exp(−βS_E)

The discriminating test: sweep inverse temperature β and measure KL divergence
from Born rule predictions. H1 predicts convergence at high β; H0 does not.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from src.math_engine.numerical.branch_ensemble import (
    BranchEnsemble,
    evolve_constrained,
    evolve_unconstrained,
    initialize_ensemble,
    measure_born_rule_adherence,
)
from src.math_engine.numerical.monte_carlo import (
    born_rule_probabilities,
    gibbs_probabilities,
    kl_divergence,
    temperature_sweep,
)


@dataclass
class Sim1Config:
    n_initial_branches: int = 16
    n_generations: int = 6
    branching_factor: int = 2
    action_scale: float = 1.0
    action_noise: float = 0.3
    beta_range: tuple[float, float] = (0.01, 10.0)
    n_beta_points: int = 50
    n_trials: int = 20
    seed: int = 42


@dataclass
class Sim1Result:
    betas: NDArray[np.float64]
    kl_unconstrained: NDArray[np.float64]
    kl_constrained: NDArray[np.float64]
    kl_std_unconstrained: NDArray[np.float64]
    kl_std_constrained: NDArray[np.float64]
    final_actions_unconstrained: NDArray[np.float64]
    final_actions_constrained: NDArray[np.float64]
    born_probs: NDArray[np.float64]
    gibbs_probs_best_beta: NDArray[np.float64]


def run_single_trial(
    config: Sim1Config,
    beta: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Run one trial at a given beta, return KL divergences for both models."""
    ensemble = initialize_ensemble(config.n_initial_branches, config.action_scale, rng)

    unc_ensemble = ensemble
    con_ensemble = ensemble
    for _ in range(config.n_generations):
        unc_ensemble = evolve_unconstrained(
            unc_ensemble, config.branching_factor, config.action_noise, rng
        )
        con_ensemble = evolve_constrained(
            con_ensemble, config.branching_factor, config.action_noise, beta, rng
        )

    unc_amps = unc_ensemble.amplitudes
    con_amps = con_ensemble.amplitudes
    unc_actions = unc_ensemble.actions
    con_actions = con_ensemble.actions

    born_unc = born_rule_probabilities(unc_amps)
    born_con = born_rule_probabilities(con_amps)
    gibbs_unc = gibbs_probabilities(unc_actions, beta)
    gibbs_con = gibbs_probabilities(con_actions, beta)

    kl_unc = kl_divergence(born_unc, gibbs_unc)
    kl_con = kl_divergence(born_con, gibbs_con)

    return kl_unc, kl_con


def run_simulation(config: Sim1Config | None = None) -> Sim1Result:
    """Execute the full Simulation 1 with temperature sweep."""
    config = config or Sim1Config()
    rng = np.random.default_rng(config.seed)

    betas = np.geomspace(config.beta_range[0], config.beta_range[1], config.n_beta_points)
    kl_unc_all = np.zeros((config.n_beta_points, config.n_trials))
    kl_con_all = np.zeros((config.n_beta_points, config.n_trials))

    for i, beta in enumerate(betas):
        for j in range(config.n_trials):
            trial_rng = np.random.default_rng(config.seed + i * 1000 + j)
            kl_unc, kl_con = run_single_trial(config, beta, trial_rng)
            kl_unc_all[i, j] = min(kl_unc, 20.0)  # cap for plotting
            kl_con_all[i, j] = min(kl_con, 20.0)

    best_beta_idx = np.argmin(np.mean(kl_con_all, axis=1))
    best_beta = betas[best_beta_idx]

    trial_rng = np.random.default_rng(config.seed)
    ensemble = initialize_ensemble(config.n_initial_branches, config.action_scale, trial_rng)
    unc_ens = ensemble
    con_ens = ensemble
    for _ in range(config.n_generations):
        unc_ens = evolve_unconstrained(unc_ens, config.branching_factor, config.action_noise, trial_rng)
        con_ens = evolve_constrained(con_ens, config.branching_factor, config.action_noise, best_beta, trial_rng)

    return Sim1Result(
        betas=betas,
        kl_unconstrained=np.mean(kl_unc_all, axis=1),
        kl_constrained=np.mean(kl_con_all, axis=1),
        kl_std_unconstrained=np.std(kl_unc_all, axis=1),
        kl_std_constrained=np.std(kl_con_all, axis=1),
        final_actions_unconstrained=unc_ens.actions,
        final_actions_constrained=con_ens.actions,
        born_probs=born_rule_probabilities(con_ens.amplitudes),
        gibbs_probs_best_beta=gibbs_probabilities(con_ens.actions, best_beta),
    )
