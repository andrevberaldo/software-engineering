from functools import lru_cache

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from ..config import get_settings
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """\
Você é o assistente de IA da NovaSeguro Corretora, uma corretora de seguros \
fictícia que trabalha com várias seguradoras parceiras.

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


@lru_cache
def get_agent():
    """Cria (uma única vez por processo) o deep agent com suas ferramentas.

    O checkpointer em memória mantém o histórico de cada conversa (por
    thread_id) apenas enquanto o processo do backend estiver de pé — em uma
    evolução futura, pode ser trocado por um checkpointer Postgres para
    persistir entre reinícios.
    """
    model = _build_model()
    return create_deep_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
