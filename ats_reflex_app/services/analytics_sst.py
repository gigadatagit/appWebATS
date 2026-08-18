from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import text

from ..access_control import is_admin


@dataclass(frozen=True)
class SSTDashboardFilters:
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    selected_siso_user_id: int = 0
    selected_format_code: str = ""
    origen: str = "TODOS"
    estado: str = "TODOS"


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _format_date(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def load_siso_user_options(session) -> list[dict]:
    rows = (
        session.execute(
            text(
                """
                SELECT
                    u.id AS id,
                    COALESCE(u.nombre_completo, u.username) AS label
                FROM public.usuario u
                JOIN public.rol r ON r.id = u.rol_id
                WHERE UPPER(r.codigo) = 'SISO'
                  AND u.activo IS TRUE
                ORDER BY label ASC
                """
            )
        )
        .mappings()
        .all()
    )
    options = [{"id": 0, "id_str": "0", "label": "Todos"}]
    for row in rows:
        user_id = _as_int(row.get("id"))
        if user_id <= 0:
            continue
        options.append(
            {
                "id": user_id,
                "id_str": str(user_id),
                "label": _as_str(row.get("label")) or f"Usuario {user_id}",
            }
        )
    return options


def _build_registros_where(
    filters: SSTDashboardFilters,
    *,
    current_user_id: int,
    role_code: str,
    forced_format_code: str = "",
) -> tuple[str, dict[str, Any]]:
    params: dict[str, Any] = {}
    clauses: list[str] = ["1 = 1"]

    if is_admin(role_code):
        if int(filters.selected_siso_user_id or 0) > 0:
            clauses.append("r.creado_por_usuario_id = :selected_siso_user_id")
            params["selected_siso_user_id"] = int(filters.selected_siso_user_id)
    else:
        clauses.append("r.creado_por_usuario_id = :current_user_id")
        params["current_user_id"] = int(current_user_id or 0)

    format_code = _as_str(forced_format_code or filters.selected_format_code).upper()
    if format_code and format_code != "TODOS":
        clauses.append("r.formato_codigo = :format_code")
        params["format_code"] = format_code

    if filters.fecha_inicio is not None:
        clauses.append("r.fecha_principal >= :fecha_inicio")
        params["fecha_inicio"] = filters.fecha_inicio
    if filters.fecha_fin is not None:
        clauses.append("r.fecha_principal <= :fecha_fin")
        params["fecha_fin"] = filters.fecha_fin

    origen = _as_str(filters.origen).upper()
    if origen == "MOVIL":
        clauses.append("r.importado_desde_movil IS TRUE")
    elif origen == "WEB":
        clauses.append("r.importado_desde_movil IS FALSE")

    estado = _as_str(filters.estado).upper()
    if estado == "PENDIENTE_CIERRE":
        clauses.append("r.pendiente_cierre IS TRUE")
    elif estado == "DOCUMENTADO":
        clauses.append("r.tiene_documento IS TRUE")
    elif estado == "SIN_DOCUMENTO":
        clauses.append("r.tiene_documento IS FALSE")
    elif estado == "ASOCIADO_ATS":
        clauses.append("r.ats_id IS NOT NULL")

    return "WHERE " + " AND ".join(clauses), params


def _run_rows(session, sql: str, params: dict[str, Any]) -> list[dict]:
    return [dict(row) for row in session.execute(text(sql), params).mappings().all()]


def _run_one(session, sql: str, params: dict[str, Any]) -> dict:
    row = session.execute(text(sql), params).mappings().first()
    return dict(row) if row is not None else {}


def fetch_sst_dashboard(
    session,
    filters: SSTDashboardFilters,
    *,
    current_user_id: int,
    role_code: str,
    forced_format_code: str = "",
) -> dict:
    where_sql, params = _build_registros_where(
        filters,
        current_user_id=current_user_id,
        role_code=role_code,
        forced_format_code=forced_format_code,
    )
    base_from = f"FROM public.vw_sst_registros_consolidado r {where_sql}"

    summary = _run_one(
        session,
        f"""
        SELECT
            COUNT(*) AS total_registros,
            COALESCE(SUM(r.total_documentos), 0) AS total_documentos,
            COUNT(*) FILTER (WHERE r.pendiente_cierre IS TRUE) AS total_pendientes_cierre,
            COUNT(*) FILTER (WHERE r.importado_desde_movil IS TRUE) AS total_importados_movil,
            COUNT(*) FILTER (WHERE r.ats_id IS NOT NULL) AS total_asociados_ats,
            COALESCE(SUM(r.total_no), 0) AS total_respuestas_no,
            COALESCE(SUM(r.total_firmas), 0) AS total_firmas
        {base_from}
        """,
        params,
    )

    by_format = _run_rows(
        session,
        f"""
        SELECT
            r.formato_nombre AS label,
            COUNT(*) AS total
        {base_from}
        GROUP BY r.formato_codigo, r.formato_nombre
        ORDER BY total DESC, r.formato_nombre ASC
        """,
        params,
    )

    by_month = _run_rows(
        session,
        f"""
        SELECT
            TO_CHAR(r.fecha_principal, 'YYYY-MM') AS periodo,
            COUNT(*) AS total
        {base_from}
          AND r.fecha_principal IS NOT NULL
        GROUP BY TO_CHAR(r.fecha_principal, 'YYYY-MM')
        ORDER BY periodo ASC
        """,
        params,
    )

    by_user = _run_rows(
        session,
        f"""
        SELECT
            COALESCE(NULLIF(TRIM(r.usuario_nombre), ''), 'Sin usuario') AS usuario,
            COUNT(*) AS total
        {base_from}
        GROUP BY COALESCE(NULLIF(TRIM(r.usuario_nombre), ''), 'Sin usuario')
        ORDER BY total DESC, usuario ASC
        LIMIT 12
        """,
        params,
    )

    by_category = _run_rows(
        session,
        f"""
        SELECT
            COALESCE(NULLIF(TRIM(r.categoria_principal), ''), 'Sin categoria') AS categoria,
            COUNT(*) AS total
        {base_from}
        GROUP BY COALESCE(NULLIF(TRIM(r.categoria_principal), ''), 'Sin categoria')
        ORDER BY total DESC, categoria ASC
        LIMIT 12
        """,
        params,
    )

    by_origin = _run_rows(
        session,
        f"""
        SELECT
            CASE WHEN r.importado_desde_movil IS TRUE THEN 'Movil offline' ELSE 'Web' END AS name,
            COUNT(*) AS value
        {base_from}
        GROUP BY CASE WHEN r.importado_desde_movil IS TRUE THEN 'Movil offline' ELSE 'Web' END
        ORDER BY value DESC, name ASC
        """,
        params,
    )

    by_document = _run_rows(
        session,
        f"""
        SELECT
            CASE WHEN r.tiene_documento IS TRUE THEN 'Con documento' ELSE 'Sin documento' END AS name,
            COUNT(*) AS value
        {base_from}
        GROUP BY CASE WHEN r.tiene_documento IS TRUE THEN 'Con documento' ELSE 'Sin documento' END
        ORDER BY value DESC, name ASC
        """,
        params,
    )

    pending_rows = _run_rows(
        session,
        f"""
        SELECT
            r.formato_nombre,
            r.codigo_publico,
            r.ats_codigo_publico,
            r.fecha_principal,
            r.usuario_nombre,
            r.actividad,
            r.ubicacion,
            r.total_no,
            r.total_documentos,
            r.importado_desde_movil
        {base_from}
          AND r.pendiente_cierre IS TRUE
        ORDER BY r.fecha_principal DESC NULLS LAST, r.registro_id DESC
        LIMIT 12
        """,
        params,
    )

    recent_rows = _run_rows(
        session,
        f"""
        SELECT
            r.formato_nombre,
            r.codigo_publico,
            r.ats_codigo_publico,
            r.fecha_principal,
            r.usuario_nombre,
            r.actividad,
            r.ubicacion,
            r.total_no,
            r.total_documentos,
            r.pendiente_cierre,
            r.importado_desde_movil
        {base_from}
        ORDER BY r.fecha_principal DESC NULLS LAST, r.registro_id DESC
        LIMIT 15
        """,
        params,
    )

    return {
        "summary": summary,
        "by_format": [{"label": _as_str(r.get("label")), "total": _as_int(r.get("total"))} for r in by_format],
        "by_month": [{"periodo": _as_str(r.get("periodo")), "total": _as_int(r.get("total"))} for r in by_month],
        "by_user": [{"usuario": _as_str(r.get("usuario")), "total": _as_int(r.get("total"))} for r in by_user],
        "by_category": [
            {"categoria": _as_str(r.get("categoria")), "total": _as_int(r.get("total"))}
            for r in by_category
        ],
        "by_origin": [{"name": _as_str(r.get("name")), "value": _as_int(r.get("value"))} for r in by_origin],
        "by_document": [
            {"name": _as_str(r.get("name")), "value": _as_int(r.get("value"))}
            for r in by_document
        ],
        "pending_rows": [_normalize_record_row(row) for row in pending_rows],
        "recent_rows": [_normalize_record_row(row) for row in recent_rows],
    }


def _normalize_record_row(row: dict) -> dict:
    return {
        "formato_nombre": _as_str(row.get("formato_nombre")),
        "codigo_publico": _as_str(row.get("codigo_publico")),
        "ats_codigo_publico": _as_str(row.get("ats_codigo_publico")) or "Sin ATS",
        "fecha_principal": _format_date(row.get("fecha_principal")),
        "usuario_nombre": _as_str(row.get("usuario_nombre")) or "Sin usuario",
        "actividad": _as_str(row.get("actividad")) or "Sin actividad",
        "ubicacion": _as_str(row.get("ubicacion")) or "Sin ubicacion",
        "total_no": _as_int(row.get("total_no")),
        "total_documentos": _as_int(row.get("total_documentos")),
        "pendiente_cierre": bool(row.get("pendiente_cierre")),
        "pendiente_cierre_label": "Pendiente" if bool(row.get("pendiente_cierre")) else "Cerrado/NA",
        "importado_desde_movil": bool(row.get("importado_desde_movil")),
        "origen_label": "Movil" if bool(row.get("importado_desde_movil")) else "Web",
    }


def fetch_sst_documents(
    session,
    *,
    current_user_id: int,
    role_code: str,
    selected_format_code: str = "",
    search_query: str = "",
    limit: int = 150,
) -> list[dict]:
    clauses = ["1 = 1"]
    params: dict[str, Any] = {"limit": int(limit or 150)}

    if is_admin(role_code):
        pass
    else:
        clauses.append("d.creado_por_usuario_id = :current_user_id")
        params["current_user_id"] = int(current_user_id or 0)

    format_code = _as_str(selected_format_code).upper()
    if format_code and format_code != "TODOS":
        clauses.append("d.formato_codigo = :format_code")
        params["format_code"] = format_code

    query_value = _as_str(search_query).lower()
    if len(query_value) >= 2:
        clauses.append(
            """
            (
                LOWER(COALESCE(d.codigo_publico, '')) LIKE :search_term
                OR LOWER(COALESCE(d.ats_codigo_publico, '')) LIKE :search_term
                OR LOWER(COALESCE(d.nombre_archivo, '')) LIKE :search_term
                OR LOWER(COALESCE(d.formato_nombre, '')) LIKE :search_term
            )
            """
        )
        params["search_term"] = f"%{query_value}%"

    where_sql = "WHERE " + " AND ".join(clauses)
    rows = _run_rows(
        session,
        f"""
        SELECT
            d.formato_codigo,
            d.formato_nombre,
            d.documento_id,
            d.registro_id,
            d.codigo_publico,
            d.ats_codigo_publico,
            d.tipo_documento,
            d.nombre_archivo,
            d.ruta_archivo,
            d.mime_type,
            d.version,
            d.generado_por_nombre,
            d.created_at
        FROM public.vw_sst_documentos_consolidado d
        {where_sql}
        ORDER BY d.created_at DESC NULLS LAST, d.documento_id DESC
        LIMIT :limit
        """,
        params,
    )
    return [
        {
            "formato_codigo": _as_str(row.get("formato_codigo")),
            "formato_nombre": _as_str(row.get("formato_nombre")),
            "documento_id": _as_int(row.get("documento_id")),
            "registro_id": _as_int(row.get("registro_id")),
            "codigo_publico": _as_str(row.get("codigo_publico")),
            "ats_codigo_publico": _as_str(row.get("ats_codigo_publico")) or "Sin ATS",
            "tipo_documento": _as_str(row.get("tipo_documento")),
            "nombre_archivo": _as_str(row.get("nombre_archivo")),
            "ruta_archivo": _as_str(row.get("ruta_archivo")),
            "mime_type": _as_str(row.get("mime_type")),
            "version": _as_int(row.get("version")) or 1,
            "version_str": str(_as_int(row.get("version")) or 1),
            "generado_por_nombre": _as_str(row.get("generado_por_nombre")) or "Sin usuario",
            "created_at": _format_date(row.get("created_at")),
        }
        for row in rows
    ]
