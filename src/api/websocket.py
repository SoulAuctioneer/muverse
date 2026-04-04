"""WebSocket endpoint for real-time agent streaming."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agents.base import AgentState, build_theory_context, load_system_prompt, make_messages
from src.agents.orchestrator import create_initial_state
from src.llm.provider import stream

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/agent-stream")
async def agent_stream(ws: WebSocket):
    """Stream agent responses in real time.

    Client sends: {"agent": "theorist", "task": "...", "phase": "formalize"}
    Server streams: {"type": "chunk", "content": "..."} then {"type": "done"}
    """
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            agent_name = data.get("agent", "theorist")
            task = data.get("task", "")
            phase = data.get("phase", "formalize")

            state = create_initial_state()
            state.phase = phase
            system_prompt = load_system_prompt(agent_name)
            theory_ctx = build_theory_context(state)
            messages = make_messages(system_prompt, theory_ctx, task)

            await ws.send_json({"type": "start", "agent": agent_name})

            full_response = ""
            async for chunk in stream(messages, role=agent_name):
                full_response += chunk
                await ws.send_json({"type": "chunk", "content": chunk})

            await ws.send_json({
                "type": "done",
                "agent": agent_name,
                "full_response": full_response,
            })

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        manager.disconnect(ws)
