"""FastAPI application entrypoint for the Muverse platform."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.agents import router as agents_router
from src.api.routes.math import router as math_router
from src.api.routes.paper import router as paper_router
from src.api.routes.simulations import router as simulations_router
from src.api.routes.theory import router as theory_router
from src.api.websocket import router as ws_router
from src.storage.database import close_pool, init_schema

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_schema()
    yield
    await close_pool()


app = FastAPI(
    title="Muverse",
    description="Agentic Physics Theory Development Platform — Thermodynamic Darwinism",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(theory_router, prefix="/api/theory", tags=["theory"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(simulations_router, prefix="/api/simulations", tags=["simulations"])
app.include_router(paper_router, prefix="/api/paper", tags=["paper"])
app.include_router(math_router, prefix="/api/math", tags=["math"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "muverse"}
