#!/usr/bin/env python3
"""Gera os embeddings da base de conhecimento (tabela `documentos`).

Roda separado do seed SQL porque depende de uma OPENAI_API_KEY válida.
Sem isso, as apólices/clientes/previsões já funcionam normalmente — só a
ferramenta de busca por documentos (RAG) fica sem resultado.

Uso (a partir de backend/, com o venv do backend ativado):
    OPENAI_API_KEY=sk-... DATABASE_URL=postgresql://... python3 ../db/seed_embeddings.py
"""
import os
import sys

import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://novaseguro:novaseguro_dev_pw@localhost:5432/novaseguro"
)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def main() -> int:
    if not OPENAI_API_KEY:
        print("Defina OPENAI_API_KEY para gerar os embeddings.", file=sys.stderr)
        return 1

    client = OpenAI(api_key=OPENAI_API_KEY)

    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id, conteudo FROM documentos WHERE embedding IS NULL")
            pendentes = cur.fetchall()

            if not pendentes:
                print("Nenhum documento pendente de embedding.")
                return 0

            for doc_id, conteudo in pendentes:
                resp = client.embeddings.create(model=EMBEDDING_MODEL, input=conteudo)
                embedding = resp.data[0].embedding
                cur.execute(
                    "UPDATE documentos SET embedding = %s WHERE id = %s",
                    (embedding, doc_id),
                )
                print(f"Embedding gerado para documento #{doc_id}")

        conn.commit()

    print(f"Concluído: {len(pendentes)} documento(s) processado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
