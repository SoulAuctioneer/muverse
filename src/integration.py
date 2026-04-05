"""End-to-end integration: seed theory, run simulations, generate paper.

This module can be run standalone (without LLM API keys) to:
1. Seed the theory from source documents
2. Run all eight simulations
3. Generate figures from results
4. Produce the complete LaTeX paper draft
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


# ---------------------------------------------------------------------------
# Simulation runners
# ---------------------------------------------------------------------------

def run_all_simulations() -> dict:
    """Run all eight simulations and return their results keyed by sim id."""
    results: dict = {}

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

    logger.info("Running Simulation 4: Born Rule Deviation Test...")
    t0 = time.time()
    from src.simulations.sim4_born_deviation import Sim4Config, run_simulation as run_sim4
    sim4 = run_sim4(Sim4Config())
    results["sim4"] = sim4
    logger.info("  Sim 4 complete in %.1fs", time.time() - t0)

    logger.info("Running Simulation 5: Lindblad Master Equation Test...")
    t0 = time.time()
    from src.simulations.sim5_lindblad_test import Sim5Config, run_simulation as run_sim5
    sim5 = run_sim5(Sim5Config())
    results["sim5"] = sim5
    logger.info("  Sim 5 complete in %.1fs", time.time() - t0)

    logger.info("Running Simulation 6: HEOM Non-Markovian Dynamics...")
    t0 = time.time()
    try:
        from src.simulations.sim6_heom_nonmarkov import Sim6Config, run_simulation as run_sim6
        sim6 = run_sim6(Sim6Config())
        results["sim6"] = sim6
        logger.info("  Sim 6 complete in %.1fs", time.time() - t0)
    except Exception as exc:
        logger.warning("  Sim 6 failed (may require QuTiP HEOM): %s", exc)

    logger.info("Running Simulation 7: Landauer Pointer-State Test...")
    t0 = time.time()
    from src.simulations.sim7_landauer_pointer import Sim7Config, run_simulation as run_sim7
    sim7 = run_sim7(Sim7Config())
    results["sim7"] = sim7
    logger.info("  Sim 7 complete in %.1fs", time.time() - t0)

    logger.info("Running Simulation 8: Jarzynski Double-Stochasticity Test...")
    t0 = time.time()
    from src.simulations.sim8_jarzynski_test import Sim8Config, run_simulation as run_sim8
    sim8 = run_sim8(Sim8Config())
    results["sim8"] = sim8
    logger.info("  Sim 8 complete in %.1fs — unitary DS verified: %s, dissipative DS broken: %s",
                time.time() - t0, sim8.a4_verified_unitary, sim8.a4_broken_dissipative)

    return results


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------

def generate_figures(results: dict) -> list[str]:
    """Generate publication-quality figures from simulation results."""
    figures: list[str] = []

    sim1 = results.get("sim1")
    if sim1 is not None:
        figures.append(plot_sim1_kl_divergence(
            sim1.betas, sim1.kl_unconstrained, sim1.kl_constrained,
            sim1.kl_std_unconstrained, sim1.kl_std_constrained,
        ))
        logger.info("  Generated: %s", figures[-1])

    sim2 = results.get("sim2")
    if sim2 is not None:
        figures.append(plot_sim2_temperature_sweep(
            sim2.temperatures, sim2.kl_from_born, sim2.kl_from_gibbs,
        ))
        logger.info("  Generated: %s", figures[-1])

    sim3 = results.get("sim3")
    if sim3 is not None:
        figures.append(plot_sim3_populations(
            sim3.temperatures, sim3.steady_state_pops,
            sim3.gibbs_predictions, sim3.energies,
        ))
        logger.info("  Generated: %s", figures[-1])

    figures.append(plot_theory_chain())
    logger.info("  Generated: %s", figures[-1])

    return figures


# ---------------------------------------------------------------------------
# Paper generation
# ---------------------------------------------------------------------------

def generate_paper(sim_results: dict | None = None) -> str:
    """Generate the LaTeX paper source from current theory state and sim results."""
    theory = build_seed_theory()
    outline = create_default_outline()
    return generate_full_paper(theory, outline, sim_results=sim_results)


def generate_bibtex() -> str:
    """Generate the BibTeX references file."""
    citations = build_seed_citations()
    return citations_to_bibtex(citations)


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

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
    logger.info("  %d simulations completed", len(results))

    logger.info("")
    logger.info("Step 3: Generating figures...")
    figures = generate_figures(results)
    logger.info("  %d figures generated", len(figures))

    logger.info("")
    logger.info("Step 4: Generating LaTeX paper...")
    paper_tex = generate_paper(sim_results=results)
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
