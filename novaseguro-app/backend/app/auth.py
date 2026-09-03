from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from .config import get_settings


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Valida o JWT repassado pelo BFF no header Authorization: Bearer <token>.

    O backend não faz login por conta própria — ele confia no token que o
    BFF já validou/emitiu, verificando apenas a assinatura com o mesmo
    segredo compartilhado (JWT_SECRET).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente",
        )

    token = authorization.removeprefix("Bearer ").strip()
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido",
        ) from exc

    return payload
