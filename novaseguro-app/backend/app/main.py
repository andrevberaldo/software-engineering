from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, chat, data, documents, health, public, tenants

settings = get_settings()

app = FastAPI(
    title="NovaSeguro — Backend",
    description="Autenticação, dados da carteira, identidade visual por "
    "assinante e um deep agent (LangChain/deepagents) com ferramentas de "
    "RAG e previsão de renovação — multi-tenant, consumido diretamente "
    "pelo frontend Next.js (não há BFF intermediário).",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(public.router)
app.include_router(data.router)
app.include_router(chat.router)
app.include_router(documents.router)
