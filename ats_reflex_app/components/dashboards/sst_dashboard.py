from __future__ import annotations

import reflex as rx

from ...components.cards import metric_card
from ...state import SSTAnalyticsState
from ...styles import CARD_STYLE, SELECT_TRIGGER_STYLE, TABLE_SCROLL_STYLE

DASHBOARD_TABLE_MIN_WIDTH = "760px"
DASHBOARD_CHART_MIN_WIDTH = "680px"


def _empty_data_notice() -> rx.Component:
    return rx.text("Sin datos para mostrar.", color="#94a3b8", size="2")


def _responsive_table(table: rx.Component, min_width: str = DASHBOARD_TABLE_MIN_WIDTH) -> rx.Component:
    return rx.box(
        rx.box(table, min_width=min_width, width="100%"),
        min_width="0",
        **TABLE_SCROLL_STYLE,
    )


def _responsive_chart(chart: rx.Component, min_width: str = DASHBOARD_CHART_MIN_WIDTH) -> rx.Component:
    return rx.box(
        rx.box(chart, width="100%", min_width=min_width),
        width="100%",
        min_width="0",
        overflow_x="auto",
    )


def _select_field(label: str, select_component: rx.Component) -> rx.Component:
    return rx.box(
        rx.text(label, size="2", color="#475569", font_weight="600"),
        select_component,
        width="100%",
        min_width="0",
        display="grid",
        gap="0.35rem",
    )


def _filter_panel() -> rx.Component:
    format_selector = _select_field(
        "Formato",
        rx.select.root(
            rx.select.trigger(placeholder="Formato", **SELECT_TRIGGER_STYLE),
            rx.select.content(
                rx.foreach(
                    SSTAnalyticsState.format_options,
                    lambda item: rx.select.item(item["label"], value=item["id"]),
                )
            ),
            value=SSTAnalyticsState.selected_format_code,
            on_change=SSTAnalyticsState.set_selected_format_from_select,
            width="100%",
        ),
    )

    fixed_format = rx.box(
        rx.text("Formato", size="2", color="#475569", font_weight="600"),
        rx.badge(SSTAnalyticsState.selected_format_label, variant="soft", color_scheme="green", radius="full"),
        width="100%",
        display="grid",
        align_content="start",
        gap="0.55rem",
    )

    return rx.box(
        rx.hstack(
            rx.heading("Filtros SST", size="5"),
            rx.spacer(),
            rx.hstack(
                rx.badge(
                    rx.hstack(rx.text("Usuario:"), rx.text(SSTAnalyticsState.selected_siso_user_label, font_weight="700"), spacing="1"),
                    variant="soft",
                    color_scheme="green",
                ),
                rx.badge(
                    rx.hstack(rx.text("Fechas:"), rx.text(SSTAnalyticsState.rango_fechas_label, font_weight="700"), spacing="1"),
                    variant="soft",
                    color_scheme="gray",
                ),
                rx.badge(
                    rx.hstack(rx.text("Origen:"), rx.text(SSTAnalyticsState.origen_label, font_weight="700"), spacing="1"),
                    variant="soft",
                    color_scheme="gray",
                ),
                spacing="2",
                flex_wrap="wrap",
                justify="end",
            ),
            width="100%",
            align={"base": "start", "md": "center"},
            direction={"base": "column", "md": "row"},
            spacing="2",
        ),
        rx.grid(
            _select_field(
                "Empleado SISO",
                rx.select.root(
                    rx.select.trigger(placeholder="Selecciona empleado", **SELECT_TRIGGER_STYLE),
                    rx.select.content(
                        rx.foreach(
                            SSTAnalyticsState.siso_user_options,
                            lambda item: rx.select.item(item["label"], value=item["id_str"]),
                        )
                    ),
                    value=SSTAnalyticsState.selected_siso_user_id.to_string(),
                    on_change=SSTAnalyticsState.set_selected_siso_user_from_select,
                    width="100%",
                ),
            ),
            rx.cond(SSTAnalyticsState.is_global_dashboard, format_selector, fixed_format),
            _select_field(
                "Origen",
                rx.select.root(
                    rx.select.trigger(placeholder="Origen", **SELECT_TRIGGER_STYLE),
                    rx.select.content(
                        rx.select.item("Todos", value="TODOS"),
                        rx.select.item("Web", value="WEB"),
                        rx.select.item("Movil offline", value="MOVIL"),
                    ),
                    value=SSTAnalyticsState.selected_origen,
                    on_change=SSTAnalyticsState.set_selected_origen_from_select,
                    width="100%",
                ),
            ),
            _select_field(
                "Estado derivado",
                rx.select.root(
                    rx.select.trigger(placeholder="Estado", **SELECT_TRIGGER_STYLE),
                    rx.select.content(
                        rx.select.item("Todos", value="TODOS"),
                        rx.select.item("Pendiente cierre", value="PENDIENTE_CIERRE"),
                        rx.select.item("Documentado", value="DOCUMENTADO"),
                        rx.select.item("Sin documento", value="SIN_DOCUMENTO"),
                        rx.select.item("Asociado a ATS", value="ASOCIADO_ATS"),
                    ),
                    value=SSTAnalyticsState.selected_estado,
                    on_change=SSTAnalyticsState.set_selected_estado_from_select,
                    width="100%",
                ),
            ),
            _select_field(
                "Fecha inicio",
                rx.input(
                    type="date",
                    value=SSTAnalyticsState.filter_fecha_inicio,
                    on_change=SSTAnalyticsState.set_filter_fecha_inicio,
                    width="100%",
                ),
            ),
            _select_field(
                "Fecha fin",
                rx.input(
                    type="date",
                    value=SSTAnalyticsState.filter_fecha_fin,
                    on_change=SSTAnalyticsState.set_filter_fecha_fin,
                    width="100%",
                ),
            ),
            rx.box(
                rx.text("Accion", size="2", color="#475569", font_weight="600"),
                rx.button(
                    "Limpiar filtros",
                    variant="soft",
                    color_scheme="gray",
                    on_click=SSTAnalyticsState.clear_filters,
                    width="100%",
                ),
                width="100%",
                display="grid",
                gap="0.35rem",
            ),
            columns={"base": "1", "sm": "2", "xl": "4"},
            spacing="3",
            width="100%",
        ),
        rx.text(
            "Los estados de los formatos nuevos se derivan desde cierres, documentos, firmas y origen de captura.",
            color="#64748b",
            size="2",
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
        display="grid",
        gap="0.85rem",
    )


def _primary_distribution_card() -> rx.Component:
    return rx.box(
        rx.heading(SSTAnalyticsState.primary_distribution_title, size="5"),
        rx.cond(
            SSTAnalyticsState.has_primary_distribution,
            _responsive_chart(
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.x_axis(data_key="label"),
                    rx.recharts.y_axis(allow_decimals=False),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    rx.recharts.bar(
                        rx.foreach(
                            SSTAnalyticsState.primary_distribution_rows,
                            lambda row: rx.recharts.cell(fill=row["fill"]),
                        ),
                        data_key="total",
                    ),
                    data=SSTAnalyticsState.primary_distribution_rows,
                    width="100%",
                    height=320,
                )
            ),
            _empty_data_notice(),
        ),
        _responsive_table(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Categoria"),
                        rx.table.column_header_cell("Total"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        SSTAnalyticsState.primary_distribution_rows,
                        lambda row: rx.table.row(
                            rx.table.cell(row["label"]),
                            rx.table.cell(row["total"]),
                        ),
                    )
                ),
                width="100%",
            )
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
        display="grid",
        gap="0.75rem",
    )


def _month_trend_card() -> rx.Component:
    return rx.box(
        rx.heading("Tendencia mensual", size="5"),
        rx.cond(
            SSTAnalyticsState.has_month_data,
            _responsive_chart(
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.x_axis(data_key="periodo"),
                    rx.recharts.y_axis(allow_decimals=False),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    rx.recharts.line(
                        data_key="total",
                        stroke="#15803d",
                        stroke_width=3,
                        dot=True,
                        type_="monotone",
                        name="Registros",
                    ),
                    data=SSTAnalyticsState.registros_por_mes,
                    width="100%",
                    height=320,
                )
            ),
            _empty_data_notice(),
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
    )


def _user_distribution_card() -> rx.Component:
    return rx.box(
        rx.heading("Registros por usuario", size="5"),
        rx.cond(
            SSTAnalyticsState.has_user_data,
            _responsive_chart(
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.x_axis(type_="number", allow_decimals=False),
                    rx.recharts.y_axis(type_="category", data_key="usuario", width=220),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    rx.recharts.bar(
                        rx.foreach(
                            SSTAnalyticsState.registros_por_usuario,
                            lambda row: rx.recharts.cell(fill=row["fill"]),
                        ),
                        data_key="total",
                    ),
                    data=SSTAnalyticsState.registros_por_usuario,
                    layout="vertical",
                    width="100%",
                    height=360,
                )
            ),
            _empty_data_notice(),
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
    )


def _pie_card(title: str, data_var, has_data_var) -> rx.Component:
    return rx.box(
        rx.heading(title, size="5"),
        rx.cond(
            has_data_var,
            _responsive_chart(
                rx.recharts.pie_chart(
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(vertical_align="bottom"),
                    rx.recharts.pie(
                        rx.foreach(data_var, lambda row: rx.recharts.cell(fill=row["fill"])),
                        data_key="value",
                        name_key="name",
                        data=data_var,
                        inner_radius="45%",
                        outer_radius="75%",
                        padding_angle=3,
                    ),
                    width="100%",
                    height=300,
                )
            ),
            _empty_data_notice(),
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
    )


def _records_table(title: str, rows_var) -> rx.Component:
    return rx.box(
        rx.heading(title, size="5"),
        _responsive_table(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Formato"),
                        rx.table.column_header_cell("Codigo"),
                        rx.table.column_header_cell("ATS"),
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell("Usuario"),
                        rx.table.column_header_cell("Actividad"),
                        rx.table.column_header_cell("Alertas"),
                        rx.table.column_header_cell("Docs"),
                        rx.table.column_header_cell("Origen"),
                        rx.table.column_header_cell("Estado"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        rows_var,
                        lambda row: rx.table.row(
                            rx.table.cell(row["formato_nombre"]),
                            rx.table.cell(row["codigo_publico"]),
                            rx.table.cell(row["ats_codigo_publico"]),
                            rx.table.cell(row["fecha_principal"]),
                            rx.table.cell(row["usuario_nombre"]),
                            rx.table.cell(row["actividad"]),
                            rx.table.cell(row["total_no"]),
                            rx.table.cell(row["total_documentos"]),
                            rx.table.cell(rx.badge(row["origen_label"], variant="soft", color_scheme="gray")),
                            rx.table.cell(
                                rx.badge(
                                    row["pendiente_cierre_label"],
                                    variant="soft",
                                    color_scheme=rx.cond(row["pendiente_cierre"], "orange", "green"),
                                )
                            ),
                        ),
                    )
                ),
                width="100%",
            )
        ),
        **CARD_STYLE,
        width="100%",
        min_width="0",
        display="grid",
        gap="0.75rem",
    )


def sst_dashboard_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            SSTAnalyticsState.has_error,
            rx.callout(
                SSTAnalyticsState.error_message,
                icon="triangle_alert",
                color_scheme="amber",
                width="100%",
            ),
        ),
        _filter_panel(),
        rx.grid(
            metric_card("Registros", SSTAnalyticsState.total_registros),
            metric_card("Documentos", SSTAnalyticsState.total_documentos),
            metric_card("Pendientes cierre", SSTAnalyticsState.total_pendientes_cierre),
            metric_card("Importados movil", SSTAnalyticsState.total_importados_movil),
            columns={"base": "1", "md": "2", "xl": "4"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            metric_card("Asociados a ATS", SSTAnalyticsState.total_asociados_ats),
            metric_card("Respuestas NO", SSTAnalyticsState.total_respuestas_no, "Alertas de checklist."),
            metric_card("Firmas capturadas", SSTAnalyticsState.total_firmas),
            columns={"base": "1", "md": "3"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            _primary_distribution_card(),
            _month_trend_card(),
            columns={"base": "1", "xl": "2"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            _user_distribution_card(),
            _pie_card("Origen de captura", SSTAnalyticsState.origen_pie, SSTAnalyticsState.has_origin_data),
            _pie_card("Estado documental", SSTAnalyticsState.documento_pie, SSTAnalyticsState.has_document_data),
            columns={"base": "1", "xl": "3"},
            spacing="4",
            width="100%",
        ),
        _records_table("Pendientes de cierre", SSTAnalyticsState.pendientes_rows),
        _records_table("Registros recientes", SSTAnalyticsState.recientes_rows),
        width="100%",
        align="stretch",
        spacing="4",
        min_width="0",
    )
