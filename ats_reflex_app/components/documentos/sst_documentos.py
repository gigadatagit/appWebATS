from __future__ import annotations

import reflex as rx

from ...state import SSTDocumentsState
from ...styles import (
    CARD_STYLE,
    CALLOUT_STYLE,
    INPUT_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    SELECT_TRIGGER_STYLE,
    TABLE_SCROLL_STYLE,
)


def _link_button(label: str, icon: str, href) -> rx.Component:
    return rx.link(
        rx.button(
            rx.hstack(
                rx.icon(tag=icon, size=15),
                rx.text(label),
                spacing="2",
                align="center",
            ),
            variant="soft",
            color_scheme="green",
            **SECONDARY_BUTTON_STYLE,
        ),
        href=href,
        target="_blank",
        rel="noopener noreferrer",
    )


def _format_filter() -> rx.Component:
    return rx.box(
        rx.text("Formato", size="2", color="#475569", font_weight="600"),
        rx.select.root(
            rx.select.trigger(placeholder="Formato", **SELECT_TRIGGER_STYLE),
            rx.select.content(
                rx.foreach(
                    SSTDocumentsState.format_options,
                    lambda item: rx.select.item(item["label"], value=item["id"]),
                )
            ),
            value=SSTDocumentsState.selected_format_code,
            on_change=SSTDocumentsState.set_selected_format_from_select,
            width="100%",
        ),
        width="100%",
        min_width="0",
        display="grid",
        gap="0.35rem",
    )


def _generation_status_messages() -> rx.Component:
    return rx.fragment(
        rx.cond(
            SSTDocumentsState.generation_error != "",
            rx.callout(
                SSTDocumentsState.generation_error,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
                **CALLOUT_STYLE,
            ),
        ),
        rx.cond(
            SSTDocumentsState.generation_success != "",
            rx.callout(
                SSTDocumentsState.generation_success,
                icon="circle_check",
                color_scheme="green",
                width="100%",
                **CALLOUT_STYLE,
            ),
        ),
        rx.cond(
            SSTDocumentsState.has_generation_warnings,
            rx.callout(
                rx.vstack(
                    rx.text("El documento se genero con advertencias:", font_weight="700"),
                    rx.foreach(
                        SSTDocumentsState.generation_warnings,
                        lambda warning: rx.text(warning, size="2"),
                    ),
                    align="start",
                    spacing="1",
                ),
                icon="triangle_alert",
                color_scheme="amber",
                width="100%",
                **CALLOUT_STYLE,
            ),
        ),
    )


def _generation_candidate_option(item) -> rx.Component:
    return rx.popover.close(
        rx.button(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        item["codigo_publico"],
                        font_weight="700",
                        color="#0f172a",
                        size="2",
                    ),
                    rx.spacer(),
                    rx.badge(
                        rx.cond(
                            item["fecha_principal"] != "",
                            item["fecha_principal"],
                            "Sin fecha de cierre",
                        ),
                        variant="soft",
                        color_scheme="green",
                        flex_shrink="0",
                    ),
                    width="100%",
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    rx.cond(item["actividad"] != "", item["actividad"], "Sin actividad"),
                    color="#334155",
                    size="2",
                    width="100%",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                rx.hstack(
                    rx.icon(tag="map_pin", size=13, color="#64748b", flex_shrink="0"),
                    rx.text(
                        rx.cond(item["ubicacion"] != "", item["ubicacion"], "Sin ubicacion"),
                        color="#64748b",
                        size="1",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    width="100%",
                    min_width="0",
                    align="center",
                    spacing="1",
                ),
                width="100%",
                min_width="0",
                align="start",
                spacing="1",
            ),
            on_click=SSTDocumentsState.select_generation_candidate(
                item["id"],
                item["codigo_publico"],
                item["label"],
            ),
            variant="ghost",
            color_scheme="gray",
            width="100%",
            height="auto",
            min_width="0",
            padding="0.7rem 0.75rem",
            border="1px solid #e2e8f0",
            border_radius="10px",
            bg="white",
            text_align="left",
            white_space="normal",
            cursor="pointer",
            _hover={"bg": "#f0fdf4", "border_color": "#86efac"},
            _focus_visible={
                "outline": "none",
                "box_shadow": "0 0 0 3px rgba(34, 197, 94, 0.22)",
            },
            role="option",
            title=item["label"],
        )
    )


def _generation_record_combobox() -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(
                    rx.icon(tag="search", size=15, color="#64748b", flex_shrink="0"),
                    rx.text(
                        rx.cond(
                            SSTDocumentsState.selected_record_id > 0,
                            SSTDocumentsState.selected_record_label,
                            rx.cond(
                                SSTDocumentsState.can_select_generation_record,
                                "Selecciona un registro",
                                "Selecciona primero un formato",
                            ),
                        ),
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                        text_align="left",
                        width="100%",
                        min_width="0",
                        color=rx.cond(
                            SSTDocumentsState.selected_record_id > 0,
                            "#0f172a",
                            "#64748b",
                        ),
                    ),
                    rx.icon(tag="chevron_down", size=15, color="#64748b", flex_shrink="0"),
                    width="100%",
                    min_width="0",
                    align="center",
                    spacing="2",
                ),
                disabled=rx.cond(
                    SSTDocumentsState.can_select_generation_record,
                    False,
                    True,
                ),
                variant="surface",
                color_scheme="gray",
                width="100%",
                height="42px",
                min_width="0",
                padding_x="0.75rem",
                justify_content="flex-start",
                overflow="hidden",
                border="1px solid #cbd5e1",
                border_radius="12px",
                bg="white",
                title=rx.cond(
                    SSTDocumentsState.selected_record_id > 0,
                    SSTDocumentsState.selected_record_label,
                    "Busca y selecciona un registro",
                ),
                aria_label="Seleccionar registro para generar HTML",
                _hover={"border_color": "#22c55e", "bg": "#f8fafc"},
                _focus_visible={
                    "outline": "none",
                    "box_shadow": "0 0 0 3px rgba(34, 197, 94, 0.22)",
                    "border_color": "#15803d",
                },
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.box(
                    rx.input(
                        placeholder="Buscar por codigo, ATS, actividad o ubicacion",
                        value=SSTDocumentsState.generation_record_query,
                        on_change=SSTDocumentsState.set_generation_record_query,
                        auto_complete=False,
                        debounce_timeout=300,
                        auto_focus=True,
                        **INPUT_STYLE,
                    ),
                    width="100%",
                ),
                rx.cond(
                    SSTDocumentsState.generation_search_error != "",
                    rx.callout(
                        SSTDocumentsState.generation_search_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        width="100%",
                        size="1",
                    ),
                ),
                rx.cond(
                    SSTDocumentsState.has_generation_candidates,
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                SSTDocumentsState.generation_candidates,
                                _generation_candidate_option,
                            ),
                            width="100%",
                            spacing="2",
                        ),
                        type="auto",
                        scrollbars="vertical",
                        height="min(320px, 50vh)",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon(tag="search_x", size=22, color="#94a3b8"),
                            rx.text("No hay registros que coincidan.", color="#64748b", size="2"),
                            align="center",
                            spacing="2",
                        ),
                        width="100%",
                        padding_y="1.5rem",
                    ),
                ),
                width="100%",
                min_width="0",
                spacing="3",
            ),
            align="start",
            side="bottom",
            side_offset=8,
            width={"base": "calc(100vw - 2rem)", "md": "540px"},
            max_width="calc(100vw - 2rem)",
            padding="0.75rem",
        ),
    )


def documentos_sst_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            SSTDocumentsState.has_error,
            rx.callout(
                SSTDocumentsState.error_message,
                icon="triangle_alert",
                color_scheme="amber",
                width="100%",
            ),
        ),
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("Generar HTML", size="5"),
                    rx.text(
                        "Genera HTML autocontenido y consulta el historial documental consolidado.",
                        color="#64748b",
                    ),
                    spacing="1",
                    align="start",
                ),
                width="100%",
                align={"base": "start", "md": "center"},
                direction={"base": "column", "md": "row"},
                spacing="3",
            ),
            rx.grid(
                _format_filter(),
                rx.box(
                    rx.text("Registro", size="2", color="#475569", font_weight="600"),
                    _generation_record_combobox(),
                    width="100%",
                    min_width="0",
                    display="grid",
                    gap="0.35rem",
                ),
                rx.box(
                    rx.text("Accion", size="2", color="#475569", font_weight="600"),
                    rx.button(
                        "Limpiar filtros",
                        variant="soft",
                        color_scheme="gray",
                        on_click=SSTDocumentsState.clear_filters,
                        width="100%",
                        **SECONDARY_BUTTON_STYLE,
                    ),
                    width="100%",
                    min_width="0",
                    display="grid",
                    gap="0.35rem",
                ),
                rx.box(
                    rx.text("Accion", size="2", color="#475569", font_weight="600"),
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="file_plus_2", size=15),
                            rx.text("Generar HTML"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=SSTDocumentsState.generate_selected_document_html,
                        disabled=rx.cond(SSTDocumentsState.can_generate, False, True),
                        width="100%",
                        **PRIMARY_BUTTON_STYLE,
                    ),
                    width="100%",
                    min_width="0",
                    display="grid",
                    gap="0.35rem",
                ),
                columns={"base": "1", "md": "2", "xl": "4"},
                spacing="3",
                width="100%",
            ),
            rx.callout(
                SSTDocumentsState.generation_notice,
                icon="info",
                color_scheme="green",
                width="100%",
            ),
            _generation_status_messages(),
            **CARD_STYLE,
            width="100%",
            display="grid",
            gap="1rem",
        ),
        rx.box(
            rx.heading("Historial consolidado", size="5"),
            rx.cond(
                SSTDocumentsState.has_documents,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Formato"),
                                rx.table.column_header_cell("Registro"),
                                rx.table.column_header_cell("ATS"),
                                rx.table.column_header_cell("Archivo"),
                                rx.table.column_header_cell("Version"),
                                rx.table.column_header_cell("Generado por"),
                                rx.table.column_header_cell("Fecha"),
                                rx.table.column_header_cell("Accion"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                SSTDocumentsState.documentos,
                                lambda row: rx.table.row(
                                    rx.table.cell(row["formato_nombre"]),
                                    rx.table.cell(row["codigo_publico"]),
                                    rx.table.cell(row["ats_codigo_publico"]),
                                    rx.table.cell(
                                        rx.vstack(
                                            rx.text(row["nombre_archivo"], size="2"),
                                            rx.badge(row["tipo_label"], variant="soft", color_scheme="gray", width="fit-content"),
                                            spacing="1",
                                            align="start",
                                        )
                                    ),
                                    rx.table.cell(row["version_str"]),
                                    rx.table.cell(row["generado_por_nombre"]),
                                    rx.table.cell(row["created_at"]),
                                    rx.table.cell(
                                        rx.cond(
                                            row["archivo_preview_url"] != "",
                                            rx.hstack(
                                                _link_button("Abrir", "external_link", row["archivo_preview_url"]),
                                                _link_button("Descargar", "download", row["archivo_download_url"]),
                                                spacing="2",
                                                flex_wrap="wrap",
                                            ),
                                            rx.badge("No disponible", variant="soft", color_scheme="gray"),
                                        )
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                        min_width="860px",
                    ),
                    min_width="0",
                    **TABLE_SCROLL_STYLE,
                ),
                rx.text("Sin documentos para mostrar.", color="#94a3b8", size="2"),
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
