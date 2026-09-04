from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from .config import get_settings

# Hash bcrypt de uma senha aleatória, usado só para comparar contra ele
# quando o e-mail não existe naquele tenant — mantém o tempo de resposta
# do login igual em ambos os casos, evitando enumerar e-mails/tenants por
# timing.
DUMMY_PASSWORD_HASH = "$2b$12$CY1mTbjDwKYBF.3J04t9I.V6HmDMCd60VAmmvneYG7ETUe1.vIfIm"


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user: dict) -> str:
    """Assina o JWT de sessão no login, com o mesmo formato de claims que o
    frontend (lib/session.ts) espera ao verificar o cookie.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "tenant_id": user["tenant_id"],
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expires_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(request: Request) -> dict:
    """Valida o JWT enviado no cookie de sessão (emitido em /auth/login)."""
    settings = get_settings()
    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
        )

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
        ) from exc

    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Igual a get_current_user, mas só libera usuários com role 'admin' —
    usado nas rotas que alteram a identidade visual do tenant.
    """
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem fazer isso",
        )
    return user
