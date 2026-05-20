from __future__ import annotations

from typing import Any

from supabase import Client, ClientOptions, create_client

from .config import (
    get_supabase_signed_url_ttl_seconds,
    get_supabase_storage_bucket,
    require_supabase_storage_env,
)


def _build_service_supabase_client() -> Client:
    supabase_url, service_role_key, _ = require_supabase_storage_env()
    return create_client(
        supabase_url,
        service_role_key,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


def _resolve_bucket(bucket: str | None = None) -> str:
    resolved = str(bucket or "").strip() or get_supabase_storage_bucket()
    if not resolved:
        raise RuntimeError("No se pudo resolver el bucket de Supabase Storage.")
    return resolved


def _normalize_storage_path(storage_path: str) -> str:
    normalized = str(storage_path or "").replace("\\", "/").strip().strip("/")
    if normalized == "":
        raise RuntimeError("La ruta del archivo en Storage es invalida.")
    return normalized


def upload_pdf_bytes(
    storage_path: str,
    pdf_bytes: bytes,
    *,
    bucket: str | None = None,
) -> str:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)
    if not isinstance(pdf_bytes, (bytes, bytearray)) or len(pdf_bytes) <= 0:
        raise RuntimeError("El contenido PDF en memoria esta vacio.")

    client = _build_service_supabase_client()
    try:
        client.storage.from_(target_bucket).upload(
            path=normalized_path,
            file=bytes(pdf_bytes),
            file_options={
                "content-type": "application/pdf",
                "cache-control": "3600",
                "x-upsert": "false",
            },
        )
    except Exception as exc:
        raise RuntimeError(f"No se pudo subir el PDF al bucket privado '{target_bucket}'.") from exc

    return normalized_path


def create_signed_file_url(
    storage_path: str,
    *,
    expires_in_seconds: int | None = None,
    bucket: str | None = None,
    download_name: str | None = None,
) -> str:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)

    ttl_raw = int(expires_in_seconds or 0)
    ttl = ttl_raw if ttl_raw > 0 else int(get_supabase_signed_url_ttl_seconds())

    options: dict[str, Any]
    if str(download_name or "").strip():
        options = {"download": str(download_name).strip()}
    else:
        options = {"download": True}

    client = _build_service_supabase_client()
    try:
        response = client.storage.from_(target_bucket).create_signed_url(
            path=normalized_path,
            expires_in=ttl,
            options=options,
        )
    except Exception as exc:
        raise RuntimeError("No se pudo generar la URL firmada del PDF.") from exc

    signed_url = str(response.get("signedURL") or response.get("signedUrl") or "").strip()
    if signed_url == "":
        raise RuntimeError("Supabase no devolvio URL firmada para el documento.")
    return signed_url


def delete_file_if_exists(storage_path: str, *, bucket: str | None = None) -> bool:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)
    client = _build_service_supabase_client()
    try:
        client.storage.from_(target_bucket).remove([normalized_path])
        return True
    except Exception:
        return False
