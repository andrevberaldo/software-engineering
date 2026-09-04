from functools import lru_cache

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from ..config import get_settings
from ..db import get_cursor
from .tools import build_tools

SYSTEM_PROMPT_TEMPLATE = """\
Você é o assistente de IA da {nome_empresa}, uma corretora de seguros \
que trabalha com várias seguradoras parceiras.

Seu trabalho é ajudar corretores humanos a:
- consultar informações de clientes, apólices e seguradoras;
- responder dúvidas sobre coberturas e políticas internas, sempre citando o \
documento de origem quando usar a ferramenta de busca;
- estimar a probabilidade de renovação e a receita futura projetada de apólices;
- priorizar quais clientes precisam de atenção antes do vencimento da apólice;
- registrar contatos automáticos de renovação quando fizer sentido.

Regras importantes:
- Responda sempre em português do Brasil, em tom direto e profissional.
- Nunca invente números de apólice, nomes de clientes ou valores: use as \
ferramentas disponíveis para consultar dados reais da base.
- Antes de registrar um contato de renovação, calcule a previsão de \
renovação da apólice para saber o nível de risco e escreva você mesmo uma \
mensagem curta, cordial e específica para aquele cliente.
- Se não tiver certeza de algo, diga isso claramente em vez de adivinhar.
"""


def _build_model() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Defina a variável de ambiente "
            "para habilitar o assistente de IA."
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )


def _nome_empresa(tenant_id: int) -> str:
    with get_cursor() as cur:
        cur.execute("SELECT nome_empresa FROM tenants WHERE id = %(id)s", {"id": tenant_id})
        tenant = cur.fetchone()
    return tenant["nome_empresa"] if tenant else "sua corretora"


@lru_cache
def get_agent(tenant_id: int):
    """Cria (uma única vez por tenant, por processo) o deep agent com
    ferramentas escopadas àquele tenant (`build_tools(tenant_id)`).

    Uma entrada de cache por tenant também dá isolamento de conversa de
    graça: cada tenant tem seu próprio `InMemorySaver`, então o histórico
    de chat de um assinante nunca aparece pra outro. Esse checkpointer em
    memória dura só enquanto o processo do backend estiver de pé — numa
    evolução futura, pode virar um checkpointer Postgres para persistir
    entre reinícios.
    """
    model = _build_model()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(nome_empresa=_nome_empresa(tenant_id))
    return create_deep_agent(
        model=model,
        tools=build_tools(tenant_id),
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )
