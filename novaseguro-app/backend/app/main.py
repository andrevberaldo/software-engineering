from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import chat, health

settings = get_settings()

app = FastAPI(
    title="NovaSeguro — Backend de IA",
    description="Expõe um deep agent (LangChain/deepagents) com ferramentas "
    "de RAG e previsão de renovação para a corretora fictícia NovaSeguro.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
