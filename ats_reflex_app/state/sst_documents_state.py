from __future__ import annotations

import reflex as rx
from sqlalchemy.exc import SQLAlchemyError

from ..access_control import get_current_auth_context
from ..config import get_supabase_signed_url_ttl_seconds
from ..services.analytics_sst import fetch_sst_documents
from ..services.documentos import get_document_format_config
from ..services.documentos.html_documents import (
    HTML_MIME_TYPE,
    fetch_generation_candidates,
    generate_and_store_document,
)
from ..services.sst_formats import sst_format_options
from ..storage_supabase import create_signed_file_url
from .session_state import SessionState


class SSTDocumentsState(rx.State):
    selected_format_code: str = "TODOS"
    error_message: str = ""
    documentos: list[dict] = []
    format_options: list[dict] = sst_format_options(include_all=True)
    generation_record_query: str = ""
    generation_candidates: list[dict] = []
    selected_record_id: int = 0
    selected_record_code: str = ""
    selected_record_label: str = ""
    generation_search_error: str = ""
    generation_error: str = ""
    generation_success: str = ""
    generation_warnings: list[str] = []

    @rx.var
    def has_error(self) -> bool:
        return str(self.error_message or "").strip() != ""

    @rx.var
    def has_documents(self) -> bool:
        return len(self.documentos) > 0

    @rx.var
    def can_generate(self) -> bool:
        return (
            str(self.selected_format_code or "").strip().upper() not in {"", "TODOS"}
            and int(self.selected_record_id or 0) > 0
        )

    @rx.var
    def can_select_generation_record(self) -> bool:
        return str(self.selected_format_code or "").strip().upper() not in {"", "TODOS"}

    @rx.var
    def has_generation_candidates(self) -> bool:
        return len(self.generation_candidates) > 0

    @rx.var
    def has_generation_warnings(self) -> bool:
        return len(self.generation_warnings) > 0

    @rx.var
    def selected_format_label(self) -> str:
        code = str(self.selected_format_code or "TODOS").strip().upper()
        for item in self.format_options:
            if str(item.get("id") or "").upper() == code:
                return str(item.get("label") or "Todos")
        return "Todos"

    @rx.var
    def generation_notice(self) -> str:
        code = str(self.selected_format_code or "TODOS").strip().upper()
        if code in {"", "TODOS"}:
            return "Selecciona un formato y un registro para generar un HTML autocontenido."
        config = get_document_format_config(code)
        if config is None:
            return "Formato no reconocido para generacion documental."
        if config.generation_enabled:
            return f"Plantilla HTML habilitada: {config.name}."
        return f"No esta disponible la plantilla: {config.template_path}"

    @staticmethod
    def _is_legacy_local_document_path(file_path: str) -> bool:
        normalized = str(file_path or "").replace("\\", "/").strip()
        return normalized.startswith("assets/") or normalized.startswith("documentos/") or normalized.startswith("/documentos/")

    @staticmethod
    def _asset_url_from_path(file_path: str) -> str:
        normalized = str(file_path or "").replace("\\", "/").strip().lstrip("/")
        if normalized.startswith("assets/"):
            normalized = normalized[len("assets/") :]
        return f"/{normalized}"

    def _resolve_document_file_urls(self, storage_path: str, file_name: str) -> tuple[str, str, str]:
        normalized = str(storage_path or "").replace("\\", "/").strip()
        if normalized == "":
            return "", "", ""
        if self._is_legacy_local_document_path(normalized):
            url = self._asset_url_from_path(normalized)
            return url, url, ""
        try:
            return (
                create_signed_file_url(
                    storage_path=normalized,
                    expires_in_seconds=get_supabase_signed_url_ttl_seconds(),
                    force_download=False,
                ),
                create_signed_file_url(
                    storage_path=normalized,
                    expires_in_seconds=get_supabase_signed_url_ttl_seconds(),
                    download_name=str(file_name or "").strip() or None,
                    force_download=True,
                ),
                "",
            )
        except Exception as exc:
            return "", "", f"No se pudo generar URL firmada para un documento: {exc}"

    def _load_generation_candidates_with_session(self, session, auth_context):
        code = str(self.selected_format_code or "").strip().upper()
        if code in {"", "TODOS"}:
            self.generation_candidates = []
            self.selected_record_id = 0
            return
        rows = fetch_generation_candidates(
            session,
            auth_context=auth_context,
            format_code=code,
            search_query=self.generation_record_query,
        )
        self.generation_candidates = rows

    async def load_documents_page_data(self):
        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            self.documentos = []
            return rx.redirect("/login")

        auth_context = get_current_auth_context(session_state)
        self.error_message = ""
        self.format_options = sst_format_options(include_all=True)

        with rx.session() as session:
            try:
                rows = fetch_sst_documents(
                    session,
                    current_user_id=auth_context.current_user_id,
                    role_code=auth_context.current_user_role_codigo,
                    selected_format_code=self.selected_format_code,
                )
                self._load_generation_candidates_with_session(session, auth_context)
            except SQLAlchemyError as exc:
                self.documentos = []
                self.error_message = (
                    "No fue posible consultar vw_sst_documentos_consolidado. "
                    "Ejecuta primero sql/02_views_sst_analytics.sql en Supabase. "
                    f"Detalle: {exc.__class__.__name__}"
                )
                return
            except Exception as exc:
                self.documentos = []
                self.error_message = f"No fue posible cargar documentos SST: {exc}"
                return

        resolved: list[dict] = []
        first_url_error = ""
        for row in rows:
            item = dict(row)
            preview_url, download_url, url_error = self._resolve_document_file_urls(
                str(item.get("ruta_archivo") or ""),
                str(item.get("nombre_archivo") or ""),
            )
            if url_error and first_url_error == "":
                first_url_error = url_error
            item["archivo_preview_url"] = preview_url
            item["archivo_download_url"] = download_url
            item["tipo_label"] = str(item.get("tipo_documento") or "Documento").upper()
            resolved.append(item)

        self.documentos = resolved
        if first_url_error and not self.error_message:
            self.error_message = first_url_error

    async def set_selected_format_from_select(self, value: str):
        self.selected_format_code = str(value or "TODOS").strip().upper() or "TODOS"
        self.generation_record_query = ""
        self.selected_record_id = 0
        self.selected_record_code = ""
        self.selected_record_label = ""
        self.generation_search_error = ""
        self.generation_error = ""
        self.generation_success = ""
        self.generation_warnings = []
        await self.load_documents_page_data()

    async def set_generation_record_query(self, value: str):
        self.generation_record_query = str(value or "")
        self.selected_record_id = 0
        self.selected_record_code = ""
        self.selected_record_label = ""
        self.generation_search_error = ""
        self.generation_error = ""
        self.generation_success = ""
        self.generation_warnings = []

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")
        auth_context = get_current_auth_context(session_state)
        with rx.session() as session:
            try:
                self._load_generation_candidates_with_session(session, auth_context)
            except Exception as exc:
                self.generation_candidates = []
                self.selected_record_id = 0
                self.generation_search_error = f"No fue posible buscar registros: {exc}"

    async def select_generation_candidate(self, record_id: int, code: str, label: str):
        try:
            parsed_id = int(record_id or 0)
        except Exception:
            parsed_id = 0
        self.selected_record_id = max(0, parsed_id)
        self.selected_record_code = str(code or "").strip()
        self.selected_record_label = str(label or "").strip()
        self.generation_record_query = ""
        self.generation_search_error = ""
        self.generation_error = ""
        self.generation_success = ""
        self.generation_warnings = []

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")
        auth_context = get_current_auth_context(session_state)
        with rx.session() as session:
            try:
                self._load_generation_candidates_with_session(session, auth_context)
            except Exception as exc:
                self.generation_candidates = []
                self.generation_search_error = f"No fue posible actualizar los registros: {exc}"

    async def generate_selected_document_html(self):
        self.generation_error = ""
        self.generation_success = ""
        self.generation_warnings = []

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")
        auth_context = get_current_auth_context(session_state)
        code = str(self.selected_format_code or "").strip().upper()
        record_id = int(self.selected_record_id or 0)
        if code in {"", "TODOS"} or record_id <= 0:
            self.generation_error = "Selecciona un formato y un registro validos."
            return
        config = get_document_format_config(code)
        if config is None or not config.generation_enabled:
            self.generation_error = "La plantilla HTML del formato no esta disponible."
            return

        with rx.session() as session:
            try:
                generated = generate_and_store_document(
                    session,
                    format_code=code,
                    record_id=record_id,
                    auth_context=auth_context,
                )
            except Exception as exc:
                self.generation_error = f"No fue posible generar el documento HTML: {exc}"
                return

        self.generation_warnings = list(generated.warnings)
        self.generation_success = (
            f"HTML generado correctamente: {generated.file_name} (v{generated.version})."
        )
        await self.load_documents_page_data()
        return rx.download(
            data=generated.html_bytes,
            filename=generated.file_name,
            mime_type=HTML_MIME_TYPE,
        )

    def redirect_legacy_ats_documents(self):
        return rx.redirect("/sst/documentos")

    async def clear_filters(self):
        self.selected_format_code = "TODOS"
        self.generation_record_query = ""
        self.generation_candidates = []
        self.selected_record_id = 0
        self.selected_record_code = ""
        self.selected_record_label = ""
        self.generation_search_error = ""
        await self.load_documents_page_data()
