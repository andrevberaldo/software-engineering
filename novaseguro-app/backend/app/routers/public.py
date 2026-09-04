"""Endpoints sem autenticação, usados pela home pública e pela tela de
login para já mostrarem a marca do assinante antes de qualquer sessão
existir. Tenant resolvido por subdomínio (ver `tenancy.py`).
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..db import get_cursor
from ..storage import resolve_path
from ..tenancy import resolve_tenant_from_host

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/branding")
def public_branding(tenant: dict = Depends(resolve_tenant_from_host)) -> dict:
    return {
        "slug": tenant["slug"],
        "nomeEmpresa": tenant["nome_empresa"],
        "headerColor": tenant["header_color"],
        "hasLogo": bool(tenant["logo_path"]),
    }


@router.get("/tenants/{slug}/logo")
def tenant_logo(slug: str):
    with get_cursor() as cur:
        cur.execute("SELECT logo_path FROM tenants WHERE slug = %(slug)s", {"slug": slug})
        tenant = cur.fetchone()

    if tenant is None or not tenant["logo_path"]:
        raise HTTPException(status_code=404, detail="Este assinante não tem logo")

    path = resolve_path(tenant["logo_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo de logo não encontrado")

    # Sem `filename=`: isso forçaria Content-Disposition: attachment e
    # quebraria a exibição via <img>. O CSP neutraliza script embutido no
    # SVG mesmo se alguém navegar direto para esta URL (fora do <img>,
    # onde o navegador já não executaria).
    return FileResponse(
        path,
        media_type="image/svg+xml",
        headers={
            "Content-Security-Policy": "script-src 'none'; sandbox",
            "X-Content-Type-Options": "nosniff",
        },
    )
