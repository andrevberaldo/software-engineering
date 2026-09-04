# NovaSeguro Copiloto

Aplicação de exemplo que implementa o caso prático explorado na apresentação
"Como Nascem os Produtos Digitais": um copiloto de IA para uma corretora de
seguros fictícia (NovaSeguro), com consulta a apólices via RAG, visão
relacionada de clientes/seguradoras, previsão de receita e risco de
cancelamento, e antecipação automatizada de renovação.

## Arquitetura

```
┌─────────────┐                          ┌────────────────────┐      ┌──────────────┐
│  Next.js +  │ ───────────────────────▶ │  Backend Python     │ ───▶ │   OpenAI     │
│  MUI (3000) │ ◀─────────────────────── │  (FastAPI) — auth,  │ ◀─── │   (LLM)      │
│             │                          │  dados, deep agent, │      │              │
└─────────────┘                          │  8000               │      └──────────────┘
                                          └──────────┬──────────┘
                                                      │
                                                      ▼
                                   ┌────────────────────────────────────┐
                                   │   Postgres + pgvector (5432)        │
                                   │   users, clientes, apólices,        │
                                   │   documentos + documento_chunks     │
                                   └────────────────────────────────────┘
                                                      │
                                                      ▼
                                   ┌────────────────────────────────────┐
                                   │  Volume "documentos_data" (backend) │
                                   │  PDFs originais, para download      │
                                   └────────────────────────────────────┘
```

Não existe um BFF separado: o frontend fala diretamente com o backend
Python, que concentra autenticação, dados de negócio e o agente de IA — um
único serviço a mais, sem hop de rede nem lógica duplicada entre duas
linguagens (veja a justificativa dessa escolha no fim desta seção).

- **frontend/** — Next.js (App Router) + Material UI. Página inicial pública
  com apresentação da ferramenta e botão "Entrar"; páginas `/dashboard`,
  `/chat`, `/clientes` e `/documentos` protegidas por sessão (verificada em
  `proxy.ts`). A página `/clientes` funciona como um dashboard do
  patrimônio segurado: para cada cliente, mostra o patrimônio total
  assegurado e, ao expandir a linha, o valor e a descrição do patrimônio
  de cada apólice (o carro, o imóvel, os equipamentos da empresa), além das
  datas de início e de renovação.
- **backend/** — Python/FastAPI. Além do *deep agent* (biblioteca
  [`deepagents`](https://pypi.org/project/deepagents/), construída sobre
  LangChain/LangGraph) com ferramentas de RAG (pgvector), consulta
  relacional de clientes/apólices, previsão heurística de renovação e
  registro de contatos automáticos de renovação, o backend também cuida de:
  - **Autenticação** (`/auth/login`, `/auth/logout`, `/auth/me`): confere a
    senha com bcrypt contra a tabela `users` e emite o cookie de sessão
    (JWT, `httpOnly`) que o `proxy.ts` do Next.js e as próprias rotas do
    backend usam para proteger o que precisa de login.
  - **Dados de negócio** (`/data/dashboard`, `/data/clientes`,
    `/data/seguradoras`): consultas diretas ao Postgres para os
    indicadores e a carteira de clientes exibidos no frontend.
  - **Ingestão de PDFs** (`/documents/*`) com
    [Docling](https://github.com/docling-project/docling) (veja a seção
    dedicada abaixo).
- **db/** — schema SQL, seed de dados fictícios e script para gerar os
  embeddings da base de conhecimento.

### Por que não tem um BFF?

A primeira versão desta aplicação tinha um BFF em Node/Express entre o
frontend e o backend de IA. Na prática, ele só fazia três coisas: login
(bcrypt + emissão de JWT em cookie), três consultas simples ao Postgres
(dashboard, clientes, seguradoras) e um proxy de streaming para upload/
download de PDF — nenhuma delas exclusiva de Node, e o backend Python já
mantém sua própria conexão com o banco. Com um único frontend e um único
backend de IA, esse hop extra só somava latência e mais um serviço para
subir/monitorar sem ganho real, então essas três responsabilidades foram
absorvidas pelo FastAPI e o BFF foi removido. Reintroduzir um BFF voltaria
a valer a pena se surgisse mais de um cliente (app mobile, painel interno)
consumindo backends diferentes, ou se quiséssemos manter o serviço de IA
livre de qualquer preocupação de sessão web.

## Login padrão

Usuário administrador semeado no banco:

- **Email:** `admin@novaseguro.com.br`
- **Senha:** `admin`

Apenas usuários autenticados acessam `/dashboard`, `/chat`, `/clientes` e
`/documentos` — isso é garantido tanto pelo `proxy.ts` do Next.js (que
verifica o JWT antes de renderizar a página) quanto pela dependência
`get_current_user` do backend (que protege as rotas da API lendo o mesmo
cookie de sessão).

## Rodando com Docker Compose

```bash
cp .env.example .env
# edite o .env e preencha OPENAI_API_KEY (e troque JWT_SECRET/POSTGRES_PASSWORD
# em qualquer ambiente que não seja a sua máquina local)

docker compose up --build
```

Serviços: frontend em `http://localhost:3000`, backend em `:8000`, Postgres
em `:5432`. O schema e o seed de dados fictícios rodam automaticamente na
primeira subida do Postgres (via `db/init/*.sql`).

Para gerar os embeddings pendentes (dos textos do seed e de qualquer PDF
enviado antes de configurar a chave), rode o script dentro do próprio
container `backend` — a pasta `db/` é montada nele para isso:

```bash
docker compose exec -e OPENAI_API_KEY=sk-... backend python db/seed_embeddings.py
```

(ou rode `db/seed_embeddings.py` localmente apontando `DATABASE_URL` para
`localhost:5432`, fora do container — veja a seção abaixo).

## Rodando localmente sem Docker

Requer Postgres 16+ com a extensão `pgvector` instalada e Node.js 20+ e
Python 3.11+.

```bash
# 1. Banco de dados
createdb novaseguro
psql -d novaseguro -f db/init/01_schema.sql
psql -d novaseguro -f db/init/02_seed.sql
psql -d novaseguro -f db/init/03_documentos_chunks.sql
psql -d novaseguro -f db/init/04_patrimonio_apolices.sql

# 2. Backend (Python)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha DATABASE_URL, OPENAI_API_KEY, JWT_SECRET
uvicorn app.main:app --reload --port 8000

# 3. Frontend (Next.js) — em outro terminal
cd frontend
npm install
cp .env.example .env.local   # mesmo JWT_SECRET do backend
npm run dev

# 4. (opcional) Embeddings para a busca RAG
cd backend && source .venv/bin/activate
OPENAI_API_KEY=sk-... python3 ../db/seed_embeddings.py
```

Acesse `http://localhost:3000`.

## Dados de exemplo

O seed cria 8 clientes fictícios, 4 seguradoras parceiras, 10 apólices com
datas de renovação espalhadas (de 8 a 300 dias a partir de hoje), alguns
sinistros e interações (elogios, reclamações, uso do portal) — o suficiente
para o modelo heurístico de previsão gerar respostas diferentes por
cliente. Veja `db/init/02_seed.sql`.

## Ingestão de PDFs (Docling)

A página `/documentos` (e a API por trás dela, `/documents/*` no backend)
permite enviar o PDF de uma apólice para virar conhecimento pesquisável do
assistente:

1. O PDF é salvo em disco — em Docker, no volume nomeado `documentos_data`
   montado em `/data/documentos` dentro do container `backend` (ou seja, o
   próprio `docker compose` funciona como armazenamento; o arquivo some se
   o volume for removido, mas sobrevive a `docker compose down`/restarts).
2. O [Docling](https://github.com/docling-project/docling) converte o PDF
   e o `HybridChunker` quebra o conteúdo em trechos coerentes com a
   estrutura do documento (respeitando títulos/seções).
3. Cada trecho vira uma linha em `documento_chunks`, com seu próprio
   embedding (OpenAI) — é isso que a ferramenta `buscar_documentos` do
   agente consulta via similaridade.
4. A tabela `documentos` guarda só os metadados (título, seguradora,
   nome/caminho do arquivo, tamanho) — é o que alimenta o botão "Baixar" na
   tela e o endpoint `GET /documents/{id}/download`.

Endpoints (todos exigem o cookie de sessão emitido em `/auth/login`):

| Rota | O que faz |
|---|---|
| `POST /documents/upload` | multipart (`titulo`, `seguradora_id` opcional, `file`); processa e responde com o total de chunks gerados |
| `GET /documents` | lista documentos + contagem de chunks |
| `GET /documents/{id}/download` | download do PDF original |

**Sobre o modelo de layout do Docling:** na primeira conversão de um PDF,
o Docling baixa um modelo de análise de layout do Hugging Face Hub (fica
em cache depois disso). Isso exige que o container/máquina do `backend`
tenha acesso de saída a `huggingface.co` na primeira vez que alguém enviar
um PDF — normal em qualquer ambiente com internet padrão, mas vale saber
caso o backend rode atrás de um proxy restritivo. OCR vem desligado por
padrão (`do_ocr=False` em `app/agent/ingestion.py`), já que a maioria das
apólices é gerada digitalmente pelas seguradoras; ligue essa opção se
precisar processar PDFs escaneados (o Docling baixa um modelo de OCR
adicional nesse caso).

Assim como os textos digitados manualmente no seed, um PDF enviado sem uma
`OPENAI_API_KEY` configurada é processado e fica salvo normalmente (dá
para baixá-lo), só sem embedding — rode `db/seed_embeddings.py` depois de
configurar a chave para preencher os embeddings pendentes de qualquer
chunk, incluindo os de uploads antigos.

## Sobre o modelo de previsão

`backend/app/agent/prediction.py` implementa um modelo **heurístico**
(regras simples, não machine learning) só para tornar a demonstração
funcional de ponta a ponta sem precisar de um histórico real de renovações
para treinar um modelo. Está isolado em uma função só, pensado para ser
substituído por um modelo de verdade no futuro.
