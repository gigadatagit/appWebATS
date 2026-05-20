from __future__ import annotations

import reflex as rx

from ..components.cards import metric_card
from ..state import DashboardState
from ..styles import CARD_STYLE, SELECT_TRIGGER_STYLE, TABLE_SCROLL_STYLE
from ..template import protected_page


def _empty_data_notice() -> rx.Component:
    return rx.text("Sin datos para mostrar.", color="#94a3b8", size="2")


def _responsive_table(table: rx.Component, min_width: str = "540px") -> rx.Component:
    return rx.box(table, min_width=min_width, **TABLE_SCROLL_STYLE)


def _filter_panel() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("Filtro de analisis", size="5"),
            rx.spacer(),
            rx.hstack(
                rx.badge(
                    rx.hstack(
                        rx.text("Vista:"),
                        rx.text(DashboardState.filtro_usuario_label, font_weight="700"),
                        spacing="1",
                        align="center",
                    ),
                    variant="soft",
                    color_scheme="green",
                ),
                rx.badge(
                    rx.hstack(
                        rx.text("Fechas:"),
                        rx.text(DashboardState.rango_fechas_label, font_weight="700"),
                        spacing="1",
                        align="center",
                    ),
                    variant="soft",
                    color_scheme=rx.cond(DashboardState.has_active_date_filter, "green", "gray"),
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
            rx.box(
                rx.text("Empleado SISO", size="2", color="#475569", font_weight="600"),
                rx.select.root(
                    rx.select.trigger(placeholder="Selecciona empleado", **SELECT_TRIGGER_STYLE),
                    rx.select.content(
                        rx.foreach(
                            DashboardState.siso_user_options,
                            lambda item: rx.select.item(item["label"], value=item["id_str"]),
                        )
                    ),
                    value=DashboardState.selected_siso_user_id.to_string(),
                    on_change=DashboardState.set_selected_siso_user_from_select,
                    width="100%",
                ),
                width="100%",
                display="grid",
                gap="0.35rem",
            ),
            rx.box(
                rx.text("Fecha inicio", size="2", color="#475569", font_weight="600"),
                rx.input(
                    type="date",
                    value=DashboardState.filter_fecha_inicio,
                    on_change=DashboardState.set_filter_fecha_inicio,
                    width="100%",
                ),
                width="100%",
                display="grid",
                gap="0.35rem",
            ),
            rx.box(
                rx.text("Fecha fin", size="2", color="#475569", font_weight="600"),
                rx.input(
                    type="date",
                    value=DashboardState.filter_fecha_fin,
                    on_change=DashboardState.set_filter_fecha_fin,
                    width="100%",
                ),
                width="100%",
                display="grid",
                gap="0.35rem",
            ),
            rx.box(
                rx.text("Accion", size="2", color="#475569", font_weight="600"),
                rx.button(
                    "Limpiar fechas",
                    variant="soft",
                    color_scheme="gray",
                    on_click=DashboardState.clear_date_range_filter,
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
            "Todas las metricas y graficas se recalculan por el empleado seleccionado. "
            "La opcion Todos agrega solo usuarios con rol SISO y el rango de fechas aplica sobre fecha de elaboracion.",
            color="#64748b",
            size="2",
        ),
        **CARD_STYLE,
        width="100%",
        display="grid",
        gap="0.75rem",
    )


@rx.page(route="/admin/dashboard", title="Dashboard Admin | ATS", on_load=DashboardState.load_metrics)
def admin_dashboard_page() -> rx.Component:
    content = rx.vstack(
        _filter_panel(),
        rx.grid(
            metric_card("Total ATS", DashboardState.total_ats),
            metric_card("Alto riesgo", DashboardState.total_alto_riesgo),
            metric_card("No alto riesgo", DashboardState.total_no_alto_riesgo),
            metric_card("% Alto riesgo", DashboardState.porcentaje_alto_riesgo),
            columns={"base": "1", "md": "2", "xl": "3"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            metric_card(
                "Promedio controles / ATS",
                DashboardState.promedio_controles_por_ats_label,
                "Promedio de controles aplicados por formato.",
            ),
            metric_card(
                "Top peligro",
                DashboardState.top_peligro_total,
                DashboardState.top_peligro_nombre,
            ),
            metric_card(
                "Top control",
                DashboardState.top_control_total,
                DashboardState.top_control_nombre,
            ),
            columns={"base": "1", "md": "3"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            rx.box(
                rx.heading("ATS por estado", size="5"),
                rx.cond(
                    DashboardState.has_estado_data,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(allow_decimals=False),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(
                            rx.foreach(
                                DashboardState.ats_por_estado,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data_key="total",
                        ),
                        data=DashboardState.ats_por_estado,
                        width="100%",
                        height=300,
                    ),
                    _empty_data_notice(),
                ),
                _responsive_table(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Total"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.ats_por_estado,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["estado"]),
                                    rx.table.cell(row["total"]),
                                ),
                            ),
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            rx.box(
                rx.heading("ATS por tipo", size="5"),
                rx.cond(
                    DashboardState.has_tipo_data,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.x_axis(data_key="tipo"),
                        rx.recharts.y_axis(allow_decimals=False),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(
                            rx.foreach(
                                DashboardState.ats_por_tipo,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data_key="total",
                        ),
                        data=DashboardState.ats_por_tipo,
                        width="100%",
                        height=300,
                    ),
                    _empty_data_notice(),
                ),
                _responsive_table(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Tipo"),
                                rx.table.column_header_cell("Total"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.ats_por_tipo,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["tipo"]),
                                    rx.table.cell(row["total"]),
                                ),
                            )
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            columns={"base": "1", "xl": "2"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            rx.box(
                rx.heading("Alto riesgo vs No alto riesgo", size="5"),
                rx.cond(
                    DashboardState.has_alto_riesgo_data,
                    rx.recharts.pie_chart(
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(vertical_align="bottom"),
                        rx.recharts.pie(
                            rx.foreach(
                                DashboardState.ats_alto_riesgo_pie,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data=DashboardState.ats_alto_riesgo_pie,
                            data_key="value",
                            name_key="name",
                            inner_radius="45%",
                            outer_radius="75%",
                            padding_angle=3,
                        ),
                        width="100%",
                        height=300,
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
                                DashboardState.ats_alto_riesgo_pie,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["name"]),
                                    rx.table.cell(row["value"]),
                                ),
                            )
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            rx.box(
                rx.heading("ATS por usuario creador (SISO)", size="5"),
                rx.cond(
                    DashboardState.has_usuario_data,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.x_axis(data_key="usuario"),
                        rx.recharts.y_axis(allow_decimals=False),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(
                            rx.foreach(
                                DashboardState.ats_por_usuario,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data_key="total",
                        ),
                        data=DashboardState.ats_por_usuario,
                        width="100%",
                        height=300,
                    ),
                    _empty_data_notice(),
                ),
                _responsive_table(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Usuario"),
                                rx.table.column_header_cell("Total"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.ats_por_usuario,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["usuario"]),
                                    rx.table.cell(row["total"]),
                                ),
                            )
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            columns={"base": "1", "xl": "2"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            rx.box(
                rx.heading("Peligros mas frecuentes", size="5"),
                rx.cond(
                    DashboardState.has_peligro_data,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.x_axis(type_="number", allow_decimals=False),
                        rx.recharts.y_axis(type_="category", data_key="peligro", width=250),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(
                            rx.foreach(
                                DashboardState.ats_por_peligro,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data_key="total",
                        ),
                        data=DashboardState.ats_por_peligro,
                        layout="vertical",
                        width="100%",
                        height=420,
                    ),
                    _empty_data_notice(),
                ),
                _responsive_table(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Peligro"),
                                rx.table.column_header_cell("Total"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.ats_por_peligro,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["peligro"]),
                                    rx.table.cell(row["total"]),
                                ),
                            )
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            rx.box(
                rx.heading("Controles mas frecuentes", size="5"),
                rx.cond(
                    DashboardState.has_control_data,
                    rx.recharts.bar_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.x_axis(type_="number", allow_decimals=False),
                        rx.recharts.y_axis(type_="category", data_key="control", width=300),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(
                            rx.foreach(
                                DashboardState.ats_por_control,
                                lambda row: rx.recharts.cell(fill=row["fill"]),
                            ),
                            data_key="total",
                        ),
                        data=DashboardState.ats_por_control,
                        layout="vertical",
                        width="100%",
                        height=420,
                    ),
                    _empty_data_notice(),
                ),
                _responsive_table(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Control"),
                                rx.table.column_header_cell("Total"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.ats_por_control,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["control"]),
                                    rx.table.cell(row["total"]),
                                ),
                            )
                        ),
                        width="100%",
                    )
                ),
                **CARD_STYLE,
                width="100%",
                display="grid",
                gap="0.75rem",
            ),
            columns={"base": "1", "xl": "2"},
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.heading("Tendencia mensual de ATS", size="5"),
            rx.cond(
                DashboardState.has_mes_data,
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
                        name="ATS",
                    ),
                    data=DashboardState.ats_por_mes,
                    width="100%",
                    height=320,
                ),
                _empty_data_notice(),
            ),
            _responsive_table(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Mes"),
                            rx.table.column_header_cell("Total ATS"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            DashboardState.ats_por_mes,
                            lambda row: rx.table.row(
                                rx.table.cell(row["periodo"]),
                                rx.table.cell(row["total"]),
                            ),
                        )
                    ),
                    width="100%",
                )
            ),
            **CARD_STYLE,
            width="100%",
            display="grid",
            gap="0.75rem",
        ),
        width="100%",
        align="stretch",
        spacing="4",
    )
    return protected_page(
        "Dashboard administrativo",
        content,
        admin_only=True,
        subtitle="Metricas ATS filtrables por empleado SISO para seguimiento operativo.",
        current_route="/admin/dashboard",
    )
