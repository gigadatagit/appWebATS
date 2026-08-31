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


def dashboard_links(current_route: str) -> rx.Component:
    return rx.fragment(
        rx.divider(),
        rx.text("Dashboards", color="#64748b", size="2", font_weight="600"),
        sidebar_link("Dashboard SST", "/sst/dashboard", "layout_dashboard", active=current_route == "/sst/dashboard"),
        sidebar_link(
            "Preoperacionales",
            "/sst/dashboard/preoperacionales",
            "wrench",
            active=current_route == "/sst/dashboard/preoperacionales",
        ),
        sidebar_link(
            "Alturas",
            "/sst/dashboard/alturas",
            "mountain",
            active=current_route == "/sst/dashboard/alturas",
        ),
        sidebar_link(
            "Medios de acceso",
            "/sst/dashboard/medios-acceso",
            "waves_ladder",
            active=current_route == "/sst/dashboard/medios-acceso",
        ),
        sidebar_link(
            "Energias peligrosas",
            "/sst/dashboard/energias-peligrosas",
            "zap",
            active=current_route == "/sst/dashboard/energias-peligrosas",
        ),
        sidebar_link(
            "Trabajo caliente",
            "/sst/dashboard/trabajo-caliente",
            "flame",
            active=current_route == "/sst/dashboard/trabajo-caliente",
        ),
        sidebar_link(
            "ATS",
            "/admin/dashboard",
            "layout_dashboard",
            active=current_route == "/admin/dashboard",
        ),
    )


def sidebar(current_route: str = "/sst/documentos", in_drawer: bool = False) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                rx.text("Sesion activa", color="#94a3b8", size="1", text_transform="uppercase", letter_spacing="0.08em"),
                rx.text(f"Bienvenid@, {SessionState.nombre_usuario}", font_weight="500"),
                rx.text(f"Rol: {SessionState.rol_codigo}", color="#64748b", size="2"),
                **INFO_SURFACE_STYLE,
            ),
            rx.divider(),
            rx.text("Formatos", color="#64748b", size="2", font_weight="600"),
            sidebar_link("Documentos SST", "/sst/documentos", "file_text", active=current_route == "/sst/documentos"),
            rx.cond(SessionState.is_admin, dashboard_links(current_route)),
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
            min_height="100%",
            spacing="4",
        ),
        **CARD_STYLE,
        width="100%",
        min_height="auto" if in_drawer else {"base": "auto", "md": "calc(100vh - 2rem)"},
        max_height="none" if in_drawer else {"base": "none", "md": "calc(100vh - 2rem)"},
        overflow_y="visible" if in_drawer else {"base": "visible", "md": "auto"},
        overscroll_behavior="auto" if in_drawer else "contain",
        position="relative" if in_drawer else {"base": "relative", "md": "sticky"},
        top="0" if in_drawer else "1rem",
    )
