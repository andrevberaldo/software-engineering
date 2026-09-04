-- Transforma o app de single-tenant (uma corretora só) em multi-tenant de
-- verdade: cada assinante ("tenant") tem seus próprios dados isolados e sua
-- própria identidade visual (nome, cor do header, logotipo).
--
-- Decisão de segurança: em rotas autenticadas, o tenant_id sempre vem da
-- claim do JWT (definida no login) — nunca é re-derivado de host/query
-- string depois disso. Resolução por subdomínio (Host) só é usada nos
-- pontos sem sessão ainda: login e as leituras públicas de branding.

CREATE TABLE tenants (
    id            SERIAL PRIMARY KEY,
    slug          VARCHAR(63) NOT NULL UNIQUE
                  CHECK (slug ~ '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'),
    nome_empresa  VARCHAR(255) NOT NULL,
    header_color  VARCHAR(7) NOT NULL DEFAULT '#1E2761'
                  CHECK (header_color ~ '^#[0-9A-Fa-f]{6}$'),
    logo_path     VARCHAR(500),
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO tenants (id, slug, nome_empresa, header_color) VALUES
    (1, 'novaseguro', 'NovaSeguro Corretora', '#1E2761');
SELECT setval(pg_get_serial_sequence('tenants', 'id'), 1);

-- ---------------------------------------------------------------------
-- tenant_id em todas as tabelas existentes: adiciona, faz backfill pro
-- tenant 1 (dados que já existiam antes do multi-tenant) e só então torna
-- obrigatório.
-- ---------------------------------------------------------------------
ALTER TABLE users ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE seguradoras ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE clientes ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE apolices ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE sinistros ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE interacoes ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE previsoes_renovacao ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE contatos_renovacao ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE documentos ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
ALTER TABLE documento_chunks ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);

UPDATE users SET tenant_id = 1;
UPDATE seguradoras SET tenant_id = 1;
UPDATE clientes SET tenant_id = 1;
UPDATE apolices SET tenant_id = 1;
UPDATE sinistros SET tenant_id = 1;
UPDATE interacoes SET tenant_id = 1;
UPDATE previsoes_renovacao SET tenant_id = 1;
UPDATE contatos_renovacao SET tenant_id = 1;
UPDATE documentos SET tenant_id = 1;
UPDATE documento_chunks SET tenant_id = 1;

ALTER TABLE users ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE seguradoras ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE clientes ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE apolices ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE sinistros ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE interacoes ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE previsoes_renovacao ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE contatos_renovacao ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE documentos ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE documento_chunks ALTER COLUMN tenant_id SET NOT NULL;

-- ---------------------------------------------------------------------
-- Unicidade global -> por tenant (dois assinantes podem ter um cliente
-- com o mesmo e-mail, ou uma seguradora parceira com o mesmo nome).
-- ---------------------------------------------------------------------
ALTER TABLE users DROP CONSTRAINT users_email_key,
    ADD CONSTRAINT users_tenant_email_key UNIQUE (tenant_id, email);
ALTER TABLE seguradoras DROP CONSTRAINT seguradoras_nome_key,
    ADD CONSTRAINT seguradoras_tenant_nome_key UNIQUE (tenant_id, nome);
ALTER TABLE clientes DROP CONSTRAINT clientes_email_key,
    ADD CONSTRAINT clientes_tenant_email_key UNIQUE (tenant_id, email);

-- ---------------------------------------------------------------------
-- FKs compostas (tenant_id, id): torna estruturalmente impossível, a
-- nível de banco, vincular um registro filho a um pai de outro tenant —
-- mesmo que um endpoint futuro esqueça de filtrar por tenant_id.
-- ---------------------------------------------------------------------
ALTER TABLE clientes ADD CONSTRAINT clientes_tenant_id_uq UNIQUE (tenant_id, id);
ALTER TABLE seguradoras ADD CONSTRAINT seguradoras_tenant_id_uq UNIQUE (tenant_id, id);
ALTER TABLE apolices ADD CONSTRAINT apolices_tenant_id_uq UNIQUE (tenant_id, id);
ALTER TABLE documentos ADD CONSTRAINT documentos_tenant_id_uq UNIQUE (tenant_id, id);

ALTER TABLE apolices DROP CONSTRAINT apolices_cliente_id_fkey,
    ADD CONSTRAINT apolices_cliente_tenant_fk FOREIGN KEY (tenant_id, cliente_id)
        REFERENCES clientes (tenant_id, id) ON DELETE CASCADE;
ALTER TABLE apolices DROP CONSTRAINT apolices_seguradora_id_fkey,
    ADD CONSTRAINT apolices_seguradora_tenant_fk FOREIGN KEY (tenant_id, seguradora_id)
        REFERENCES seguradoras (tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE sinistros DROP CONSTRAINT sinistros_apolice_id_fkey,
    ADD CONSTRAINT sinistros_apolice_tenant_fk FOREIGN KEY (tenant_id, apolice_id)
        REFERENCES apolices (tenant_id, id) ON DELETE CASCADE;
ALTER TABLE interacoes DROP CONSTRAINT interacoes_cliente_id_fkey,
    ADD CONSTRAINT interacoes_cliente_tenant_fk FOREIGN KEY (tenant_id, cliente_id)
        REFERENCES clientes (tenant_id, id) ON DELETE CASCADE;
ALTER TABLE previsoes_renovacao DROP CONSTRAINT previsoes_renovacao_apolice_id_fkey,
    ADD CONSTRAINT previsoes_apolice_tenant_fk FOREIGN KEY (tenant_id, apolice_id)
        REFERENCES apolices (tenant_id, id) ON DELETE CASCADE;
ALTER TABLE contatos_renovacao DROP CONSTRAINT contatos_renovacao_apolice_id_fkey,
    ADD CONSTRAINT contatos_apolice_tenant_fk FOREIGN KEY (tenant_id, apolice_id)
        REFERENCES apolices (tenant_id, id) ON DELETE CASCADE;
-- seguradora_id em documentos é nullable: MATCH SIMPLE (padrão do Postgres)
-- deixa a FK composta passar quando qualquer coluna referenciante é NULL.
ALTER TABLE documentos DROP CONSTRAINT documentos_seguradora_id_fkey,
    ADD CONSTRAINT documentos_seguradora_tenant_fk FOREIGN KEY (tenant_id, seguradora_id)
        REFERENCES seguradoras (tenant_id, id) ON DELETE SET NULL;
ALTER TABLE documento_chunks DROP CONSTRAINT documento_chunks_documento_id_fkey,
    ADD CONSTRAINT documento_chunks_documento_tenant_fk FOREIGN KEY (tenant_id, documento_id)
        REFERENCES documentos (tenant_id, id) ON DELETE CASCADE;

-- ---------------------------------------------------------------------
-- Índices: tenant_id como coluna líder evita que um tenant grande deixe
-- consultas de um tenant pequeno mais lentas (index range scan isola o
-- intervalo de cada tenant).
-- ---------------------------------------------------------------------
CREATE INDEX documento_chunks_tenant_idx ON documento_chunks (tenant_id);
CREATE INDEX apolices_tenant_status_idx ON apolices (tenant_id, status);
