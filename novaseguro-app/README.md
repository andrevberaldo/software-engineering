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
                      │   documentos + documento_chunks     │
                      └────────────────────────────────────┘
                                       │
                                       ▼
                      ┌────────────────────────────────────┐
                      │  Volume "documentos_data" (backend) │
                      │  PDFs originais, para download      │
                      └────────────────────────────────────┘
```

- **frontend/** — Next.js (App Router) + Material UI. Página inicial pública
  com apresentação da ferramenta e botão "Entrar"; páginas `/dashboard`,
  `/chat`, `/clientes` e `/documentos` protegidas por sessão (verificada em
  `proxy.ts`).
- **bff/** — Node.js/Express. Único serviço que fala com o Postgres para
  autenticação e dados simples; emite o cookie de sessão (JWT) e repassa
  esse mesmo token como Bearer para o backend de IA. Também repassa (via
  streaming, sem carregar o arquivo inteiro em memória) o upload e o
  download de PDFs para o backend.
- **backend/** — Python/FastAPI expondo um *deep agent* (biblioteca
  [`deepagents`](https://pypi.org/project/deepagents/), construída sobre
  LangChain/LangGraph) com ferramentas de RAG (pgvector), consulta
  relacional de clientes/apólices, previsão heurística de renovação e
  registro de contatos automáticos de renovação. Usa a OpenAI como LLM.
  Também expõe `/documents/*` para ingestão de PDFs com
  [Docling](https://github.com/docling-project/docling) (veja a seção
  dedicada abaixo).
- **db/** — schema SQL, seed de dados fictícios e script para gerar os
  embeddings da base de conhecimento.

## Login padrão

Usuário administrador semeado no banco:

- **Email:** `admin@novaseguro.com.br`
- **Senha:** `admin`

Apenas usuários autenticados acessam `/dashboard`, `/chat`, `/clientes` e
`/documentos` —
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

Para gerar os embeddings pendentes (dos textos do seed e de qualquer PDF
enviado antes de configurar a chave), rode o script dentro do próprio
container `backend` — a pasta `db/` é montada nele para isso:

```bash
docker compose exec -e OPENAI_API_KEY=sk-... backend python db/seed_embeddings.py
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
psql -d novaseguro -f db/init/03_documentos_chunks.sql

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

Endpoints (todos exigem sessão autenticada, repassada pelo BFF):

| Rota (backend) | Via BFF | O que faz |
|---|---|---|
| `POST /documents/upload` | `POST /api/documents/upload` | multipart (`titulo`, `seguradora_id` opcional, `file`); processa e responde com o total de chunks gerados |
| `GET /documents` | `GET /api/documents` | lista documentos + contagem de chunks |
| `GET /documents/{id}/download` | `GET /api/documents/{id}/download` | stream do PDF original |

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
