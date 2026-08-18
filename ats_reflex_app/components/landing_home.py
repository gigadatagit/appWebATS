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


def bp(
    initial: str,
    sm: str | None = None,
    md: str | None = None,
    lg: str | None = None,
    xl: str | None = None,
):
    values = {"initial": initial}

    if sm is not None:
        values["sm"] = sm
    if md is not None:
        values["md"] = md
    if lg is not None:
        values["lg"] = lg
    if xl is not None:
        values["xl"] = xl

    return rx.breakpoints(**values)


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
        max_width="1180px",
        margin_x="auto",
        padding_x=bp("1.15rem", sm="1.5rem", lg="2rem"),
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
        text_decoration="none",
        _hover={"text_decoration": "none"},
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
            text_decoration="none",
            _hover={"text_decoration": "none"},
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
                                "Plataforma SST",
                                font_weight="900",
                                color=COLORS["green_soft"],
                                letter_spacing="0",
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
                            "Gestiona, analiza y documenta formatos SST en una sola plataforma.",
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
                width=bp("86vw", sm="360px"),
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
                                "Plataforma SST",
                                font_weight="900",
                                color=COLORS["green_soft"],
                                letter_spacing="0",
                                line_height="1",
                            ),
                            rx.text(
                                "Plataforma web operativa",
                                color=COLORS["soft"],
                                size="1",
                                display=bp("none", sm="block"),
                            ),
                            spacing="0",
                            align="start",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    href="#top",
                    text_decoration="none",
                    _hover={"text_decoration": "none"},
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
            width="52px",
            height="52px",
            border_radius="18px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.14)",
            border=f"1px solid {COLORS['border']}",
            margin_bottom="1.35rem",
        ),
        rx.heading(
            title,
            size="5",
            color=COLORS["text"],
            margin_bottom="0.85rem",
            letter_spacing="0",
            line_height="1.2",
        ),
        rx.text(
            text,
            color=COLORS["muted"],
            line_height="1.7",
            font_size="0.97rem",
        ),
        padding=bp("1.45rem", md="1.85rem"),
        min_height=bp("210px", md="240px"),
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
        return rx.link(
            content,
            href=href,
            width="100%",
            height="100%",
            color="inherit",
            text_decoration="none",
            _hover={"text_decoration": "none"},
        )

    return content


def intro_section() -> rx.Component:
    return rx.box(
        _container(
            rx.vstack(
                rx.badge(
                    "App web SST",
                    color_scheme="green",
                    variant="soft",
                    radius="full",
                    padding_x="0.85rem",
                    padding_y="0.35rem",
                ),
                rx.heading(
                    "Gestion integral de formatos SST.",
                    size=bp("8", md="9"),
                    line_height="1.03",
                    letter_spacing="0",
                    text_align="center",
                    max_width="820px",
                ),
                rx.text(
                    (
                        "Una plataforma web para centralizar ATS, permisos, listas de chequeo, "
                        "analitica operativa, trazabilidad y generacion documental para la gestion SST."
                    ),
                    color=COLORS["muted"],
                    line_height="1.8",
                    font_size=bp("1rem", md="1.12rem"),
                    text_align="center",
                    max_width="760px",
                ),
                rx.hstack(
                    _button_link("Ver módulos", "#modulos", primary=False),
                    _button_link("Entrar al sistema", "/login", primary=True),
                    spacing="3",
                    justify="center",
                    flex_wrap="wrap",
                    margin_top="1rem",
                ),
                width="100%",
                align="center",
                max_width="940px",
                margin_x="auto",
                spacing="5",
            )
        ),
        id="top",
        padding_top=bp("4.75rem", md="6.5rem"),
        padding_bottom=bp("6rem", md="8rem"),
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
                        margin_bottom="1rem",
                        text_align="center",
                    ),
                    rx.heading(
                        "Formatos SST, analitica y documentos en una experiencia consistente.",
                        size=bp("7", md="8"),
                        line_height="1.08",
                        letter_spacing="0",
                        text_align="center",
                        max_width="840px",
                        margin_x="auto",
                        margin_bottom="1.1rem",
                    ),
                    rx.text(
                        "Cada modulo abre una vista operativa para gestionar trazabilidad, tableros y evidencia documental.",
                        color=COLORS["muted"],
                        line_height="1.7",
                        text_align="center",
                        max_width="720px",
                        margin_x="auto",
                    ),
                    width="100%",
                    margin_bottom=bp("1.75rem", md="2.5rem"),
                ),
                rx.grid(
                    module_card(
                        "clipboard_check",
                        "ATS",
                        "Captura datos generales, tareas, peligros, controles, observaciones y cierre.",
                        "/ats/formato",
                    ),
                    module_card(
                        "tractor",
                        "Preoperacionales",
                        "Analiza inspecciones de maquinaria, operadores, certificacion y respuestas criticas.",
                        "/sst/dashboard/preoperacionales",
                    ),
                    module_card(
                        "mountain",
                        "Trabajo en alturas",
                        "Consulta permisos, medios de acceso, vigencias, cierres, firmas y alertas de checklist.",
                        "/sst/dashboard/alturas",
                    ),
                    module_card(
                        "waves_ladder",
                        "Medios de acceso",
                        "Revisa listas de chequeo asociadas a permisos de alturas y su estado documental.",
                        "/sst/dashboard/medios-acceso",
                    ),
                    module_card(
                        "zap",
                        "Energias peligrosas",
                        "Controla permisos, tipos de tension, reglas de oro, cierres y evidencias.",
                        "/sst/dashboard/energias-peligrosas",
                    ),
                    module_card(
                        "flame",
                        "Trabajo caliente",
                        "Visualiza permisos, soldadura, vigencias, suspensiones, documentos y alertas.",
                        "/sst/dashboard/trabajo-caliente",
                    ),
                    module_card(
                        "layout_dashboard",
                        "Dashboard SST",
                        "Consolida registros, pendientes, documentos, origen movil y tendencias por formato.",
                        "/sst/dashboard",
                    ),
                    module_card(
                        "file_text",
                        "Documentos SST",
                        "Centraliza el historial de PDF por formato y mantiene la generacion ATS actual.",
                        "/sst/documentos",
                    ),
                    width="100%",
                    display="grid",
                    grid_template_columns=bp(
                        "1fr",
                        md="repeat(2, minmax(0, 1fr))",
                        xl="repeat(3, minmax(0, 1fr))",
                    ),
                    gap=bp("1.25rem", md="1.75rem", xl="2rem"),
                    align_items="stretch",
                ),
                width="100%",
                align="stretch",
                spacing="0",
            )
        ),
        id="modulos",
        padding_top=bp("5.75rem", md="7rem"),
        padding_bottom=bp("6.5rem", md="8rem"),
        bg="linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0.006))",
        border_top=f"1px solid {COLORS['border_soft']}",
        scroll_margin_top="100px",
    )


def footer() -> rx.Component:
    return rx.box(
        _container(
            rx.hstack(
                rx.text(
                    f"© {datetime.now().year} Plataforma SST",
                    color=COLORS["soft"],
                    font_weight="700",
                ),
                rx.text(
                    "Plataforma web para gestion, analitica y documentacion de formatos SST.",
                    color=COLORS["soft"],
                    text_align=bp("left", md="right"),
                    max_width="620px",
                ),
                justify="between",
                align="center",
                width="100%",
                flex_wrap="wrap",
                spacing="3",
            )
        ),
        padding_y=bp("2.5rem", md="3rem"),
        border_top=f"1px solid {COLORS['border_soft']}",
    )


def landing_page() -> rx.Component:
    return rx.box(
        top_bar(),
        intro_section(),
        modules_section(),
        footer(),
        **PAGE_STYLE,
        scroll_behavior="smooth",
    )
