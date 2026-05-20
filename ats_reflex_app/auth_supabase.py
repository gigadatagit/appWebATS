from __future__ import annotations

from typing import Any

from supabase import Client, ClientOptions, create_client

from .config import require_supabase_auth_env


def _build_supabase_client() -> Client:
    supabase_url, supabase_anon_key = require_supabase_auth_env()
    return create_client(
        supabase_url,
        supabase_anon_key,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            dumped = value.model_dump()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            return {}
    if hasattr(value, "__dict__"):
        return {
            key: raw
            for key, raw in value.__dict__.items()
            if not str(key).startswith("_")
        }
    return {}


def sign_in_with_password(email: str, password: str) -> dict[str, str]:
    if not str(email or "").strip() or not str(password or "").strip():
        raise RuntimeError("Debes ingresar correo y contrasena.")

    client = _build_supabase_client()
    response = client.auth.sign_in_with_password(
        {
            "email": str(email).strip(),
            "password": str(password),
        }
    )

    user_obj = getattr(response, "user", None)
    session_obj = getattr(response, "session", None)

    if user_obj is None and session_obj is not None:
        user_obj = getattr(session_obj, "user", None)

    payload = _as_dict(response)
    if user_obj is None:
        user_obj = payload.get("user")
    if session_obj is None:
        session_obj = payload.get("session")

    user_data = _as_dict(user_obj)
    if not user_data and isinstance(user_obj, dict):
        user_data = user_obj

    auth_user_id = str(user_data.get("id") or "").strip()
    auth_user_email = str(user_data.get("email") or str(email or "")).strip()
    access_token = ""
    session_data = _as_dict(session_obj)
    if session_data:
        access_token = str(session_data.get("access_token") or "").strip()

    if not auth_user_id:
        raise RuntimeError("Supabase Auth no devolvio un usuario valido.")

    return {
        "auth_user_id": auth_user_id,
        "email": auth_user_email,
        "access_token": access_token,
    }
