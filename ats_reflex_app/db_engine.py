from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from .config import get_database_url


def create_sqlalchemy_engine(use_null_pool: bool = False) -> Engine:
    database_url = get_database_url()
    if use_null_pool:
        return create_engine(database_url, poolclass=NullPool)
    return create_engine(database_url)


def test_database_connection(use_null_pool: bool = False) -> tuple[bool, str]:
    engine = create_sqlalchemy_engine(use_null_pool=use_null_pool)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Connection successful!"
    except Exception as exc:  # pragma: no cover
        return False, f"Failed to connect: {exc}"
