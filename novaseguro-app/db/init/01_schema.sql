-- NovaSeguro Corretora — schema inicial
-- Habilita pgvector e cria todas as tabelas usadas pelo BFF (auth) e pelo
-- backend de IA (RAG + previsão de renovação).

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------
-- Autenticação (usada pelo BFF)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name          VARCHAR(255) NOT NULL,
    role          VARCHAR(50)  NOT NULL DEFAULT 'corretor',
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- Domínio da corretora (usado pelo backend de IA)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seguradoras (
    id    SERIAL PRIMARY KEY,
    nome  VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS clientes (
    id                    SERIAL PRIMARY KEY,
    nome                  VARCHAR(255) NOT NULL,
    email                 VARCHAR(255) NOT NULL UNIQUE,
    corretor_responsavel  VARCHAR(255) NOT NULL DEFAULT 'Não atribuído',
    criado_em             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS apolices (
    id               SERIAL PRIMARY KEY,
    cliente_id       INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    seguradora_id    INTEGER NOT NULL REFERENCES seguradoras(id) ON DELETE RESTRICT,
    tipo_cobertura   VARCHAR(120) NOT NULL,
    valor_mensal     NUMERIC(10, 2) NOT NULL,
    data_inicio      DATE NOT NULL,
    data_renovacao   DATE NOT NULL,
    status           VARCHAR(30) NOT NULL DEFAULT 'ativa'
                     CHECK (status IN ('ativa', 'renovada', 'cancelada'))
);

CREATE TABLE IF NOT EXISTS sinistros (
    id          SERIAL PRIMARY KEY,
    apolice_id  INTEGER NOT NULL REFERENCES apolices(id) ON DELETE CASCADE,
    data        DATE NOT NULL,
    descricao   TEXT NOT NULL,
    valor       NUMERIC(10, 2) NOT NULL DEFAULT 0
);

-- Sinais de uso e relacionamento usados pela previsão de renovação
CREATE TABLE IF NOT EXISTS interacoes (
    id          SERIAL PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    tipo        VARCHAR(60) NOT NULL,  -- ex: login_portal, chamado_suporte, reclamacao, elogio
    data        DATE NOT NULL,
    resumo      TEXT
);

-- Saída do modelo (heurístico) de previsão de receita e risco de cancelamento
CREATE TABLE IF NOT EXISTS previsoes_renovacao (
    id                    SERIAL PRIMARY KEY,
    apolice_id            INTEGER NOT NULL REFERENCES apolices(id) ON DELETE CASCADE,
    probabilidade_renovacao NUMERIC(5, 2) NOT NULL, -- 0-100
    receita_projetada      NUMERIC(10, 2) NOT NULL,
    risco                 VARCHAR(20) NOT NULL CHECK (risco IN ('baixo', 'medio', 'alto')),
    fatores               JSONB,
    calculado_em          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Log de contatos de renovação disparados automaticamente pela IA
CREATE TABLE IF NOT EXISTS contatos_renovacao (
    id           SERIAL PRIMARY KEY,
    apolice_id   INTEGER NOT NULL REFERENCES apolices(id) ON DELETE CASCADE,
    canal        VARCHAR(30) NOT NULL DEFAULT 'email',
    mensagem     TEXT NOT NULL,
    motivo       VARCHAR(30) NOT NULL DEFAULT 'risco_baixo'
                 CHECK (motivo IN ('risco_baixo', 'risco_medio', 'risco_alto')),
    enviado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Base de conhecimento consultada via RAG (embeddings gerados pela OpenAI,
-- text-embedding-3-small = 1536 dimensões)
CREATE TABLE IF NOT EXISTS documentos (
    id             SERIAL PRIMARY KEY,
    titulo         VARCHAR(255) NOT NULL,
    seguradora_id  INTEGER REFERENCES seguradoras(id) ON DELETE SET NULL,
    conteudo       TEXT NOT NULL,
    embedding      vector(1536),
    criado_em      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índice aproximado para busca por similaridade (cosine distance)
CREATE INDEX IF NOT EXISTS documentos_embedding_idx
    ON documentos USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS apolices_data_renovacao_idx ON apolices (data_renovacao);
CREATE INDEX IF NOT EXISTS interacoes_cliente_idx ON interacoes (cliente_id);
