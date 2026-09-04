"""Ingestão de PDFs (apólices) com Docling: converte o arquivo, quebra em
chunks coerentes com a estrutura do documento (HybridChunker) e grava cada
chunk com seu embedding em `documento_chunks`.

OCR fica desligado por padrão — a maioria das apólices é gerada
digitalmente pelos sistemas das seguradoras, então o texto já vem embutido
no PDF. Para digitalizações (PDFs escaneados), habilite
`PdfPipelineOptions(do_ocr=True)`, o que faz o Docling baixar um modelo de
OCR na primeira execução.

Nota: na primeira conversão, o Docling baixa o modelo de layout do
Hugging Face Hub (uma única vez, fica em cache depois). Isso exige acesso
de rede ao huggingface.co no ambiente onde o backend roda.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path

from .embeddings import embed_texts

logger = logging.getLogger(__name__)


@lru_cache
def _get_converter():
    # Import pesado (docling puxa torch/transformers) e a instanciação do
    # conversor só acontecem na primeira ingestão de verdade — não no
    # startup do backend. Na primeira conversão, o Docling baixa o modelo
    # de layout do Hugging Face Hub (fica em cache depois).
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    pipeline_options = PdfPipelineOptions(do_ocr=False)
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )


@lru_cache
def _get_chunker():
    from docling.chunking import HybridChunker

    return HybridChunker()


def extract_chunks(pdf_path: Path) -> list[dict]:
    """Converte o PDF e devolve uma lista de chunks: [{"texto", "metadados"}]."""
    converter = _get_converter()
    chunker = _get_chunker()

    result = converter.convert(str(pdf_path))
    doc = result.document

    chunks = []
    for chunk in chunker.chunk(doc):
        texto = chunker.contextualize(chunk)
        meta = (
            chunk.meta.model_dump(mode="json", exclude_none=True)
            if hasattr(chunk.meta, "model_dump")
            else {}
        )
        chunks.append({"texto": texto, "metadados": meta})
    return chunks


def ingest_pdf(cur, documento_id: int, pdf_path: Path, tenant_id: int) -> int:
    """Extrai, faz o chunking e grava os embeddings de um PDF já salvo em
    disco, associando cada chunk ao `documento_id` (e ao `tenant_id` do
    documento, para a busca por similaridade poder filtrar por tenant sem
    precisar de join). Devolve quantos chunks foram gravados (0 se o PDF
    não tiver texto extraível).
    """
    chunks = extract_chunks(pdf_path)
    if not chunks:
        logger.warning("Nenhum chunk extraído de %s", pdf_path)
        return 0

    textos = [c["texto"] for c in chunks]
    embeddings = embed_texts(textos)

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        cur.execute(
            """
            INSERT INTO documento_chunks (documento_id, tenant_id, chunk_index, conteudo, embedding, metadados)
            VALUES (%(documento_id)s, %(tenant_id)s, %(chunk_index)s, %(conteudo)s, %(embedding)s, %(metadados)s)
            ON CONFLICT (documento_id, chunk_index) DO UPDATE
                SET conteudo = EXCLUDED.conteudo,
                    embedding = EXCLUDED.embedding,
                    metadados = EXCLUDED.metadados
            """,
            {
                "documento_id": documento_id,
                "tenant_id": tenant_id,
                "chunk_index": index,
                "conteudo": chunk["texto"],
                "embedding": embedding,
                "metadados": json.dumps(chunk["metadados"], ensure_ascii=False),
            },
        )

    return len(chunks)
