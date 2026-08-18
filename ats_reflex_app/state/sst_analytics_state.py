from __future__ import annotations

from datetime import date

import reflex as rx
from sqlalchemy.exc import SQLAlchemyError

from ..access_control import get_current_auth_context
from ..services.analytics_sst import (
    SSTDashboardFilters,
    fetch_sst_dashboard,
    load_siso_user_options,
)
from ..services.sst_formats import SST_FORMATS, get_sst_format, sst_format_options
from .session_state import SessionState


SST_DASHBOARD_COLOR_SCALE: tuple[str, ...] = (
    "#14532d",
    "#15803d",
    "#22c55e",
    "#0f766e",
    "#0284c7",
    "#7c3aed",
)


class SSTAnalyticsState(rx.State):
    current_dashboard_format_code: str = ""
    selected_siso_user_id: int = 0
    selected_format_code: str = "TODOS"
    filter_fecha_inicio: str = ""
    filter_fecha_fin: str = ""
    selected_origen: str = "TODOS"
    selected_estado: str = "TODOS"

    error_message: str = ""
    siso_user_options: list[dict] = [{"id": 0, "id_str": "0", "label": "Todos"}]
    format_options: list[dict] = sst_format_options(include_all=True)

    total_registros: int = 0
    total_documentos: int = 0
    total_pendientes_cierre: int = 0
    total_importados_movil: int = 0
    total_asociados_ats: int = 0
    total_respuestas_no: int = 0
    total_firmas: int = 0

    registros_por_formato: list[dict] = []
    registros_por_mes: list[dict] = []
    registros_por_usuario: list[dict] = []
    registros_por_categoria: list[dict] = []
    origen_pie: list[dict] = []
    documento_pie: list[dict] = []
    pendientes_rows: list[dict] = []
    recientes_rows: list[dict] = []

    @staticmethod
    def _normalize_iso_date(value: str) -> str:
        raw = str(value or "").strip()
        if raw == "":
            return ""
        try:
            return date.fromisoformat(raw).isoformat()
        except Exception:
            return ""

    def _resolved_date_range(self) -> tuple[str, str]:
        start = self._normalize_iso_date(self.filter_fecha_inicio)
        end = self._normalize_iso_date(self.filter_fecha_fin)
        if start and end and start > end:
            start, end = end, start
        self.filter_fecha_inicio = start
        self.filter_fecha_fin = end
        return start, end

    @staticmethod
    def _apply_palette(rows: list[dict], value_key: str = "total", color_key: str = "fill") -> list[dict]:
        colored: list[dict] = []
        for index, row in enumerate(rows):
            item = dict(row)
            item[color_key] = SST_DASHBOARD_COLOR_SCALE[index % len(SST_DASHBOARD_COLOR_SCALE)]
            colored.append(item)
        return colored

    @rx.var
    def is_global_dashboard(self) -> bool:
        return str(self.current_dashboard_format_code or "").strip() == ""

    @rx.var
    def current_format_name(self) -> str:
        code = str(self.current_dashboard_format_code or "").strip().upper()
        item = get_sst_format(code)
        return item.name if item is not None else "Sistema SST"

    @rx.var
    def current_dashboard_title(self) -> str:
        if self.is_global_dashboard:
            return "Dashboard global SST"
        return f"Dashboard {self.current_format_name}"

    @rx.var
    def current_dashboard_subtitle(self) -> str:
        if self.is_global_dashboard:
            return "Analitica consolidada de formatos SST, documentos, cierres y origen de captura."
        return "Metricas operativas del formato, con filtros por fecha, usuario, origen y estado derivado."

    @rx.var
    def primary_distribution_title(self) -> str:
        return "Registros por formato" if self.is_global_dashboard else "Registros por categoria"

    @rx.var
    def selected_siso_user_label(self) -> str:
        selected_id = int(self.selected_siso_user_id or 0)
        for item in self.siso_user_options:
            if int(item.get("id", 0) or 0) == selected_id:
                return str(item.get("label") or "Todos")
        return "Todos"

    @rx.var
    def selected_format_label(self) -> str:
        if not self.is_global_dashboard:
            return self.current_format_name
        code = str(self.selected_format_code or "TODOS").strip().upper()
        for item in self.format_options:
            if str(item.get("id") or "").upper() == code:
                return str(item.get("label") or "Todos")
        return "Todos"

    @rx.var
    def rango_fechas_label(self) -> str:
        start = str(self.filter_fecha_inicio or "").strip()
        end = str(self.filter_fecha_fin or "").strip()
        if start and end:
            return f"{start} a {end}"
        if start:
            return f"Desde {start}"
        if end:
            return f"Hasta {end}"
        return "Sin filtro"

    @rx.var
    def origen_label(self) -> str:
        value = str(self.selected_origen or "TODOS").upper()
        if value == "MOVIL":
            return "Movil offline"
        if value == "WEB":
            return "Web"
        return "Todos"

    @rx.var
    def estado_label(self) -> str:
        value = str(self.selected_estado or "TODOS").upper()
        labels = {
            "PENDIENTE_CIERRE": "Pendiente cierre",
            "DOCUMENTADO": "Documentado",
            "SIN_DOCUMENTO": "Sin documento",
            "ASOCIADO_ATS": "Asociado a ATS",
        }
        return labels.get(value, "Todos")

    @rx.var
    def has_error(self) -> bool:
        return str(self.error_message or "").strip() != ""

    @rx.var
    def has_primary_distribution(self) -> bool:
        return len(self.registros_por_formato if self.is_global_dashboard else self.registros_por_categoria) > 0

    @rx.var
    def primary_distribution_rows(self) -> list[dict]:
        return self.registros_por_formato if self.is_global_dashboard else self.registros_por_categoria

    @rx.var
    def has_month_data(self) -> bool:
        return len(self.registros_por_mes) > 0

    @rx.var
    def has_user_data(self) -> bool:
        return len(self.registros_por_usuario) > 0

    @rx.var
    def has_origin_data(self) -> bool:
        return len(self.origen_pie) > 0

    @rx.var
    def has_document_data(self) -> bool:
        return len(self.documento_pie) > 0

    def _reset_dashboard(self):
        self.total_registros = 0
        self.total_documentos = 0
        self.total_pendientes_cierre = 0
        self.total_importados_movil = 0
        self.total_asociados_ats = 0
        self.total_respuestas_no = 0
        self.total_firmas = 0
        self.registros_por_formato = []
        self.registros_por_mes = []
        self.registros_por_usuario = []
        self.registros_por_categoria = []
        self.origen_pie = []
        self.documento_pie = []
        self.pendientes_rows = []
        self.recientes_rows = []

    def _filters(self) -> SSTDashboardFilters:
        start, end = self._resolved_date_range()
        return SSTDashboardFilters(
            fecha_inicio=date.fromisoformat(start) if start else None,
            fecha_fin=date.fromisoformat(end) if end else None,
            selected_siso_user_id=int(self.selected_siso_user_id or 0),
            selected_format_code=str(self.selected_format_code or "TODOS"),
            origen=str(self.selected_origen or "TODOS"),
            estado=str(self.selected_estado or "TODOS"),
        )

    async def _load_dashboard(self, forced_format_code: str = ""):
        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            self._reset_dashboard()
            return rx.redirect("/login")

        auth_context = get_current_auth_context(session_state)
        self.current_dashboard_format_code = str(forced_format_code or "").strip().upper()
        self.error_message = ""
        self.format_options = sst_format_options(include_all=True)

        with rx.session() as session:
            try:
                self.siso_user_options = load_siso_user_options(session)
                valid_ids = {int(item.get("id") or 0) for item in self.siso_user_options}
                if int(self.selected_siso_user_id or 0) not in valid_ids:
                    self.selected_siso_user_id = 0

                payload = fetch_sst_dashboard(
                    session,
                    self._filters(),
                    current_user_id=auth_context.current_user_id,
                    role_code=auth_context.current_user_role_codigo,
                    forced_format_code=self.current_dashboard_format_code,
                )
            except SQLAlchemyError as exc:
                self._reset_dashboard()
                self.error_message = (
                    "No fue posible consultar las views SST. Ejecuta primero "
                    "sql/02_views_sst_analytics.sql en Supabase. Detalle: "
                    f"{exc.__class__.__name__}"
                )
                return
            except Exception as exc:
                self._reset_dashboard()
                self.error_message = f"No fue posible cargar el dashboard SST: {exc}"
                return

        summary = payload.get("summary", {})
        self.total_registros = int(summary.get("total_registros") or 0)
        self.total_documentos = int(summary.get("total_documentos") or 0)
        self.total_pendientes_cierre = int(summary.get("total_pendientes_cierre") or 0)
        self.total_importados_movil = int(summary.get("total_importados_movil") or 0)
        self.total_asociados_ats = int(summary.get("total_asociados_ats") or 0)
        self.total_respuestas_no = int(summary.get("total_respuestas_no") or 0)
        self.total_firmas = int(summary.get("total_firmas") or 0)
        self.registros_por_formato = self._apply_palette(list(payload.get("by_format", [])))
        self.registros_por_mes = list(payload.get("by_month", []))
        self.registros_por_usuario = self._apply_palette(list(payload.get("by_user", [])))
        category_rows = [
            {"label": str(row.get("categoria") or ""), "total": int(row.get("total") or 0)}
            for row in list(payload.get("by_category", []))
        ]
        self.registros_por_categoria = self._apply_palette(category_rows)
        self.origen_pie = self._apply_palette(list(payload.get("by_origin", [])), value_key="value")
        self.documento_pie = self._apply_palette(list(payload.get("by_document", [])), value_key="value")
        self.pendientes_rows = list(payload.get("pending_rows", []))
        self.recientes_rows = list(payload.get("recent_rows", []))

    async def load_global_dashboard(self):
        await self._load_dashboard("")

    async def load_preoperacionales_dashboard(self):
        await self._load_dashboard("PREOPERACIONAL_MAQUINARIA")

    async def load_alturas_dashboard(self):
        await self._load_dashboard("TRABAJO_ALTURAS")

    async def load_medios_acceso_dashboard(self):
        await self._load_dashboard("MEDIO_ACCESO")

    async def load_energias_dashboard(self):
        await self._load_dashboard("ENERGIAS_PELIGROSAS")

    async def load_trabajo_caliente_dashboard(self):
        await self._load_dashboard("TRABAJO_CALIENTE")

    async def reload_current_dashboard(self):
        await self._load_dashboard(self.current_dashboard_format_code)

    async def set_selected_siso_user_from_select(self, value: str):
        try:
            parsed = int(str(value or "").strip() or "0")
        except Exception:
            parsed = 0
        self.selected_siso_user_id = max(0, parsed)
        await self.reload_current_dashboard()

    async def set_selected_format_from_select(self, value: str):
        self.selected_format_code = str(value or "TODOS").strip().upper() or "TODOS"
        await self.reload_current_dashboard()

    async def set_filter_fecha_inicio(self, value: str):
        self.filter_fecha_inicio = self._normalize_iso_date(value)
        self._resolved_date_range()
        await self.reload_current_dashboard()

    async def set_filter_fecha_fin(self, value: str):
        self.filter_fecha_fin = self._normalize_iso_date(value)
        self._resolved_date_range()
        await self.reload_current_dashboard()

    async def set_selected_origen_from_select(self, value: str):
        self.selected_origen = str(value or "TODOS").strip().upper() or "TODOS"
        await self.reload_current_dashboard()

    async def set_selected_estado_from_select(self, value: str):
        self.selected_estado = str(value or "TODOS").strip().upper() or "TODOS"
        await self.reload_current_dashboard()

    async def clear_filters(self):
        self.selected_siso_user_id = 0
        self.selected_format_code = "TODOS"
        self.filter_fecha_inicio = ""
        self.filter_fecha_fin = ""
        self.selected_origen = "TODOS"
        self.selected_estado = "TODOS"
        await self.reload_current_dashboard()
