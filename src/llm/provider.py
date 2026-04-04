"""Provider-agnostic LLM interface via litellm.

Swap models by changing environment variables — no code changes needed.
Each agent role can use a different model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

import litellm
from dotenv import load_dotenv

load_dotenv()

litellm.drop_params = True

DEFAULT_MODEL = os.getenv("MODEL_ORCHESTRATOR", "gemini/gemini-2.5-flash")

ROLE_MODELS: dict[str, str] = {
    "theorist": os.getenv("MODEL_THEORIST", DEFAULT_MODEL),
    "critic": os.getenv("MODEL_CRITIC", DEFAULT_MODEL),
    "literature": os.getenv("MODEL_LITERATURE", DEFAULT_MODEL),
    "simulator": os.getenv("MODEL_SIMULATOR", DEFAULT_MODEL),
    "writer": os.getenv("MODEL_WRITER", DEFAULT_MODEL),
    "orchestrator": os.getenv("MODEL_ORCHESTRATOR", DEFAULT_MODEL),
}


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_id: str | None = None


def _to_dict(msg: Message) -> dict[str, Any]:
    d: dict[str, Any] = {"role": msg.role, "content": msg.content}
    if msg.tool_call_id:
        d["tool_call_id"] = msg.tool_call_id
    if msg.tool_calls:
        d["tool_calls"] = msg.tool_calls
    return d


async def complete(
    messages: list[Message],
    *,
    role: str = "orchestrator",
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 16384,
    tools: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> Message:
    """Single-turn completion. Returns the assistant message."""
    model = model or ROLE_MODELS.get(role, DEFAULT_MODEL)

    call_kwargs: dict[str, Any] = {
        "model": model,
        "messages": [_to_dict(m) for m in messages],
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs,
    }
    if tools:
        call_kwargs["tools"] = tools

    response = await litellm.acompletion(**call_kwargs)
    choice = response.choices[0].message

    return Message(
        role="assistant",
        content=choice.content or "",
        tool_calls=choice.tool_calls or [],
    )


async def stream(
    messages: list[Message],
    *,
    role: str = "orchestrator",
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 16384,
    **kwargs: Any,
) -> AsyncIterator[str]:
    """Streaming completion — yields content chunks."""
    model = model or ROLE_MODELS.get(role, DEFAULT_MODEL)

    response = await litellm.acompletion(
        model=model,
        messages=[_to_dict(m) for m in messages],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        **kwargs,
    )

    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content
