from fastapi import APIRouter

from ..config import get_settings
from ..db import get_cursor

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    db_ok = True
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "openai_configured": bool(settings.openai_api_key),
    }
