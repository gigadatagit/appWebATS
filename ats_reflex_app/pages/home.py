from __future__ import annotations

import reflex as rx

from ..components.brand import app_brand
from ..state import SessionState
from ..styles import (
    BASE_PAGE_STYLE,
    CARD_STYLE,
    PAGE_SUBTITLE_STYLE,
    PAGE_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


@rx.page(route="/", title="Inicio | ATS", on_load=SessionState.redirect_authenticated_home)
def home_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                rx.center(
                    app_brand(subtitle="Analisis de Trabajo Seguro"),
                    width="100%",
                ),
                rx.vstack(
                    rx.heading("Gestion ATS", align="center", text_align="center", **PAGE_TITLE_STYLE),
                    rx.text(
                        "Centraliza el analisis, control de riesgos y generacion de documentos ATS en un solo flujo.",
                        text_align="center",
                        **PAGE_SUBTITLE_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.hstack(
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.icon(tag="log_in", size=15),
                                rx.text("Iniciar sesion"),
                                spacing="2",
                                align="center",
                            ),
                            width="100%",
                            **PRIMARY_BUTTON_STYLE,
                        ),
                        href="/login",
                        width="100%",
                    ),
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.icon(tag="file_text", size=15),
                                rx.text("Ver documentos"),
                                spacing="2",
                                align="center",
                            ),
                            width="100%",
                            variant="soft",
                            color_scheme="gray",
                            **SECONDARY_BUTTON_STYLE,
                        ),
                        href="/ats/documentos",
                        width="100%",
                    ),
                    width="100%",
                    spacing="3",
                    direction={"base": "column", "sm": "row"},
                    align="stretch",
                ),
                spacing="4",
                width="100%",
                align="stretch",
            ),
            **CARD_STYLE,
            width="100%",
            max_width="680px",
        ),
        padding="1rem",
        **BASE_PAGE_STYLE,
    )
