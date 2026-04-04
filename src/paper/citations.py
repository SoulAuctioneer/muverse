"""Citation manager for the Thermodynamic Darwinism paper.

Seeds the BibTeX database from the source documents' references
and provides lookup/insertion utilities.
"""

from __future__ import annotations

from src.core.paper_schema import Citation


def build_seed_citations() -> list[Citation]:
    """Build the initial citation database from the source documents."""
    return [
        Citation(
            bibtex_key="everett1957",
            title="Relative State Formulation of Quantum Mechanics",
            authors=["Hugh Everett III"],
            year=1957,
            journal="Reviews of Modern Physics",
            url="https://en.wikipedia.org/wiki/Many-worlds_interpretation",
        ),
        Citation(
            bibtex_key="zurek2003",
            title="Quantum Darwinism",
            authors=["Wojciech H. Zurek"],
            year=2003,
            journal="Nature Physics",
            url="https://en.wikipedia.org/wiki/Quantum_Darwinism",
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
            title="Self-Locating Uncertainty and the Origin of Probability in Everettian Quantum Mechanics",
            authors=["Charles T. Sebens", "Sean M. Carroll"],
            year=2018,
            journal="British Journal for the Philosophy of Science",
            url="https://philsci-archive.pitt.edu/27013/1/mwi-selflocating2025fop.pdf",
        ),
        Citation(
            bibtex_key="friston2010",
            title="The free-energy principle: a unified brain theory?",
            authors=["Karl Friston"],
            year=2010,
            journal="Nature Reviews Neuroscience",
            url="https://en.wikipedia.org/wiki/Free_energy_principle",
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
            url="https://www.researchgate.net/publication/346440148_The_World_as_a_Neural_Network",
        ),
        Citation(
            bibtex_key="jarzynski1997",
            title="Nonequilibrium Equality for Free Energy Differences",
            authors=["Christopher Jarzynski"],
            year=1997,
            journal="Physical Review Letters",
            url="https://en.wikipedia.org/wiki/Jarzynski_equality",
        ),
        Citation(
            bibtex_key="landauer1961",
            title="Irreversibility and Heat Generation in the Computing Process",
            authors=["Rolf Landauer"],
            year=1961,
            journal="IBM Journal of Research and Development",
            url="https://en.wikipedia.org/wiki/Landauer%27s_principle",
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
            title="Branch-counting in the Everett Interpretation of Quantum Mechanics",
            authors=["Simon Saunders"],
            year=2010,
            journal="Proceedings of the Royal Society A",
            url="https://royalsocietypublishing.org/rspa/article/477/2255/20210600",
        ),
        Citation(
            bibtex_key="mandt2017",
            title="Stochastic Gradient Descent as Approximate Bayesian Inference",
            authors=["Stephan Mandt", "Matthew D. Hoffman", "David M. Blei"],
            year=2017,
            journal="Journal of Machine Learning Research",
        ),
        Citation(
            bibtex_key="wallace2012",
            title="The Emergent Multiverse: Quantum Theory according to the Everett Interpretation",
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
