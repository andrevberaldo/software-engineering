"""Modelo heurístico (não é machine learning de verdade) de previsão de
renovação: existe só para tornar a demonstração funcional de ponta a ponta.
Numa evolução real, isso seria substituído por um modelo treinado com
histórico de renovações passadas.
"""
import json
from datetime import date


def compute_prediction(cur, apolice_id: int) -> dict:
    cur.execute(
        """
        SELECT a.id, a.valor_mensal, a.data_renovacao, a.tipo_cobertura,
               a.cliente_id, c.nome AS cliente_nome, s.nome AS seguradora_nome
        FROM apolices a
        JOIN clientes c ON c.id = a.cliente_id
        JOIN seguradoras s ON s.id = a.seguradora_id
        WHERE a.id = %(id)s
        """,
        {"id": apolice_id},
    )
    apolice = cur.fetchone()
    if apolice is None:
        raise ValueError(f"Apólice {apolice_id} não encontrada")

    cliente_id = apolice["cliente_id"]

    cur.execute(
        """
        SELECT tipo, data FROM interacoes
        WHERE cliente_id = %(cliente_id)s
        """,
        {"cliente_id": cliente_id},
    )
    interacoes = cur.fetchall()

    cur.execute(
        """
        SELECT data, valor FROM sinistros WHERE apolice_id = %(apolice_id)s
        """,
        {"apolice_id": apolice_id},
    )
    sinistros = cur.fetchall()

    hoje = date.today()
    score = 85.0
    fatores = []

    for i in interacoes:
        idade_dias = (hoje - i["data"]).days
        if i["tipo"] == "reclamacao" and idade_dias <= 30:
            score -= 15
            fatores.append(f"Reclamação recente ({idade_dias} dias atrás): -15")
        elif i["tipo"] == "elogio" and idade_dias <= 90:
            score += 5
            fatores.append(f"Elogio recente ({idade_dias} dias atrás): +5")
        elif i["tipo"] == "login_portal" and idade_dias <= 60:
            score += 3
            fatores.append(f"Uso ativo do portal ({idade_dias} dias atrás): +3")

    for sin in sinistros:
        idade_dias = (hoje - sin["data"]).days
        if idade_dias <= 180:
            valor = float(sin["valor"] or 0)
            penalidade = 10 if valor > 5000 else 3
            score -= penalidade
            fatores.append(
                f"Sinistro nos últimos 180 dias (R$ {valor:,.2f}): -{penalidade}"
            )

    dias_ate_renovacao = (apolice["data_renovacao"] - hoje).days
    if dias_ate_renovacao <= 15:
        fatores.append("Renovação em menos de 15 dias: janela de ação curta")

    score = max(5.0, min(98.0, score))

    if score >= 70:
        risco = "baixo"
    elif score >= 40:
        risco = "medio"
    else:
        risco = "alto"

    valor_mensal = float(apolice["valor_mensal"])
    receita_projetada = round(valor_mensal * 12 * (score / 100), 2)

    resultado = {
        "apolice_id": apolice_id,
        "cliente_nome": apolice["cliente_nome"],
        "seguradora_nome": apolice["seguradora_nome"],
        "tipo_cobertura": apolice["tipo_cobertura"],
        "data_renovacao": apolice["data_renovacao"].isoformat(),
        "dias_ate_renovacao": dias_ate_renovacao,
        "probabilidade_renovacao": round(score, 1),
        "receita_projetada": receita_projetada,
        "risco": risco,
        "fatores": fatores,
    }

    cur.execute(
        """
        INSERT INTO previsoes_renovacao
            (apolice_id, probabilidade_renovacao, receita_projetada, risco, fatores)
        VALUES (%(apolice_id)s, %(probabilidade_renovacao)s, %(receita_projetada)s,
                %(risco)s, %(fatores)s)
        """,
        {
            **resultado,
            "fatores": json.dumps(fatores, ensure_ascii=False),
        },
    )

    return resultado
