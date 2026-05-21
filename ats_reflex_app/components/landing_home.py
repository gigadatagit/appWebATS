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

SIDEBAR_WIDTH = "280px"

PAGE_STYLE = {
    "min_height": "100vh",
    "color": COLORS["text"],
    "bg": (
        "radial-gradient(circle at 8% 5%, rgba(22, 199, 132, 0.18), transparent 34%), "
        "radial-gradient(circle at 88% 10%, rgba(55, 255, 155, 0.10), transparent 30%), "
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
    "padding_x": "1.35rem",
    "padding_y": "0.95rem",
    "font_weight": "800",
    "box_shadow": "0 20px 48px rgba(22, 199, 132, 0.34)",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": "0 28px 62px rgba(22, 199, 132, 0.42)",
    },
}

BUTTON_SECONDARY_STYLE = {
    "bg": "rgba(255, 255, 255, 0.07)",
    "color": COLORS["text"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "999px",
    "padding_x": "1.35rem",
    "padding_y": "0.95rem",
    "font_weight": "700",
    "_hover": {
        "bg": "rgba(255, 255, 255, 0.14)",
        "transform": "translateY(-2px)",
    },
}


def _main_container(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children,
        width="100%",
        max_width="1120px",
        margin_x="auto",
        padding_x={"base": "1rem", "md": "2rem", "xl": "2.5rem"},
    )


def sidebar_link(label: str, href: str, icon_tag: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.box(
                rx.icon(tag=icon_tag, size=17, color=COLORS["green_soft"]),
                width="34px",
                height="34px",
                border_radius="12px",
                display="grid",
                place_items="center",
                bg="rgba(22, 199, 132, 0.12)",
                border=f"1px solid {COLORS['border_soft']}",
                flex_shrink="0",
            ),
            rx.text(label, font_weight="700", color=COLORS["muted"]),
            spacing="3",
            align="center",
            width="100%",
            padding="0.75rem",
            border_radius="16px",
            transition="all 180ms ease",
            _hover={
                "bg": "rgba(255, 255, 255, 0.08)",
                "transform": "translateX(3px)",
            },
        ),
        href=href,
        width="100%",
    )


def landing_sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.link(
                rx.hstack(
                    app_brand(show_text=False, logo_size="46px"),
                    rx.vstack(
                        rx.text(
                            "App ATS SST",
                            font_weight="900",
                            color=COLORS["green_soft"],
                            letter_spacing="-0.03em",
                            line_height="1",
                        ),
                        rx.text(
                            "Gestión SST digital",
                            color=COLORS["soft"],
                            size="1",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                href="#top",
            ),
            rx.box(
                height="1px",
                width="100%",
                bg=COLORS["border_soft"],
                margin_y="0.75rem",
            ),
            rx.vstack(
                sidebar_link("Inicio", "#top", "home"),
                sidebar_link("Módulos", "#modulos", "layout_grid"),
                sidebar_link("Entrar al sistema", "/login", "log_in"),
                spacing="3",
                width="100%",
                align="stretch",
            ),
            rx.spacer(),
            rx.box(
                rx.text(
                    "Digitaliza el ATS con trazabilidad, documentos PDF y control operativo.",
                    color=COLORS["soft"],
                    line_height="1.55",
                    font_size="0.9rem",
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
        width=SIDEBAR_WIDTH,
        min_width=SIDEBAR_WIDTH,
        height="calc(100vh - 2rem)",
        position="sticky",
        top="1rem",
        padding="1rem",
        margin="1rem",
        display={"base": "none", "lg": "block"},
        **CARD_STYLE,
    )


def mobile_nav() -> rx.Component:
    return rx.box(
        _main_container(
            rx.hstack(
                rx.link(
                    rx.hstack(
                        app_brand(show_text=False, logo_size="40px"),
                        rx.text(
                            "App ATS SST",
                            font_weight="900",
                            color=COLORS["green_soft"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    href="#top",
                ),
                rx.hstack(
                    rx.link("Inicio", href="#top", color=COLORS["green_soft"], font_weight="700"),
                    rx.link("Módulos", href="#modulos", color=COLORS["green_soft"], font_weight="700"),
                    rx.link(
                        rx.button("Entrar", **BUTTON_PRIMARY_STYLE),
                        href="/login",
                    ),
                    spacing="3",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
                spacing="3",
            )
        ),
        display={"base": "block", "lg": "none"},
        position="sticky",
        top="0",
        z_index="50",
        padding_y="0.8rem",
        bg="rgba(3, 16, 10, 0.88)",
        backdrop_filter="blur(12px)",
        border_bottom=f"1px solid {COLORS['border']}",
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


def hero_bullet(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(tag="badge_check", size=15, color=COLORS["green_soft"]),
            width="28px",
            height="28px",
            border_radius="999px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.14)",
            border=f"1px solid {COLORS['border']}",
            flex_shrink="0",
        ),
        rx.text(text, color=COLORS["muted"], line_height="1.5"),
        spacing="3",
        align="center",
        width="100%",
    )


def dashboard_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Vista general ATS", color=COLORS["green_soft"], font_weight="800"),
                rx.badge("ADMIN", color_scheme="green", variant="soft", radius="full"),
                justify="between",
                width="100%",
                align="center",
            ),
            rx.grid(
                rx.box(
                    rx.heading("128", size="7", color=COLORS["green_soft"]),
                    rx.text("ATS gestionados", color=COLORS["soft"], size="2"),
                    padding="1rem",
                    border_radius="18px",
                    bg="rgba(255,255,255,0.06)",
                    border=f"1px solid {COLORS['border_soft']}",
                ),
                rx.box(
                    rx.heading("27%", size="7", color=COLORS["green_soft"]),
                    rx.text("Alto riesgo", color=COLORS["soft"], size="2"),
                    padding="1rem",
                    border_radius="18px",
                    bg="rgba(255,255,255,0.06)",
                    border=f"1px solid {COLORS['border_soft']}",
                ),
                columns={"base": "1", "sm": "2"},
                gap="1rem",
                width="100%",
            ),
            rx.box(
                rx.hstack(
                    rx.text("Trazabilidad documental", color=COLORS["muted"], size="2"),
                    rx.text("78%", color=COLORS["green_soft"], size="2", font_weight="800"),
                    justify="between",
                    width="100%",
                    margin_bottom="0.6rem",
                ),
                rx.box(
                    rx.box(
                        width="78%",
                        height="100%",
                        border_radius="999px",
                        bg=f"linear-gradient(90deg, {COLORS['green']}, {COLORS['green_neon']})",
                    ),
                    width="100%",
                    height="9px",
                    border_radius="999px",
                    bg="rgba(255,255,255,0.12)",
                ),
                width="100%",
                padding="1rem",
                border_radius="18px",
                bg="rgba(255,255,255,0.06)",
                border=f"1px solid {COLORS['border_soft']}",
            ),
            spacing="4",
            width="100%",
        ),
        padding={"base": "1.25rem", "md": "1.5rem"},
        **CARD_STYLE,
    )


def hero_section() -> rx.Component:
    return rx.box(
        _main_container(
            rx.grid(
                rx.box(
                    rx.badge(
                        "App web ATS SST",
                        color_scheme="green",
                        variant="soft",
                        radius="full",
                        padding_x="0.8rem",
                        padding_y="0.35rem",
                        margin_bottom="1.25rem",
                    ),
                    rx.heading(
                        "Gestiona el ATS con trazabilidad, PDF versionado y métricas claras.",
                        size={"base": "8", "md": "9"},
                        line_height="0.98",
                        letter_spacing="-0.06em",
                        max_width="780px",
                        margin_bottom="1.1rem",
                    ),
                    rx.text(
                        (
                            "Una plataforma web para centralizar el proceso SST: registro estructurado, "
                            "control documental, seguimiento por roles y consulta rápida de información operativa."
                        ),
                        color=COLORS["muted"],
                        line_height="1.75",
                        font_size={"base": "1rem", "md": "1.1rem"},
                        max_width="720px",
                        margin_bottom="1.6rem",
                    ),
                    rx.vstack(
                        hero_bullet("Registro ATS por fases con información clara y ordenada."),
                        hero_bullet("Relación entre tarea, peligro y control aplicado."),
                        hero_bullet("Documentos PDF y trazabilidad para seguimiento operativo."),
                        spacing="3",
                        width="100%",
                        align="stretch",
                        margin_bottom="2rem",
                    ),
                    rx.hstack(
                        _button_link("Entrar al sistema", "/login", primary=True),
                        _button_link("Ver módulos", "#modulos", primary=False),
                        spacing="3",
                        flex_wrap="wrap",
                    ),
                    width="100%",
                ),
                dashboard_preview(),
                columns={"base": "1", "xl": "2"},
                gap={"base": "3rem", "xl": "4rem"},
                align_items="center",
                width="100%",
            )
        ),
        id="top",
        padding_top={"base": "4rem", "md": "5.5rem"},
        padding_bottom={"base": "4.5rem", "md": "6rem"},
        scroll_margin_top="100px",
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
            margin_bottom="1.1rem",
        ),
        rx.heading(
            title,
            size="5",
            margin_bottom="0.7rem",
            letter_spacing="-0.02em",
        ),
        rx.text(
            text,
            color=COLORS["muted"],
            line_height="1.65",
            font_size="0.96rem",
        ),
        padding={"base": "1.35rem", "md": "1.65rem"},
        min_height={"base": "auto", "md": "240px"},
        transition="all 180ms ease",
        _hover={
            "transform": "translateY(-4px)",
            "bg": COLORS["card_alt"],
        },
        **CARD_STYLE,
    )

    if href:
        return rx.link(content, href=href, width="100%")

    return content


def modules_section() -> rx.Component:
    return rx.box(
        _main_container(
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
                    ),
                    rx.heading(
                        "Una experiencia simple para gestionar el ciclo ATS.",
                        size={"base": "7", "md": "8"},
                        line_height="1.05",
                        letter_spacing="-0.04em",
                        max_width="780px",
                        margin_bottom="1rem",
                    ),
                    rx.text(
                        (
                            "La landing queda más limpia y enfocada: primero explica el valor de la plataforma "
                            "y luego presenta los módulos que el usuario puede usar dentro del sistema."
                        ),
                        color=COLORS["muted"],
                        line_height="1.7",
                        max_width="760px",
                    ),
                    width="100%",
                ),
                rx.grid(
                    module_card(
                        "clipboard_check",
                        "Formato ATS",
                        "Captura la información del análisis de trabajo seguro por fases, con estructura clara para el equipo SISO.",
                        "/ats/formato",
                    ),
                    module_card(
                        "route",
                        "Paso, peligro y control",
                        "Permite relacionar cada actividad con sus peligros y controles aplicados para mejorar la trazabilidad.",
                    ),
                    module_card(
                        "file_text",
                        "Documentos PDF",
                        "Consulta, genera y descarga documentos ATS con historial y control documental.",
                        "/ats/documentos",
                    ),
                    module_card(
                        "layout_dashboard",
                        "Dashboard administrativo",
                        "Visualiza métricas para seguimiento gerencial, control por estado y análisis de riesgos.",
                        "/admin/dashboard",
                    ),
                    columns={"base": "1", "md": "2"},
                    gap={"base": "1rem", "md": "1.35rem", "xl": "1.5rem"},
                    width="100%",
                ),
                spacing="7",
                width="100%",
                align="stretch",
            )
        ),
        id="modulos",
        padding_top={"base": "4.5rem", "md": "6rem"},
        padding_bottom={"base": "5rem", "md": "7rem"},
        bg="linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0.006))",
        border_top=f"1px solid {COLORS['border_soft']}",
        scroll_margin_top="100px",
    )


def footer() -> rx.Component:
    return rx.box(
        _main_container(
            rx.hstack(
                rx.text(
                    f"(c) {datetime.now().year} App ATS SST",
                    color=COLORS["soft"],
                    font_weight="700",
                ),
                rx.text(
                    "Plataforma web para gestión operativa de Análisis de Trabajo Seguro.",
                    color=COLORS["soft"],
                ),
                justify="between",
                align="center",
                width="100%",
                flex_wrap="wrap",
                spacing="3",
            )
        ),
        padding_y="1.5rem",
        border_top=f"1px solid {COLORS['border_soft']}",
    )


def landing_page() -> rx.Component:
    return rx.box(
        mobile_nav(),
        rx.hstack(
            landing_sidebar(),
            rx.box(
                hero_section(),
                modules_section(),
                footer(),
                width="100%",
                min_width="0",
            ),
            align="start",
            spacing="0",
            width="100%",
        ),
        **PAGE_STYLE,
        custom_attrs={"style": "scroll-behavior: smooth;"},
    )