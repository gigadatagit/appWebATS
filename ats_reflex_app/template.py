from __future__ import annotations

import reflex as rx

from .components.brand import app_brand
from .components.sidebar import sidebar
from .state import SessionState
from .styles import (
    BASE_PAGE_STYLE,
    CARD_STYLE,
    MOBILE_DRAWER_PANEL_STYLE,
    MOBILE_NAV_BAR_STYLE,
    PAGE_SUBTITLE_STYLE,
    PAGE_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


def _login_prompt() -> rx.Component:
    return rx.center(
        rx.vstack(
            app_brand(subtitle="Debes autenticarte"),
            rx.heading("Debes iniciar sesion", **PAGE_TITLE_STYLE),
            rx.text("Accede primero para usar la plataforma SST.", **PAGE_SUBTITLE_STYLE),
            rx.link(
                rx.button("Ir al login", **PRIMARY_BUTTON_STYLE),
                href="/login",
            ),
            spacing="4",
            width="100%",
            max_width="440px",
        ),
        padding="1rem",
        **BASE_PAGE_STYLE,
    )


def _restricted_prompt() -> rx.Component:
    return rx.center(
        rx.vstack(
            app_brand(subtitle="Permiso requerido"),
            rx.heading("Acceso restringido", **PAGE_TITLE_STYLE),
            rx.text("Esta seccion es solo para administradores.", **PAGE_SUBTITLE_STYLE),
            rx.link(
                rx.button(
                    "Ir al inicio SST",
                    variant="soft",
                    color_scheme="gray",
                    **SECONDARY_BUTTON_STYLE,
                ),
                href="/sst/dashboard",
            ),
            spacing="4",
            width="100%",
            max_width="440px",
        ),
        padding="1rem",
        **BASE_PAGE_STYLE,
    )


def _top_nav(current_route: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            app_brand(show_text=False, logo_size="108px"),
            rx.spacer(),
            rx.drawer.root(
                rx.drawer.trigger(
                    rx.button(
                        rx.icon(tag="menu", size=20),
                        variant="soft",
                        color_scheme="gray",
                        custom_attrs={"aria-label": "Abrir navegacion"},
                        **SECONDARY_BUTTON_STYLE,
                    ),
                ),
                rx.drawer.portal(
                    rx.drawer.overlay(bg="rgba(15, 23, 42, 0.55)"),
                    rx.drawer.content(
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    app_brand(show_text=False, logo_size="108px"),
                                    rx.spacer(),
                                    rx.drawer.close(
                                        rx.button(
                                            rx.icon(tag="x", size=18),
                                            variant="soft",
                                            color_scheme="gray",
                                            custom_attrs={"aria-label": "Cerrar navegacion"},
                                            **SECONDARY_BUTTON_STYLE,
                                        ),
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                                sidebar(
                                    current_route=current_route,
                                    in_drawer=True,
                                ),
                                width="100%",
                                align="stretch",
                                spacing="3",
                            ),
                            **MOBILE_DRAWER_PANEL_STYLE,
                        ),
                        align_items="stretch",
                        justify_content="start",
                        padding="0",
                    ),
                ),
                direction="left",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        display="block",
        **MOBILE_NAV_BAR_STYLE,
    )


def protected_page(
    title: str,
    content: rx.Component,
    admin_only: bool = False,
    subtitle: str = "",
    current_route: str = "",
) -> rx.Component:
    page_body = rx.box(
        rx.vstack(
            _top_nav(current_route),
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.vstack(
                            rx.heading(title, **PAGE_TITLE_STYLE),
                            rx.cond(subtitle != "", rx.text(subtitle, **PAGE_SUBTITLE_STYLE)),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        **CARD_STYLE,
                        width="100%",
                    ),
                    content,
                    spacing="4",
                    align="stretch",
                ),
                width="100%",
                min_width="0",
            ),
            spacing="4",
            width="100%",
            align="stretch",
        ),
        padding="1rem",
        **BASE_PAGE_STYLE,
    )

    protected_content = rx.cond(SessionState.is_admin, page_body, _restricted_prompt()) if admin_only else page_body

    return rx.box(
        rx.cond(
            SessionState.is_authenticated,
            protected_content,
            _login_prompt(),
        )
    )
