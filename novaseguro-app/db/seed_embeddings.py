#!/usr/bin/env python3
"""Gera os embeddings pendentes da base de conhecimento (`documento_chunks`).

Roda separado do seed SQL porque depende de uma OPENAI_API_KEY válida.
Sem isso, as apólices/clientes/previsões já funcionam normalmente — só a
ferramenta de busca por documentos (RAG) fica sem resultado.

Serve tanto para os textos digitados manualmente no seed (que viram um
único chunk cada) quanto para PDFs enviados por /documents/upload que
foram salvos sem embedding (ex.: upload feito antes de configurar a
OPENAI_API_KEY).

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
            cur.execute("SELECT id, conteudo FROM documento_chunks WHERE embedding IS NULL")
            pendentes = cur.fetchall()

            if not pendentes:
                print("Nenhum chunk pendente de embedding.")
                return 0

            for chunk_id, conteudo in pendentes:
                resp = client.embeddings.create(model=EMBEDDING_MODEL, input=conteudo)
                embedding = resp.data[0].embedding
                cur.execute(
                    "UPDATE documento_chunks SET embedding = %s WHERE id = %s",
                    (embedding, chunk_id),
                )
                print(f"Embedding gerado para o chunk #{chunk_id}")

        conn.commit()

    print(f"Concluído: {len(pendentes)} chunk(s) processado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
