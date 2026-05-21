from __future__ import annotations

import reflex as rx

from ..state import AtsFormState
from ..template import protected_page
from ..styles import (
    CARD_STYLE,
    CALLOUT_STYLE,
    INPUT_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    SELECT_TRIGGER_STYLE,
    TABLE_SCROLL_STYLE,
)


@rx.page(route="/ats/documentos", title="Documentos ATS", on_load=AtsFormState.load_documentos_page_data)
def ats_documentos_page() -> rx.Component:
    content = rx.vstack(
        rx.box(
            rx.heading("Creación de documentos", size="5"),
            rx.text(
                "Genera un PDF del ATS seleccionado y registra el resultado en el historial de documentos.",
                color="#64748b",
            ),
            rx.vstack(
                rx.flex(
                    rx.box(
                        rx.input(
                            placeholder="Buscar ATS por fecha, numero/codigo o empresa/persona (minimo 2 caracteres)",
                            value=AtsFormState.documento_search_query,
                            on_change=AtsFormState.set_documento_search_query,
                            **INPUT_STYLE,
                        ),
                        width="100%",
                        min_width="0",
                        flex="1",
                    ),
                    rx.box(
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecciona un ATS", **SELECT_TRIGGER_STYLE),
                            rx.select.content(
                                rx.foreach(
                                    AtsFormState.documentos_ats_options,
                                    lambda item: rx.select.item(
                                        item["label"],
                                        value=item["id_str"],
                                    ),
                                )
                            ),
                            value=rx.cond(
                                AtsFormState.documento_selected_ats_id > 0,
                                AtsFormState.documento_selected_ats_id.to_string(),
                                "",
                            ),
                            on_change=AtsFormState.set_documento_selected_ats_id_from_select,
                            width="100%",
                        ),
                        width="100%",
                        min_width="0",
                        flex="1",
                    ),
                    direction={"base": "column", "md": "row"},
                    gap="1rem",
                    width="100%",
                    min_width="0",
                    align="stretch",
                ),
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="file_plus_2", size=15),
                            rx.text("Generar PDF"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=AtsFormState.generar_documento_pdf,
                        **PRIMARY_BUTTON_STYLE,
                    ),
                    rx.cond(
                        AtsFormState.documento_generado_url != "",
                        rx.link(
                            rx.button(
                                rx.hstack(
                                    rx.icon(tag="external_link", size=15),
                                    rx.text("Ver último PDF"),
                                    spacing="2",
                                    align="center",
                                ),
                                variant="soft",
                                color_scheme="green",
                                **SECONDARY_BUTTON_STYLE,
                            ),
                            href=AtsFormState.documento_generado_url,
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                    ),
                    spacing="3",
                    flex_wrap="wrap",
                    width="100%",
                ),
                rx.cond(
                    AtsFormState.documento_error != "",
                    rx.callout(AtsFormState.documento_error, color_scheme="red", icon="triangle_alert", **CALLOUT_STYLE),
                ),
                rx.cond(
                    AtsFormState.documento_success != "",
                    rx.callout(AtsFormState.documento_success, color_scheme="green", icon="circle_check", **CALLOUT_STYLE),
                ),
                display="grid",
                gap="1rem",
                width="100%",
                min_width="0",
            ),
            **CARD_STYLE,
            width="100%",
        ),
        rx.box(
            rx.heading("Documentos generados", size="5"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ATS"),
                            rx.table.column_header_cell("Archivo"),
                            rx.table.column_header_cell("Versión"),
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Acción"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AtsFormState.documentos_generados,
                            lambda row: rx.table.row(
                                rx.table.cell(row["codigo_publico"]),
                                rx.table.cell(row["nombre_archivo"]),
                                rx.table.cell(row["version_str"]),
                                rx.table.cell(row["created_at"]),
                                rx.table.cell(
                                    rx.cond(
                                        row["archivo_url"] != "",
                                        rx.link(
                                            "Ver PDF",
                                            href=row["archivo_url"],
                                            target="_blank",
                                            rel="noopener noreferrer",
                                        ),
                                        rx.badge("No disponible", variant="soft", color_scheme="gray"),
                                    ),
                                ),
                            ),
                        )
                    ),
                    width="100%",
                    min_width="680px",
                ),
                min_width="0",
                **TABLE_SCROLL_STYLE,
            ),
            **CARD_STYLE,
            width="100%",
        ),
        rx.box(
            rx.heading("ATS recientes", size="5"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Código"),
                            rx.table.column_header_cell("Empresa"),
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Estado"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AtsFormState.ats_recientes,
                            lambda row: rx.table.row(
                                rx.table.cell(row["codigo_publico"]),
                                rx.table.cell(row["empresa_persona_ejecuta"]),
                                rx.table.cell(row["fecha_elaboracion"]),
                                rx.table.cell(row["estado"]),
                            ),
                        )
                    ),
                    width="100%",
                    min_width="640px",
                ),
                min_width="0",
                **TABLE_SCROLL_STYLE,
            ),
            **CARD_STYLE,
            width="100%",
        ),
        width="100%",
        align="stretch",
        spacing="4",
    )
    return protected_page(
        "Documentos ATS",
        content,
        subtitle="Genera y consulta documentos sin salir del módulo ATS.",
        current_route="/ats/documentos",
    )
