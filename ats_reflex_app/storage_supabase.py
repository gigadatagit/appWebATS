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


def upload_html_bytes(
    storage_path: str,
    html_bytes: bytes,
    *,
    bucket: str | None = None,
) -> str:
    return upload_file_bytes(
        storage_path=storage_path,
        file_bytes=html_bytes,
        content_type="text/html; charset=utf-8",
        bucket=bucket,
        content_label="HTML",
    )


def upload_file_bytes(
    storage_path: str,
    file_bytes: bytes,
    *,
    content_type: str,
    bucket: str | None = None,
    content_label: str = "archivo",
) -> str:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)
    if not isinstance(file_bytes, (bytes, bytearray)) or len(file_bytes) <= 0:
        raise RuntimeError(f"El contenido {content_label} en memoria esta vacio.")
    resolved_content_type = str(content_type or "").strip()
    if not resolved_content_type:
        raise RuntimeError("El tipo MIME del archivo es obligatorio.")

    client = _build_service_supabase_client()
    try:
        client.storage.from_(target_bucket).upload(
            path=normalized_path,
            file=bytes(file_bytes),
            file_options={
                "content-type": resolved_content_type,
                "cache-control": "3600",
                "x-upsert": "false",
            },
        )
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo subir el {content_label} al bucket privado '{target_bucket}'."
        ) from exc

    return normalized_path


def create_signed_file_url(
    storage_path: str,
    *,
    expires_in_seconds: int | None = None,
    bucket: str | None = None,
    download_name: str | None = None,
    force_download: bool = True,
) -> str:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)

    ttl_raw = int(expires_in_seconds or 0)
    ttl = ttl_raw if ttl_raw > 0 else int(get_supabase_signed_url_ttl_seconds())

    options: dict[str, Any]
    if force_download and str(download_name or "").strip():
        options = {"download": str(download_name).strip()}
    elif force_download:
        options = {"download": True}
    else:
        options = {}

    client = _build_service_supabase_client()
    try:
        response = client.storage.from_(target_bucket).create_signed_url(
            path=normalized_path,
            expires_in=ttl,
            options=options,
        )
    except Exception as exc:
        raise RuntimeError("No se pudo generar la URL firmada del documento.") from exc

    signed_url = str(response.get("signedURL") or response.get("signedUrl") or "").strip()
    if signed_url == "":
        raise RuntimeError("Supabase no devolvio URL firmada para el documento.")
    return signed_url


def download_file_bytes(storage_path: str, *, bucket: str | None = None) -> bytes:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)
    client = _build_service_supabase_client()
    try:
        payload = client.storage.from_(target_bucket).download(normalized_path)
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo descargar el recurso del bucket privado '{target_bucket}'."
        ) from exc
    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise RuntimeError("Supabase devolvio un recurso vacio.")
    return bytes(payload)


def delete_file_if_exists(storage_path: str, *, bucket: str | None = None) -> bool:
    target_bucket = _resolve_bucket(bucket)
    normalized_path = _normalize_storage_path(storage_path)
    client = _build_service_supabase_client()
    try:
        client.storage.from_(target_bucket).remove([normalized_path])
        return True
    except Exception:
        return False
