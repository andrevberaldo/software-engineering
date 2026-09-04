"""Consultas simples de dados de negócio (carteira, dashboard, seguradoras).

Não envolvem o deep agent nem RAG — são as mesmas queries que antes viviam
no BFF Node.js, hoje direto no backend Python já que ele mantém sua própria
conexão com o Postgres. Todas escopadas pelo tenant do usuário logado
(`user["tenant_id"]`, vindo da claim do JWT).
"""
from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..db import get_cursor

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/seguradoras")
def listar_seguradoras(user: dict = Depends(get_current_user)) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, nome FROM seguradoras WHERE tenant_id = %(tenant_id)s ORDER BY nome",
            {"tenant_id": user["tenant_id"]},
        )
        rows = cur.fetchall()
    return {"seguradoras": rows}


@router.get("/dashboard")
def dashboard(user: dict = Depends(get_current_user)) -> dict:
    tenant_id = user["tenant_id"]
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*)::int AS total FROM clientes WHERE tenant_id = %(tenant_id)s",
            {"tenant_id": tenant_id},
        )
        total_clientes = cur.fetchone()["total"]

        cur.execute(
            "SELECT COUNT(*)::int AS total FROM apolices WHERE tenant_id = %(tenant_id)s AND status = 'ativa'",
            {"tenant_id": tenant_id},
        )
        apolices_ativas = cur.fetchone()["total"]

        cur.execute(
            """
            SELECT COUNT(*)::int AS total FROM apolices
            WHERE tenant_id = %(tenant_id)s AND status = 'ativa'
              AND data_renovacao <= CURRENT_DATE + INTERVAL '30 days'
            """,
            {"tenant_id": tenant_id},
        )
        apolices_em_risco_30d = cur.fetchone()["total"]

        cur.execute(
            """
            SELECT AVG(probabilidade_renovacao)::numeric(5,1) AS media
            FROM (
                SELECT DISTINCT ON (apolice_id) apolice_id, probabilidade_renovacao
                FROM previsoes_renovacao
                WHERE tenant_id = %(tenant_id)s
                ORDER BY apolice_id, calculado_em DESC
            ) ultimas
            """,
            {"tenant_id": tenant_id},
        )
        media = cur.fetchone()["media"]

    return {
        "totalClientes": total_clientes,
        "apolicesAtivas": apolices_ativas,
        "apolicesEmRisco30d": apolices_em_risco_30d,
        "probabilidadeMediaRenovacao": float(media) if media is not None else None,
    }


@router.get("/clientes")
def listar_clientes(user: dict = Depends(get_current_user)) -> dict:
    tenant_id = user["tenant_id"]
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                c.id,
                c.nome,
                c.email,
                c.corretor_responsavel,
                COUNT(a.id)::int AS total_apolices,
                MIN(a.data_renovacao) FILTER (WHERE a.status = 'ativa') AS proxima_renovacao,
                COALESCE(SUM(a.valor_patrimonio_segurado) FILTER (WHERE a.status = 'ativa'), 0) AS patrimonio_total
            FROM clientes c
            LEFT JOIN apolices a ON a.cliente_id = c.id AND a.tenant_id = c.tenant_id
            WHERE c.tenant_id = %(tenant_id)s
            GROUP BY c.id
            ORDER BY proxima_renovacao NULLS LAST
            """,
            {"tenant_id": tenant_id},
        )
        clientes = cur.fetchall()

        cur.execute(
            """
            SELECT
                a.id,
                a.cliente_id,
                a.tipo_cobertura,
                a.status,
                a.data_inicio,
                a.data_renovacao,
                a.valor_patrimonio_segurado,
                a.descricao_patrimonio,
                s.nome AS seguradora
            FROM apolices a
            JOIN seguradoras s ON s.id = a.seguradora_id AND s.tenant_id = a.tenant_id
            WHERE a.tenant_id = %(tenant_id)s
            ORDER BY a.data_renovacao
            """,
            {"tenant_id": tenant_id},
        )
        apolices = cur.fetchall()

    apolices_por_cliente: dict[int, list[dict]] = {}
    for apolice in apolices:
        apolices_por_cliente.setdefault(apolice["cliente_id"], []).append(apolice)

    for cliente in clientes:
        cliente["apolices"] = apolices_por_cliente.get(cliente["id"], [])

    return {"clientes": clientes}
