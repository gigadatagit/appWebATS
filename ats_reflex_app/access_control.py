from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import select

from .models import Ats


class AccessDeniedError(PermissionError):
    pass


@dataclass(frozen=True)
class AuthContext:
    auth_user_id: str
    current_user_id: int
    current_user_role_codigo: str
    is_authenticated: bool


def normalize_role(role: str) -> str:
    return str(role or "").strip().upper()


def is_admin(role: str) -> bool:
    return normalize_role(role) == "ADMIN"


def is_siso(role: str) -> bool:
    return normalize_role(role) == "SISO"


def get_current_auth_context(state) -> AuthContext:
    auth_user_id = str(getattr(state, "current_auth_user_id", "") or "").strip()
    current_user_id = int(
        getattr(state, "current_user_id", getattr(state, "user_id", 0)) or 0
    )
    current_user_role_codigo = normalize_role(
        str(
            getattr(
                state,
                "current_user_role_codigo",
                getattr(state, "rol_codigo", ""),
            )
            or ""
        )
    )
    is_authenticated = bool(getattr(state, "is_authenticated", False))

    return AuthContext(
        auth_user_id=auth_user_id,
        current_user_id=current_user_id,
        current_user_role_codigo=current_user_role_codigo,
        is_authenticated=is_authenticated,
    )


def apply_ats_scope_filter(query, current_user_id: int, current_user_role_codigo: str):
    if is_admin(current_user_role_codigo):
        return query
    return query.where(Ats.creado_por_usuario_id == int(current_user_id or 0))


def can_access_ats(
    session,
    ats_id: int,
    current_user_id: int,
    current_user_role_codigo: str,
) -> bool:
    target_ats_id = int(ats_id or 0)
    if target_ats_id <= 0:
        return False

    base = select(Ats.id).where(Ats.id == target_ats_id)
    scoped = apply_ats_scope_filter(
        base,
        current_user_id=int(current_user_id or 0),
        current_user_role_codigo=current_user_role_codigo,
    )
    row = session.exec(scoped).first()
    return row is not None


def assert_can_access_ats(
    session,
    ats_id: int,
    current_user_id: int,
    current_user_role_codigo: str,
) -> None:
    if not can_access_ats(
        session,
        ats_id=ats_id,
        current_user_id=current_user_id,
        current_user_role_codigo=current_user_role_codigo,
    ):
        raise AccessDeniedError("No tienes permisos para acceder a este ATS.")


def assert_can_edit_ats(
    session,
    ats_id: int,
    current_user_id: int,
    current_user_role_codigo: str,
) -> None:
    if not can_access_ats(
        session,
        ats_id=ats_id,
        current_user_id=current_user_id,
        current_user_role_codigo=current_user_role_codigo,
    ):
        raise AccessDeniedError("No tienes permisos para editar este ATS.")


def resolve_ats_id_by_codigo(
    session,
    codigo_publico: str,
    current_user_id: int,
    current_user_role_codigo: str,
) -> int:
    codigo = str(codigo_publico or "").strip()
    if not codigo:
        return 0
    query = select(Ats.id).where(Ats.codigo_publico == codigo)
    query = apply_ats_scope_filter(query, current_user_id, current_user_role_codigo)
    row = session.exec(query).first()
    return int(row or 0)


def resolve_ats_id_by_uuid(
    session,
    ats_uuid: str,
    current_user_id: int,
    current_user_role_codigo: str,
) -> int:
    value = str(ats_uuid or "").strip()
    if not value:
        return 0
    query = select(Ats.id).where(Ats.uuid == value)
    query = apply_ats_scope_filter(query, current_user_id, current_user_role_codigo)
    row = session.exec(query).first()
    return int(row or 0)
