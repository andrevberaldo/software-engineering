-- Cada apólice segura um patrimônio específico do cliente (o veículo, o
-- imóvel, os equipamentos da empresa, etc.). Guardamos o valor desse
-- patrimônio e uma descrição curta para alimentar o dashboard de clientes.

ALTER TABLE apolices
    ADD COLUMN IF NOT EXISTS valor_patrimonio_segurado NUMERIC(14, 2),
    ADD COLUMN IF NOT EXISTS descricao_patrimonio      VARCHAR(500);

-- Preenche o patrimônio segurado das apólices fictícias do seed
-- (02_seed.sql), casando pelo trio cliente + seguradora + tipo de
-- cobertura, que é único entre as 10 apólices semeadas.
UPDATE apolices a
SET valor_patrimonio_segurado = v.valor_patrimonio,
    descricao_patrimonio = v.descricao
FROM (VALUES
    ('mariana.costa@example.com',   'Seguradora Atlas',       'Auto Completo',     85000.00,  'Honda Civic 2022, sedã, uso particular'),
    ('roberto.alves@example.com',   'Seguradora Horizonte',   'Residencial',       420000.00, 'Apartamento de 3 quartos, Zona Sul, 95m²'),
    ('fernanda.lima@example.com',   'Seguradora Confiança',   'Auto Compreensivo', 130000.00, 'Jeep Compass 2023, SUV, uso particular'),
    ('eduardo.santos@example.com',  'Seguradora Atlas',       'Vida em Grupo',     200000.00, 'Capital segurado por morte natural ou acidental'),
    ('juliana.pereira@example.com', 'Seguradora Vitalis',     'Auto Completo',     78000.00,  'Toyota Corolla 2021, sedã, uso particular'),
    ('carlos.mendes@example.com',   'Seguradora Horizonte',   'Residencial',       380000.00, 'Casa térrea, bairro residencial, 140m²'),
    ('beatriz.rocha@example.com',   'Seguradora Confiança',   'Empresarial',       1250000.00,'Equipamentos, estoque e mobiliário do escritório'),
    ('thiago.almeida@example.com',  'Seguradora Vitalis',     'Auto Compreensivo', 95000.00,  'Hyundai Creta 2023, SUV compacto, uso particular'),
    ('mariana.costa@example.com',   'Seguradora Horizonte',   'Residencial',       510000.00, 'Casa de veraneio no litoral, 110m²'),
    ('beatriz.rocha@example.com',   'Seguradora Atlas',       'Vida em Grupo',     150000.00, 'Capital segurado por morte natural ou acidental, extensão para sócios')
) AS v(email_cliente, nome_seguradora, tipo_cobertura, valor_patrimonio, descricao)
JOIN clientes c ON c.email = v.email_cliente
JOIN seguradoras s ON s.nome = v.nome_seguradora
WHERE a.cliente_id = c.id
  AND a.seguradora_id = s.id
  AND a.tipo_cobertura = v.tipo_cobertura;
