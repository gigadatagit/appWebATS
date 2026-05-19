from __future__ import annotations

import reflex as rx

from ..state import SessionState
from ..styles import (
    CARD_STYLE,
    GREEN,
    GREEN_DARK,
    GREEN_SOFT,
    INFO_SURFACE_STYLE,
    SECONDARY_BUTTON_STYLE,
    SIDEBAR_LINK_INNER_STYLE,
    SIDEBAR_LINK_WRAPPER_STYLE,
)


def sidebar_link(label: str, href: str, icon_tag: str, active: bool = False) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon_tag, size=16, color=rx.cond(active, GREEN_DARK, "#64748b")),
            rx.text(label, font_weight=rx.cond(active, "700", "600")),
            rx.spacer(),
            rx.cond(active, rx.icon(tag="chevron_right", size=14, color=GREEN_DARK)),
            border=rx.cond(active, f"1px solid {GREEN}", "1px solid transparent"),
            bg=rx.cond(active, GREEN_SOFT, "transparent"),
            color=rx.cond(active, GREEN_DARK, "#0f172a"),
            _hover={"bg": "#f8fafc"},
            **SIDEBAR_LINK_INNER_STYLE,
        ),
        href=href,
        custom_attrs={"title": label, "aria-label": label},
        **SIDEBAR_LINK_WRAPPER_STYLE,
    )


def sidebar(current_route: str = "/ats/formato", in_drawer: bool = False) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                rx.text("Sesion activa", color="#94a3b8", size="1", text_transform="uppercase", letter_spacing="0.08em"),
                rx.text(f"Bienvenid@, {SessionState.nombre_usuario}", font_weight="500"),
                rx.text(f"Rol: {SessionState.rol_codigo}", color="#64748b", size="2"),
                **INFO_SURFACE_STYLE,
            ),
            rx.divider(),
            rx.text("Navegacion", color="#64748b", size="2", font_weight="600"),
            sidebar_link("Formato ATS", "/ats/formato", "clipboard_check", active=current_route == "/ats/formato"),
            sidebar_link("Documentos", "/ats/documentos", "file_text", active=current_route == "/ats/documentos"),
            rx.cond(
                SessionState.is_admin,
                sidebar_link(
                    "Tablero de Administrador",
                    "/admin/dashboard",
                    "layout_dashboard",
                    active=current_route == "/admin/dashboard",
                ),
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon(tag="log_out", size=15),
                    rx.text("Cerrar sesion"),
                    spacing="2",
                    align="center",
                ),
                on_click=SessionState.logout,
                width="100%",
                color_scheme="red",
                variant="soft",
                **SECONDARY_BUTTON_STYLE,
            ),
            align="stretch",
            height="100%",
            spacing="4",
        ),
        **CARD_STYLE,
        width="100%",
        min_height="auto" if in_drawer else {"base": "auto", "md": "calc(100vh - 2rem)"},
        position="relative" if in_drawer else {"base": "relative", "md": "sticky"},
        top="0" if in_drawer else "1rem",
    )
