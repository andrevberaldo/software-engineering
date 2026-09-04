-- Segundo assinante fictício, só para provar que o isolamento multi-tenant
-- e a identidade visual por assinante funcionam de ponta a ponta. Mesmo
-- estilo de 02_seed.sql, com um dataset bem menor (não é para exercitar o
-- modelo de previsão, só a separação de dados e a marca).

INSERT INTO tenants (slug, nome_empresa, header_color) VALUES
    ('beta', 'Beta Seguros', '#7A1F3D')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO users (tenant_id, email, password_hash, name, role)
SELECT t.id, 'admin@betaseguros.com.br',
       '$2b$10$azDcftB6Ppb8WuqdotVVd.WaUYevlnddTi0xPrk9bN5L1nP9/ngrC',
       'Administrador', 'admin'
FROM tenants t WHERE t.slug = 'beta'
ON CONFLICT (tenant_id, email) DO NOTHING;

INSERT INTO seguradoras (tenant_id, nome)
SELECT t.id, v.nome
FROM tenants t, (VALUES ('Seguradora Ipê'), ('Seguradora Aurora')) AS v(nome)
WHERE t.slug = 'beta'
ON CONFLICT (tenant_id, nome) DO NOTHING;

INSERT INTO clientes (tenant_id, nome, email, corretor_responsavel)
SELECT t.id, v.nome, v.email, v.corretor
FROM tenants t, (VALUES
    ('Larissa Nogueira', 'larissa.nogueira@example.com', 'Diego Farias'),
    ('Marcelo Prado',    'marcelo.prado@example.com',    'Diego Farias'),
    ('Renata Suzuki',    'renata.suzuki@example.com',    'Diego Farias')
) AS v(nome, email, corretor)
WHERE t.slug = 'beta'
ON CONFLICT (tenant_id, email) DO NOTHING;

INSERT INTO apolices (
    tenant_id, cliente_id, seguradora_id, tipo_cobertura, valor_mensal,
    data_inicio, data_renovacao, status, valor_patrimonio_segurado, descricao_patrimonio
)
SELECT t.id, c.id, s.id, v.tipo_cobertura, v.valor_mensal,
       CURRENT_DATE - (v.dias_desde_inicio || ' days')::interval,
       CURRENT_DATE + (v.dias_ate_renovacao || ' days')::interval,
       'ativa', v.valor_patrimonio, v.descricao
FROM (VALUES
    ('larissa.nogueira@example.com', 'Seguradora Ipê',    'Auto Completo', 300.00, 200, 20,  92000.00, 'Chevrolet Onix 2023, hatch, uso particular'),
    ('marcelo.prado@example.com',    'Seguradora Aurora', 'Residencial',   180.00, 150, 45,  460000.00,'Apartamento de 2 quartos, região central, 70m²'),
    ('renata.suzuki@example.com',    'Seguradora Ipê',    'Empresarial',   950.00, 90,  10,  980000.00,'Equipamentos e estoque de loja de varejo')
) AS v(email_cliente, nome_seguradora, tipo_cobertura, valor_mensal, dias_desde_inicio, dias_ate_renovacao, valor_patrimonio, descricao)
JOIN tenants t ON t.slug = 'beta'
JOIN clientes c ON c.tenant_id = t.id AND c.email = v.email_cliente
JOIN seguradoras s ON s.tenant_id = t.id AND s.nome = v.nome_seguradora;
