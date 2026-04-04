"""PostgreSQL storage layer via asyncpg.

Manages a connection pool and provides async helpers for persisting
theory state, simulation results, agent history, and citations.
When the database is unreachable the functions degrade gracefully
(return None / empty lists) so the app can run without Postgres.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import asyncpg
from dotenv import load_dotenv

from src.core.paper_schema import Citation
from src.core.simulation_schema import SimConfig, SimResult
from src.core.theory_schema import TheoryState
from src.storage.models import SCHEMA_SQL

load_dotenv()
logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool | None:
    global _pool
    if _pool is not None:
        return _pool

    dsn = os.getenv("DATABASE_URL", "")
    if not dsn:
        logger.warning("DATABASE_URL not set — running without persistence")
        return None

    try:
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
        return _pool
    except Exception as e:
        logger.warning("Could not connect to PostgreSQL: %s", e)
        return None


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_schema() -> None:
    """Create tables if they don't exist yet."""
    pool = await get_pool()
    if pool is None:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(SCHEMA_SQL)
        logger.info("Database schema initialised")
    except Exception as e:
        logger.error("Schema init failed: %s", e)


# ---------------------------------------------------------------------------
# Theory persistence
# ---------------------------------------------------------------------------

async def save_theory_version(theory: TheoryState) -> str | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO theory_versions (version, name, state_json)
                   VALUES ($1, $2, $3::jsonb)
                   RETURNING id""",
                theory.version,
                theory.name,
                json.dumps(theory.model_dump(mode="json")),
            )
            return str(row["id"]) if row else None
    except Exception as e:
        logger.error("Failed to save theory version: %s", e)
        return None


async def load_latest_theory() -> TheoryState | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT state_json FROM theory_versions
                   ORDER BY version DESC LIMIT 1"""
            )
            if row:
                data = row["state_json"]
                if isinstance(data, str):
                    data = json.loads(data)
                return TheoryState(**data)
        return None
    except Exception as e:
        logger.error("Failed to load theory: %s", e)
        return None


# ---------------------------------------------------------------------------
# Simulation results
# ---------------------------------------------------------------------------

async def save_simulation_config(config: SimConfig) -> str | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO simulation_configs (simulation_name, parameters, description)
                   VALUES ($1, $2::jsonb, $3)
                   RETURNING id""",
                config.simulation_name,
                json.dumps(config.parameters),
                config.description,
            )
            return str(row["id"]) if row else None
    except Exception as e:
        logger.error("Failed to save sim config: %s", e)
        return None


async def save_simulation_result(sim_result: SimResult) -> str | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO simulation_results
                   (config_id, status, metrics, figures, raw_data,
                    analysis_notes, started_at, completed_at, error_message)
                   VALUES ($1::uuid, $2, $3::jsonb, $4, $5::jsonb, $6, $7, $8, $9)
                   RETURNING id""",
                sim_result.config_id,
                sim_result.status.value,
                json.dumps(sim_result.metrics),
                sim_result.figures,
                json.dumps(sim_result.raw_data) if sim_result.raw_data else None,
                sim_result.analysis_notes,
                sim_result.started_at,
                sim_result.completed_at,
                sim_result.error_message,
            )
            return str(row["id"]) if row else None
    except Exception as e:
        logger.error("Failed to save sim result: %s", e)
        return None


# ---------------------------------------------------------------------------
# Agent history
# ---------------------------------------------------------------------------

async def save_agent_output(
    agent_name: str,
    phase: str,
    output_text: str,
    task: str = "",
    theory_version: int = 0,
    iteration: int = 0,
) -> str | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO agent_history
                   (agent_name, phase, task, output_text, theory_version, iteration)
                   VALUES ($1, $2, $3, $4, $5, $6)
                   RETURNING id""",
                agent_name,
                phase,
                task,
                output_text,
                theory_version,
                iteration,
            )
            return str(row["id"]) if row else None
    except Exception as e:
        logger.error("Failed to save agent output: %s", e)
        return None


async def get_agent_history(
    agent_name: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    pool = await get_pool()
    if pool is None:
        return []

    try:
        async with pool.acquire() as conn:
            if agent_name:
                rows = await conn.fetch(
                    """SELECT * FROM agent_history
                       WHERE agent_name = $1
                       ORDER BY created_at DESC LIMIT $2""",
                    agent_name,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """SELECT * FROM agent_history
                       ORDER BY created_at DESC LIMIT $1""",
                    limit,
                )
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get agent history: %s", e)
        return []


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------

async def save_citation(citation: Citation) -> str | None:
    pool = await get_pool()
    if pool is None:
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO citations (bibtex_key, title, authors, year, journal, url, bibtex)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)
                   ON CONFLICT (bibtex_key) DO UPDATE SET
                     title = EXCLUDED.title,
                     authors = EXCLUDED.authors,
                     year = EXCLUDED.year,
                     journal = EXCLUDED.journal,
                     url = EXCLUDED.url,
                     bibtex = EXCLUDED.bibtex
                   RETURNING id""",
                citation.bibtex_key,
                citation.title,
                citation.authors,
                citation.year,
                citation.journal,
                citation.url,
                citation.bibtex,
            )
            return str(row["id"]) if row else None
    except Exception as e:
        logger.error("Failed to save citation: %s", e)
        return None


async def get_all_citations() -> list[dict[str, Any]]:
    pool = await get_pool()
    if pool is None:
        return []

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM citations")
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get citations: %s", e)
        return []
