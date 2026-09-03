from contextlib import contextmanager
from functools import lru_cache

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector

from .config import get_settings


def _configure_connection(conn: psycopg.Connection) -> None:
    register_vector(conn)


@lru_cache
def get_pool() -> ConnectionPool:
    settings = get_settings()
    return ConnectionPool(
        conninfo=settings.database_url,
        min_size=1,
        max_size=5,
        configure=_configure_connection,
        open=True,
    )


@contextmanager
def get_cursor():
    """Yields a dict-row cursor from a pooled connection, committing on success."""
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur
