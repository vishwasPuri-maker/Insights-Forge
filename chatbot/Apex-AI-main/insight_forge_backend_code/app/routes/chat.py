"""Chat over WebSocket: /chat/stream.

The frontend opens a WebSocket, authenticates with the access token as a query
param (`?token=...`), then sends `{"message": "..."}` frames. The server streams
back `{"type":"token","content":"..."}` frames and a final `{"type":"done"}`.

The LLM is called server-side. If no LLM key is configured we fall back to a
simple echo-style streamed reply so the frontend can build/integrate against the
socket without external dependencies. (No cleaning/ML here — chat only.)
"""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException

from app.auth.jwt_handler import TokenData, decode_token
from app.config import settings

router = APIRouter(tags=["chat"])


def _authenticate(token: str | None) -> TokenData | None:
    if not token:
        return None
    try:
        payload = decode_token(token, expected_type="access")
    except HTTPException:
        return None
    return TokenData(
        organization_id=payload["organization_id"],
        user_id=payload["sub"],
        role=payload["role"],
        sector=payload["sector"],
    )


async def _stream_reply(ws: WebSocket, prompt: str, user: TokenData) -> None:
    """Stream a reply token-by-token. Uses the LLM if configured, else a stub."""
    if settings.llm_api_key:
        await _stream_llm(ws, prompt, user)
    else:
        reply = f"[{user.sector}] You said: {prompt}"
        for word in reply.split(" "):
            await ws.send_json({"type": "token", "content": word + " "})
            await asyncio.sleep(0.02)
    await ws.send_json({"type": "done"})


async def _stream_llm(ws: WebSocket, prompt: str, user: TokenData) -> None:
    """Server-side LLM call (OpenAI-compatible), streamed to the client.

    Imported lazily so the socket still works when the SDK/key is absent.
    """
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.llm_api_key)
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You help with {user.sector} decisions."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                await ws.send_json({"type": "token", "content": delta})
    except Exception as exc:  # noqa: BLE001 — surface as a chat error frame, don't crash the socket
        await ws.send_json({"type": "error", "message": f"llm error: {exc}"})


@router.websocket("/chat/stream")
async def chat_stream(ws: WebSocket) -> None:
    user = _authenticate(ws.query_params.get("token"))
    if user is None:
        # 1008 = policy violation; reject before accepting the stream.
        await ws.close(code=1008)
        return
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            prompt = (data or {}).get("message", "").strip()
            if not prompt:
                await ws.send_json(
                    {"type": "error", "message": "message is required"}
                )
                continue
            await _stream_reply(ws, prompt, user)
    except WebSocketDisconnect:
        return
