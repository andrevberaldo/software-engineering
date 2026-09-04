"""Resolução de tenant por subdomínio — usada SÓ nos pontos que ainda não
têm uma sessão autenticada (login, branding público). Em qualquer rota
autenticada, o tenant vem da claim `tenant_id` do JWT, nunca daqui: se o
tenant fosse re-derivado do host a cada requisição autenticada, um usuário
logado poderia trocar o parâmetro de host e ler/escrever dados de outro
assinante.
"""
import re

from fastapi import HTTPException, Query, Request, status

from .config import get_settings
from .db import get_cursor

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _slug_from_host(raw_host: str, default_slug: str) -> str:
    host = (raw_host or "").split(":")[0].strip().lower()
    if not host or host == "localhost" or _IP_RE.match(host) or "." not in host:
        return default_slug
    return host.split(".")[0]


def resolve_tenant_from_host(
    request: Request,
    host: str | None = Query(
        default=None,
        description="Host do navegador (window.location.host), para resolver "
        "o tenant antes de existir sessão. Ignorado em rotas autenticadas.",
    ),
) -> dict:
    raw_host = host or request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
    settings = get_settings()
    slug = _slug_from_host(raw_host, settings.default_tenant_slug)

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, slug, nome_empresa, header_color, logo_path FROM tenants WHERE slug = %(slug)s",
            {"slug": slug},
        )
        tenant = cur.fetchone()

    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assinante não encontrado")

    return tenant
