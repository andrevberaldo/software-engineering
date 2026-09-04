"""Identidade visual do tenant do usuário logado: nome da empresa, cor do
header e logotipo em SVG. Leitura para qualquer usuário autenticado;
edição só para admins (`require_admin`) — e sempre no tenant do próprio
usuário (`user["tenant_id"]`), nunca num id vindo do corpo da requisição.
"""
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..auth import get_current_user, require_admin
from ..db import get_cursor
from ..storage import save_named_file

router = APIRouter(prefix="/tenants", tags=["tenants"])

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_LOGO_BYTES = 512 * 1024
_SVG_DANGEROUS_RE = re.compile(rb"<script|on\w+\s*=|javascript:", re.IGNORECASE)


def _branding_dict(tenant: dict) -> dict:
    return {
        "slug": tenant["slug"],
        "nomeEmpresa": tenant["nome_empresa"],
        "headerColor": tenant["header_color"],
        "hasLogo": bool(tenant["logo_path"]),
    }


def _validate_svg(raw: bytes) -> None:
    if len(raw) > MAX_LOGO_BYTES:
        raise HTTPException(status_code=413, detail="Logo maior que 512KB")
    head = raw.lstrip()[:256]
    if not (head.startswith(b"<?xml") or head.startswith(b"<svg")):
        raise HTTPException(status_code=400, detail="Envie um arquivo SVG válido")
    if _SVG_DANGEROUS_RE.search(raw):
        raise HTTPException(
            status_code=400, detail="SVG contém conteúdo não permitido (script)"
        )


@router.get("/branding")
def get_branding(user: dict = Depends(get_current_user)) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "SELECT slug, nome_empresa, header_color, logo_path FROM tenants WHERE id = %(id)s",
            {"id": user["tenant_id"]},
        )
        tenant = cur.fetchone()

    if tenant is None:
        raise HTTPException(status_code=404, detail="Assinante não encontrado")
    return _branding_dict(tenant)


@router.put("/branding")
async def update_branding(
    nome_empresa: str = Form(...),
    header_color: str = Form(...),
    logo: UploadFile | None = File(None),
    user: dict = Depends(require_admin),
) -> dict:
    if not HEX_COLOR_RE.match(header_color):
        raise HTTPException(status_code=400, detail="Cor inválida — use o formato #RRGGBB")

    tenant_id = user["tenant_id"]
    logo_path = None
    if logo is not None:
        raw = await logo.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Arquivo de logo vazio")
        _validate_svg(raw)
        # Nome do arquivo sempre forçado no backend — nunca confia na
        # extensão que o cliente enviou.
        logo_path = save_named_file(raw, f"tenants/{tenant_id}/logo.svg")

    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE tenants
            SET nome_empresa = %(nome)s,
                header_color = %(cor)s,
                logo_path = COALESCE(%(logo)s, logo_path)
            WHERE id = %(id)s
            RETURNING slug, nome_empresa, header_color, logo_path
            """,
            {
                "nome": nome_empresa,
                "cor": header_color,
                "logo": logo_path,
                "id": tenant_id,
            },
        )
        tenant = cur.fetchone()

    return _branding_dict(tenant)
