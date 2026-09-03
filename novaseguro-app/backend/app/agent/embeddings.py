"""Wrapper fino sobre a API de embeddings da OpenAI, usado tanto pela busca
(buscar_documentos) quanto pela ingestão de PDFs. Nunca levanta exceção:
sem OPENAI_API_KEY ou em caso de falha da API, devolve None por item, para
que o restante do pipeline (salvar o arquivo, gravar o texto do chunk)
continue funcionando mesmo sem a chave configurada.
"""
import logging

from openai import OpenAI

from ..config import get_settings

logger = logging.getLogger(__name__)


def embed_texts(texts: list[str]) -> list[list[float] | None]:
    settings = get_settings()
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY ausente — retornando embeddings vazios (%d itens).", len(texts))
        return [None] * len(texts)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [item.embedding for item in response.data]
    except Exception:
        logger.exception("Falha ao chamar a API de embeddings da OpenAI")
        return [None] * len(texts)


def embed_text(text: str) -> list[float] | None:
    return embed_texts([text])[0]
