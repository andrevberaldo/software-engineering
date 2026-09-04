# NovaSeguro Copiloto

Aplicação de exemplo que implementa o caso prático explorado na apresentação
"Como Nascem os Produtos Digitais": um copiloto de IA para uma corretora de
seguros fictícia (NovaSeguro), com consulta a apólices via RAG, visão
relacionada de clientes/seguradoras, previsão de receita e risco de
cancelamento, e antecipação automatizada de renovação.

É um **SaaS multi-tenant de verdade**: cada assinante ("tenant") tem seus
dados completamente isolados dos demais e sua própria identidade visual
(nome da empresa, cor do cabeçalho, logotipo), editável por um admin em
**Configurações > Identidade Visual**. Veja a seção
[Multi-tenant e identidade visual](#multi-tenant-e-identidade-visual).

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
  - **Identidade visual** (`/tenants/branding`, leitura/gravação; e
    `/public/branding` + `/public/tenants/{slug}/logo`, leitura pública):
    veja a seção dedicada abaixo.
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

Dois assinantes fictícios são semeados no banco, para provar o isolamento
multi-tenant e a identidade visual por assinante:

| Assinante | Slug | Email | Senha | Cor do cabeçalho |
|---|---|---|---|---|
| NovaSeguro Corretora | `novaseguro` | `admin@novaseguro.com.br` | `admin` | `#1E2761` (navy) |
| Beta Seguros | `beta` | `admin@betaseguros.com.br` | `admin` | `#7A1F3D` (bordô) |

Sem subdomínio configurado (ex.: acessando `http://localhost:3000`
direto), o login sempre resolve para o tenant padrão
(`DEFAULT_TENANT_SLUG`, `novaseguro`) — é assim que o assinante
`admin@betaseguros.com.br` só consegue entrar acessando pelo subdomínio
`beta` (veja [Testando multi-tenant por subdomínio
localmente](#testando-multi-tenant-por-subdomínio-localmente)).

Apenas usuários autenticados acessam `/dashboard`, `/chat`, `/clientes`,
`/documentos` e `/configuracoes` — isso é garantido tanto pelo `proxy.ts`
do Next.js (que verifica o JWT antes de renderizar a página) quanto pela
dependência `get_current_user` do backend (que protege as rotas da API
lendo o mesmo cookie de sessão). Só usuários com `role = 'admin'` veem o
item "Configurações" e conseguem de fato gravar mudanças em
`PUT /tenants/branding` — a checagem no `proxy.ts` é só UX, quem garante
de verdade é o `require_admin` do backend.

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
psql -d novaseguro -f db/init/05_multi_tenant.sql
psql -d novaseguro -f db/init/06_seed_tenant_beta.sql

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

## Multi-tenant e identidade visual

Cada assinante ("tenant") é uma linha em `tenants` (`slug`, `nome_empresa`,
`header_color`, `logo_path`). Todas as outras tabelas (`users`, `clientes`,
`apolices`, `documentos`, etc.) têm uma coluna `tenant_id` — e, além dela,
**chaves estrangeiras compostas** `(tenant_id, id)` (veja
`db/init/05_multi_tenant.sql`): isso torna estruturalmente impossível, a
nível de banco, vincular um registro filho a um pai de outro tenant, mesmo
que um endpoint futuro esqueça de filtrar por `tenant_id`.

**Regra de segurança central:** em qualquer rota autenticada, o
`tenant_id` vem exclusivamente da claim do JWT (definida no login) —
nunca é re-derivado de `Host`/query string naquela requisição. Resolução
de tenant por subdomínio (`app/tenancy.py: resolve_tenant_from_host`) só é
usada nos 3 pontos que ainda não têm sessão: `POST /auth/login`,
`GET /public/branding` e `GET /public/tenants/{slug}/logo`. Se o tenant
autenticado fosse re-derivado do host a cada chamada, um admin do tenant A
logado poderia trocar o parâmetro de host e ler/escrever dados do tenant B.

Isso também fecha um IDOR que existia antes do multi-tenant:
`GET /documents/{id}/download` hoje exige que o documento pertença ao
tenant do usuário autenticado, não só que o id exista.

### Resolução por subdomínio

Em produção, cada assinante acessa por um subdomínio próprio (ex.:
`acme.suaempresa.com`). Isso exige, fora do que este repositório provisiona:

- **DNS coringa** (`*.suaempresa.com`) apontando para os mesmos servidores.
- **Certificado TLS coringa** (ou um por subdomínio).
- `COOKIE_DOMAIN=.suaempresa.com` no backend, para o cookie de sessão
  valer em todos os subdomínios (por padrão é host-only, ou seja, funciona
  só com um domínio/tenant).
- `CORS_ORIGIN_REGEX=^https://.*\.suaempresa\.com$` no backend.

Um reverse proxy (Traefik/nginx) na frente dos containers para rotear
`*.suaempresa.com` para o `frontend` **não** está incluído no
`docker-compose.yml` deste repositório — é infraestrutura específica de
cada ambiente de deploy.

### Identidade visual (Configurações > Identidade Visual)

Só admins editam (`PUT /tenants/branding`, `require_admin` no backend).
Qualquer usuário autenticado só lê (`GET /tenants/branding`); a home
pública e o login usam a leitura sem autenticação
(`GET /public/branding?host=...`) para já mostrar a marca certa antes do
login.

O logotipo é sempre SVG, salvo como `tenants/{tenant_id}/logo.svg` (nome
fixo no backend — nunca confia na extensão enviada pelo cliente) e servido
via `GET /public/tenants/{slug}/logo`. Como é exibido via `<img src>` (não
inline), scripts embutidos no SVG não executam nesse contexto — mas
navegar direto para a URL do arquivo executaria, então o upload rejeita
conteúdo com `<script`, `on*=` ou `javascript:`, e a resposta do endpoint
sempre inclui `Content-Security-Policy: script-src 'none'; sandbox` como
proteção adicional.

### Testando multi-tenant por subdomínio localmente

`next dev` bloqueia por padrão requisições vindas de um host diferente do
que o servidor foi iniciado (proteção do próprio Next.js, não afeta
`next start`/produção). Para testar os dois assinantes de exemplo em
subdomínios diferentes na sua máquina:

1. Escolha um domínio local que **não** seja `.localhost` — navegadores
   recusam `Set-Cookie` com `Domain=.localhost` (é tratado como TLD
   reservado). Um domínio qualquer com 2+ partes funciona, ex.:
   `appteste.dev` (não precisa existir de verdade, é só resolvido local).
2. Adicione ao `/etc/hosts`:
   ```
   127.0.0.1 novaseguro.appteste.dev
   127.0.0.1 beta.appteste.dev
   127.0.0.1 api.appteste.dev
   ```
   (o backend também precisa de um host **dentro do mesmo domínio**, já
   que o cookie com `Domain=.appteste.dev` só é aceito pelo navegador se
   quem o emitiu — o backend — também estiver em `*.appteste.dev`.)
3. `backend/.env`: `COOKIE_DOMAIN=.appteste.dev`,
   `CORS_ORIGIN_REGEX=^http://([a-z0-9-]+\.)?appteste\.dev:3000$`
4. `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://api.appteste.dev:8000`,
   `NEXT_DEV_ALLOWED_ORIGINS=*.appteste.dev`
5. Acesse `http://novaseguro.appteste.dev:3000` e
   `http://beta.appteste.dev:3000` — cada um mostra a marca certa antes do
   login, e o login de cada assinante só funciona no respectivo subdomínio.

Isso é só para desenvolvimento local; nenhuma dessas variáveis precisa
estar definida para rodar a aplicação normalmente em um domínio só (o
comportamento padrão, sem nada disso configurado, é exatamente o mesmo de
antes do multi-tenant).

## Dados de exemplo

O tenant `novaseguro` tem 8 clientes fictícios, 4 seguradoras parceiras, 10
apólices com datas de renovação espalhadas (de 8 a 300 dias a partir de
hoje), alguns sinistros e interações (elogios, reclamações, uso do portal)
— o suficiente para o modelo heurístico de previsão gerar respostas
diferentes por cliente. Veja `db/init/02_seed.sql`. O tenant `beta` tem um
dataset bem menor (3 clientes, 2 seguradoras, 3 apólices) só para provar o
isolamento e a identidade visual — veja `db/init/06_seed_tenant_beta.sql`.

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
