import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..agent.ingestion import ingest_pdf
from ..auth import get_current_user
from ..db import get_cursor
from ..storage import resolve_path, save_upload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


class DocumentOut(BaseModel):
    id: int
    titulo: str
    seguradora_id: int | None
    seguradora_nome: str | None
    arquivo_nome: str | None
    mime_type: str | None
    tamanho_bytes: int | None
    total_chunks: int
    criado_em: str


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    titulo: str = Form(...),
    seguradora_id: str | None = Form(None),
    file: UploadFile = File(...),
    _user: dict = Depends(get_current_user),
) -> DocumentOut:
    if not (file.filename or "").lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo maior que 20MB")

    seguradora_id_int = int(seguradora_id) if seguradora_id else None
    disk_name = save_upload(raw, file.filename or "documento.pdf")

    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO documentos (titulo, seguradora_id, arquivo_nome, arquivo_caminho, mime_type, tamanho_bytes)
            VALUES (%(titulo)s, %(seguradora_id)s, %(arquivo_nome)s, %(arquivo_caminho)s, %(mime_type)s, %(tamanho_bytes)s)
            RETURNING id, criado_em
            """,
            {
                "titulo": titulo,
                "seguradora_id": seguradora_id_int,
                "arquivo_nome": file.filename,
                "arquivo_caminho": disk_name,
                "mime_type": file.content_type or "application/pdf",
                "tamanho_bytes": len(raw),
            },
        )
        criado = cur.fetchone()
        documento_id = criado["id"]

        try:
            total_chunks = ingest_pdf(cur, documento_id, resolve_path(disk_name))
        except Exception as exc:
            logger.exception("Falha ao processar PDF #%s com o Docling", documento_id)
            raise HTTPException(
                status_code=422, detail=f"Falha ao processar o PDF com o Docling: {exc}"
            ) from exc

        seguradora_nome = None
        if seguradora_id_int:
            cur.execute("SELECT nome FROM seguradoras WHERE id = %(id)s", {"id": seguradora_id_int})
            seg = cur.fetchone()
            seguradora_nome = seg["nome"] if seg else None

    return DocumentOut(
        id=documento_id,
        titulo=titulo,
        seguradora_id=seguradora_id_int,
        seguradora_nome=seguradora_nome,
        arquivo_nome=file.filename,
        mime_type=file.content_type,
        tamanho_bytes=len(raw),
        total_chunks=total_chunks,
        criado_em=criado["criado_em"].isoformat(),
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(_user: dict = Depends(get_current_user)) -> list[DocumentOut]:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT d.id, d.titulo, d.seguradora_id, s.nome AS seguradora_nome,
                   d.arquivo_nome, d.mime_type, d.tamanho_bytes, d.criado_em,
                   COUNT(c.id) AS total_chunks
            FROM documentos d
            LEFT JOIN seguradoras s ON s.id = d.seguradora_id
            LEFT JOIN documento_chunks c ON c.documento_id = d.id
            GROUP BY d.id, s.nome
            ORDER BY d.criado_em DESC
            """
        )
        rows = cur.fetchall()

    return [
        DocumentOut(
            id=r["id"],
            titulo=r["titulo"],
            seguradora_id=r["seguradora_id"],
            seguradora_nome=r["seguradora_nome"],
            arquivo_nome=r["arquivo_nome"],
            mime_type=r["mime_type"],
            tamanho_bytes=r["tamanho_bytes"],
            total_chunks=r["total_chunks"],
            criado_em=r["criado_em"].isoformat(),
        )
        for r in rows
    ]


@router.get("/{documento_id}/download")
def download_document(documento_id: int, _user: dict = Depends(get_current_user)):
    with get_cursor() as cur:
        cur.execute(
            "SELECT arquivo_nome, arquivo_caminho, mime_type FROM documentos WHERE id = %(id)s",
            {"id": documento_id},
        )
        row = cur.fetchone()

    if row is None or not row["arquivo_caminho"]:
        raise HTTPException(status_code=404, detail="Documento sem arquivo para download")

    path = resolve_path(row["arquivo_caminho"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no armazenamento")

    return FileResponse(
        path,
        media_type=row["mime_type"] or "application/pdf",
        filename=row["arquivo_nome"] or path.name,
    )
