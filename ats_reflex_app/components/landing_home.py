from __future__ import annotations

from datetime import datetime

import reflex as rx

from .brand import app_brand


COLORS = {
    "bg_deep": "#020d08",
    "bg_base": "#04130c",
    "card": "rgba(255, 255, 255, 0.06)",
    "card_alt": "rgba(255, 255, 255, 0.09)",
    "border": "rgba(167, 243, 208, 0.22)",
    "border_soft": "rgba(167, 243, 208, 0.14)",
    "text": "#f4fff8",
    "muted": "#bddbca",
    "soft": "#84ab98",
    "green": "#16c784",
    "green_dark": "#0b8a55",
    "green_soft": "#a7f3d0",
    "green_neon": "#37ff9b",
}


PAGE_STYLE = {
    "min_height": "100vh",
    "color": COLORS["text"],
    "bg": (
        "radial-gradient(circle at 8% 4%, rgba(22, 199, 132, 0.18), transparent 36%), "
        "radial-gradient(circle at 88% 8%, rgba(55, 255, 155, 0.11), transparent 32%), "
        "linear-gradient(155deg, #020d08 0%, #07190f 48%, #0b2619 100%)"
    ),
}


CARD_STYLE = {
    "bg": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "26px",
    "box_shadow": "0 24px 70px rgba(0, 0, 0, 0.32)",
    "backdrop_filter": "blur(10px)",
}


BUTTON_PRIMARY_STYLE = {
    "bg": f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})",
    "color": "#032015",
    "border_radius": "999px",
    "padding_x": "1.25rem",
    "padding_y": "0.9rem",
    "font_weight": "800",
    "box_shadow": "0 20px 48px rgba(22, 199, 132, 0.34)",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": "0 28px 62px rgba(22, 199, 132, 0.42)",
    },
    "_active": {"transform": "translateY(1px)"},
}


BUTTON_SECONDARY_STYLE = {
    "bg": "rgba(255, 255, 255, 0.07)",
    "color": COLORS["text"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "999px",
    "padding_x": "1.25rem",
    "padding_y": "0.9rem",
    "font_weight": "700",
    "transition": "all 180ms ease",
    "_hover": {
        "bg": "rgba(255, 255, 255, 0.14)",
        "transform": "translateY(-2px)",
    },
}


def _container(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children,
        width="100%",
        max_width="1120px",
        margin_x="auto",
        padding_x={"base": "1rem", "sm": "1.25rem", "lg": "2rem"},
    )


def _button_link(label: str, href: str, primary: bool = True) -> rx.Component:
    return rx.link(
        rx.button(
            rx.hstack(
                rx.text(label),
                rx.icon(tag="arrow_right", size=15),
                spacing="2",
                align="center",
            ),
            **(BUTTON_PRIMARY_STYLE if primary else BUTTON_SECONDARY_STYLE),
        ),
        href=href,
    )


def drawer_link(label: str, href: str, icon_tag: str, primary: bool = False) -> rx.Component:
    return rx.drawer.close(
        rx.link(
            rx.hstack(
                rx.box(
                    rx.icon(
                        tag=icon_tag,
                        size=18,
                        color="#032015" if primary else COLORS["green_soft"],
                    ),
                    width="38px",
                    height="38px",
                    border_radius="14px",
                    display="grid",
                    place_items="center",
                    bg=(
                        f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})"
                        if primary
                        else "rgba(22, 199, 132, 0.14)"
                    ),
                    border=f"1px solid {COLORS['border']}",
                    flex_shrink="0",
                ),
                rx.text(
                    label,
                    font_weight="800",
                    color="#032015" if primary else COLORS["text"],
                ),
                spacing="3",
                align="center",
                width="100%",
                padding="0.85rem",
                border_radius="18px",
                bg=(
                    f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})"
                    if primary
                    else "rgba(255,255,255,0.06)"
                ),
                border=f"1px solid {COLORS['border']}",
                transition="all 180ms ease",
                _hover={
                    "transform": "translateX(3px)",
                    "bg": (
                        f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})"
                        if primary
                        else "rgba(255,255,255,0.1)"
                    ),
                },
            ),
            href=href,
            width="100%",
        )
    )


def landing_drawer() -> rx.Component:
    return rx.drawer.root(
        rx.drawer.trigger(
            rx.button(
                rx.icon(tag="menu", size=22),
                variant="ghost",
                color=COLORS["green_soft"],
                width="44px",
                height="44px",
                border_radius="14px",
                bg="rgba(255,255,255,0.06)",
                border=f"1px solid {COLORS['border']}",
                _hover={"bg": "rgba(255,255,255,0.12)"},
                custom_attrs={"aria-label": "Abrir menú"},
            )
        ),
        rx.drawer.overlay(
            bg="rgba(0, 0, 0, 0.55)",
            backdrop_filter="blur(4px)",
            z_index="90",
        ),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        app_brand(show_text=False, logo_size="46px"),
                        rx.vstack(
                            rx.drawer.title(
                                "App ATS SST",
                                font_weight="900",
                                color=COLORS["green_soft"],
                                letter_spacing="-0.03em",
                                line_height="1",
                            ),
                            rx.drawer.description(
                                "Menú de navegación",
                                color=COLORS["soft"],
                                font_size="0.85rem",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.drawer.close(
                            rx.button(
                                rx.icon(tag="x", size=18),
                                variant="ghost",
                                color=COLORS["green_soft"],
                                width="38px",
                                height="38px",
                                border_radius="12px",
                                _hover={"bg": "rgba(255,255,255,0.1)"},
                                custom_attrs={"aria-label": "Cerrar menú"},
                            )
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.box(
                        height="1px",
                        width="100%",
                        bg=COLORS["border_soft"],
                        margin_y="0.75rem",
                    ),
                    rx.vstack(
                        drawer_link("Módulos", "#modulos", "layout_grid"),
                        drawer_link("Entrar al sistema", "/login", "log_in", primary=True),
                        spacing="3",
                        width="100%",
                        align="stretch",
                    ),
                    rx.spacer(),
                    rx.box(
                        rx.text(
                            "Gestiona el ATS de forma digital, clara y trazable.",
                            color=COLORS["muted"],
                            line_height="1.6",
                            font_size="0.95rem",
                        ),
                        padding="1rem",
                        border_radius="20px",
                        bg="rgba(22, 199, 132, 0.10)",
                        border=f"1px solid {COLORS['border_soft']}",
                        width="100%",
                    ),
                    width="100%",
                    height="100%",
                    align="stretch",
                    spacing="4",
                ),
                width={"base": "86vw", "sm": "360px"},
                height="100vh",
                padding="1.15rem",
                bg="rgba(3, 16, 10, 0.96)",
                border_right=f"1px solid {COLORS['border']}",
                box_shadow="0 24px 80px rgba(0,0,0,0.45)",
            )
        ),
        direction="left",
    )


def top_bar() -> rx.Component:
    return rx.box(
        _container(
            rx.hstack(
                rx.link(
                    rx.hstack(
                        app_brand(show_text=False, logo_size="42px"),
                        rx.vstack(
                            rx.text(
                                "App ATS SST",
                                font_weight="900",
                                color=COLORS["green_soft"],
                                letter_spacing="-0.03em",
                                line_height="1",
                            ),
                            rx.text(
                                "Plataforma web operativa",
                                color=COLORS["soft"],
                                size="1",
                                display={"base": "none", "sm": "block"},
                            ),
                            spacing="0",
                            align="start",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    href="#top",
                ),
                rx.spacer(),
                landing_drawer(),
                width="100%",
                align="center",
                spacing="3",
            )
        ),
        position="sticky",
        top="0",
        z_index="80",
        padding_y="0.85rem",
        bg="rgba(3, 16, 10, 0.86)",
        backdrop_filter="blur(14px)",
        border_bottom=f"1px solid {COLORS['border']}",
    )


def module_card(icon_tag: str, title: str, text: str, href: str | None = None) -> rx.Component:
    content = rx.box(
        rx.box(
            rx.icon(tag=icon_tag, size=22, color=COLORS["green_soft"]),
            width="50px",
            height="50px",
            border_radius="17px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.14)",
            border=f"1px solid {COLORS['border']}",
            margin_bottom="1.25rem",
        ),
        rx.heading(
            title,
            size="5",
            margin_bottom="0.75rem",
            letter_spacing="-0.02em",
        ),
        rx.text(
            text,
            color=COLORS["muted"],
            line_height="1.65",
            font_size="0.96rem",
        ),
        padding={"base": "1.5rem", "md": "1.85rem"},
        min_height={"base": "220px", "md": "250px"},
        width="100%",
        height="100%",
        display="flex",
        flex_direction="column",
        justify_content="flex-start",
        transition="all 180ms ease",
        _hover={
            "transform": "translateY(-4px)",
            "bg": COLORS["card_alt"],
            "border_color": "rgba(167, 243, 208, 0.38)",
        },
        **CARD_STYLE,
    )

    if href:
        return rx.link(content, href=href, width="100%", height="100%")

    return content


def intro_section() -> rx.Component:
    return rx.box(
        _container(
            rx.vstack(
                rx.badge(
                    "App web ATS SST",
                    color_scheme="green",
                    variant="soft",
                    radius="full",
                    padding_x="0.85rem",
                    padding_y="0.35rem",
                ),
                rx.heading(
                    "Gestión digital del Análisis de Trabajo Seguro.",
                    size={"base": "8", "md": "9"},
                    line_height="1.01",
                    letter_spacing="-0.06em",
                    text_align="center",
                    max_width={"base": "100%", "md": "760px"},
                ),
                rx.text(
                    (
                        "Una plataforma web para centralizar el proceso ATS: registro estructurado, "
                        "trazabilidad operativa, control documental, generación de PDF y métricas útiles "
                        "para la gestión SST."
                    ),
                    color=COLORS["muted"],
                    line_height="1.8",
                    font_size={"base": "1rem", "md": "1.1rem"},
                    text_align="center",
                    max_width={"base": "100%", "md": "700px"},
                ),
                rx.hstack(
                    _button_link("Ver módulos", "#modulos", primary=False),
                    _button_link("Entrar al sistema", "/login", primary=True),
                    spacing={"base": "2", "sm": "3"},
                    justify="center",
                    flex_wrap="wrap",
                    margin_top={"base": "0.45rem", "md": "0.8rem"},
                ),
                width="100%",
                align="center",
                max_width="920px",
                margin_x="auto",
                spacing={"base": "4", "md": "5"},
            )
        ),
        id="top",
        padding_top={"base": "5.25rem", "md": "7rem"},
        padding_bottom={"base": "5rem", "md": "6.5rem"},
        scroll_margin_top="100px",
    )


def modules_section() -> rx.Component:
    return rx.box(
        _container(
            rx.vstack(
                rx.box(
                    rx.text(
                        "Módulos principales",
                        color=COLORS["green_soft"],
                        text_transform="uppercase",
                        letter_spacing="0.16em",
                        font_weight="800",
                        font_size="0.76rem",
                        margin_bottom="0.85rem",
                        text_align="center",
                    ),
                    rx.heading(
                        "Todo el ciclo ATS en una experiencia simple y consistente.",
                        size={"base": "7", "md": "8"},
                        line_height="1.05",
                        letter_spacing="-0.04em",
                        text_align="center",
                        max_width="820px",
                        margin_x="auto",
                        margin_bottom="1rem",
                    ),
                    rx.text(
                        "Cada módulo responde a un punto crítico del proceso operativo y documental.",
                        color=COLORS["muted"],
                        line_height="1.7",
                        text_align="center",
                        max_width="720px",
                        margin_x="auto",
                    ),
                    width="100%",
                ),
                rx.grid(
                    module_card(
                        "clipboard_check",
                        "Formato ATS por fases",
                        "Captura datos generales, tareas, peligros, controles, observaciones y cierre.",
                        "/ats/formato",
                    ),
                    module_card(
                        "route",
                        "Matriz paso-peligro-control",
                        "Relaciona cada paso de la actividad con sus peligros y medidas de control aplicadas.",
                    ),
                    module_card(
                        "users",
                        "Trabajadores y firmas",
                        "Integra el catálogo de personal, snapshot histórico y firma operativa como evidencia.",
                    ),
                    module_card(
                        "file_text",
                        "Documentos PDF",
                        "Permite búsqueda, generación, descarga y control del historial de versiones.",
                        "/ats/documentos",
                    ),
                    module_card(
                        "layout_dashboard",
                        "Dashboard administrativo",
                        "Centraliza KPIs y analítica por estado, tipo de riesgo, usuario y periodos.",
                        "/admin/dashboard",
                    ),
                    module_card(
                        "shield",
                        "Control por roles",
                        "ADMIN visualiza toda la operación; SISO trabaja sobre sus ATS autorizados.",
                    ),
                    columns={"base": "1", "md": "2", "xl": "3"},
                    gap={"base": "1.25rem", "md": "1.75rem", "xl": "2rem"},
                    width="100%",
                ),
                width="100%",
                align="stretch",
                spacing={"base": "7", "md": "8"},
            )
        ),
        id="modulos",
        padding_top={"base": "5.25rem", "md": "7rem"},
        padding_bottom={"base": "6rem", "md": "8rem"},
        bg="linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0.006))",
        border_top=f"1px solid {COLORS['border_soft']}",
        scroll_margin_top="100px",
    )


def footer() -> rx.Component:
    return rx.box(
        _container(
            rx.hstack(
                rx.text(
                    f"(c) {datetime.now().year} App ATS SST",
                    color=COLORS["soft"],
                    font_weight="700",
                ),
                rx.text(
                    "Plataforma web para gestión operativa de Análisis de Trabajo Seguro.",
                    color=COLORS["soft"],
                    text_align={"base": "left", "md": "right"},
                    max_width={"base": "100%", "md": "620px"},
                ),
                justify="between",
                align="center",
                width="100%",
                flex_wrap="wrap",
                spacing={"base": "2", "md": "3"},
            )
        ),
        padding_y={"base": "2.2rem", "md": "2.75rem"},
        border_top=f"1px solid {COLORS['border_soft']}",
    )


def landing_page() -> rx.Component:
    return rx.box(
        top_bar(),
        intro_section(),
        modules_section(),
        footer(),
        **PAGE_STYLE,
        custom_attrs={"style": "scroll-behavior: smooth;"},
    )
