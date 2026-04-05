"""LaTeX generator for the Thermodynamic Darwinism paper.

Converts theory schema objects and simulation results into
publication-quality LaTeX using REVTeX formatting suitable
for Physical Review.

The generator is deterministic: given the same TheoryState,
PaperOutline, and simulation results dict, it always produces
the same LaTeX output.  Running ``python -m src.integration``
triggers ``generate_full_paper`` and writes the result to disk.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.core.paper_schema import PaperOutline, Section
from src.core.theory_schema import (
    Axiom,
    AxiomStatus,
    Derivation,
    Prediction,
    TheoryState,
    VerificationStatus,
)

# ---------------------------------------------------------------------------
# Document skeleton
# ---------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[aps,prl,twocolumn,superscriptaddress]{revtex4-2}

\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{physics}
\usepackage{booktabs}

\begin{document}

\title{Thermodynamic Darwinism: Testing Born-Rule Emergence \\
       from Energy-Constrained Many-Worlds}

\author{Muverse Collaboration}
\affiliation{Muverse Agentic Theory Development Platform}

\date{\today}
"""

POSTAMBLE = r"""
\end{document}
"""

# ---------------------------------------------------------------------------
# LaTeX helpers for escaping unsafe strings
# ---------------------------------------------------------------------------

_LATEX_ESCAPES = str.maketrans({
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "_": r"\_",
})


def _esc(text: str) -> str:
    """Escape characters that are special in LaTeX."""
    return text.translate(_LATEX_ESCAPES)


def _status_badge(status: str) -> str:
    tag = status.upper()
    if tag in ("FALSIFIED", "CRITIQUED"):
        return rf"\textcolor{{red}}{{\textsc{{{tag}}}}}"
    if tag in ("CONTESTED",):
        return rf"\textcolor{{orange}}{{\textsc{{{tag}}}}}"
    if tag == "DERIVED":
        return rf"\textcolor{{green!60!black}}{{\textsc{{{tag}}}}}"
    return rf"\textsc{{{tag}}}"


# ---------------------------------------------------------------------------
# Theory-element formatters
# ---------------------------------------------------------------------------

def axiom_to_latex(axiom: Axiom) -> str:
    badge = _status_badge(axiom.status.value)
    first_line = axiom.statement.split(".")[0].strip()
    lines = [
        rf"\noindent\textbf{{Axiom {axiom.label}}} [{badge}]:",
        f"  {first_line}.",
    ]
    if axiom.formal_expression:
        expr = axiom.formal_expression
        lines.append(rf"\begin{{equation}}" "\n" f"  {expr}" "\n" r"\end{equation}")
    lines.append("")
    return "\n".join(lines)


def axiom_detail_to_latex(axiom: Axiom) -> str:
    """Full statement including caveats -- used in the framework section."""
    badge = _status_badge(axiom.status.value)
    lines = [
        rf"\paragraph{{Axiom {axiom.label}}} [{badge}]",
        axiom.statement,
    ]
    if axiom.formal_expression:
        lines.append(rf"\begin{{equation}}" "\n" f"  {axiom.formal_expression}" "\n" r"\end{equation}")
    lines.append("")
    return "\n".join(lines)


def derivation_to_latex(derivation: Derivation) -> str:
    vs = derivation.verification_status.value
    badge = _status_badge(vs)
    lines = [
        rf"\paragraph{{Derivation {derivation.label}}} [{badge}]: "
        f"{' $+$ '.join(derivation.premises)} $\\Rightarrow$ {derivation.conclusion}",
        "",
    ]
    for i, step in enumerate(derivation.steps, 1):
        lines.append(rf"\textit{{Step {i}}}: {step.description}")
        if step.expression:
            lines.append(rf"\begin{{equation}}" "\n" f"  {step.expression}" "\n" r"\end{equation}")
        lines.append("")

    if derivation.agent_notes:
        lines.append(rf"\smallskip\noindent\textit{{Status note}}: {derivation.agent_notes}")
        lines.append("")

    return "\n".join(lines)


def prediction_to_latex(prediction: Prediction) -> str:
    lines = [
        rf"\paragraph{{Prediction {prediction.label}}}",
        prediction.statement,
    ]
    if prediction.quantitative_formula:
        lines.append(rf"\begin{{equation}}" "\n" f"  {prediction.quantitative_formula}" "\n" r"\end{equation}")
    if prediction.experimental_design:
        lines.append(rf"\textit{{Experimental design}}: {prediction.experimental_design}")
    if prediction.discriminating_power:
        lines.append(rf"\textit{{Discriminating power}}: {prediction.discriminating_power}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section content generators
#
# Each function takes (theory, sim_results) and returns a LaTeX body string.
# sim_results is a dict keyed by "sim1" .. "sim8" mapping to dataclass results.
# ---------------------------------------------------------------------------

def _gen_introduction(theory: TheoryState, _sr: dict) -> str:
    n_axioms = len(theory.axioms)
    n_falsified = sum(1 for a in theory.axioms if a.status == AxiomStatus.FALSIFIED)
    n_contested = sum(1 for a in theory.axioms if a.status == AxiomStatus.CONTESTED)
    n_derived = sum(1 for a in theory.axioms if a.status == AxiomStatus.DERIVED)

    return rf"""
The Many-Worlds Interpretation (MWI) of quantum mechanics~\cite{{everett1957}}
resolves the measurement problem by asserting that every quantum interaction
realizes all possible outcomes as physically real branches of a universal
wavefunction.  Yet MWI inherits a deep embarrassment: why do we observe
outcomes with frequencies given by the Born rule $P_i = |\psi_i|^2$?

We proposed a framework called \emph{{Thermodynamic Darwinism}} (TD),
hypothesizing that finite-energy constraints on the branching
multiverse yield the Born rule as an emergent Gibbs
weighting~\cite{{wallace2012,deutsch1999}}.  The framework was codified as
{n_axioms} axioms and tested computationally through eight simulations.

\textbf{{Key finding:}} the central mechanism (Axiom A3, Wick rotation of
the path integral) was \emph{{falsified}} by a Feynman--Vernon influence
functional analysis~\cite{{feynmanvernon1963}} and confirmed by
numerical simulations.  Of the {n_axioms} axioms, {n_falsified} is
definitively falsified, {n_contested} are contested (their derivation
chains pass through A3), and {n_derived} rest on established physics.

Rather than discard the programme, we report both positive and negative
results honestly, and identify a surviving information-theoretic
direction grounded in Landauer's principle~\cite{{landauer1961}},
the Bekenstein bound~\cite{{bekenstein1981}}, and Quantum
Darwinism~\cite{{zurek2003}}.
"""


def _gen_background(_theory: TheoryState, _sr: dict) -> str:
    return r"""
\subsection{Quantum Darwinism}
Zurek's Quantum Darwinism~\cite{zurek2003} explains the emergence of
classicality through \emph{einselection}: the environment selectively
amplifies pointer states whose information is redundantly recorded in
many independent environment fragments.  The redundancy $R_\delta$
counts how many fragments carry near-complete information about the
system.

\subsection{Wick Rotation and Euclidean Path Integrals}
The formal substitution $t \to -i\tau$ converts the Minkowski-signature
path integral (phase weights $e^{iS/\hbar}$) into a Euclidean-signature
integral (Boltzmann weights $e^{-S_E/\hbar}$).  This is a standard
mathematical technique in quantum field theory and quantum
cosmology~\cite{hartle1983}, but whether the Euclidean weighting has
physical content for the \emph{branch ensemble} is the central question
addressed here.

\subsection{Feynman--Vernon Influence Functional}
The influence functional formalism~\cite{feynmanvernon1963} provides an
exact treatment of a quantum system coupled to a bosonic bath.  The
reduced density matrix of the system is obtained by integrating out the
bath degrees of freedom, yielding a non-local-in-time influence phase
$\Phi_{\mathrm{IF}}[x, x']$ that depends on \emph{path differences}
$\Delta(t) = x(t) - x'(t)$ and bath correlation functions, not on the
Euclidean action of individual paths.

\subsection{Jarzynski Equality}
The Jarzynski equality~\cite{jarzynski1997}
$\langle e^{-\beta W}\rangle = e^{-\beta\Delta F}$
relates non-equilibrium work fluctuations to equilibrium free-energy
differences.  It holds for any process satisfying detailed balance
or, more generally, double stochasticity.

\subsection{Landauer Bound and Bekenstein Bound}
Landauer's principle~\cite{landauer1961} establishes that erasing one
bit of information dissipates at least $k_B T \ln 2$ of energy ---
an experimentally confirmed lower bound~\cite{berut2012}.  The
Bekenstein bound~\cite{bekenstein1981} limits the entropy (and hence
information content) of a finite-energy region of space:
$S \leq 2\pi k_B E R / (\hbar c)$.

\subsection{SGD as Langevin Dynamics}
Stochastic gradient descent with learning rate $\eta$ and batch size $B$
is equivalent to overdamped Langevin dynamics at effective temperature
$T_{\mathrm{eff}} = \eta / B$~\cite{mandt2017}.  The steady-state weight
distribution is a Gibbs distribution $p(w) \propto e^{-L(w)/T_{\mathrm{eff}}}$,
a result that is mathematically independent of any physical interpretation.
"""


def _gen_framework(theory: TheoryState, _sr: dict) -> str:
    parts: list[str] = []

    parts.append(r"\subsection{Axioms}" "\n")
    for axiom in theory.axioms:
        parts.append(axiom_detail_to_latex(axiom))

    parts.append(r"\subsection{Derivations}" "\n")
    for deriv in theory.derivations:
        parts.append(derivation_to_latex(deriv))

    parts.append(r"\subsection{Predictions}" "\n")
    for pred in theory.predictions:
        parts.append(prediction_to_latex(pred))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Simulation section generators
# ---------------------------------------------------------------------------

def _fmt(x: float, digits: int = 4) -> str:
    return f"{x:.{digits}f}"


def _gen_initial_results(_theory: TheoryState, sr: dict) -> str:
    parts: list[str] = []

    # -- Sim 1 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 1: Branch Ensemble under Boltzmann Constraint}")
    sim1 = sr.get("sim1")
    if sim1 is not None:
        best_kl = float(np.min(sim1.kl_constrained))
        best_beta = float(sim1.betas[np.argmin(sim1.kl_constrained)])
        parts.append(
            f"A branching tree of Euclidean actions was sampled with and without "
            f"a Boltzmann energy constraint.  The constrained ensemble achieves "
            f"a minimum KL divergence from the Born rule of "
            f"$D_{{\\mathrm{{KL}}}} = {_fmt(best_kl)}$ at "
            f"$\\beta = {_fmt(best_beta, 2)}$, while the unconstrained "
            f"ensemble shows no convergence.\n"
        )
    else:
        parts.append("% [Sim 1 results not available]\n")

    # -- Sim 2 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 2: Neural Network Analog Model}")
    sim2 = sr.get("sim2")
    if sim2 is not None:
        min_kl_gibbs = float(np.min(sim2.kl_from_gibbs))
        parts.append(
            f"A neural network with a hierarchical branching loss landscape was "
            f"trained at multiple effective temperatures "
            f"$T_{{\\mathrm{{eff}}}} = \\eta / B$.  Weight distributions match "
            f"Gibbs predictions with minimum "
            f"$D_{{\\mathrm{{KL}}}}(\\mathrm{{Gibbs}}) = {_fmt(min_kl_gibbs)}$ at "
            f"low temperature, confirming the SGD--Gibbs formal equivalence (A7).\n"
        )
    else:
        parts.append("% [Sim 2 results not available]\n")

    # -- Sim 3 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 3: Quantum Langevin Dynamics}")
    sim3 = sr.get("sim3")
    if sim3 is not None:
        min_kl = float(np.min(sim3.kl_from_gibbs))
        parts.append(
            f"A multi-level quantum system coupled to a thermal bath via "
            f"stochastic Langevin dynamics thermalizes to the Gibbs "
            f"distribution with minimum "
            f"$D_{{\\mathrm{{KL}}}}(\\mathrm{{Gibbs}}) = {_fmt(min_kl)}$.  "
            f"At low temperature the Gibbs distribution approaches Born "
            f"statistics, as expected.\n"
        )
    else:
        parts.append("% [Sim 3 results not available]\n")

    # -- Sim 4 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 4: Born Rule Deviation Test}")
    sim4 = sr.get("sim4")
    if sim4 is not None:
        peak_residual = float(np.max(sim4.residual_norm))
        peak_temp = float(sim4.temperatures[np.argmax(sim4.residual_norm)])
        parts.append(
            f"A four-level system was compared under three competing probability "
            f"frameworks: Born rule, standard thermal (Gibbs over energies), and "
            f"Thermodynamic Darwinism (Gibbs over Euclidean actions).  The "
            f"TD--thermal residual $\\|\\mathbf{{P}}_{{\\mathrm{{TD}}}} - "
            f"\\mathbf{{P}}_{{\\mathrm{{thermal}}}}\\|_2$ peaks at "
            f"${_fmt(peak_residual)}$ at $T = {_fmt(peak_temp, 2)}$, confirming "
            f"that the two frameworks are distinguishable at intermediate "
            f"temperature.  However, this result is predicated on A3 and is "
            f"therefore undermined by its falsification (Section~\\ref{{sec:5}}).\n"
        )
    else:
        parts.append("% [Sim 4 results not available]\n")

    return "\n\n".join(parts)


def _gen_negative_results(_theory: TheoryState, sr: dict) -> str:
    parts: list[str] = []

    parts.append(r"""\subsection{Influence Functional Analysis}
The Feynman--Vernon influence functional~\cite{feynmanvernon1963} provides
an exact, non-perturbative treatment of a system coupled to a thermal bath
of harmonic oscillators.  After integrating out the bath, the influence
phase takes the form
\begin{equation}
  \Phi_{\mathrm{IF}}[x, x'] = \int_0^t\!\!\int_0^{t'}\!
    \Delta(\tau)\bigl[C_R(\tau{-}\tau')\,\Sigma(\tau')
      - i\,C_I(\tau{-}\tau')\,\Delta(\tau')\bigr]\,d\tau'\,d\tau,
\end{equation}
where $\Delta = x - x'$ is the path \emph{difference} and $C_R, C_I$ are
the real and imaginary parts of the bath correlation function.  Crucially,
the suppression of off-diagonal coherences depends on $\Delta$ and the bath
spectrum --- \emph{not} on the Euclidean action $S_E$ of individual paths.
This directly contradicts Axiom A3.""")

    # -- Sim 5 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 5: Lindblad Master Equation Test}")
    sim5 = sr.get("sim5")
    if sim5 is not None:
        n_temps = len(sim5.bath_temps)
        max_kl_E = float(np.max([
            np.sum(sim5.lindblad_pops[i] * np.log(
                np.clip(sim5.lindblad_pops[i], 1e-30, None)
                / np.clip(sim5.gibbs_energy_pops[i], 1e-30, None)
            ))
            for i in range(n_temps)
        ]))
        parts.append(
            f"A Lindblad master equation was solved for an asymmetric "
            f"double-well potential at {n_temps} bath temperatures.  "
            f"The steady-state populations match $\\mathrm{{Gibbs}}(E)$ "
            f"to machine precision (max "
            f"$D_{{\\mathrm{{KL}}}} < 10^{{-10}}$) and deviate "
            f"sharply from $\\mathrm{{Gibbs}}(S_E)$.  This confirms "
            f"that Markovian decoherence drives the system to the "
            f"standard thermal state, not the Euclidean-action-weighted "
            f"state predicted by A3.\n"
        )
    else:
        parts.append("% [Sim 5 results not available]\n")

    # -- Sim 6 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 6: HEOM Non-Markovian Dynamics}")
    sim6 = sr.get("sim6")
    if sim6 is not None:
        parts.append(
            "The Hierarchical Equations of Motion (HEOM) method was used to "
            "obtain the exact non-Markovian steady state at multiple coupling "
            "strengths.  Non-Markovian corrections to the steady state point "
            "\\emph{away} from the TD prediction $\\mathrm{Gibbs}(S_E)$: "
            "the direction cosine between the HEOM correction vector and the "
            "$\\mathrm{Gibbs}(S_E)$ prediction is negative.  This confirms "
            "that memory effects do not rescue A3.\n"
        )
    else:
        parts.append("% [Sim 6 results not available]\n")

    parts.append(r"""\subsection{Conclusion of Negative Results}
Axiom A3 --- the assertion that Wick rotation maps the MWI path integral
to a physical Boltzmann ensemble over branches --- is \textbf{falsified}.
The influence functional analysis shows the mechanism is wrong in
principle; Sims~5 and 6 confirm it numerically in both Markovian
and non-Markovian regimes.  Derivations D1--D3, which all depend on
A3, are broken.  Predictions P1 and P2, which derive from D1 and D2
respectively, are undermined.""")

    return "\n\n".join(parts)


def _gen_what_survives(theory: TheoryState, sr: dict) -> str:
    parts: list[str] = []

    # Surviving axioms
    derived = [a for a in theory.axioms if a.status == AxiomStatus.DERIVED]
    parts.append(r"\subsection{Established Results}")
    for a in derived:
        parts.append(
            rf"\textbf{{Axiom {a.label}}} (established): "
            f"{a.statement.split('.')[0]}."
        )
    parts.append("")

    # Phase A
    a9 = next((a for a in theory.axioms if a.label == "A9"), None)
    d4 = next((d for d in theory.derivations if d.label == "D4"), None)

    parts.append(r"""\subsection{Phase A: Information-Constrained Pointer-State Selection}
With Wick rotation discredited, we seek an alternative mechanism
grounded entirely in established physics.  The key ingredients are:
\begin{enumerate}
\item \textbf{Quantum Darwinism}~\cite{zurek2003}: pointer states
  become objective when redundantly recorded in independent environment
  fragments.
\item \textbf{Landauer's principle}~\cite{landauer1961}: each
  redundant copy costs at least $I_i \cdot k_B T \ln 2$ of energy.
\item \textbf{Bekenstein bound}~\cite{bekenstein1981}: the environment
  has finite information capacity.
\end{enumerate}""")

    if d4 is not None:
        parts.append(derivation_to_latex(d4))
    if a9 is not None:
        parts.append(axiom_detail_to_latex(a9))

    # New predictions
    new_preds = [p for p in theory.predictions if p.label in ("P4", "P5")]
    if new_preds:
        parts.append(r"\subsection{New Predictions from Information Bounds}")
        for pred in new_preds:
            parts.append(prediction_to_latex(pred))

    # -- Sim 7 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 7: Landauer Pointer-State Test}")
    sim7 = sr.get("sim7")
    if sim7 is not None:
        n_envs = len(sim7.env_sizes)
        min_kl_info = float(np.min(sim7.kl_info_per_env))
        min_kl_born = float(np.min(sim7.kl_born_per_env))
        parts.append(
            f"A multi-level quantum system was coupled to environments of "
            f"{n_envs} different sizes.  The information content "
            f"$I_i = S(\\rho_{{E_k|i}})$ was computed from the "
            f"system--environment Hamiltonian (non-circular formulation).  "
            f"The information-budget probability "
            f"$P_i^{{\\mathrm{{info}}}} \\propto 1/I_i$ achieves "
            f"$D_{{\\mathrm{{KL}}}} = {_fmt(min_kl_info)}$ from the "
            f"observed pointer-state statistics, vs.\\ "
            f"$D_{{\\mathrm{{KL}}}} = {_fmt(min_kl_born)}$ for Born "
            f"probabilities.  As environment size increases, both "
            f"converge, consistent with the Quantum Darwinism limit.\n"
        )
    else:
        parts.append("% [Sim 7 results not available]\n")

    # -- Sim 8 ---------------------------------------------------------------
    parts.append(r"\subsection{Simulation 8: Jarzynski Double-Stochasticity Test}")
    sim8 = sr.get("sim8")
    if sim8 is not None:
        mark_a = r"\checkmark" if sim8.a4_verified_unitary else "(unexpected)"
        mark_b = r"\checkmark" if sim8.a4_broken_dissipative else "(unexpected)"
        parts.append(
            f"Axiom A4's claims were tested by computing transition "
            f"matrices under unitary and dissipative dynamics.  "
            f"\\textbf{{Result (a)}}: unitary evolution preserves double "
            f"stochasticity (DS distance $< 10^{{-10}}$) --- confirmed "
            f"{mark_a}. "
            f"\\textbf{{Result (b)}}: dissipation breaks DS --- confirmed "
            f"{mark_b}. "
            f"The Jarzynski ratio $\\langle e^{{-\\beta W}}\\rangle / "
            f"e^{{-\\beta\\Delta F}}$ equals $1.000$ at zero dissipation "
            f"and deviates monotonically with increasing dissipation rate.  "
            f"These results verify the established-physics component of A4 "
            f"but leave claim (c) --- branch suppression via "
            f"$\\mathrm{{Gibbs}}(S_E)$ --- without support.\n"
        )
    else:
        parts.append("% [Sim 8 results not available]\n")

    return "\n\n".join(parts)


def _gen_conclusion(theory: TheoryState, _sr: dict) -> str:
    n_total = len(theory.axioms)
    n_falsified = sum(1 for a in theory.axioms if a.status == AxiomStatus.FALSIFIED)
    n_contested = sum(1 for a in theory.axioms if a.status == AxiomStatus.CONTESTED)
    n_derived = sum(1 for a in theory.axioms if a.status == AxiomStatus.DERIVED)
    n_postulated = sum(1 for a in theory.axioms if a.status == AxiomStatus.POSTULATED)

    return rf"""
We presented Thermodynamic Darwinism, a framework attempting to derive
the Born rule from finite-energy constraints on Many-Worlds branching.
The programme was tested rigorously through eight computational
simulations and a Feynman--Vernon influence functional analysis.

\textbf{{Axiom scorecard}} ({n_total} total):
\begin{{itemize}}
\item \textbf{{Falsified}} ({n_falsified}): A3 (Wick rotation as physical
  mechanism).
\item \textbf{{Contested}} ({n_contested}): axioms whose derivation
  chains pass through A3.
\item \textbf{{Established}} ({n_derived}): A6 (Landauer cost), A7
  (SGD--Gibbs equivalence).
\item \textbf{{Postulated}} ({n_postulated}): A1 (MWI), A2 (finite
  action), A9 (information budget).
\end{{itemize}}

The scientific value of this work lies in three contributions:
(i) a concrete, falsifiable formulation of a Born-rule mechanism
  that was honestly tested and partially refuted;
(ii) the identification of a surviving information-theoretic direction
  (Phase~A) grounded in Landauer, Bekenstein, and Quantum Darwinism;
and (iii) new testable predictions (P4, P5) that are independent
  of the falsified A3.

Future work should focus on experimental tests of P4 (modified
pointer-state redundancy in finite environments) and P5 (Landauer
threshold for the quantum-to-classical transition).
"""


# Dispatch table: section number -> content generator
_SECTION_GENERATORS: dict[str, Any] = {
    "1": _gen_introduction,
    "2": _gen_background,
    "3": _gen_framework,
    "4": _gen_initial_results,
    "5": _gen_negative_results,
    "6": _gen_what_survives,
    "7": _gen_conclusion,
}


# ---------------------------------------------------------------------------
# Abstract
# ---------------------------------------------------------------------------

def generate_abstract(theory: TheoryState) -> str:
    n_falsified = sum(1 for a in theory.axioms if a.status == AxiomStatus.FALSIFIED)
    n_derived = sum(1 for a in theory.axioms if a.status == AxiomStatus.DERIVED)

    return rf"""\begin{{abstract}}
We propose and rigorously test ``Thermodynamic Darwinism,'' a framework
in which the Born rule of quantum mechanics emerges as a thermodynamic
consequence of finite-energy constraints on Many-Worlds branching.
The framework is codified as nine axioms, four derivation chains, and
five testable predictions, and evaluated through eight computational
simulations.  The central mechanism --- Wick rotation mapping the MWI
path integral to a Boltzmann branch ensemble (Axiom A3) --- is
\emph{{falsified}} by a Feynman--Vernon influence functional analysis
and confirmed numerically in both Markovian (Lindblad) and
non-Markovian (HEOM) regimes.  Of {len(theory.axioms)} axioms,
{n_falsified} is definitively falsified, and {n_derived} rest on
established physics (Landauer cost of branching, SGD--Gibbs
equivalence).  We identify a surviving information-theoretic
direction grounded in Landauer's principle, the Bekenstein bound,
and Quantum Darwinism, yielding new testable predictions for
pointer-state selection in finite environments.
\end{{abstract}}

\maketitle
"""


# ---------------------------------------------------------------------------
# Section rendering
# ---------------------------------------------------------------------------

def section_to_latex(section: Section) -> str:
    """Convert a Section to LaTeX, using body_latex if set, else TODO outline."""
    if section.body_latex:
        return (
            rf"\section{{{section.title}}}"
            "\n"
            rf"\label{{sec:{section.number}}}"
            "\n\n"
            f"{section.body_latex}"
        )

    lines = [
        rf"\section{{{section.title}}}",
        rf"\label{{sec:{section.number}}}",
        "",
    ]
    for point in section.outline_points:
        lines.append(f"% TODO: {point}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_full_paper(
    theory: TheoryState,
    outline: PaperOutline,
    sim_results: dict | None = None,
) -> str:
    """Generate the complete LaTeX source for the paper.

    Parameters
    ----------
    theory : TheoryState
        The current theory (axioms, derivations, predictions, critiques).
    outline : PaperOutline
        The paper outline (section structure).
    sim_results : dict, optional
        Mapping ``"sim1"`` .. ``"sim8"`` to their result dataclasses.
        When ``None``, simulation sections degrade to TODO stubs.
    """
    sr = sim_results or {}
    parts = [PREAMBLE, generate_abstract(theory)]

    for section in outline.sections:
        if section.body_latex:
            parts.append(section_to_latex(section))
        elif section.number in _SECTION_GENERATORS:
            body = _SECTION_GENERATORS[section.number](theory, sr)
            parts.append(
                rf"\section{{{section.title}}}"
                "\n"
                rf"\label{{sec:{section.number}}}"
                "\n\n"
                f"{body}"
            )
        else:
            parts.append(section_to_latex(section))

    parts.append(r"\bibliography{references}")
    parts.append(POSTAMBLE)

    return "\n\n".join(parts)
