"""LaTeX generator for the Thermodynamic Darwinism paper.

Converts theory schema objects into publication-quality LaTeX using
REVTeX formatting suitable for Physical Review.
"""

from __future__ import annotations

from src.core.paper_schema import PaperOutline, Section
from src.core.theory_schema import Axiom, Derivation, Prediction, TheoryState

PREAMBLE = r"""\documentclass[aps,prl,twocolumn,superscriptaddress]{revtex4-2}

\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{physics}

\begin{document}

\title{Thermodynamic Darwinism: The Born Rule as Emergent Gibbs Weighting \\
       in Energy-Constrained Many-Worlds}

\author{Muverse Collaboration}
\affiliation{Muverse Agentic Theory Development Platform}

\date{\today}
"""

POSTAMBLE = r"""
\end{document}
"""


def generate_abstract(theory: TheoryState) -> str:
    """Generate the abstract from the theory's key prediction."""
    return r"""\begin{abstract}
We propose a framework in which the Born rule of quantum mechanics
emerges as a thermodynamic consequence of finite energy constraints
on the Many-Worlds branching structure. Under Wick rotation, the
MWI path integral becomes a Boltzmann-weighted partition function
over branches, with high-action branches exponentially suppressed.
The key prediction is that branch probabilities are
temperature-dependent, recovering $|\psi|^2$ exactly only in the
zero-temperature limit, with measurable deviations scaling as
$\exp(-S_E / k_B T)$. We present computational evidence from
three simulations: a branch ensemble under Boltzmann constraint,
a neural network analog model, and quantum Langevin dynamics.
This framework unifies elements of Quantum Darwinism, the Free
Energy Principle, and the established mathematical chain from
path integrals through Fokker-Planck equations to stochastic
gradient descent.
\end{abstract}

\maketitle
"""


def axiom_to_latex(axiom: Axiom) -> str:
    """Convert an Axiom to a LaTeX paragraph."""
    lines = [
        f"\\textbf{{Axiom {axiom.label}}} ({axiom.status.value}): {axiom.statement}",
    ]
    if axiom.formal_expression:
        lines.append(f"\\begin{{equation}}\n{axiom.formal_expression}\n\\end{{equation}}")
    return "\n".join(lines)


def derivation_to_latex(derivation: Derivation) -> str:
    """Convert a Derivation to a LaTeX proof block."""
    lines = [
        f"\\textbf{{Derivation {derivation.label}}}: "
        f"{' $+$ '.join(derivation.premises)} $\\Rightarrow$ {derivation.conclusion}",
        "",
    ]
    for i, step in enumerate(derivation.steps, 1):
        lines.append(f"\\textit{{Step {i}}}: {step.description}")
        if step.expression:
            lines.append(f"\\begin{{equation}}\n{step.expression}\n\\end{{equation}}")
        lines.append("")

    if derivation.agent_notes:
        lines.append(f"\\textit{{Note}}: {derivation.agent_notes}")

    return "\n".join(lines)


def prediction_to_latex(prediction: Prediction) -> str:
    """Convert a Prediction to a LaTeX paragraph."""
    lines = [
        f"\\textbf{{Prediction {prediction.label}}}: {prediction.statement}",
    ]
    if prediction.quantitative_formula:
        lines.append(
            f"\\begin{{equation}}\n{prediction.quantitative_formula}\n\\end{{equation}}"
        )
    if prediction.experimental_design:
        lines.append(f"\n\\textit{{Experimental design}}: {prediction.experimental_design}")
    if prediction.discriminating_power:
        lines.append(
            f"\n\\textit{{Discriminating power}}: {prediction.discriminating_power}"
        )
    return "\n".join(lines)


def section_to_latex(section: Section) -> str:
    """Convert a Section to LaTeX."""
    if section.body_latex:
        return f"\\section{{{section.title}}}\n\\label{{sec:{section.number}}}\n\n{section.body_latex}"

    lines = [
        f"\\section{{{section.title}}}",
        f"\\label{{sec:{section.number}}}",
        "",
    ]
    for point in section.outline_points:
        lines.append(f"% TODO: {point}")
    lines.append("")
    return "\n".join(lines)


def generate_full_paper(
    theory: TheoryState,
    outline: PaperOutline,
) -> str:
    """Generate the complete LaTeX source for the paper."""
    parts = [PREAMBLE, generate_abstract(theory)]

    for section in outline.sections:
        if section.body_latex:
            parts.append(section_to_latex(section))
        elif section.number == "3":
            parts.append(f"\\section{{{section.title}}}\n\\label{{sec:3}}\n")
            for axiom in theory.axioms:
                parts.append(axiom_to_latex(axiom))
                parts.append("")
        elif section.number == "4":
            parts.append(f"\\section{{{section.title}}}\n\\label{{sec:4}}\n")
            for deriv in theory.derivations:
                parts.append(derivation_to_latex(deriv))
                parts.append("")
        elif section.number == "5":
            parts.append(f"\\section{{{section.title}}}\n\\label{{sec:5}}\n")
            for pred in theory.predictions:
                parts.append(prediction_to_latex(pred))
                parts.append("")
        else:
            parts.append(section_to_latex(section))

    parts.append(r"\bibliography{references}")
    parts.append(POSTAMBLE)

    return "\n\n".join(parts)
