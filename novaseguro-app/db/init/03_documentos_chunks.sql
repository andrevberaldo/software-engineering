-- Evolui a base de conhecimento para suportar PDFs de verdade: um documento
-- (apólice enviada por uma seguradora) agora pode ter várias partes
-- (chunks), cada uma com seu próprio embedding, além de guardar o arquivo
-- original para download.

CREATE TABLE IF NOT EXISTS documento_chunks (
    id            SERIAL PRIMARY KEY,
    documento_id  INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    chunk_index   INTEGER NOT NULL,
    conteudo      TEXT NOT NULL,
    embedding     vector(1536),
    metadados     JSONB,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (documento_id, chunk_index)
);

-- Migra o conteúdo hoje guardado direto em `documentos` (os textos digitados
-- manualmente no seed) para virar o chunk único de cada documento, antes de
-- remover essas colunas de `documentos`.
INSERT INTO documento_chunks (documento_id, chunk_index, conteudo, embedding)
SELECT id, 0, conteudo, embedding
FROM documentos
WHERE conteudo IS NOT NULL
ON CONFLICT (documento_id, chunk_index) DO NOTHING;

ALTER TABLE documentos
    ADD COLUMN IF NOT EXISTS arquivo_nome     VARCHAR(255),
    ADD COLUMN IF NOT EXISTS arquivo_caminho  VARCHAR(500),
    ADD COLUMN IF NOT EXISTS mime_type        VARCHAR(100),
    ADD COLUMN IF NOT EXISTS tamanho_bytes    INTEGER;

ALTER TABLE documentos
    DROP COLUMN IF EXISTS conteudo,
    DROP COLUMN IF EXISTS embedding;

CREATE INDEX IF NOT EXISTS documento_chunks_embedding_idx
    ON documento_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documento_chunks_documento_idx
    ON documento_chunks (documento_id);
