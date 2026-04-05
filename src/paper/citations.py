"""Citation manager for the Thermodynamic Darwinism paper.

Seeds the BibTeX database from the source documents' references
and provides lookup/insertion utilities.
"""

from __future__ import annotations

from src.core.paper_schema import Citation


def build_seed_citations() -> list[Citation]:
    """Build the complete citation database for the v2 paper."""
    return [
        Citation(
            bibtex_key="everett1957",
            title="Relative State Formulation of Quantum Mechanics",
            authors=["Hugh Everett III"],
            year=1957,
            journal="Reviews of Modern Physics",
        ),
        Citation(
            bibtex_key="zurek2003",
            title="Quantum Darwinism",
            authors=["Wojciech H. Zurek"],
            year=2003,
            journal="Nature Physics",
        ),
        Citation(
            bibtex_key="smolin1992",
            title="Did the Universe Evolve?",
            authors=["Lee Smolin"],
            year=1992,
            journal="Classical and Quantum Gravity",
        ),
        Citation(
            bibtex_key="carroll2018",
            title=(
                "Self-Locating Uncertainty and the Origin of Probability "
                "in Everettian Quantum Mechanics"
            ),
            authors=["Charles T. Sebens", "Sean M. Carroll"],
            year=2018,
            journal="British Journal for the Philosophy of Science",
        ),
        Citation(
            bibtex_key="friston2010",
            title="The free-energy principle: a unified brain theory?",
            authors=["Karl Friston"],
            year=2010,
            journal="Nature Reviews Neuroscience",
        ),
        Citation(
            bibtex_key="england2013",
            title="Statistical physics of self-replication",
            authors=["Jeremy L. England"],
            year=2013,
            journal="The Journal of Chemical Physics",
        ),
        Citation(
            bibtex_key="vanchurin2020",
            title="The World as a Neural Network",
            authors=["Vitaly Vanchurin"],
            year=2020,
            journal="Entropy",
        ),
        Citation(
            bibtex_key="jarzynski1997",
            title="Nonequilibrium Equality for Free Energy Differences",
            authors=["Christopher Jarzynski"],
            year=1997,
            journal="Physical Review Letters",
        ),
        Citation(
            bibtex_key="landauer1961",
            title=(
                "Irreversibility and Heat Generation in the Computing Process"
            ),
            authors=["Rolf Landauer"],
            year=1961,
            journal="IBM Journal of Research and Development",
        ),
        Citation(
            bibtex_key="hartle1983",
            title="Wave function of the Universe",
            authors=["James B. Hartle", "Stephen W. Hawking"],
            year=1983,
            journal="Physical Review D",
        ),
        Citation(
            bibtex_key="saunders2010",
            title=(
                "Branch-counting in the Everett Interpretation "
                "of Quantum Mechanics"
            ),
            authors=["Simon Saunders"],
            year=2010,
            journal="Proceedings of the Royal Society A",
        ),
        Citation(
            bibtex_key="mandt2017",
            title=(
                "Stochastic Gradient Descent as Approximate "
                "Bayesian Inference"
            ),
            authors=["Stephan Mandt", "Matthew D. Hoffman", "David M. Blei"],
            year=2017,
            journal="Journal of Machine Learning Research",
        ),
        Citation(
            bibtex_key="wallace2012",
            title=(
                "The Emergent Multiverse: Quantum Theory according "
                "to the Everett Interpretation"
            ),
            authors=["David Wallace"],
            year=2012,
            journal="Oxford University Press",
        ),
        Citation(
            bibtex_key="deutsch1999",
            title="Quantum Theory of Probability and Decisions",
            authors=["David Deutsch"],
            year=1999,
            journal="Proceedings of the Royal Society A",
        ),
        Citation(
            bibtex_key="kaila2008",
            title="Natural selection for least action",
            authors=["Ville R. I. Kaila", "Arto Annila"],
            year=2008,
            journal="Proceedings of the Royal Society A",
        ),
        # --- Phase B / v2 additions ---
        Citation(
            bibtex_key="feynmanvernon1963",
            title=(
                "The Theory of a General Quantum System Interacting "
                "with a Linear Dissipative System"
            ),
            authors=["Richard P. Feynman", "Frank L. Vernon Jr."],
            year=1963,
            journal="Annals of Physics",
        ),
        Citation(
            bibtex_key="caldeiralegget1983",
            title=(
                "Path integral approach to quantum Brownian motion"
            ),
            authors=["Amir O. Caldeira", "Anthony J. Leggett"],
            year=1983,
            journal="Physica A",
        ),
        Citation(
            bibtex_key="bekenstein1981",
            title=(
                "Universal upper bound on the entropy-to-energy ratio "
                "for bounded systems"
            ),
            authors=["Jacob D. Bekenstein"],
            year=1981,
            journal="Physical Review D",
        ),
        Citation(
            bibtex_key="berut2012",
            title=(
                "Experimental verification of Landauer's principle "
                "linking information and thermodynamics"
            ),
            authors=[
                "Antoine B\\'{e}rut", "Artak Arakelyan",
                "Artyom Petrosyan", "Sergio Ciliberto",
                "Raoul Dillenschneider", "Eric Lutz",
            ],
            year=2012,
            journal="Nature",
        ),
        Citation(
            bibtex_key="tanimura2020",
            title=(
                "Numerically ``exact'' approach to open quantum dynamics: "
                "The hierarchical equations of motion (HEOM)"
            ),
            authors=["Yoshitaka Tanimura"],
            year=2020,
            journal="The Journal of Chemical Physics",
        ),
        Citation(
            bibtex_key="zurek2009",
            title="Quantum Darwinism",
            authors=["Wojciech H. Zurek"],
            year=2009,
            journal="Nature Physics",
        ),
    ]


def citations_to_bibtex(citations: list[Citation]) -> str:
    """Convert citation list to BibTeX format."""
    entries = []
    for c in citations:
        authors_str = " and ".join(c.authors)
        entry = f"""@article{{{c.bibtex_key},
  title = {{{c.title}}},
  author = {{{authors_str}}},"""
        if c.year:
            entry += f"\n  year = {{{c.year}}},"
        if c.journal:
            entry += f"\n  journal = {{{c.journal}}},"
        if c.url:
            entry += f"\n  url = {{{c.url}}},"
        entry += "\n}"
        entries.append(entry)
    return "\n\n".join(entries)
