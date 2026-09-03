# Apresentação: Como Nascem os Produtos Digitais

Apresentação de engenharia de software para público não técnico, cobrindo o
ciclo de vida de produtos e funcionalidades, os papéis de Product Owner,
System Engineer e Tech Lead, metodologias ágeis com ciclos de validação
rápida, e um estudo de caso fictício de IA (RAG e GraphRAG) aplicado a uma
corretora de seguros.

O `.pptx` é gerado a partir de Markdown usando o [Pandoc](https://pandoc.org/),
com um template PowerPoint customizado (`assets/reference.pptx`) para a
identidade visual (paleta navy/gelo/âmbar) e diagramas gerados com
Matplotlib.

## Estrutura

- `conteudo.md` — conteúdo da apresentação em Markdown (sintaxe de slides do Pandoc)
- `assets/reference.pptx` — template de referência (tema, cores, fontes, layouts)
- `assets/diagrama_*.png` — diagramas gerados por script
- `scripts/build_reference.py` — gera `assets/reference.pptx`
- `scripts/generate_diagrams.py` — gera os diagramas em `assets/`
- `apresentacao.pptx` — arquivo final gerado

## Como regenerar

Rodar sempre a partir da raiz do repositório:

```bash
# 1. (Re)gerar o template de referência e os diagramas, se necessário
python3 presentation/scripts/build_reference.py
python3 presentation/scripts/generate_diagrams.py

# 2. Converter o Markdown para PPTX
cd presentation
pandoc conteudo.md -o apresentacao.pptx --slide-level=2 --reference-doc=assets/reference.pptx
```

Dependências: `pandoc`, `python-pptx`, `matplotlib` (todas instaláveis via
`pip`/`apt`).

## Estrutura do Markdown

- `#` (H1) sem conteúdo abaixo → slide divisor de seção (fundo navy)
- `##` (H2) → slide de conteúdo (fundo branco, título navy)
- Imagem sozinha em um parágrafo → slide de imagem
- Bloco `::: notes ... :::` → notas do apresentador
