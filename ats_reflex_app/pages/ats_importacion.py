from __future__ import annotations

import reflex as rx

from ..styles import CARD_STYLE, INPUT_STYLE, PRIMARY_BUTTON_STYLE
from ..template import protected_page


@rx.page(route="/ats/importacion", title="Importacion SST")
def ats_importacion_page() -> rx.Component:
    content = rx.vstack(
        rx.box(
            rx.heading("Importacion de registros SST", size="5"),
            rx.text(
                "Esta seccion queda preparada para importar registros multi-formato generados por la App Movil Offline.",
                color="#64748b",
            ),
            rx.vstack(
                rx.box(
                    rx.text("Archivo de registros SST", size="2", font_weight="600", color="#0f172a"),
                    rx.input(
                        type="file",
                        custom_attrs={"aria-label": "Seleccionar archivo de registros ATS"},
                        **INPUT_STYLE,
                    ),
                    width="100%",
                    display="grid",
                    gap="0.35rem",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon(tag="upload", size=15),
                        rx.text("Importar"),
                        spacing="2",
                        align="center",
                    ),
                    **PRIMARY_BUTTON_STYLE,
                ),
                align="start",
                spacing="3",
                width="100%",
            ),
            **CARD_STYLE,
            width="100%",
            display="grid",
            gap="1rem",
        ),
        width="100%",
        align="stretch",
        spacing="4",
    )
    return protected_page(
        "Importacion SST",
        content,
        subtitle="Base futura para validar, mapear e importar registros offline por tipo de formato.",
        current_route="/ats/importacion",
    )
