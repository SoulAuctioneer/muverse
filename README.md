# Muverse — Agentic Physics Theory Development Platform

A web-based, provider-agnostic agentic system for formalizing, testing, and critiquing
the **Thermodynamic Darwinism** framework: the proposal that MWI branch persistence is
governed by finite-resource thermodynamic constraints.

**Current status (v2):** The original Wick-rotation mechanism (Axiom A3) has been
**falsified** by influence functional analysis and numerical simulation (Lindblad + HEOM).
The Born rule cannot emerge from a Gibbs distribution over Euclidean actions because
decoherence does not produce such a distribution. The theory is being rebuilt on
information-theoretic foundations: Landauer bounds on pointer-state creation, Bekenstein
bounds on branching capacity, and information-constrained Quantum Darwinism.

**IMPORTANT CAVEAT:** This is purely an experiment in developing such a framework and presenting a theory in an interactive and engaging way. I am not a mathematician or a physicist. The science itself is a rigorous *exploration* — including the honest documentation of negative results.

## Quick Start

```bash
# 1. Start PostgreSQL via Docker
docker compose up -d db

# 2. Install Python dependencies
uv pip install -e ".[dev]"

# 3. Copy and fill in environment variables
cp .env.example .env

# 4. Start the API server (auto-creates tables on first run)
uvicorn src.api.main:app --reload

# 5. Start the frontend (separate terminal)
cd frontend && pnpm install && pnpm dev
```

## Architecture


| Layer           | Technology                | Purpose                                                        |
| --------------- | ------------------------- | -------------------------------------------------------------- |
| **Agents**      | LangGraph + litellm       | Theorist, Critic, Literature, Simulator, Writer                |
| **Math Engine** | SymPy, JAX, QuTiP         | Symbolic derivations, numerical simulation, quantum dynamics   |
| **Simulations** | NumPy, SciPy              | Branch Boltzmann ensemble, NN analog, quantum Langevin         |
| **API**         | FastAPI + WebSocket       | REST endpoints, real-time agent streaming                      |
| **Frontend**    | Next.js, D3.js, Plotly    | Theory graph, agent panel, simulation lab, paper preview       |
| **Storage**     | PostgreSQL (local Docker) | Theory versions, simulation results, literature, agent history |


## Core Simulations

1. **Branch Ensemble under Boltzmann Constraint** — discrete MWI branching with energy-weighted selection
2. **Neural Network Analog Model** — SGD as a physical analog of branch selection under finite energy
3. **Quantum Langevin Dynamics** — QuTiP-based quantum branching with tunable thermal bath
4. **Born Rule Deviation Test (P1)** — distinguishes TD from standard QM predictions
5. **Lindblad Master Equation Test** — exact Markovian steady state vs Gibbs(E) vs Gibbs(S_E) *[falsified A3]*
6. **HEOM Non-Markovian Test** — exact non-Markovian dynamics via influence functional *[falsified A3]*
7. **Landauer Pointer-State Test** — information-constrained pointer-state selection *[Phase A]*

## Paper Pipeline

The system produces a publication-ready paper by:

- Formalizing theory axioms and derivation chains
- Running simulations and generating figures
- Having a Writer agent draft sections from structured data
- Having a Critic agent review every claim for circularity and empirical conflict

