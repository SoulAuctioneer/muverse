"""End-to-end integration: seed theory, run simulations, generate paper.

This module can be run standalone (without LLM API keys) to:
1. Seed the theory from source documents
2. Run all three simulations
3. Generate figures from results
4. Produce the initial LaTeX paper draft
5. Generate the BibTeX citations file

For the full agentic pipeline (requiring LLM keys), use:
  from src.agents.orchestrator import run_full_pipeline
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from src.core.seed_theory import build_seed_theory
from src.paper.citations import build_seed_citations, citations_to_bibtex
from src.paper.figures import (
    plot_sim1_kl_divergence,
    plot_sim2_temperature_sweep,
    plot_sim3_populations,
    plot_theory_chain,
)
from src.paper.latex_generator import generate_full_paper
from src.paper.outline import create_default_outline

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

OUTPUT_DIR = Path("output")


def run_all_simulations() -> dict:
    """Run all three simulations and return their results."""
    results = {}

    logger.info("Running Simulation 1: Branch Ensemble under Boltzmann Constraint...")
    t0 = time.time()
    from src.simulations.sim1_branch_boltzmann import Sim1Config, run_simulation as run_sim1
    sim1 = run_sim1(Sim1Config(n_trials=10, n_beta_points=30))
    results["sim1"] = sim1
    logger.info("  Sim 1 complete in %.1fs — best constrained KL: %.4f",
                time.time() - t0, float(min(sim1.kl_constrained)))

    logger.info("Running Simulation 2: Neural Network Analog Model...")
    t0 = time.time()
    from src.simulations.sim2_nn_analog import Sim2Config, run_simulation as run_sim2
    sim2 = run_sim2(Sim2Config(n_trials=5))
    results["sim2"] = sim2
    logger.info("  Sim 2 complete in %.1fs", time.time() - t0)

    logger.info("Running Simulation 3: Quantum Langevin Dynamics...")
    t0 = time.time()
    from src.simulations.sim3_quantum_langevin import Sim3Config, run_simulation as run_sim3
    sim3 = run_sim3(Sim3Config(n_trials=3, t_max=50.0))
    results["sim3"] = sim3
    logger.info("  Sim 3 complete in %.1fs", time.time() - t0)

    return results


def generate_figures(results: dict) -> list[str]:
    """Generate all paper figures from simulation results."""
    figures = []

    sim1 = results["sim1"]
    figures.append(plot_sim1_kl_divergence(
        sim1.betas, sim1.kl_unconstrained, sim1.kl_constrained,
        sim1.kl_std_unconstrained, sim1.kl_std_constrained,
    ))
    logger.info("  Generated: %s", figures[-1])

    sim2 = results["sim2"]
    figures.append(plot_sim2_temperature_sweep(
        sim2.temperatures, sim2.kl_from_born, sim2.kl_from_gibbs,
    ))
    logger.info("  Generated: %s", figures[-1])

    sim3 = results["sim3"]
    figures.append(plot_sim3_populations(
        sim3.temperatures, sim3.steady_state_pops,
        sim3.gibbs_predictions, sim3.energies,
    ))
    logger.info("  Generated: %s", figures[-1])

    figures.append(plot_theory_chain())
    logger.info("  Generated: %s", figures[-1])

    return figures


def generate_paper() -> str:
    """Generate the LaTeX paper source."""
    theory = build_seed_theory()
    outline = create_default_outline()
    return generate_full_paper(theory, outline)


def generate_bibtex() -> str:
    """Generate the BibTeX references file."""
    citations = build_seed_citations()
    return citations_to_bibtex(citations)


def run_full_integration():
    """Execute the complete integration pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=== Muverse Integration Pipeline ===")
    logger.info("")

    logger.info("Step 1: Seeding theory from source documents...")
    theory = build_seed_theory()
    logger.info("  Theory v%d: %d axioms, %d derivations, %d predictions, %d critiques",
                theory.version, len(theory.axioms), len(theory.derivations),
                len(theory.predictions), len(theory.critiques))

    logger.info("")
    logger.info("Step 2: Running simulations...")
    results = run_all_simulations()

    logger.info("")
    logger.info("Step 3: Generating figures...")
    figures = generate_figures(results)
    logger.info("  %d figures generated", len(figures))

    logger.info("")
    logger.info("Step 4: Generating LaTeX paper...")
    paper_tex = generate_paper()
    tex_path = OUTPUT_DIR / "thermodynamic_darwinism.tex"
    tex_path.write_text(paper_tex)
    logger.info("  Paper written to %s (%d chars)", tex_path, len(paper_tex))

    logger.info("")
    logger.info("Step 5: Generating BibTeX references...")
    bibtex = generate_bibtex()
    bib_path = OUTPUT_DIR / "references.bib"
    bib_path.write_text(bibtex)
    logger.info("  References written to %s (%d citations)", bib_path, bibtex.count("@"))

    logger.info("")
    logger.info("=== Integration complete ===")
    logger.info("Output directory: %s", OUTPUT_DIR.resolve())

    return {
        "theory": theory,
        "results": results,
        "figures": figures,
        "paper_path": str(tex_path),
        "bib_path": str(bib_path),
    }


if __name__ == "__main__":
    run_full_integration()
