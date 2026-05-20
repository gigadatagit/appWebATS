from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

DEFAULT_SQLITE_URL = "sqlite:///data/ats_app.db"
DEFAULT_POSTGRES_SSLMODE = "require"
DEFAULT_POSTGRES_PORT = "5432"
DEFAULT_SUPABASE_STORAGE_BUCKET = "ATSDocumentos"
DEFAULT_ATS_PDF_ENGINE = "word"
DEFAULT_SIGNED_URL_TTL_SECONDS = 600

load_dotenv()


def _get_first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def build_database_url_from_parts() -> str:
    user = _get_first_env("DB_USER", "POSTGRES_USER", "user")
    #dbname = _get_first_env("DB_NAME", "POSTGRES_DB", "dbname")
    password = _get_first_env("DB_PASSWORD", "POSTGRES_PASSWORD", "password")
    host = _get_first_env("DB_HOST", "POSTGRES_HOST", "host")
    port = _get_first_env("DB_PORT", "POSTGRES_PORT", "port") or DEFAULT_POSTGRES_PORT
    dbname = _get_first_env("DB_NAME", "POSTGRES_DB", "dbname")
    sslmode = _get_first_env("DB_SSLMODE", "PGSSLMODE", "sslmode") or DEFAULT_POSTGRES_SSLMODE

    if not all([user, password, host, port, dbname]):
        return ""

    #encoded_user = quote_plus(user)
    #encoded_password = quote_plus(password)
    #encoded_dbname = quote_plus(dbname)
    #return (
    #    f"postgresql+psycopg2://{encoded_user}:{encoded_password}"
    #    f"@{host}:{port}/{encoded_dbname}?sslmode={sslmode}"
    #)
    return (f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require")


def get_database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        return value
    from_parts = build_database_url_from_parts()
    return from_parts or DEFAULT_SQLITE_URL


def is_sqlite_url(db_url: str | None = None) -> bool:
    value = (db_url or get_database_url()).strip().lower()
    return value.startswith("sqlite")


def get_app_env() -> str:
    return os.getenv("APP_ENV", "development").strip().lower()


def get_supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "").strip()


def get_supabase_anon_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY", "").strip()


def is_supabase_auth_configured() -> bool:
    return bool(get_supabase_url() and get_supabase_anon_key())


def require_supabase_auth_env() -> tuple[str, str]:
    supabase_url = get_supabase_url()
    supabase_anon_key = get_supabase_anon_key()
    if not supabase_url or not supabase_anon_key:
        raise RuntimeError(
            "Falta configuracion de Supabase Auth. Define SUPABASE_URL y SUPABASE_ANON_KEY."
        )
    return supabase_url, supabase_anon_key


def get_supabase_service_role_key() -> str:
    return os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()


def get_supabase_storage_bucket() -> str:
    return os.getenv("SUPABASE_STORAGE_BUCKET", DEFAULT_SUPABASE_STORAGE_BUCKET).strip() or DEFAULT_SUPABASE_STORAGE_BUCKET


def normalize_ats_pdf_engine(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    if raw == "":
        if sys.platform.startswith("linux"):
            return "libreoffice"
        return DEFAULT_ATS_PDF_ENGINE
    if raw not in {"word", "libreoffice"}:
        raise RuntimeError(
            "Valor invalido para ATS_PDF_ENGINE. Usa 'word' o 'libreoffice'."
        )
    return raw


def get_ats_pdf_engine() -> str:
    return normalize_ats_pdf_engine(os.getenv("ATS_PDF_ENGINE", ""))


def get_supabase_signed_url_ttl_seconds() -> int:
    raw = str(os.getenv("SUPABASE_SIGNED_URL_TTL_SECONDS", "")).strip()
    if raw == "":
        return DEFAULT_SIGNED_URL_TTL_SECONDS
    try:
        parsed = int(raw)
    except Exception:
        return DEFAULT_SIGNED_URL_TTL_SECONDS
    if parsed <= 0:
        return DEFAULT_SIGNED_URL_TTL_SECONDS
    return parsed


def require_supabase_storage_env() -> tuple[str, str, str]:
    supabase_url = get_supabase_url()
    service_role_key = get_supabase_service_role_key()
    bucket = get_supabase_storage_bucket()
    if not supabase_url or not service_role_key:
        raise RuntimeError(
            "Falta configuracion de Supabase Storage privado. "
            "Define SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en backend."
        )
    if not bucket:
        raise RuntimeError("Falta nombre de bucket en SUPABASE_STORAGE_BUCKET.")
    return supabase_url, service_role_key, bucket
