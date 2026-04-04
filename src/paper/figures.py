"""Figure generation for the paper from simulation results.

Each simulation produces specific publication-quality plots
using Matplotlib.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path("output/figures")


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def set_paper_style():
    """Set matplotlib style for publication-quality figures."""
    plt.rcParams.update({
        "figure.figsize": (3.4, 2.5),
        "font.size": 8,
        "font.family": "serif",
        "axes.linewidth": 0.5,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "lines.linewidth": 1.0,
        "legend.fontsize": 7,
        "figure.dpi": 300,
    })


def plot_sim1_kl_divergence(
    betas: np.ndarray,
    kl_unconstrained: np.ndarray,
    kl_constrained: np.ndarray,
    kl_std_unc: np.ndarray | None = None,
    kl_std_con: np.ndarray | None = None,
) -> str:
    """Plot KL divergence from Born rule vs inverse temperature.

    This is the key figure for Simulation 1: shows that constrained
    (Gibbs-weighted) branches converge to Born rule at high β while
    unconstrained branches do not.
    """
    ensure_output_dir()
    set_paper_style()

    fig, ax = plt.subplots()
    ax.semilogx(betas, kl_unconstrained, "o-", color="#ef4444", markersize=3,
                label="Unconstrained (standard MWI)")
    ax.semilogx(betas, kl_constrained, "s-", color="#4a9eff", markersize=3,
                label="Constrained (Gibbs-weighted)")

    if kl_std_unc is not None:
        ax.fill_between(betas, kl_unconstrained - kl_std_unc,
                        kl_unconstrained + kl_std_unc, alpha=0.15, color="#ef4444")
    if kl_std_con is not None:
        ax.fill_between(betas, kl_constrained - kl_std_con,
                        kl_constrained + kl_std_con, alpha=0.15, color="#4a9eff")

    ax.set_xlabel(r"Inverse temperature $\beta$")
    ax.set_ylabel(r"$D_\mathrm{KL}(\mathrm{Born}\,||\,\mathrm{Gibbs})$")
    ax.legend()
    ax.set_title("Sim 1: Born Rule Adherence vs Temperature")

    path = str(OUTPUT_DIR / "sim1_kl_divergence.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_sim2_temperature_sweep(
    temperatures: np.ndarray,
    kl_from_born: np.ndarray,
    kl_from_gibbs: np.ndarray,
) -> str:
    """Plot KL divergence from Born and Gibbs predictions vs effective temperature.

    Key figure for Simulation 2: shows that NN weight distributions
    match Gibbs predictions (low KL from Gibbs) and approach Born rule
    at low temperature.
    """
    ensure_output_dir()
    set_paper_style()

    fig, ax = plt.subplots()
    ax.plot(temperatures, kl_from_born, "o-", color="#8b5cf6", markersize=3,
            label=r"$D_\mathrm{KL}$ from Born rule")
    ax.plot(temperatures, kl_from_gibbs, "s-", color="#34d399", markersize=3,
            label=r"$D_\mathrm{KL}$ from Gibbs prediction")

    ax.set_xlabel(r"Effective temperature $T_\mathrm{eff} = \eta / B$")
    ax.set_ylabel(r"KL Divergence")
    ax.legend()
    ax.set_title("Sim 2: NN Weight Distribution vs Temperature")

    path = str(OUTPUT_DIR / "sim2_nn_temperature.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_sim3_populations(
    temperatures: np.ndarray,
    steady_state_pops: np.ndarray,
    gibbs_predictions: np.ndarray,
    energies: np.ndarray,
) -> str:
    """Plot steady-state populations vs Gibbs predictions at multiple temperatures.

    Key figure for Simulation 3: shows quantum system thermalization
    to Gibbs distribution with temperature dependence.
    """
    ensure_output_dir()
    set_paper_style()

    n_temps = len(temperatures)
    n_show = min(4, n_temps)
    indices = np.linspace(0, n_temps - 1, n_show, dtype=int)

    fig, axes = plt.subplots(1, n_show, figsize=(3.4 * n_show / 2, 2.5), sharey=True)
    if n_show == 1:
        axes = [axes]

    n_levels = steady_state_pops.shape[1]
    x = np.arange(n_levels)

    for i, idx in enumerate(indices):
        ax = axes[i]
        T = temperatures[idx]
        ax.bar(x - 0.15, steady_state_pops[idx], width=0.3, color="#4a9eff",
               alpha=0.8, label="Simulation")
        ax.bar(x + 0.15, gibbs_predictions[idx], width=0.3, color="#34d399",
               alpha=0.8, label="Gibbs")
        ax.set_xlabel("Energy level")
        ax.set_title(f"T = {T:.2f}")
        if i == 0:
            ax.set_ylabel("Population")
        if i == n_show - 1:
            ax.legend(fontsize=6)

    fig.suptitle("Sim 3: Quantum Langevin Steady-State Populations", fontsize=9)
    fig.tight_layout()

    path = str(OUTPUT_DIR / "sim3_populations.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_theory_chain() -> str:
    """Generate the mathematical chain diagram.

    Quantum path integral → Partition function → Fokker-Planck →
    Langevin → SGD
    """
    ensure_output_dir()
    set_paper_style()

    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.axis("off")

    labels = [
        "Quantum\nPath Integral",
        "Partition\nFunction",
        "Fokker-\nPlanck",
        "Langevin\nDynamics",
        "SGD",
    ]
    arrows = [
        "Wick\nrotation",
        "continuous\nlimit",
        "discretize",
        "stochastic\ngradient",
    ]

    n = len(labels)
    for i, label in enumerate(labels):
        x = i / (n - 1)
        ax.text(x, 0.5, label, ha="center", va="center", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#4a9eff20",
                         edgecolor="#4a9eff", linewidth=0.5))

    for i, arrow_label in enumerate(arrows):
        x1 = i / (n - 1) + 0.06
        x2 = (i + 1) / (n - 1) - 0.06
        ax.annotate("", xy=(x2, 0.5), xytext=(x1, 0.5),
                    arrowprops=dict(arrowstyle="->", color="#4a9eff", lw=0.8))
        ax.text((x1 + x2) / 2, 0.2, arrow_label, ha="center", va="center",
                fontsize=5, color="#9898b0")

    path = str(OUTPUT_DIR / "theory_chain.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
