"""Armazenamento dos PDFs originais em disco (volume do docker-compose em
produção, pasta local em dev) — só o suficiente para permitir o download do
documento enviado; o conteúdo pesquisável vive no Postgres via
`documento_chunks`.
"""
import uuid
from pathlib import Path

from .config import get_settings


def _storage_root() -> Path:
    root = Path(get_settings().storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_upload(file_bytes: bytes, original_filename: str) -> str:
    """Grava o arquivo com um nome único em disco e devolve o nome salvo
    (não o caminho completo — o caminho é sempre resolvido a partir de
    STORAGE_DIR, para não depender de como o volume está montado)."""
    suffix = Path(original_filename).suffix or ".pdf"
    disk_name = f"{uuid.uuid4().hex}{suffix}"
    (_storage_root() / disk_name).write_bytes(file_bytes)
    return disk_name


def resolve_path(disk_name: str) -> Path:
    return _storage_root() / disk_name
