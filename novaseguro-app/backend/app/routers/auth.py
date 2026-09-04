from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from ..auth import DUMMY_PASSWORD_HASH, create_access_token, get_current_user, verify_password
from ..config import get_settings
from ..db import get_cursor
from ..tenancy import resolve_tenant_from_host

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


def _public_user(user: dict) -> dict:
    return {
        "id": user["id"] if "id" in user else user.get("sub"),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


def _public_tenant(tenant: dict) -> dict:
    return {
        "slug": tenant["slug"],
        "nomeEmpresa": tenant["nome_empresa"],
        "headerColor": tenant["header_color"],
        "hasLogo": bool(tenant["logo_path"]),
    }


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    tenant: dict = Depends(resolve_tenant_from_host),
) -> dict:
    settings = get_settings()
    email = payload.email.strip().lower()

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, tenant_id, email, password_hash, name, role
            FROM users WHERE tenant_id = %(tenant_id)s AND email = %(email)s
            """,
            {"tenant_id": tenant["id"], "email": email},
        )
        user = cur.fetchone()

    # Compara sempre contra um hash (real ou dummy) para não vazar por
    # timing se o e-mail existe em outro tenant.
    password_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    if not user or not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    token = create_access_token(user)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_expires_minutes * 60,
        path="/",
        domain=settings.cookie_domain,
    )
    return {"user": _public_user(user)}


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.cookie_name, path="/", domain=settings.cookie_domain)


@router.get("/me")
def me(user: dict = Depends(get_current_user)) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "SELECT slug, nome_empresa, header_color, logo_path FROM tenants WHERE id = %(id)s",
            {"id": user["tenant_id"]},
        )
        tenant = cur.fetchone()

    return {"user": _public_user(user), "tenant": _public_tenant(tenant) if tenant else None}
