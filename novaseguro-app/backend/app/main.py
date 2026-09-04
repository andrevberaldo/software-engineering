from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, chat, data, documents, health

settings = get_settings()

app = FastAPI(
    title="NovaSeguro — Backend",
    description="Autenticação, dados da carteira e um deep agent "
    "(LangChain/deepagents) com ferramentas de RAG e previsão de renovação "
    "para a corretora fictícia NovaSeguro. Consumido diretamente pelo "
    "frontend Next.js — não há BFF intermediário.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(chat.router)
app.include_router(documents.router)
