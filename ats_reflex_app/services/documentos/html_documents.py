from __future__ import annotations

import base64
import binascii
import copy
import logging
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from sqlalchemy import text

from ...access_control import AccessDeniedError, AuthContext, is_admin, is_siso
from ...config import get_supabase_storage_bucket, get_supabase_url
from ...storage_supabase import delete_file_if_exists, download_file_bytes, upload_html_bytes
from ..sst_formats import PROJECT_ROOT, get_sst_format


logger = logging.getLogger(__name__)

ASSETS_ROOT = (PROJECT_ROOT / "assets").resolve()
TEMPLATES_ROOT = (PROJECT_ROOT / "templates").resolve()
LOGO_ASSET_PATH = "brand/logoGIGAJPEG.jpeg"
HTML_MIME_TYPE = "text/html; charset=utf-8"
MAX_IMAGE_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class ResourceResult:
    data_uri: str
    available: bool
    warning: str = ""


@dataclass(frozen=True)
class RenderedHtml:
    html_bytes: bytes
    record_code: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedDocument:
    format_code: str
    record_id: int
    document_id: int
    version: int
    file_name: str
    storage_path: str
    html_bytes: bytes
    warnings: tuple[str, ...]


def _rows(session, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in session.execute(text(sql), params or {}).mappings().all()
    ]


def _one(session, sql: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    row = session.execute(text(sql), params or {}).mappings().first()
    return dict(row) if row is not None else {}


def _auth_scope(alias: str, auth: AuthContext) -> tuple[str, dict[str, Any]]:
    role = str(auth.current_user_role_codigo or "").strip().upper()
    if not (is_admin(role) or is_siso(role)):
        raise AccessDeniedError("Tu rol actual no tiene permisos para generar documentos SST.")
    if int(auth.current_user_id or 0) <= 0:
        raise AccessDeniedError("La sesion no contiene un usuario valido.")
    if is_admin(role):
        return "1 = 1", {}
    return f"{alias}.creado_por_usuario_id = :current_user_id", {
        "current_user_id": int(auth.current_user_id)
    }


def _base_context(format_code: str, record: dict[str, Any]) -> dict[str, Any]:
    config = get_sst_format(format_code)
    if config is None:
        raise RuntimeError(f"Formato documental no soportado: {format_code}.")
    return {
        "formato": {
            "codigo": config.code,
            "nombre": config.name,
            "codigo_encabezado": config.header_code,
            "version_encabezado": config.header_version,
            "fecha_vigencia": config.header_effective_date,
        },
        "documento": {
            "registro_id": int(record.get("id") or 0),
            "codigo_publico": str(record.get("codigo_publico") or ""),
            "ats_codigo_publico": str(record.get("ats_codigo_publico") or ""),
        },
        "general": record,
        "apoyos": [],
        "certificados": [],
        "peligros": [],
        "pasos": [],
        "tipos_trabajo": [],
        "tipos_tension": [],
        "medios_acceso": [],
        "checklist_secciones": [],
        "trabajadores": [],
        "firmas": [],
        "cierre": {},
        "recurso_principal": {
            "available": False,
            "data_uri": "",
            "message": "Imagen no disponible",
        },
        "warnings": [],
    }


def _group_checklist(rows: list[dict[str, Any]], default_section: str) -> list[dict[str, Any]]:
    sections: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        code = str(row.get("seccion_codigo_snapshot") or "GENERAL").strip() or "GENERAL"
        name = str(row.get("seccion_nombre_snapshot") or default_section).strip() or default_section
        key = (code, name)
        section = sections.setdefault(
            key,
            {"codigo": code, "nombre": name, "items": []},
        )
        section["items"].append(
            {
                "codigo": str(row.get("item_codigo_snapshot") or ""),
                "numero_orden": int(row.get("numero_orden_snapshot") or 0),
                "pregunta": str(row.get("pregunta_snapshot") or ""),
                "respuesta": str(row.get("respuesta") or ""),
                "observacion": str(row.get("observacion") or ""),
                "descripcion_otro": str(row.get("descripcion_otro") or ""),
                "ayuda_texto": str(row.get("ayuda_texto_snapshot") or ""),
            }
        )
    return list(sections.values())


def _normalize_workers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    workers: list[dict[str, Any]] = []
    for row in rows:
        workers.append(
            {
                "numero_orden": int(row.get("numero_orden") or 0),
                "nombre": str(
                    row.get("nombre_snapshot")
                    or row.get("nombre_trabajador")
                    or row.get("nombre_operador")
                    or ""
                ),
                "tipo_identificacion": str(row.get("tipo_identificacion") or ""),
                "documento": str(
                    row.get("documento_snapshot")
                    or row.get("numero_documento")
                    or row.get("numero_identificacion")
                    or ""
                ),
                "cargo": str(
                    row.get("cargo_snapshot")
                    or row.get("cargo_trabajador")
                    or ""
                ),
                "firma_base64": str(row.get("firma_base64") or ""),
            }
        )
    return workers


def _normalize_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signatures: list[dict[str, Any]] = []
    for row in rows:
        signatures.append(
            {
                "tipo_codigo": str(row.get("tipo_codigo") or ""),
                "tipo_nombre": str(row.get("tipo_nombre") or "Firma"),
                "nombre": str(row.get("nombre_completo") or ""),
                "cedula": str(row.get("cedula") or ""),
                "cargo": str(row.get("cargo") or ""),
                "celular": str(row.get("celular") or ""),
                "matricula": str(row.get("matricula") or ""),
                "firma_base64": str(row.get("firma_base64") or ""),
            }
        )
    return signatures


def _load_ats(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("a", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT a.*, t.codigo AS tipo_ats_codigo, t.nombre AS tipo_ats,
               a.codigo_publico AS ats_codigo_publico
        FROM public.ats a
        LEFT JOIN public.ats_tipo t ON t.id = a.tipo_ats_id
        WHERE a.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe el ATS solicitado o no tienes acceso.")
    context = _base_context("ATS", record)
    query_params = {"record_id": int(record_id)}
    context["apoyos"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro
        FROM public.ats_apoyo x
        JOIN public.apoyo_catalogo c ON c.id = x.apoyo_id
        WHERE x.ats_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["certificados"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro
        FROM public.ats_certificado x
        JOIN public.certificado_catalogo c ON c.id = x.certificado_id
        WHERE x.ats_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["peligros"] = _rows(
        session,
        """
        SELECT c.codigo, c.numero_visual, c.nombre, x.descripcion_otro
        FROM public.ats_peligro x
        JOIN public.peligro_catalogo c ON c.id = x.peligro_id
        WHERE x.ats_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    step_rows = _rows(
        session,
        """
        SELECT p.id AS paso_id, p.numero_paso, p.descripcion_paso,
               pp.id AS paso_peligro_id, pc.numero_visual AS peligro_numero,
               pc.nombre AS peligro_nombre, pp.descripcion_otro,
               ppc.control_aplicado
        FROM public.ats_paso p
        LEFT JOIN public.ats_paso_peligro pp ON pp.ats_paso_id = p.id
        LEFT JOIN public.ats_peligro ap ON ap.id = pp.ats_peligro_id
        LEFT JOIN public.peligro_catalogo pc ON pc.id = ap.peligro_id
        LEFT JOIN public.ats_paso_peligro_control ppc ON ppc.ats_paso_peligro_id = pp.id
        WHERE p.ats_id = :record_id
        ORDER BY p.numero_paso, p.id, pc.numero_visual, pp.id, ppc.id
        """,
        query_params,
    )
    steps: dict[int, dict[str, Any]] = {}
    hazards: dict[tuple[int, int], dict[str, Any]] = {}
    for row in step_rows:
        step_id = int(row.get("paso_id") or 0)
        step = steps.setdefault(
            step_id,
            {
                "numero": int(row.get("numero_paso") or 0),
                "descripcion": str(row.get("descripcion_paso") or ""),
                "peligros": [],
            },
        )
        hazard_id = int(row.get("paso_peligro_id") or 0)
        if hazard_id <= 0:
            continue
        key = (step_id, hazard_id)
        hazard = hazards.get(key)
        if hazard is None:
            hazard = {
                "numero": int(row.get("peligro_numero") or 0),
                "nombre": str(row.get("peligro_nombre") or ""),
                "detalle": str(row.get("descripcion_otro") or ""),
                "controles": [],
            }
            hazards[key] = hazard
            step["peligros"].append(hazard)
        control = str(row.get("control_aplicado") or "").strip()
        if control and control not in hazard["controles"]:
            hazard["controles"].append(control)
    context["pasos"] = list(steps.values())
    context["trabajadores"] = _normalize_workers(
        _rows(
            session,
            """
            SELECT numero_orden, nombre_trabajador, numero_documento,
                   cargo_trabajador, nombre_snapshot, documento_snapshot,
                   cargo_snapshot, firma_base64
            FROM public.ats_trabajador WHERE ats_id = :record_id
            ORDER BY numero_orden, id
            """,
            query_params,
        )
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cargo, f.firma_base64
            FROM public.firma_tipo_catalogo ft
            LEFT JOIN public.ats_firma_final f
              ON f.firma_tipo_id = ft.id AND f.ats_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    return context


def _load_preoperational(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("m", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT m.*, a.codigo_publico AS ats_codigo_publico
        FROM public.preoperacional_maquinaria m
        LEFT JOIN public.ats a ON a.id = m.ats_id
        WHERE m.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe el preoperacional solicitado o no tienes acceso.")
    context = _base_context("PREOPERACIONAL_MAQUINARIA", record)
    query_params = {"record_id": int(record_id)}
    items = _rows(
        session,
        """
        SELECT respuesta, observacion, numero_orden_snapshot, pregunta_snapshot
        FROM public.preoperacional_maquinaria_item_respuesta
        WHERE preoperacional_maquinaria_id = :record_id
        ORDER BY numero_orden_snapshot, id
        """,
        query_params,
    )
    context["checklist_secciones"] = _group_checklist(items, "Inspeccion preoperacional")
    context["trabajadores"] = _normalize_workers(
        _rows(
            session,
            """
            SELECT numero_orden, nombre_operador, tipo_identificacion,
                   numero_identificacion, firma_base64
            FROM public.preoperacional_maquinaria_operador
            WHERE preoperacional_maquinaria_id = :record_id
            ORDER BY numero_orden, id
            """,
            query_params,
        )
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cargo, f.firma_base64
            FROM public.preoperacional_maquinaria_firma_tipo_catalogo ft
            LEFT JOIN public.preoperacional_maquinaria_firma f
              ON f.firma_tipo_id = ft.id AND f.preoperacional_maquinaria_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    return context


def _load_alturas(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("m", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT m.*, a.codigo_publico AS ats_codigo_publico
        FROM public.permiso_trabajo_alturas m
        LEFT JOIN public.ats a ON a.id = m.ats_id
        WHERE m.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe el permiso de alturas solicitado o no tienes acceso.")
    context = _base_context("TRABAJO_ALTURAS", record)
    query_params = {"record_id": int(record_id)}
    context["tipos_trabajo"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro
        FROM public.permiso_trabajo_alturas_tipo_trabajo x
        JOIN public.trabajo_alturas_tipo_trabajo_catalogo c ON c.id = x.tipo_trabajo_id
        WHERE x.permiso_trabajo_alturas_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["medios_acceso"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro
        FROM public.permiso_trabajo_alturas_medio_acceso x
        JOIN public.trabajo_alturas_medio_acceso_catalogo c ON c.id = x.medio_acceso_id
        WHERE x.permiso_trabajo_alturas_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["checklist_secciones"] = _group_checklist(
        _rows(
            session,
            """
            SELECT respuesta, observacion, descripcion_otro,
                   seccion_codigo_snapshot, seccion_nombre_snapshot,
                   numero_orden_snapshot, pregunta_snapshot, ayuda_texto_snapshot
            FROM public.permiso_trabajo_alturas_checklist_respuesta
            WHERE permiso_trabajo_alturas_id = :record_id
            ORDER BY seccion_codigo_snapshot, numero_orden_snapshot, id
            """,
            query_params,
        ),
        "Lista de chequeo",
    )
    context["trabajadores"] = _normalize_workers(
        _rows(
            session,
            "SELECT * FROM public.permiso_trabajo_alturas_trabajador WHERE permiso_trabajo_alturas_id = :record_id ORDER BY numero_orden, id",
            query_params,
        )
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cedula, f.cargo, f.firma_base64
            FROM public.trabajo_alturas_firma_tipo_catalogo ft
            LEFT JOIN public.permiso_trabajo_alturas_firma f
              ON f.firma_tipo_id = ft.id AND f.permiso_trabajo_alturas_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    context["cierre"] = _one(
        session,
        "SELECT * FROM public.permiso_trabajo_alturas_cierre WHERE permiso_trabajo_alturas_id = :record_id",
        query_params,
    )
    return context


def _load_medio_acceso(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("m", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT m.*, p.codigo_publico AS permiso_alturas_codigo_publico,
               p.ats_id, p.coordinador_nombre, p.coordinador_cargo,
               p.coordinador_celular, a.codigo_publico AS ats_codigo_publico
        FROM public.lista_chequeo_medio_acceso m
        JOIN public.permiso_trabajo_alturas p ON p.id = m.permiso_trabajo_alturas_id
        LEFT JOIN public.ats a ON a.id = p.ats_id
        WHERE m.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe la lista de medio de acceso solicitada o no tienes acceso.")
    context = _base_context("MEDIO_ACCESO", record)
    query_params = {"record_id": int(record_id)}
    context["tipos_trabajo"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro
        FROM public.lista_chequeo_medio_acceso_tipo_trabajo x
        JOIN public.trabajo_alturas_tipo_trabajo_catalogo c ON c.id = x.tipo_trabajo_id
        WHERE x.lista_chequeo_medio_acceso_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["checklist_secciones"] = _group_checklist(
        _rows(
            session,
            """
            SELECT respuesta, observacion, item_codigo_snapshot,
                   numero_orden_snapshot, pregunta_snapshot, ayuda_texto_snapshot
            FROM public.lista_chequeo_medio_acceso_item_respuesta
            WHERE lista_chequeo_medio_acceso_id = :record_id
            ORDER BY numero_orden_snapshot, id
            """,
            query_params,
        ),
        "Inspeccion del medio de acceso",
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cargo, f.firma_base64
            FROM public.lista_chequeo_medio_acceso_firma_tipo_catalogo ft
            LEFT JOIN public.lista_chequeo_medio_acceso_firma f
              ON f.firma_tipo_id = ft.id AND f.lista_chequeo_medio_acceso_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    return context


def _load_energias(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("m", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT m.*, tt.codigo AS tipo_trabajo_codigo, tt.nombre AS tipo_trabajo_nombre,
               a.codigo_publico AS ats_codigo_publico
        FROM public.permiso_trabajo_energias_peligrosas m
        JOIN public.trabajo_energias_tipo_trabajo_catalogo tt ON tt.id = m.tipo_trabajo_id
        LEFT JOIN public.ats a ON a.id = m.ats_id
        WHERE m.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe el permiso de energias solicitado o no tienes acceso.")
    context = _base_context("ENERGIAS_PELIGROSAS", record)
    context["tipos_trabajo"] = [
        {"codigo": record.get("tipo_trabajo_codigo"), "nombre": record.get("tipo_trabajo_nombre")}
    ]
    query_params = {"record_id": int(record_id)}
    context["tipos_tension"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre
        FROM public.permiso_trabajo_energias_peligrosas_tipo_tension x
        JOIN public.trabajo_energias_tipo_tension_catalogo c ON c.id = x.tipo_tension_id
        WHERE x.permiso_trabajo_energias_peligrosas_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["checklist_secciones"] = _group_checklist(
        _rows(
            session,
            """
            SELECT respuesta, observacion, descripcion_otro,
                   seccion_codigo_snapshot, seccion_nombre_snapshot,
                   item_codigo_snapshot, numero_orden_snapshot,
                   pregunta_snapshot, ayuda_texto_snapshot
            FROM public.permiso_trabajo_energias_peligrosas_checklist_respuesta
            WHERE permiso_trabajo_energias_peligrosas_id = :record_id
            ORDER BY seccion_codigo_snapshot, numero_orden_snapshot, id
            """,
            query_params,
        ),
        "Lista de chequeo",
    )
    context["trabajadores"] = _normalize_workers(
        _rows(
            session,
            "SELECT * FROM public.permiso_trabajo_energias_peligrosas_trabajador WHERE permiso_trabajo_energias_peligrosas_id = :record_id ORDER BY numero_orden, id",
            query_params,
        )
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cedula, f.cargo, f.celular,
                   f.matricula, f.firma_base64
            FROM public.trabajo_energias_firma_tipo_catalogo ft
            LEFT JOIN public.permiso_trabajo_energias_peligrosas_firma f
              ON f.firma_tipo_id = ft.id AND f.permiso_trabajo_energias_peligrosas_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    context["cierre"] = _one(
        session,
        "SELECT * FROM public.permiso_trabajo_energias_peligrosas_cierre WHERE permiso_trabajo_energias_peligrosas_id = :record_id",
        query_params,
    )
    return context


def _load_caliente(session, record_id: int, auth: AuthContext) -> dict[str, Any]:
    scope, params = _auth_scope("m", auth)
    params["record_id"] = int(record_id)
    record = _one(
        session,
        f"""
        SELECT m.*, a.codigo_publico AS ats_codigo_publico
        FROM public.permiso_trabajo_caliente m
        LEFT JOIN public.ats a ON a.id = m.ats_id
        WHERE m.id = :record_id AND {scope}
        """,
        params,
    )
    if not record:
        raise AccessDeniedError("No existe el permiso de trabajo caliente solicitado o no tienes acceso.")
    context = _base_context("TRABAJO_CALIENTE", record)
    query_params = {"record_id": int(record_id)}
    context["tipos_trabajo"] = _rows(
        session,
        """
        SELECT c.codigo, c.nombre, x.descripcion_otro, x.tipo_soldadura_descripcion
        FROM public.permiso_trabajo_caliente_tipo_trabajo x
        JOIN public.trabajo_caliente_tipo_trabajo_catalogo c ON c.id = x.tipo_trabajo_id
        WHERE x.permiso_trabajo_caliente_id = :record_id ORDER BY c.orden, c.id
        """,
        query_params,
    )
    context["checklist_secciones"] = _group_checklist(
        _rows(
            session,
            """
            SELECT respuesta, observacion, descripcion_otro,
                   seccion_codigo_snapshot, seccion_nombre_snapshot,
                   item_codigo_snapshot, numero_orden_snapshot,
                   pregunta_snapshot, ayuda_texto_snapshot
            FROM public.permiso_trabajo_caliente_checklist_respuesta
            WHERE permiso_trabajo_caliente_id = :record_id
            ORDER BY seccion_codigo_snapshot, numero_orden_snapshot, id
            """,
            query_params,
        ),
        "Lista de chequeo",
    )
    context["trabajadores"] = _normalize_workers(
        _rows(
            session,
            "SELECT * FROM public.permiso_trabajo_caliente_trabajador WHERE permiso_trabajo_caliente_id = :record_id ORDER BY numero_orden, id",
            query_params,
        )
    )
    context["firmas"] = _normalize_signatures(
        _rows(
            session,
            """
            SELECT ft.codigo AS tipo_codigo, ft.nombre AS tipo_nombre,
                   f.nombre_completo, f.cedula, f.cargo, f.firma_base64
            FROM public.trabajo_caliente_firma_tipo_catalogo ft
            LEFT JOIN public.permiso_trabajo_caliente_firma f
              ON f.firma_tipo_id = ft.id AND f.permiso_trabajo_caliente_id = :record_id
            WHERE ft.activo IS TRUE ORDER BY ft.orden, ft.id
            """,
            query_params,
        )
    )
    context["cierre"] = _one(
        session,
        "SELECT * FROM public.permiso_trabajo_caliente_cierre WHERE permiso_trabajo_caliente_id = :record_id",
        query_params,
    )
    return context


_LOADERS = {
    "ATS": _load_ats,
    "PREOPERACIONAL_MAQUINARIA": _load_preoperational,
    "TRABAJO_ALTURAS": _load_alturas,
    "MEDIO_ACCESO": _load_medio_acceso,
    "ENERGIAS_PELIGROSAS": _load_energias,
    "TRABAJO_CALIENTE": _load_caliente,
}


def build_document_context(
    session,
    format_code: str,
    record_id: int,
    auth_context: AuthContext,
) -> dict[str, Any]:
    normalized = str(format_code or "").strip().upper()
    loader = _LOADERS.get(normalized)
    if loader is None:
        raise RuntimeError(f"Formato documental no soportado: {normalized or 'vacio'}.")
    if int(record_id or 0) <= 0:
        raise RuntimeError("El registro seleccionado es invalido.")
    context = loader(session, int(record_id), auth_context)
    code = str(context.get("documento", {}).get("codigo_publico") or "").strip()
    if not code:
        raise RuntimeError("El registro no contiene codigo publico.")
    return context


def _sniff_image_mime(payload: bytes) -> str:
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if payload.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if payload.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP":
        return "image/webp"
    return ""


def _data_uri(payload: bytes) -> ResourceResult:
    if not payload or len(payload) > MAX_IMAGE_BYTES:
        return ResourceResult("", False, "El recurso de imagen esta vacio o excede 8 MB.")
    mime = _sniff_image_mime(payload)
    if not mime:
        return ResourceResult("", False, "El recurso no es una imagen PNG, JPEG, GIF o WebP valida.")
    encoded = base64.b64encode(payload).decode("ascii")
    return ResourceResult(f"data:{mime};base64,{encoded}", True)


def resolve_asset_data_uri(relative_path: str, *, required: bool = False) -> ResourceResult:
    raw = str(relative_path or "").replace("\\", "/").strip().lstrip("/")
    if raw.startswith("assets/"):
        raw = raw[len("assets/") :]
    if not raw:
        warning = "No se registro una ruta de imagen."
        if required:
            raise RuntimeError(warning)
        return ResourceResult("", False, warning)
    candidate = (ASSETS_ROOT / raw).resolve()
    try:
        candidate.relative_to(ASSETS_ROOT)
    except ValueError as exc:
        warning = "La ruta de imagen intenta salir del directorio assets."
        if required:
            raise RuntimeError(warning) from exc
        return ResourceResult("", False, warning)
    if not candidate.is_file():
        warning = f"No existe el recurso assets/{raw}."
        if required:
            raise RuntimeError(warning)
        return ResourceResult("", False, warning)
    result = _data_uri(candidate.read_bytes())
    if required and not result.available:
        raise RuntimeError(result.warning)
    return result


def _storage_path_from_supabase_url(value: str) -> str:
    parsed = urlparse(value)
    configured = urlparse(get_supabase_url())
    if not parsed.scheme or not parsed.netloc or parsed.netloc != configured.netloc:
        return ""
    bucket = get_supabase_storage_bucket()
    decoded_path = unquote(parsed.path)
    markers = [
        f"/storage/v1/object/sign/{bucket}/",
        f"/storage/v1/object/public/{bucket}/",
        f"/storage/v1/object/{bucket}/",
    ]
    for marker in markers:
        if marker in decoded_path:
            return decoded_path.split(marker, 1)[1].strip("/")
    return ""


def resolve_signature_data_uri(value: str) -> ResourceResult:
    raw = str(value or "").strip()
    if not raw:
        return ResourceResult("", False, "Firma no registrada.")
    encoded = raw
    if raw.startswith("data:"):
        match = re.fullmatch(r"data:(image/[a-zA-Z0-9.+-]+);base64,(.+)", raw, flags=re.DOTALL)
        if not match:
            return ResourceResult("", False, "La firma contiene una Data URI invalida.")
        encoded = match.group(2)
    elif raw.startswith(("http://", "https://")):
        storage_path = _storage_path_from_supabase_url(raw)
        if not storage_path:
            return ResourceResult("", False, "La firma usa una URL externa no permitida.")
        try:
            return _data_uri(download_file_bytes(storage_path))
        except Exception as exc:
            return ResourceResult("", False, f"No se pudo descargar la firma: {exc}")
    elif "/" in raw and not re.fullmatch(r"[A-Za-z0-9+/=\s]+", raw):
        try:
            return _data_uri(download_file_bytes(raw))
        except Exception as exc:
            return ResourceResult("", False, f"No se pudo descargar la firma: {exc}")
    try:
        payload = base64.b64decode(re.sub(r"\s+", "", encoded), validate=True)
    except (ValueError, binascii.Error):
        return ResourceResult("", False, "La firma Base64 es invalida.")
    return _data_uri(payload)


def _prepare_resources(context: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    prepared = copy.deepcopy(context)
    warnings: list[str] = [str(item) for item in prepared.get("warnings", []) if str(item)]
    logo = resolve_asset_data_uri(LOGO_ASSET_PATH, required=True)
    prepared["logo_data_uri"] = logo.data_uri

    general = prepared["general"]
    format_code = str(prepared.get("formato", {}).get("codigo") or "").upper()
    asset_path = ""
    if format_code == "PREOPERACIONAL_MAQUINARIA":
        asset_path = str(general.get("maquina_imagen_asset_path_snapshot") or "")
    elif format_code == "MEDIO_ACCESO":
        asset_path = str(general.get("medio_acceso_imagen_asset_path_snapshot") or "")
    resource = resolve_asset_data_uri(asset_path) if asset_path or format_code in {
        "PREOPERACIONAL_MAQUINARIA",
        "MEDIO_ACCESO",
    } else ResourceResult("", False, "")
    prepared["recurso_principal"] = {
        "available": resource.available,
        "data_uri": resource.data_uri,
        "message": "" if resource.available else "Imagen no disponible",
    }
    if resource.warning:
        warnings.append(resource.warning)

    for collection_name in ("trabajadores", "firmas"):
        for index, item in enumerate(prepared.get(collection_name, []), start=1):
            signature = resolve_signature_data_uri(str(item.get("firma_base64") or ""))
            item["firma_data_uri"] = signature.data_uri
            item["firma_disponible"] = signature.available
            if signature.warning:
                warnings.append(f"{collection_name} {index}: {signature.warning}")

    closure = prepared.get("cierre", {})
    for key, value in list(closure.items()):
        if not key.endswith("_firma_base64"):
            continue
        signature = resolve_signature_data_uri(str(value or ""))
        closure[key.replace("_base64", "_data_uri")] = signature.data_uri
        closure[key.replace("_base64", "_disponible")] = signature.available
        if signature.warning:
            warnings.append(f"cierre {key}: {signature.warning}")
    prepared["warnings"] = list(dict.fromkeys(warnings))
    return prepared, prepared["warnings"]


def _display_value(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return "No registrado"
    return str(value)


def _yes_no(value: Any) -> str:
    return "Si" if bool(value) else "No"


def _jinja_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_ROOT)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=True),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["value"] = _display_value
    env.filters["yesno"] = _yes_no
    return env


class _RenderedHtmlInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_script = False
        self.image_sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered == "script":
            self.has_script = True
        if lowered == "img":
            values = dict(attrs)
            self.image_sources.append(str(values.get("src") or ""))


def _validate_rendered_html(html_text: str, record_code: str) -> None:
    if len(html_text.encode("utf-8")) < 500:
        raise RuntimeError("El HTML renderizado esta vacio o incompleto.")
    if not html_text.lstrip().lower().startswith("<!doctype html>"):
        raise RuntimeError("El documento renderizado no contiene DOCTYPE HTML.")
    for marker in ("{{", "{%", "{#"):
        if marker in html_text:
            raise RuntimeError(f"El HTML conserva un marcador Jinja sin procesar: {marker}")
    if str(record_code or "").strip() not in html_text:
        raise RuntimeError("El HTML no corresponde al codigo publico solicitado.")
    if re.search(r"(?:file://|[A-Za-z]:[\\/]|/home/|/app/assets/)", html_text, flags=re.IGNORECASE):
        raise RuntimeError("El HTML contiene una referencia al sistema de archivos local.")
    inspector = _RenderedHtmlInspector()
    inspector.feed(html_text)
    if inspector.has_script:
        raise RuntimeError("El HTML generado no puede contener JavaScript.")
    invalid_images = [src for src in inspector.image_sources if not src.startswith("data:image/")]
    if invalid_images:
        raise RuntimeError("El HTML contiene imagenes no autocontenidas.")


def render_document_html(format_code: str, context: dict[str, Any]) -> RenderedHtml:
    normalized = str(format_code or "").strip().upper()
    config = get_sst_format(normalized)
    if config is None:
        raise RuntimeError(f"Formato documental no soportado: {normalized or 'vacio'}.")
    template_path = (PROJECT_ROOT / config.template_path).resolve()
    if not template_path.is_file() or TEMPLATES_ROOT not in template_path.parents:
        raise FileNotFoundError(f"No existe la plantilla HTML: {config.template_path}")
    prepared, warnings = _prepare_resources(context)
    record_code = str(prepared.get("documento", {}).get("codigo_publico") or "").strip()
    template_name = template_path.relative_to(TEMPLATES_ROOT).as_posix()
    html_text = _jinja_environment().get_template(template_name).render(**prepared)
    _validate_rendered_html(html_text, record_code)
    return RenderedHtml(
        html_bytes=html_text.encode("utf-8"),
        record_code=record_code,
        warnings=tuple(warnings),
    )


def _safe_document_code(value: str, fallback: str) -> str:
    safe = "".join(
        char if char.isalnum() or char in ("-", "_") else "_"
        for char in str(value or "")
    ).strip("_")
    return safe or fallback


def _is_postgres_session(session) -> bool:
    try:
        return "postgres" in str(session.get_bind().dialect.name).lower()
    except Exception:
        return False


def generate_and_store_document(
    session,
    format_code: str,
    record_id: int,
    auth_context: AuthContext,
) -> GeneratedDocument:
    normalized = str(format_code or "").strip().upper()
    config = get_sst_format(normalized)
    if config is None:
        raise RuntimeError(f"Formato documental no soportado: {normalized or 'vacio'}.")
    context = build_document_context(session, normalized, record_id, auth_context)
    rendered = render_document_html(normalized, context)
    logger.info(
        "document_html_rendered format=%s record_id=%s user_id=%s warnings=%s",
        normalized,
        int(record_id),
        int(auth_context.current_user_id or 0),
        len(rendered.warnings),
    )
    uploaded_path = ""
    try:
        if _is_postgres_session(session):
            session.execute(
                text(f"SELECT id FROM public.{config.main_table} WHERE id = :record_id FOR UPDATE"),
                {"record_id": int(record_id)},
            ).first()
        version = int(
            session.execute(
                text(
                    f"""
                    SELECT COALESCE(MAX(version), 0)
                    FROM public.{config.document_table}
                    WHERE {config.document_parent_column} = :record_id
                      AND UPPER(COALESCE(tipo_documento, '')) = 'HTML'
                    """
                ),
                {"record_id": int(record_id)},
            ).scalar_one()
            or 0
        ) + 1
        safe_code = _safe_document_code(rendered.record_code, f"{normalized}_{int(record_id)}")
        file_name = f"{safe_code}_v{version}.html"
        storage_path = f"{safe_code}/v{version}/{file_name}"
        upload_html_bytes(storage_path=storage_path, html_bytes=rendered.html_bytes)
        uploaded_path = storage_path
        result = session.execute(
            text(
                f"""
                INSERT INTO public.{config.document_table} (
                    {config.document_parent_column}, tipo_documento, nombre_archivo,
                    ruta_archivo, mime_type, version, generado_por_usuario_id
                ) VALUES (
                    :record_id, 'HTML', :file_name, :storage_path,
                    :mime_type, :version, :user_id
                ) RETURNING id
                """
            ),
            {
                "record_id": int(record_id),
                "file_name": file_name,
                "storage_path": storage_path,
                "mime_type": HTML_MIME_TYPE,
                "version": version,
                "user_id": int(auth_context.current_user_id or 0) or None,
            },
        )
        document_id = int(result.scalar_one())
        if normalized == "ATS":
            target_estado_id = session.execute(
                text(
                    """
                    SELECT id FROM public.ats_estado
                    WHERE UPPER(codigo) = 'DOCUMENTO_GENERADO' LIMIT 1
                    """
                )
            ).scalar_one_or_none()
            if not target_estado_id:
                raise RuntimeError("No existe el estado ATS DOCUMENTO_GENERADO en la base.")
            session.execute(
                text(
                    """
                    UPDATE public.ats
                    SET estado_id = :estado_id, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :record_id
                    """
                ),
                {"record_id": int(record_id), "estado_id": int(target_estado_id)},
            )
        session.commit()
        logger.info(
            "document_html_stored format=%s record_id=%s document_id=%s version=%s path=%s user_id=%s",
            normalized,
            int(record_id),
            document_id,
            version,
            storage_path,
            int(auth_context.current_user_id or 0),
        )
        return GeneratedDocument(
            format_code=normalized,
            record_id=int(record_id),
            document_id=document_id,
            version=version,
            file_name=file_name,
            storage_path=storage_path,
            html_bytes=rendered.html_bytes,
            warnings=rendered.warnings,
        )
    except Exception:
        session.rollback()
        if uploaded_path:
            delete_file_if_exists(uploaded_path)
        logger.exception(
            "document_html_generation_failed format=%s record_id=%s user_id=%s",
            normalized,
            int(record_id or 0),
            int(auth_context.current_user_id or 0),
        )
        raise


def fetch_generation_candidates(
    session,
    *,
    auth_context: AuthContext,
    format_code: str,
    search_query: str = "",
    limit: int = 250,
) -> list[dict[str, Any]]:
    normalized = str(format_code or "").strip().upper()
    if get_sst_format(normalized) is None:
        return []
    role = str(auth_context.current_user_role_codigo or "").strip().upper()
    if not (is_admin(role) or is_siso(role)):
        raise AccessDeniedError("Tu rol actual no tiene permisos para generar documentos SST.")
    clauses = ["r.formato_codigo = :format_code"]
    params: dict[str, Any] = {"format_code": normalized, "limit": int(limit)}
    if not is_admin(role):
        clauses.append("r.creado_por_usuario_id = :current_user_id")
        params["current_user_id"] = int(auth_context.current_user_id or 0)
    query = str(search_query or "").strip().lower()
    if len(query) >= 2:
        clauses.append(
            "(LOWER(COALESCE(r.codigo_publico, '')) LIKE :term OR LOWER(COALESCE(r.ats_codigo_publico, '')) LIKE :term OR LOWER(COALESCE(r.actividad, '')) LIKE :term OR LOWER(COALESCE(r.ubicacion, '')) LIKE :term)"
        )
        params["term"] = f"%{query}%"
    rows = _rows(
        session,
        f"""
        SELECT r.registro_id, r.codigo_publico, r.ats_codigo_publico,
               r.fecha_principal, r.actividad, r.ubicacion
        FROM public.vw_sst_registros_consolidado r
        WHERE {' AND '.join(clauses)}
        ORDER BY r.fecha_principal DESC NULLS LAST, r.registro_id DESC
        LIMIT :limit
        """,
        params,
    )
    return [
        {
            "id": int(row.get("registro_id") or 0),
            "id_str": str(int(row.get("registro_id") or 0)),
            "codigo_publico": str(row.get("codigo_publico") or ""),
            "fecha_principal": str(row.get("fecha_principal") or ""),
            "actividad": str(row.get("actividad") or ""),
            "ubicacion": str(row.get("ubicacion") or ""),
            "label": " | ".join(
                part
                for part in (
                    str(row.get("codigo_publico") or ""),
                    str(row.get("fecha_principal") or ""),
                    str(row.get("actividad") or ""),
                    str(row.get("ubicacion") or ""),
                )
                if part
            ),
        }
        for row in rows
        if int(row.get("registro_id") or 0) > 0
    ]
