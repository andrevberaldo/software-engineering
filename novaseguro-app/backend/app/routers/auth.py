from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from ..auth import create_access_token, get_current_user, verify_password
from ..config import get_settings
from ..db import get_cursor

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


@router.post("/login")
def login(payload: LoginRequest, response: Response) -> dict:
    settings = get_settings()
    email = payload.email.strip().lower()

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, email, password_hash, name, role FROM users WHERE email = %(email)s",
            {"email": email},
        )
        user = cur.fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
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
    )
    return {"user": _public_user(user)}


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.cookie_name, path="/")


@router.get("/me")
def me(user: dict = Depends(get_current_user)) -> dict:
    return {"user": _public_user(user)}
