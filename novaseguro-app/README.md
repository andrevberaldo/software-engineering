# NovaSeguro Copiloto

Aplicação de exemplo que implementa o caso prático explorado na apresentação
"Como Nascem os Produtos Digitais": um copiloto de IA para uma corretora de
seguros fictícia (NovaSeguro), com consulta a apólices via RAG, visão
relacionada de clientes/seguradoras, previsão de receita e risco de
cancelamento, e antecipação automatizada de renovação.

## Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌────────────────────┐      ┌──────────────┐
│  Next.js +  │ ───▶ │  BFF (Node/  │ ───▶ │  Backend Python     │ ───▶ │   OpenAI     │
│  MUI (3000) │ ◀─── │  Express) —  │ ◀─── │  (FastAPI) — deep   │ ◀─── │   (LLM)      │
│             │      │  4000        │      │  agent, 8000        │      │              │
└─────────────┘      └──────┬───────┘      └──────────┬─────────┘      └──────────────┘
                             │                          │
                             ▼                          ▼
                      ┌────────────────────────────────────┐
                      │   Postgres + pgvector (5432)        │
                      │   users, clientes, apólices,        │
                      │   sinistros, documentos (RAG), ...  │
                      └────────────────────────────────────┘
```

- **frontend/** — Next.js (App Router) + Material UI. Página inicial pública
  com apresentação da ferramenta e botão "Entrar"; páginas `/dashboard`,
  `/chat` e `/clientes` protegidas por sessão (verificada em `proxy.ts`).
- **bff/** — Node.js/Express. Único serviço que fala com o Postgres para
  autenticação e dados simples; emite o cookie de sessão (JWT) e repassa
  esse mesmo token como Bearer para o backend de IA.
- **backend/** — Python/FastAPI expondo um *deep agent* (biblioteca
  [`deepagents`](https://pypi.org/project/deepagents/), construída sobre
  LangChain/LangGraph) com ferramentas de RAG (pgvector), consulta
  relacional de clientes/apólices, previsão heurística de renovação e
  registro de contatos automáticos de renovação. Usa a OpenAI como LLM.
- **db/** — schema SQL, seed de dados fictícios e script para gerar os
  embeddings da base de conhecimento.

## Login padrão

Usuário administrador semeado no banco:

- **Email:** `admin@novaseguro.com.br`
- **Senha:** `admin`

Apenas usuários autenticados acessam `/dashboard`, `/chat` e `/clientes` —
isso é garantido tanto pelo `proxy.ts` do Next.js (que verifica o JWT antes
de renderizar a página) quanto pelo middleware `requireAuth` do BFF (que
protege as rotas de API).

## Rodando com Docker Compose

```bash
cp .env.example .env
# edite o .env e preencha OPENAI_API_KEY (e troque JWT_SECRET/POSTGRES_PASSWORD
# em qualquer ambiente que não seja a sua máquina local)

docker compose up --build
```

Serviços: frontend em `http://localhost:3000`, BFF em `:4000`, backend em
`:8000`, Postgres em `:5432`. O schema e o seed de dados fictícios rodam
automaticamente na primeira subida do Postgres (via `db/init/*.sql`).

Para habilitar a busca por documentos (RAG), gere os embeddings uma vez, com
uma OPENAI_API_KEY válida:

```bash
docker compose exec backend python -m pip install -q openai pgvector psycopg[binary]
docker compose exec -e OPENAI_API_KEY=sk-... backend python /app/../db/seed_embeddings.py
```

(ou rode `db/seed_embeddings.py` localmente apontando `DATABASE_URL` para
`localhost:5432`, fora do container — veja a seção abaixo).

## Rodando localmente sem Docker

Requer Postgres 16+ com a extensão `pgvector` instalada, Node.js 20+ e
Python 3.11+.

```bash
# 1. Banco de dados
createdb novaseguro
psql -d novaseguro -f db/init/01_schema.sql
psql -d novaseguro -f db/init/02_seed.sql

# 2. Backend (Python)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha DATABASE_URL, OPENAI_API_KEY, JWT_SECRET
uvicorn app.main:app --reload --port 8000

# 3. BFF (Node.js) — em outro terminal
cd bff
npm install
cp .env.example .env   # mesmo JWT_SECRET do backend
npm run dev

# 4. Frontend (Next.js) — em outro terminal
cd frontend
npm install
cp .env.example .env.local   # mesmo JWT_SECRET
npm run dev

# 5. (opcional) Embeddings para a busca RAG
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

## Sobre o modelo de previsão

`backend/app/agent/prediction.py` implementa um modelo **heurístico**
(regras simples, não machine learning) só para tornar a demonstração
funcional de ponta a ponta sem precisar de um histórico real de renovações
para treinar um modelo. Está isolado em uma função só, pensado para ser
substituído por um modelo de verdade no futuro.
