from __future__ import annotations

import reflex as rx

from ..components.brand import app_brand
from ..state import SessionState
from ..styles import (
    BASE_PAGE_STYLE,
    CARD_STYLE,
    INPUT_STYLE,
    PAGE_SUBTITLE_STYLE,
    PAGE_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE,
)


@rx.page(route="/login", title="Login | SST")
def login_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                rx.center(
                    app_brand(subtitle="Acceso seguro"),
                    width="100%",
                ),
                rx.vstack(
                    rx.heading("Iniciar sesión", align="center", text_align="center", **PAGE_TITLE_STYLE),
                    rx.text(
                        "Ingresa tu correo y contraseña para continuar con la plataforma SST.",
                        text_align="center",
                        **PAGE_SUBTITLE_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Correo", size="2", font_weight="600", color="#0f172a"),
                    rx.input(
                        placeholder="Ingresa tu correo",
                        value=SessionState.email,
                        on_change=SessionState.set_email,
                        auto_complete=True,
                        **INPUT_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Contraseña", size="2", font_weight="600", color="#0f172a"),
                    rx.input(
                        placeholder="Ingresa tu contraseña",
                        type="password",
                        value=SessionState.password,
                        on_change=SessionState.set_password,
                        auto_complete=True,
                        **INPUT_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    SessionState.login_error != "",
                    rx.callout(
                        SessionState.login_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.button(
                    rx.hstack(
                        rx.icon(tag="log_in", size=15),
                        rx.text("Iniciar sesión"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=SessionState.login,
                    width="100%",
                    **PRIMARY_BUTTON_STYLE,
                ),
                spacing="4",
                width="100%",
                align="stretch",
            ),
            **CARD_STYLE,
            width="100%",
            max_width="430px",
        ),
        width="100%",
        padding="1rem",
        **BASE_PAGE_STYLE,
    )
