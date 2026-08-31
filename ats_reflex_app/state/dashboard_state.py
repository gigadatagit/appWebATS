from __future__ import annotations

from datetime import date

import reflex as rx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..styles import DASHBOARD_GREEN_DARK, DASHBOARD_GREEN_LIGHT
from .session_state import SessionState


class DashboardState(rx.State):
    BRAND_GREEN_LIGHT: str = DASHBOARD_GREEN_LIGHT
    BRAND_GREEN_DARK: str = DASHBOARD_GREEN_DARK

    selected_siso_user_id: int = 0
    filter_fecha_inicio: str = ""
    filter_fecha_fin: str = ""
    siso_user_options: list[dict] = []

    total_ats: int = 0
    total_alto_riesgo: int = 0
    total_no_alto_riesgo: int = 0
    total_cerrados: int = 0
    total_documentados: int = 0
    total_formatos_asociados: int = 0
    promedio_controles_por_ats: float = 0.0

    ats_por_estado: list[dict] = []
    ats_por_tipo: list[dict] = []
    ats_por_usuario: list[dict] = []
    ats_por_peligro: list[dict] = []
    ats_por_control: list[dict] = []
    ats_por_mes: list[dict] = []
    ats_alto_riesgo_pie: list[dict] = []

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        value = color.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @classmethod
    def _interpolate_hex(cls, light: str, dark: str, ratio: float) -> str:
        light_rgb = cls._hex_to_rgb(light)
        dark_rgb = cls._hex_to_rgb(dark)
        clamped_ratio = max(0.0, min(1.0, float(ratio)))
        mixed = (
            int(light_rgb[0] + (dark_rgb[0] - light_rgb[0]) * clamped_ratio),
            int(light_rgb[1] + (dark_rgb[1] - light_rgb[1]) * clamped_ratio),
            int(light_rgb[2] + (dark_rgb[2] - light_rgb[2]) * clamped_ratio),
        )
        return cls._rgb_to_hex(mixed)

    @classmethod
    def _apply_value_gradient(
        cls,
        rows: list[dict],
        value_key: str,
        light_hex: str,
        dark_hex: str,
        color_key: str = "fill",
    ) -> list[dict]:
        if not rows:
            return []

        values = [int(row.get(value_key, 0) or 0) for row in rows]
        max_value = max(values)
        min_value = min(values)
        same_values = max_value == min_value

        colored_rows: list[dict] = []
        for row in rows:
            value = int(row.get(value_key, 0) or 0)
            ratio = 0.7 if same_values else (value - min_value) / (max_value - min_value)
            colored_row = dict(row)
            colored_row[color_key] = cls._interpolate_hex(light_hex, dark_hex, ratio)
            colored_rows.append(colored_row)
        return colored_rows

    @classmethod
    def _build_alto_riesgo_pie(cls, alto: int, no_alto: int) -> list[dict]:
        alto_value = int(alto or 0)
        no_alto_value = int(no_alto or 0)
        dark_fill = DASHBOARD_GREEN_DARK
        light_fill = DASHBOARD_GREEN_LIGHT

        # Regla estable en empate: Alto riesgo oscuro, No alto riesgo claro.
        if alto_value >= no_alto_value:
            alto_fill = dark_fill
            no_alto_fill = light_fill
        else:
            alto_fill = light_fill
            no_alto_fill = dark_fill

        return [
            {"name": "Alto riesgo", "value": alto_value, "fill": alto_fill},
            {"name": "No alto riesgo", "value": no_alto_value, "fill": no_alto_fill},
        ]

    @staticmethod
    def _filtered_ats_cte() -> str:
        return """
            WITH filtered_ats AS (
                SELECT
                    a.id,
                    a.estado_id,
                    a.tipo_ats_id,
                    a.actividad_alto_riesgo,
                    a.fecha_elaboracion,
                    a.creado_por_usuario_id
                FROM ats a
                JOIN usuario u ON u.id = a.creado_por_usuario_id
                JOIN rol r ON r.id = u.rol_id
                WHERE UPPER(r.codigo) = 'SISO'
                  AND (:usuario_id = 0 OR u.id = :usuario_id)
                  AND (:fecha_inicio IS NULL OR a.fecha_elaboracion >= :fecha_inicio)
                  AND (:fecha_fin IS NULL OR a.fecha_elaboracion <= :fecha_fin)
            )
        """

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

    @rx.var
    def porcentaje_alto_riesgo(self) -> str:
        total = int(self.total_ats or 0)
        if total <= 0:
            return "0.0%"
        value = (int(self.total_alto_riesgo or 0) * 100.0) / total
        return f"{value:.1f}%"

    @rx.var
    def porcentaje_cerrados(self) -> str:
        total = int(self.total_ats or 0)
        if total <= 0:
            return "0.0%"
        value = (int(self.total_cerrados or 0) * 100.0) / total
        return f"{value:.1f}%"

    @rx.var
    def porcentaje_documentados(self) -> str:
        total = int(self.total_ats or 0)
        if total <= 0:
            return "0.0%"
        value = (int(self.total_documentados or 0) * 100.0) / total
        return f"{value:.1f}%"

    @rx.var
    def promedio_controles_por_ats_label(self) -> str:
        return f"{float(self.promedio_controles_por_ats or 0.0):.2f}"

    @rx.var
    def filtro_usuario_label(self) -> str:
        selected_id = int(self.selected_siso_user_id or 0)
        for item in self.siso_user_options:
            if int(item.get("id", 0) or 0) == selected_id:
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
        return "Sin filtro de fechas"

    @rx.var
    def has_active_date_filter(self) -> bool:
        return bool(str(self.filter_fecha_inicio or "").strip() or str(self.filter_fecha_fin or "").strip())

    @rx.var
    def top_peligro_nombre(self) -> str:
        if len(self.ats_por_peligro) <= 0:
            return "Sin datos"
        return str(self.ats_por_peligro[0].get("peligro") or "Sin datos")

    @rx.var
    def top_peligro_total(self) -> int:
        if len(self.ats_por_peligro) <= 0:
            return 0
        return int(self.ats_por_peligro[0].get("total") or 0)

    @rx.var
    def top_control_nombre(self) -> str:
        if len(self.ats_por_control) <= 0:
            return "Sin datos"
        return str(self.ats_por_control[0].get("control") or "Sin datos")

    @rx.var
    def top_control_total(self) -> int:
        if len(self.ats_por_control) <= 0:
            return 0
        return int(self.ats_por_control[0].get("total") or 0)

    @rx.var
    def has_estado_data(self) -> bool:
        return len(self.ats_por_estado) > 0

    @rx.var
    def has_tipo_data(self) -> bool:
        return len(self.ats_por_tipo) > 0

    @rx.var
    def has_usuario_data(self) -> bool:
        return len(self.ats_por_usuario) > 0

    @rx.var
    def has_peligro_data(self) -> bool:
        return len(self.ats_por_peligro) > 0

    @rx.var
    def has_control_data(self) -> bool:
        return len(self.ats_por_control) > 0

    @rx.var
    def has_mes_data(self) -> bool:
        return len(self.ats_por_mes) > 0

    @rx.var
    def has_alto_riesgo_data(self) -> bool:
        return any(int(item.get("value", 0) or 0) > 0 for item in self.ats_alto_riesgo_pie)

    def _reset_metrics(self):
        self.total_ats = 0
        self.total_alto_riesgo = 0
        self.total_no_alto_riesgo = 0
        self.total_cerrados = 0
        self.total_documentados = 0
        self.total_formatos_asociados = 0
        self.promedio_controles_por_ats = 0.0
        self.ats_por_estado = []
        self.ats_por_tipo = []
        self.ats_por_usuario = []
        self.ats_por_peligro = []
        self.ats_por_control = []
        self.ats_por_mes = []
        self.ats_alto_riesgo_pie = []

    def _load_siso_user_options(self, session) -> None:
        rows = (
            session.execute(
                text(
                    """
                    SELECT
                        u.id AS id,
                        COALESCE(u.nombre_completo, u.username) AS label
                    FROM usuario u
                    JOIN rol r ON r.id = u.rol_id
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
            user_id = int(row["id"] or 0)
            if user_id <= 0:
                continue
            options.append(
                {
                    "id": user_id,
                    "id_str": str(user_id),
                    "label": str(row["label"] or f"Usuario {user_id}"),
                }
            )

        self.siso_user_options = options
        valid_ids = {int(item.get("id") or 0) for item in options}
        if int(self.selected_siso_user_id or 0) not in valid_ids:
            self.selected_siso_user_id = 0

    async def set_selected_siso_user_from_select(self, value: str):
        clean = (value or "").strip()
        try:
            parsed = int(clean) if clean else 0
        except Exception:
            parsed = 0
        self.selected_siso_user_id = parsed if parsed >= 0 else 0
        await self.load_metrics()

    async def set_filter_fecha_inicio(self, value: str):
        self.filter_fecha_inicio = self._normalize_iso_date(value)
        self._resolved_date_range()
        await self.load_metrics()

    async def set_filter_fecha_fin(self, value: str):
        self.filter_fecha_fin = self._normalize_iso_date(value)
        self._resolved_date_range()
        await self.load_metrics()

    async def clear_date_range_filter(self):
        self.filter_fecha_inicio = ""
        self.filter_fecha_fin = ""
        await self.load_metrics()

    async def load_metrics(self):
        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated or str(session_state.rol_codigo or "").upper() != "ADMIN":
            self._reset_metrics()
            self.siso_user_options = [{"id": 0, "id_str": "0", "label": "Todos"}]
            self.selected_siso_user_id = 0
            return

        with rx.session() as session:
            self._load_siso_user_options(session)
            date_start, date_end = self._resolved_date_range()
            parsed_start = date.fromisoformat(date_start) if date_start else None
            parsed_end = date.fromisoformat(date_end) if date_end else None
            params = {
                "usuario_id": int(self.selected_siso_user_id or 0),
                "fecha_inicio": parsed_start,
                "fecha_fin": parsed_end,
            }
            base_cte = self._filtered_ats_cte()

            self.total_ats = int(
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT COUNT(*) AS total
                        FROM filtered_ats
                        """
                    ),
                    params,
                ).scalar()
                or 0
            )

            self.total_alto_riesgo = int(
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT COUNT(*) AS total
                        FROM filtered_ats
                        WHERE actividad_alto_riesgo IS TRUE
                        """
                    ),
                    params,
                ).scalar()
                or 0
            )
            self.total_no_alto_riesgo = max(0, int(self.total_ats or 0) - int(self.total_alto_riesgo or 0))

            self.total_cerrados = int(
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT COUNT(*) AS total
                        FROM filtered_ats fa
                        JOIN ats_estado e ON e.id = fa.estado_id
                        WHERE e.codigo IN ('FINALIZADO', 'DOCUMENTO_GENERADO')
                        """
                    ),
                    params,
                ).scalar()
                or 0
            )

            self.total_documentados = int(
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT COUNT(*) AS total
                        FROM filtered_ats fa
                        JOIN ats_estado e ON e.id = fa.estado_id
                        WHERE e.codigo = 'DOCUMENTO_GENERADO'
                        """
                    ),
                    params,
                ).scalar()
                or 0
            )

            try:
                self.total_formatos_asociados = int(
                    session.execute(
                        text(
                            base_cte
                            + """
                            SELECT COALESCE(SUM(total_asociados), 0) AS total
                            FROM (
                                SELECT
                                    fa.id,
                                    (
                                        SELECT COUNT(*)
                                        FROM preoperacional_maquinaria pm
                                        WHERE pm.ats_id = fa.id
                                    )
                                    + (
                                        SELECT COUNT(*)
                                        FROM permiso_trabajo_alturas pta
                                        WHERE pta.ats_id = fa.id
                                    )
                                    + (
                                        SELECT COUNT(*)
                                        FROM permiso_trabajo_energias_peligrosas ptep
                                        WHERE ptep.ats_id = fa.id
                                    )
                                    + (
                                        SELECT COUNT(*)
                                        FROM permiso_trabajo_caliente ptc
                                        WHERE ptc.ats_id = fa.id
                                    ) AS total_asociados
                                FROM filtered_ats fa
                            ) t
                            """
                        ),
                        params,
                    ).scalar()
                    or 0
                )
            except SQLAlchemyError:
                self.total_formatos_asociados = 0

            avg_controls_raw = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT AVG(controles_por_ats) AS promedio
                        FROM (
                            SELECT
                                fa.id AS ats_id,
                                COUNT(appc.id) AS controles_por_ats
                            FROM filtered_ats fa
                            LEFT JOIN ats_paso p ON p.ats_id = fa.id
                            LEFT JOIN ats_paso_peligro app ON app.ats_paso_id = p.id
                            LEFT JOIN ats_paso_peligro_control appc ON appc.ats_paso_peligro_id = app.id
                            GROUP BY fa.id
                        ) t
                        """
                    ),
                    params,
                ).scalar()
                or 0
            )
            self.promedio_controles_por_ats = float(avg_controls_raw or 0.0)

            estado_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            e.nombre AS estado,
                            COUNT(fa.id) AS total
                        FROM ats_estado e
                        LEFT JOIN filtered_ats fa ON fa.estado_id = e.id
                        GROUP BY e.id, e.nombre, e.orden
                        ORDER BY total DESC, e.orden ASC, e.nombre ASC
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_estado = [
                {
                    "estado": str(row["estado"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in estado_rows
            ]
            self.ats_por_estado = self._apply_value_gradient(
                self.ats_por_estado,
                value_key="total",
                light_hex=self.BRAND_GREEN_LIGHT,
                dark_hex=self.BRAND_GREEN_DARK,
            )

            tipo_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            t.nombre AS tipo,
                            COUNT(fa.id) AS total
                        FROM ats_tipo t
                        LEFT JOIN filtered_ats fa ON fa.tipo_ats_id = t.id
                        GROUP BY t.id, t.nombre
                        ORDER BY total DESC, tipo ASC
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_tipo = [
                {
                    "tipo": str(row["tipo"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in tipo_rows
            ]
            self.ats_por_tipo = self._apply_value_gradient(
                self.ats_por_tipo,
                value_key="total",
                light_hex=self.BRAND_GREEN_LIGHT,
                dark_hex=self.BRAND_GREEN_DARK,
            )

            usuario_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            COALESCE(u.nombre_completo, u.username) AS usuario,
                            COUNT(fa.id) AS total
                        FROM usuario u
                        JOIN rol r ON r.id = u.rol_id
                        LEFT JOIN filtered_ats fa ON fa.creado_por_usuario_id = u.id
                        WHERE UPPER(r.codigo) = 'SISO'
                          AND (:usuario_id = 0 OR u.id = :usuario_id)
                        GROUP BY u.id, usuario
                        ORDER BY total DESC, usuario ASC
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_usuario = [
                {
                    "usuario": str(row["usuario"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in usuario_rows
            ]
            self.ats_por_usuario = self._apply_value_gradient(
                self.ats_por_usuario,
                value_key="total",
                light_hex=self.BRAND_GREEN_LIGHT,
                dark_hex=self.BRAND_GREEN_DARK,
            )

            peligro_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            'P' || pc.numero_visual || ' - ' || pc.nombre AS peligro,
                            COUNT(fa.id) AS total
                        FROM peligro_catalogo pc
                        LEFT JOIN ats_peligro ap ON ap.peligro_id = pc.id
                        LEFT JOIN filtered_ats fa ON fa.id = ap.ats_id
                        GROUP BY pc.id, pc.numero_visual, pc.nombre
                        HAVING COUNT(fa.id) > 0
                        ORDER BY total DESC, pc.numero_visual ASC
                        LIMIT 12
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_peligro = [
                {
                    "peligro": str(row["peligro"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in peligro_rows
            ]
            self.ats_por_peligro = self._apply_value_gradient(
                self.ats_por_peligro,
                value_key="total",
                light_hex=self.BRAND_GREEN_LIGHT,
                dark_hex=self.BRAND_GREEN_DARK,
            )

            control_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            COALESCE(NULLIF(TRIM(appc.control_aplicado), ''), c.nombre) AS control,
                            COUNT(appc.id) AS total
                        FROM filtered_ats fa
                        JOIN ats_paso p ON p.ats_id = fa.id
                        JOIN ats_paso_peligro app ON app.ats_paso_id = p.id
                        JOIN ats_paso_peligro_control appc ON appc.ats_paso_peligro_id = app.id
                        LEFT JOIN control_catalogo c ON c.id = appc.control_id
                        GROUP BY control
                        ORDER BY total DESC, control ASC
                        LIMIT 12
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_control = [
                {
                    "control": str(row["control"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in control_rows
            ]
            self.ats_por_control = self._apply_value_gradient(
                self.ats_por_control,
                value_key="total",
                light_hex=self.BRAND_GREEN_LIGHT,
                dark_hex=self.BRAND_GREEN_DARK,
            )

            mes_rows = (
                session.execute(
                    text(
                        base_cte
                        + """
                        SELECT
                            TO_CHAR(fa.fecha_elaboracion, 'YYYY-MM') AS periodo,
                            COUNT(*) AS total
                        FROM filtered_ats fa
                        WHERE fa.fecha_elaboracion IS NOT NULL
                        GROUP BY TO_CHAR(fa.fecha_elaboracion, 'YYYY-MM')
                        ORDER BY periodo ASC
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )
            self.ats_por_mes = [
                {
                    "periodo": str(row["periodo"] or ""),
                    "total": int(row["total"] or 0),
                }
                for row in mes_rows
            ]

            self.ats_alto_riesgo_pie = self._build_alto_riesgo_pie(
                alto=int(self.total_alto_riesgo or 0),
                no_alto=int(self.total_no_alto_riesgo or 0),
            )
