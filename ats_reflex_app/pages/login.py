from __future__ import annotations

import reflex as rx

from ..components.brand import app_brand
from ..state import SessionState
from ..styles import (
    BASE_PAGE_STYLE,
    CARD_STYLE,
    INFO_SURFACE_STYLE,
    INPUT_STYLE,
    PAGE_SUBTITLE_STYLE,
    PAGE_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE,
)


@rx.page(route="/login", title="Login | ATS")
def login_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                rx.center(
                    app_brand(subtitle="Acceso seguro"),
                    width="100%",
                ),
                rx.vstack(
                    rx.heading("Iniciar sesion", text_align="center", **PAGE_TITLE_STYLE),
                    rx.text(
                        "Ingresa tus credenciales para continuar con el flujo ATS.",
                        text_align="center",
                        **PAGE_SUBTITLE_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Usuario", size="2", font_weight="600", color="#0f172a"),
                    rx.input(
                        placeholder="Ingresa tu usuario",
                        value=SessionState.username,
                        on_change=SessionState.set_username,
                        auto_complete=True,
                        **INPUT_STYLE,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Contrasena", size="2", font_weight="600", color="#0f172a"),
                    rx.input(
                        placeholder="Ingresa tu contrasena",
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
                        rx.text("Iniciar sesion"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=SessionState.login,
                    width="100%",
                    **PRIMARY_BUTTON_STYLE,
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Usuarios demo", font_weight="700", text_align="center", color="#0f172a"),
                        rx.text("admin / Admin123*", size="2", text_align="center", color="#475569"),
                        rx.text("siso / Siso123*", size="2", text_align="center", color="#475569"),
                        spacing="1",
                        width="100%",
                    ),
                    **INFO_SURFACE_STYLE,
                ),
                spacing="4",
                width="100%",
                align="stretch",
            ),
            **CARD_STYLE,
            width="100%",
            max_width="430px",
        ),
        padding="1rem",
        **BASE_PAGE_STYLE,
    )
