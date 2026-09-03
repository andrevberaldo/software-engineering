-- Dados fictícios da NovaSeguro Corretora, usados como exemplo/demo.

-- Usuário administrador padrão (login: admin@novaseguro.com.br / senha: admin)
INSERT INTO users (email, password_hash, name, role)
VALUES (
    'admin@novaseguro.com.br',
    '$2b$10$AwwPYatOtwYOqZ6Y88SpGOrJiWGvhW7ERSedOQsvBXtze745aAySa',
    'Administrador',
    'admin'
)
ON CONFLICT (email) DO NOTHING;

-- ---------------------------------------------------------------------
-- Seguradoras parceiras
-- ---------------------------------------------------------------------
INSERT INTO seguradoras (nome) VALUES
    ('Seguradora Atlas'),
    ('Seguradora Horizonte'),
    ('Seguradora Confiança'),
    ('Seguradora Vitalis')
ON CONFLICT (nome) DO NOTHING;

-- ---------------------------------------------------------------------
-- Clientes
-- ---------------------------------------------------------------------
INSERT INTO clientes (nome, email, corretor_responsavel) VALUES
    ('Mariana Costa',   'mariana.costa@example.com',   'Ana Beraldo'),
    ('Roberto Alves',   'roberto.alves@example.com',   'Ana Beraldo'),
    ('Fernanda Lima',   'fernanda.lima@example.com',   'Bruno Teixeira'),
    ('Eduardo Santos',  'eduardo.santos@example.com',  'Bruno Teixeira'),
    ('Juliana Pereira', 'juliana.pereira@example.com', 'Ana Beraldo'),
    ('Carlos Mendes',   'carlos.mendes@example.com',   'Bruno Teixeira'),
    ('Beatriz Rocha',   'beatriz.rocha@example.com',   'Ana Beraldo'),
    ('Thiago Almeida',  'thiago.almeida@example.com',  'Bruno Teixeira')
ON CONFLICT (email) DO NOTHING;

-- ---------------------------------------------------------------------
-- Apólices (datas relativas a hoje, para a demo de renovação fazer sentido
-- sempre que o banco for semeado)
-- ---------------------------------------------------------------------
INSERT INTO apolices (cliente_id, seguradora_id, tipo_cobertura, valor_mensal, data_inicio, data_renovacao, status)
SELECT c.id, s.id, v.tipo_cobertura, v.valor_mensal,
       CURRENT_DATE - (v.dias_desde_inicio || ' days')::interval,
       CURRENT_DATE + (v.dias_ate_renovacao || ' days')::interval,
       'ativa'
FROM (VALUES
    ('mariana.costa@example.com',   'Seguradora Atlas',       'Auto Completo',        320.00, 350, 10),
    ('roberto.alves@example.com',   'Seguradora Horizonte',   'Residencial',          145.00, 355, 15),
    ('fernanda.lima@example.com',   'Seguradora Confiança',   'Auto Compreensivo',    410.00, 300, 60),
    ('eduardo.santos@example.com',  'Seguradora Atlas',       'Vida em Grupo',        95.00,  200, 200),
    ('juliana.pereira@example.com', 'Seguradora Vitalis',     'Auto Completo',        365.00, 358, 8),
    ('carlos.mendes@example.com',   'Seguradora Horizonte',   'Residencial',          130.00, 180, 120),
    ('beatriz.rocha@example.com',   'Seguradora Confiança',   'Empresarial',          890.00, 340, 22),
    ('thiago.almeida@example.com',  'Seguradora Vitalis',     'Auto Compreensivo',    380.00, 90,  270)
) AS v(email_cliente, nome_seguradora, tipo_cobertura, valor_mensal, dias_desde_inicio, dias_ate_renovacao)
JOIN clientes c ON c.email = v.email_cliente
JOIN seguradoras s ON s.nome = v.nome_seguradora;

-- Uma segunda apólice para dois clientes, para exercitar "mais de uma apólice por cliente"
INSERT INTO apolices (cliente_id, seguradora_id, tipo_cobertura, valor_mensal, data_inicio, data_renovacao, status)
SELECT c.id, s.id, v.tipo_cobertura, v.valor_mensal,
       CURRENT_DATE - (v.dias_desde_inicio || ' days')::interval,
       CURRENT_DATE + (v.dias_ate_renovacao || ' days')::interval,
       'ativa'
FROM (VALUES
    ('mariana.costa@example.com', 'Seguradora Horizonte', 'Residencial', 110.00, 120, 95),
    ('beatriz.rocha@example.com', 'Seguradora Atlas',     'Vida em Grupo', 60.00, 60, 300)
) AS v(email_cliente, nome_seguradora, tipo_cobertura, valor_mensal, dias_desde_inicio, dias_ate_renovacao)
JOIN clientes c ON c.email = v.email_cliente
JOIN seguradoras s ON s.nome = v.nome_seguradora;

-- ---------------------------------------------------------------------
-- Sinistros
-- ---------------------------------------------------------------------
INSERT INTO sinistros (apolice_id, data, descricao, valor)
SELECT a.id, CURRENT_DATE - (v.dias_atras || ' days')::interval, v.descricao, v.valor
FROM (VALUES
    ('mariana.costa@example.com',   'Auto Completo',     40,  'Colisão traseira em estacionamento', 3200.00),
    ('juliana.pereira@example.com', 'Auto Completo',     15,  'Vidro quebrado',                       450.00),
    ('beatriz.rocha@example.com',   'Empresarial',        70, 'Furto de equipamentos no escritório', 8900.00)
) AS v(email_cliente, tipo_cobertura, dias_atras, descricao, valor)
JOIN clientes c ON c.email = v.email_cliente
JOIN apolices a ON a.cliente_id = c.id AND a.tipo_cobertura = v.tipo_cobertura;

-- ---------------------------------------------------------------------
-- Interações (sinais de uso e relacionamento)
-- ---------------------------------------------------------------------
INSERT INTO interacoes (cliente_id, tipo, data, resumo)
SELECT c.id, v.tipo, CURRENT_DATE - (v.dias_atras || ' days')::interval, v.resumo
FROM (VALUES
    ('mariana.costa@example.com',   'reclamacao',     5,  'Reclamou da demora no atendimento do sinistro'),
    ('mariana.costa@example.com',   'chamado_suporte',20, 'Dúvida sobre cobertura de vidros'),
    ('juliana.pereira@example.com', 'reclamacao',     3,  'Insatisfeita com o valor do reajuste'),
    ('juliana.pereira@example.com', 'reclamacao',     18, 'Comparando preço com outra corretora'),
    ('beatriz.rocha@example.com',   'chamado_suporte',10, 'Solicitou aumento de cobertura empresarial'),
    ('roberto.alves@example.com',   'login_portal',   2,  'Consultou apólice pelo portal'),
    ('roberto.alves@example.com',   'elogio',         30, 'Elogiou o atendimento do corretor'),
    ('fernanda.lima@example.com',   'login_portal',   7,  'Consultou boletos'),
    ('eduardo.santos@example.com',  'login_portal',   45, 'Atualizou dados cadastrais'),
    ('carlos.mendes@example.com',   'elogio',         12, 'Indicou a corretora para um amigo'),
    ('thiago.almeida@example.com',  'login_portal',   5,  'Consultou cobertura da viagem')
) AS v(email_cliente, tipo, dias_atras, resumo)
JOIN clientes c ON c.email = v.email_cliente;

-- ---------------------------------------------------------------------
-- Documentos para a base de conhecimento (RAG). O campo embedding fica
-- NULL até que o script seed_embeddings.py seja executado com uma
-- OPENAI_API_KEY válida — a busca semântica só funciona a partir daí.
-- ---------------------------------------------------------------------
INSERT INTO documentos (titulo, seguradora_id, conteudo)
SELECT v.titulo, s.id, v.conteudo
FROM (VALUES
    ('Seguradora Atlas — Manual de Auto Completo', 'Seguradora Atlas',
     'O plano Auto Completo da Seguradora Atlas cobre colisão, roubo, furto e incêndio. '
     'A franquia padrão é de 8% do valor do veículo, podendo ser reduzida para 5% mediante '
     'contratação do pacote "Franquia Reduzida". Carro reserva incluso por até 15 dias em caso de sinistro.'),
    ('Seguradora Atlas — Vida em Grupo', 'Seguradora Atlas',
     'O seguro de Vida em Grupo da Atlas garante indenização por morte natural ou acidental, '
     'além de assistência funeral. Carência de 60 dias para morte natural; sem carência para acidentes.'),
    ('Seguradora Horizonte — Residencial', 'Seguradora Horizonte',
     'O seguro Residencial Horizonte cobre incêndio, queda de raio, explosão, roubo de bens e '
     'danos elétricos. Assistência 24h inclui chaveiro, encanador e eletricista, limitada a 4 acionamentos por ano.'),
    ('Seguradora Confiança — Auto Compreensivo', 'Seguradora Confiança',
     'O plano Auto Compreensivo da Confiança amplia a cobertura padrão incluindo vidros, retrovisores '
     'e faróis sem acionamento de franquia. Também cobre danos a terceiros até R$ 100.000,00.'),
    ('Seguradora Confiança — Empresarial', 'Seguradora Confiança',
     'O seguro Empresarial da Confiança cobre incêndio, roubo de equipamentos, responsabilidade civil '
     'e lucros cessantes por até 90 dias de interrupção das atividades.'),
    ('Seguradora Vitalis — Auto Completo', 'Seguradora Vitalis',
     'O Auto Completo Vitalis inclui assistência 24h em todo o território nacional, carro reserva por '
     '10 dias e cobertura para acessórios originais de fábrica até R$ 5.000,00.'),
    ('Política geral da NovaSeguro — Renovação de apólices', NULL,
     'Todas as apólices intermediadas pela NovaSeguro são renovadas anualmente. O corretor responsável '
     'deve ser notificado sempre que uma apólice estiver a menos de 30 dias do vencimento, para que o '
     'cliente seja contatado com antecedência e eventuais ajustes de cobertura sejam avaliados.'),
    ('Política geral da NovaSeguro — Atendimento a sinistros', NULL,
     'Sinistros devem ser registrados em até 48 horas do ocorrido. O corretor acompanha o andamento junto '
     'à seguradora e mantém o cliente informado a cada etapa, evitando reclamações por falta de retorno.')
) AS v(titulo, nome_seguradora, conteudo)
LEFT JOIN seguradoras s ON s.nome = v.nome_seguradora;
