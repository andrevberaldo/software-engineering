import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..agent.agent import get_agent
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, user: dict = Depends(get_current_user)) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    thread_id = payload.thread_id or f"user-{user.get('sub', 'anon')}"

    try:
        agent = get_agent(user["tenant_id"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": payload.message}]},
            config={"configurable": {"thread_id": thread_id}},
        )
    except Exception as exc:  # pragma: no cover - depende de chamada externa à OpenAI
        logger.exception("Falha ao executar o deep agent")
        raise HTTPException(status_code=502, detail=f"Falha ao consultar o assistente: {exc}") from exc

    messages = result.get("messages", [])
    reply = ""
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        if role in ("ai", "assistant"):
            reply = msg.content if isinstance(msg.content, str) else str(msg.content)
            break

    return ChatResponse(reply=reply or "(sem resposta do assistente)", thread_id=thread_id)
