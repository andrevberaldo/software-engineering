"""Ferramentas (tools) que o deep agent pode chamar.

Cada função vira uma tool do LangChain via o decorator @tool. O docstring de
cada uma é o que o modelo lê para decidir quando usá-la — por isso são
descritivos e em português, no mesmo idioma das respostas esperadas.
"""
from langchain_core.tools import tool

from ..db import get_cursor
from .embeddings import embed_text
from .prediction import compute_prediction


@tool
def buscar_documentos(pergunta: str, top_k: int = 4) -> str:
    """Busca trechos relevantes na base de conhecimento (manuais de apólices e
    políticas internas da NovaSeguro, incluindo PDFs enviados pelas
    seguradoras) usando busca por similaridade (RAG). Use esta ferramenta
    sempre que a pergunta envolver regras de cobertura, franquias, carências
    ou políticas internas. Sempre cite o título do documento na resposta
    final, para que o corretor saiba de onde veio a informação.
    """
    query_embedding = embed_text(pergunta)
    if query_embedding is None:
        return (
            "Não foi possível gerar o embedding da pergunta (verifique se "
            "OPENAI_API_KEY está configurada)."
        )

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT d.id AS documento_id, d.titulo, c.conteudo,
                   1 - (c.embedding <=> %(q)s) AS similaridade
            FROM documento_chunks c
            JOIN documentos d ON d.id = c.documento_id
            WHERE c.embedding IS NOT NULL
            ORDER BY c.embedding <=> %(q)s
            LIMIT %(k)s
            """,
            {"q": query_embedding, "k": top_k},
        )
        rows = cur.fetchall()

    if not rows:
        return (
            "Nenhum chunk com embedding foi encontrado. Envie um PDF em "
            "/documents/upload ou rode o script seed_embeddings.py (ambos "
            "precisam de uma OPENAI_API_KEY válida para gerar os vetores)."
        )

    partes = [
        f"[{r['titulo']} — documento #{r['documento_id']}] (similaridade {r['similaridade']:.2f})\n{r['conteudo']}"
        for r in rows
    ]
    return "\n\n".join(partes)


@tool
def consultar_cliente(nome_ou_email: str) -> str:
    """Consulta os dados de um cliente da NovaSeguro: suas apólices ativas,
    as seguradoras envolvidas e o histórico de sinistros. Use para responder
    perguntas sobre a situação de um cliente específico ou para comparar
    coberturas entre seguradoras diferentes para o mesmo cliente.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, nome, email, corretor_responsavel
            FROM clientes
            WHERE nome ILIKE %(termo)s OR email ILIKE %(termo)s
            LIMIT 1
            """,
            {"termo": f"%{nome_ou_email}%"},
        )
        cliente = cur.fetchone()
        if cliente is None:
            return f"Nenhum cliente encontrado para '{nome_ou_email}'."

        cur.execute(
            """
            SELECT a.id, a.tipo_cobertura, a.valor_mensal, a.data_renovacao,
                   a.status, s.nome AS seguradora
            FROM apolices a
            JOIN seguradoras s ON s.id = a.seguradora_id
            WHERE a.cliente_id = %(cid)s
            ORDER BY a.data_renovacao
            """,
            {"cid": cliente["id"]},
        )
        apolices = cur.fetchall()

        cur.execute(
            """
            SELECT sin.data, sin.descricao, sin.valor, a.tipo_cobertura
            FROM sinistros sin
            JOIN apolices a ON a.id = sin.apolice_id
            WHERE a.cliente_id = %(cid)s
            ORDER BY sin.data DESC
            """,
            {"cid": cliente["id"]},
        )
        sinistros = cur.fetchall()

    linhas = [
        f"Cliente: {cliente['nome']} ({cliente['email']})",
        f"Corretor responsável: {cliente['corretor_responsavel']}",
        "",
        "Apólices:",
    ]
    for a in apolices:
        linhas.append(
            f"- #{a['id']} {a['tipo_cobertura']} pela {a['seguradora']}, "
            f"R$ {float(a['valor_mensal']):.2f}/mês, renova em {a['data_renovacao']}, "
            f"status: {a['status']}"
        )

    if sinistros:
        linhas.append("")
        linhas.append("Sinistros:")
        for s in sinistros:
            linhas.append(
                f"- {s['data']} ({s['tipo_cobertura']}): {s['descricao']} "
                f"— R$ {float(s['valor']):.2f}"
            )

    return "\n".join(linhas)


@tool
def prever_renovacao_apolice(apolice_id: int) -> str:
    """Estima a probabilidade de renovação e a receita futura projetada de
    uma apólice específica, com base em sinais de uso, reclamações, elogios
    e sinistros recentes do cliente. Retorna também o nível de risco
    (baixo, médio ou alto) e os fatores que mais pesaram na conta.
    """
    with get_cursor() as cur:
        try:
            resultado = compute_prediction(cur, apolice_id)
        except ValueError as exc:
            return str(exc)

    fatores_txt = "\n".join(f"- {f}" for f in resultado["fatores"]) or "- Nenhum fator de destaque"
    return (
        f"Apólice #{resultado['apolice_id']} — {resultado['tipo_cobertura']} "
        f"({resultado['seguradora_nome']}) do cliente {resultado['cliente_nome']}\n"
        f"Renovação em: {resultado['data_renovacao']} ({resultado['dias_ate_renovacao']} dias)\n"
        f"Probabilidade de renovação: {resultado['probabilidade_renovacao']}%\n"
        f"Receita anual projetada: R$ {resultado['receita_projetada']:.2f}\n"
        f"Risco de cancelamento: {resultado['risco']}\n"
        f"Fatores considerados:\n{fatores_txt}"
    )


@tool
def listar_apolices_em_risco(dias: int = 30) -> str:
    """Lista as apólices que vencem nos próximos N dias (padrão 30), já com
    a previsão de renovação calculada, ordenadas da mais arriscada para a
    menos arriscada. Use para identificar prioridades de contato antes de
    disparar ações de renovação.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id FROM apolices
            WHERE status = 'ativa'
              AND data_renovacao <= CURRENT_DATE + (%(dias)s || ' days')::interval
            ORDER BY data_renovacao
            """,
            {"dias": dias},
        )
        ids = [r["id"] for r in cur.fetchall()]

        if not ids:
            return f"Nenhuma apólice ativa vence nos próximos {dias} dias."

        resultados = [compute_prediction(cur, apolice_id) for apolice_id in ids]

    resultados.sort(key=lambda r: r["probabilidade_renovacao"])

    linhas = [f"Apólices vencendo em até {dias} dias, por risco:"]
    for r in resultados:
        linhas.append(
            f"- #{r['apolice_id']} {r['cliente_nome']} ({r['tipo_cobertura']}, "
            f"{r['seguradora_nome']}): {r['probabilidade_renovacao']}% de chance de "
            f"renovar, risco {r['risco']}, renova em {r['dias_ate_renovacao']} dias"
        )
    return "\n".join(linhas)


@tool
def registrar_contato_renovacao(apolice_id: int, mensagem: str, canal: str = "email") -> str:
    """Registra (simula) um contato automático de renovação com o cliente:
    quando o risco de cancelamento é baixo/médio, o próprio sistema envia um
    lembrete direto ao cliente destacando o valor da apólice; quando o risco
    é alto, use esta ferramenta para registrar que um corretor humano foi
    priorizado em vez do contato automático. Sempre calcule a previsão de
    renovação (prever_renovacao_apolice) antes de chamar esta ferramenta, e
    escreva a mensagem você mesmo, em português, curta e cordial.
    """
    with get_cursor() as cur:
        try:
            previsao = compute_prediction(cur, apolice_id)
        except ValueError as exc:
            return str(exc)

        motivo = f"risco_{previsao['risco']}"
        cur.execute(
            """
            INSERT INTO contatos_renovacao (apolice_id, canal, mensagem, motivo)
            VALUES (%(apolice_id)s, %(canal)s, %(mensagem)s, %(motivo)s)
            RETURNING id, enviado_em
            """,
            {
                "apolice_id": apolice_id,
                "canal": canal,
                "mensagem": mensagem,
                "motivo": motivo,
            },
        )
        registro = cur.fetchone()

    destinatario = (
        "o cliente diretamente"
        if previsao["risco"] != "alto"
        else "o corretor humano, para contato prioritário"
    )
    return (
        f"Contato registrado (#{registro['id']}, {registro['enviado_em']}) via {canal}, "
        f"direcionado a {destinatario}.\nMensagem enviada:\n{mensagem}"
    )


ALL_TOOLS = [
    buscar_documentos,
    consultar_cliente,
    prever_renovacao_apolice,
    listar_apolices_em_risco,
    registrar_contato_renovacao,
]
