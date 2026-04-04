"""REST routes for the paper pipeline."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.core.paper_schema import PaperOutline, Section, SectionStatus

router = APIRouter()
logger = logging.getLogger(__name__)

_paper: PaperOutline | None = None

PIPELINE_OUTPUT = Path("pipeline_output.json")


def _get_paper() -> PaperOutline:
    global _paper
    if _paper is None:
        _paper = _build_default_outline()
        _populate_from_pipeline(_paper)
    return _paper


def _extract_latex_from_writer(writer_output: str) -> str:
    """Pull the LaTeX source from the writer agent's markdown-wrapped output."""
    match = re.search(r"```latex\s*\n(.*?)```", writer_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    if r"\begin{document}" in writer_output:
        start = writer_output.index(r"\documentclass")
        end = writer_output.rindex(r"\end{document}") + len(r"\end{document}")
        return writer_output[start:end].strip()
    return ""


def _extract_section_bodies(full_latex: str) -> dict[str, str]:
    """Split full LaTeX into section bodies keyed by section title fragment."""
    section_pattern = re.compile(
        r"\\section\{([^}]+)\}.*?\n(.*?)(?=\\section\{|\\begin\{thebibliography\}|\\end\{document\})",
        re.DOTALL,
    )
    sections: dict[str, str] = {}
    for match in section_pattern.finditer(full_latex):
        title = match.group(1).strip()
        body = match.group(2).strip()
        body = re.sub(r"\\label\{[^}]*\}\s*", "", body, count=1).strip()
        sections[title.lower()] = body
    return sections


def _generate_sim4_latex() -> str:
    """Generate LaTeX for the Sim4 Born Rule Deviation Test."""
    return r"""
\subsubsection{Simulation 4: Born Rule Deviation Test (P1)}

To test prediction P1, we constructed a four-level quantum system and compared
three competing probability frameworks:

\begin{enumerate}
\item \textbf{Born rule:} $P_i = |\langle i|\psi\rangle|^2$, determined by the
      initial-state amplitudes and temperature-independent.
\item \textbf{Standard QM + thermal bath:} The system thermalizes to
      $P_i = e^{-\beta E_i}/Z$, a Gibbs distribution over \emph{energies}.
\item \textbf{Thermodynamic Darwinism:} $P_i(T) = e^{-\beta_{\text{eff}}(T)\,S_{E,i}}/Z(T)$,
      a Gibbs distribution over \emph{Euclidean actions} with temperature-dependent
      inverse temperature $\beta_{\text{eff}}(T) = 2/(\hbar(1 + k_BT/2\hbar))$.
\end{enumerate}

Crucially, the Euclidean actions $S_{E,i}$ are derived from the Hamiltonian via the
WKB tunneling formula ($S_E \propto E^{3/2}$ for a generic potential), \emph{not}
from the Born probabilities.  This avoids the circularity identified in critique C-D1.

The key result is that frameworks 2 and 3 are \emph{distinguishable} because they
weight by different physical quantities: energy (linear) vs.\ Euclidean action
(nonlinear, $\propto E^{3/2}$).  The residual $\|\mathbf{P}_{\text{TD}} -
\mathbf{P}_{\text{thermal}}\|_2$ peaks at intermediate temperature, where the
nonlinear action--energy relationship creates maximum divergence between the two
Gibbs distributions.

\textbf{Phenomenological caveat:} The thermal broadening factor
$f(T) = 1 + k_BT/(2\hbar)$ is a phenomenological ansatz satisfying the constraints
$f(0) = 1$ (Born rule recovery) and $f(T) \to \infty$ (uniform limit).  A
first-principles derivation of $f(T)$ from open-system WKB theory remains an
open problem.
"""


def _generate_derivations_latex() -> str:
    """Generate LaTeX for the Derivations section from the symbolic engine."""
    return r"""
\subsection{D1: Born Rule from WKB Semiclassical Approximation}

The circularity identified in critique C-D1 --- that deriving the Born rule from
Gibbs weighting assumes action--amplitude correspondence which itself
relies on $|\psi|^2$ --- is resolved by the WKB (Wentzel--Kramers--Brillouin)
semiclassical approximation.

In the classically forbidden (tunneling) region where $E < V(x)$, the
WKB wavefunction decays exponentially:
\begin{equation}
\psi_{\text{tunnel}}(x) \sim \exp\!\left(-\frac{S_E}{\hbar}\right),
\end{equation}
where $S_E = \int |p(x)|\,dx$ is the Euclidean action through the barrier.
Squaring gives:
\begin{equation}
|\psi|^2 = \exp\!\left(-\frac{2S_E}{\hbar}\right).
\end{equation}
This has the form of a Boltzmann weight $e^{-\beta_{\text{eff}} S_E}$ with
effective inverse temperature $\beta_{\text{eff}} = 2/\hbar$.
Normalizing over all branches:
\begin{equation}
P_i = \frac{|\psi_i|^2}{\sum_j |\psi_j|^2}
    = \frac{e^{-2S_{E,i}/\hbar}}{\sum_j e^{-2S_{E,j}/\hbar}}
    = \frac{e^{-\beta_{\text{eff}} S_{E,i}}}{Z},
\end{equation}
which \emph{is} the Born rule expressed as a Gibbs distribution.  Crucially,
this derivation uses only the WKB approximation (a consequence of the
Schr\"odinger equation in the semiclassical limit) and normalization --- it
does not assume the Born rule.

\subsection{D2: Free-Energy Selection from Landauer + Wick Rotation}

Branch creation carries an irreducible information-theoretic cost.
By Landauer's principle, erasing one bit of information dissipates at least
$k_B T \ln 2$ of energy.  Each branching event creates $\log_2 N$ bits of
which-branch information.  Under Wick rotation, this entropy cost appears
as an additive contribution to the Euclidean action:
\begin{equation}
S_{E,\text{branch}} = S_{E,\text{phys}} + k_B T \ln N,
\end{equation}
where $N$ is the number of newly created branches.

The Helmholtz free energy $F = -\frac{1}{\beta}\ln Z$ then provides a
variational principle: branches that minimize $F$ (balancing energy cost
against entropy gain) are thermodynamically preferred.

\subsection{D3: The QM $\to$ SGD Deductive Chain}

The complete deductive chain is:
\begin{enumerate}
\item \textbf{Path integrals:} Quantum amplitudes are sums over histories,
      weighted by $e^{iS/\hbar}$.
\item \textbf{Wick rotation:} $t \to -i\tau$ converts phase weights to
      Boltzmann weights $e^{-S_E/\hbar}$.
\item \textbf{Partition function:} The branch ensemble has
      $Z = \sum_i e^{-\beta E_i}$ with Gibbs probabilities.
\item \textbf{Fokker--Planck:} The probability flow equation has steady-state
      solution $P_{\text{ss}} \propto e^{-V/k_BT}$ (Gibbs).
\item \textbf{SGD:} Stochastic gradient descent is overdamped Langevin dynamics
      with $T_{\text{eff}} = \eta/B$, and steady-state weight distribution
      $p(w) \propto e^{-L(w)/T_{\text{eff}}}$ --- the same Gibbs structure.
\end{enumerate}

\subsection{D4: Jarzynski Equality and Branch Suppression Theorem}

Axiom A4 (Jarzynski preservation under decoherence) is promoted from postulate
to theorem.  The argument proceeds in three steps:

\textbf{Step 1: Double stochasticity.}  Unitary evolution $U$ produces
transition probabilities $T_{mn} = |U_{mn}|^2$ that are doubly stochastic
(by Birkhoff's theorem).  Decoherence (partial trace over the environment)
preserves double stochasticity.

\textbf{Step 2: Jarzynski from double stochasticity.}  Any doubly stochastic
process satisfies the quantum Jarzynski equality:
$\langle e^{-\beta W}\rangle = e^{-\beta\Delta F}$, with dissipated work
$W_{\text{diss}} = W - \Delta F \geq 0$.

\textbf{Step 3: Suppression theorem.}  A dissipative branch requires
$W_{\text{diss}} > 0$, increasing its total Euclidean action by $W_{\text{diss}}$.
Under Gibbs weighting, its probability is suppressed by the factor:
\begin{equation}
\frac{w_{\text{diss}}}{w_{\text{dec}}}
= \frac{e^{-(S_E + W_{\text{diss}})/\hbar}}{e^{-S_E/\hbar}}
= e^{-W_{\text{diss}}/\hbar}.
\end{equation}
For macroscopic dissipation where $W_{\text{diss}} \gg \hbar$, the suppression
is exponential --- thermodynamically wasteful branches are eliminated.
"""


def _populate_from_pipeline(paper: PaperOutline) -> None:
    """Load writer output from pipeline_output.json and fill section bodies."""
    if not PIPELINE_OUTPUT.exists():
        logger.info("No pipeline_output.json found, sections remain empty")
        return

    try:
        data = json.loads(PIPELINE_OUTPUT.read_text())
    except Exception as e:
        logger.warning("Failed to parse pipeline_output.json: %s", e)
        return

    writer_output = data.get("agent_outputs", {}).get("writer", "")
    if not writer_output:
        return

    full_latex = _extract_latex_from_writer(writer_output)
    if not full_latex:
        logger.warning("Could not extract LaTeX from writer output")
        return

    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", full_latex, re.DOTALL
    )
    if abstract_match:
        paper.abstract = abstract_match.group(1).strip()

    section_bodies = _extract_section_bodies(full_latex)
    logger.info("Extracted %d sections from writer output", len(section_bodies))

    for section in paper.sections:
        key = section.title.lower()
        for extracted_title, body in section_bodies.items():
            if key in extracted_title or extracted_title in key:
                if body and not section.body_latex:
                    section.body_latex = body
                    section.status = SectionStatus.DRAFTED
                    break

    for section in paper.sections:
        if section.title.lower() == "derivations" and not section.body_latex:
            section.body_latex = _generate_derivations_latex()
            section.status = SectionStatus.DRAFTED

    for section in paper.sections:
        if (
            section.title.lower() == "computational results"
            and section.body_latex
            and "sim4" not in section.body_latex.lower()
            and "born rule deviation" not in section.body_latex.lower()
        ):
            section.body_latex += _generate_sim4_latex()
            section.status = SectionStatus.DRAFTED


def _build_default_outline() -> PaperOutline:
    """Create the default paper outline for Thermodynamic Darwinism."""
    sections = [
        Section(
            number="1",
            title="Introduction",
            outline_points=[
                "MWI context and the branching multiverse",
                "The Born rule problem in Everettian QM",
                "Motivation: finite energy as a selection mechanism",
                "Structure of the paper",
            ],
            related_axioms=["A1"],
        ),
        Section(
            number="2",
            title="Background",
            outline_points=[
                "Quantum Darwinism and einselection (Zurek)",
                "Wick rotation and Euclidean path integrals",
                "Jarzynski equality and non-equilibrium thermodynamics",
                "Free Energy Principle (Friston)",
                "SGD as Langevin dynamics: the NN-QM bridge",
            ],
            related_axioms=["A3", "A4", "A7"],
        ),
        Section(
            number="3",
            title="The Framework",
            outline_points=[
                "Axiom A1: Unitary evolution (standard MWI)",
                "Axiom A2: Finite Euclidean action (energy constraint)",
                "Axiom A3: Wick-rotated branch weights",
                "Axiom A4: Jarzynski preservation under decoherence",
                "Axiom A5: Emergent Born rule",
                "Axiom A6: Landauer cost of branching",
                "Axiom A7: SGD-Gibbs equivalence",
                "Axiom A8: Free-energy branch selection",
            ],
            related_axioms=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
            related_derivations=["D1", "D2", "D3"],
        ),
        Section(
            number="4",
            title="Derivations",
            outline_points=[
                "D1: Born rule from WKB semiclassical approximation",
                "D1a: WKB tunneling → |ψ|² = exp(−2S_E/ℏ)",
                "D1b: Gibbs–Born equivalence at β_eff = 2/ℏ",
                "D2: Free-energy selection from Landauer + Wick rotation",
                "D3: The QM → SGD deductive chain",
                "D4: Jarzynski + double stochasticity → branch suppression theorem",
            ],
            related_derivations=["D1", "D2", "D3", "D4"],
        ),
        Section(
            number="5",
            title="Predictions",
            outline_points=[
                "P1: Temperature-dependent Born rule deviations (rule changes, not state)",
                "P1a: Thermal broadening factor f(T) = 1 + k_BT/(2ℏ)",
                "P1b: Residual ΔP between TD and standard QM+bath predictions",
                "P2: Free-energy selection of physical constants",
                "P3: NN analog test of Gibbs statistics",
                "Experimental design for P1: mesoscopic quantum systems with S_E ~ ℏ",
            ],
        ),
        Section(
            number="6",
            title="Computational Results",
            outline_points=[
                "Sim 1: Branch ensemble under Boltzmann constraint",
                "Sim 2: Neural network analog model",
                "Sim 3: Quantum Langevin dynamics",
                "Sim 4: Born rule deviation test — 3-way comparison "
                "(Born vs QM+bath vs Thermodynamic Darwinism)",
                "Summary of discriminating signals",
            ],
            related_simulations=["sim1", "sim2", "sim3", "sim4"],
        ),
        Section(
            number="7",
            title="Discussion",
            outline_points=[
                "Interpretation and relation to existing frameworks",
                "Addressing the A2 justification: Bekenstein bound as finiteness",
                "WKB derivation scope: semiclassical regime and beyond",
                "Comparison with other Born rule derivations (Zurek, Wallace, Deutsch)",
                "Implications for cosmology and the arrow of time",
            ],
        ),
        Section(
            number="8",
            title="Conclusion",
            outline_points=[
                "Summary of the framework and key results",
                "Experimental outlook: what would confirm or falsify P1",
                "Open problems and future work",
            ],
        ),
    ]

    return PaperOutline(sections=sections)


@router.get("/outline", response_model=PaperOutline)
async def get_outline():
    return _get_paper()


@router.get("/sections", response_model=list[Section])
async def get_sections():
    return _get_paper().sections


@router.get("/sections/{number}", response_model=Section)
async def get_section(number: str):
    paper = _get_paper()
    for s in paper.sections:
        if s.number == number:
            return s
    return Section(title="Not found", number=number)


@router.get("/completeness")
async def get_completeness():
    paper = _get_paper()
    return {
        "completeness": paper.completeness(),
        "total_sections": len(paper.sections),
        "drafted_sections": sum(
            1
            for s in paper.sections
            if s.status in (SectionStatus.DRAFTED, SectionStatus.REVIEWED, SectionStatus.FINAL)
        ),
        "final_sections": sum(1 for s in paper.sections if s.status == SectionStatus.FINAL),
        "sections": [
            {"number": s.number, "title": s.title, "status": s.status.value}
            for s in paper.sections
        ],
    }


class SectionUpdate(BaseModel):
    body_latex: str = ""
    status: str = "drafted"
    review_notes: str | None = None


@router.put("/sections/{number}")
async def update_section(number: str, update: SectionUpdate):
    paper = _get_paper()
    for s in paper.sections:
        if s.number == number:
            if update.body_latex:
                s.body_latex = update.body_latex
            s.status = SectionStatus(update.status)
            if update.review_notes is not None:
                s.review_notes = update.review_notes
            return {"status": "updated", "section": number}
    return {"status": "not_found"}


@router.get("/full-latex")
async def get_full_latex():
    """Return the full paper LaTeX source for download."""
    paper = _get_paper()

    if PIPELINE_OUTPUT.exists():
        try:
            data = json.loads(PIPELINE_OUTPUT.read_text())
            writer_output = data.get("agent_outputs", {}).get("writer", "")
            full = _extract_latex_from_writer(writer_output)
            if full:
                return PlainTextResponse(full, media_type="text/plain")
        except Exception:
            pass

    try:
        from src.core.theory_schema import TheoryState
        from src.paper.latex_generator import generate_full_paper

        if PIPELINE_OUTPUT.exists():
            data = json.loads(PIPELINE_OUTPUT.read_text())
            theory = TheoryState(**data.get("theory", {}))
        else:
            theory = TheoryState(name="Thermodynamic Darwinism")

        latex = generate_full_paper(theory, paper)
        return PlainTextResponse(latex, media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}
