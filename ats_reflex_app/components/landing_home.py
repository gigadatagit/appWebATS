from __future__ import annotations

from datetime import datetime

import reflex as rx

from .brand import app_brand

COLORS = {
    "bg_deep": "#020d08",
    "bg_base": "#04130c",
    "bg_soft": "#092117",
    "bg_panel": "#0d2a1d",
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
    "lime": "#c6f86d",
}

SECTION_STYLE = {
    "width": "100%",
    "padding_y": {"base": "4.5rem", "md": "6.25rem"},
}

CARD_STYLE = {
    "bg": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "22px",
    "box_shadow": "0 22px 64px rgba(0, 0, 0, 0.3)",
    "backdrop_filter": "blur(9px)",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-4px)",
        "bg": COLORS["card_alt"],
        "border_color": "rgba(167, 243, 208, 0.38)",
    },
}

BUTTON_PRIMARY_STYLE = {
    "bg": f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})",
    "color": "#032015",
    "border_radius": "999px",
    "padding_x": "1.35rem",
    "padding_y": "0.95rem",
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
    "padding_x": "1.35rem",
    "padding_y": "0.95rem",
    "font_weight": "700",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-2px)",
        "bg": "rgba(255, 255, 255, 0.14)",
        "border_color": "rgba(167, 243, 208, 0.42)",
    },
    "_active": {"transform": "translateY(1px)"},
}

PAGE_BG_STYLE = {
    "min_height": "100vh",
    "color": COLORS["text"],
    "bg": (
        "radial-gradient(circle at 7% 4%, rgba(22, 199, 132, 0.18), transparent 38%), "
        "radial-gradient(circle at 88% 6%, rgba(198, 248, 109, 0.1), transparent 34%), "
        "radial-gradient(circle at 50% 45%, rgba(22, 199, 132, 0.07), transparent 45%), "
        "linear-gradient(155deg, #020d08 0%, #07190f 45%, #0b2619 100%)"
    ),
}

SECTION_TONES = {
    "base": "transparent",
    "soft": "linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0.01))",
    "panel": (
        "linear-gradient(180deg, rgba(22, 199, 132, 0.08), rgba(255,255,255,0.014)), "
        "linear-gradient(145deg, rgba(3, 16, 10, 0.76), rgba(7, 26, 18, 0.68))"
    ),
}


def _container(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children,
        width="100%",
        max_width="1160px",
        margin_x="auto",
        padding_x={"base": "1rem", "sm": "1.25rem", "lg": "1.5rem"},
    )


def section_shell(*children: rx.Component, section_id: str, tone: str = "base") -> rx.Component:
    return rx.box(
        _container(*children),
        id=section_id,
        bg=SECTION_TONES[tone],
        border_top=f"1px solid {COLORS['border_soft']}" if tone != "base" else "none",
        border_bottom=f"1px solid {COLORS['border_soft']}" if tone == "panel" else "none",
        **SECTION_STYLE,
    )


def section_heading(kicker: str, title: str, text: str, centered: bool = False) -> rx.Component:
    return rx.box(
        rx.text(
            kicker,
            color=COLORS["green_soft"],
            text_transform="uppercase",
            letter_spacing="0.16em",
            font_weight="800",
            font_size="0.75rem",
            margin_bottom="0.75rem",
        ),
        rx.heading(
            title,
            size={"base": "7", "md": "9"},
            line_height="1.04",
            letter_spacing="-0.04em",
            margin_bottom="0.9rem",
            max_width="860px",
            margin_x="auto" if centered else "0",
        ),
        rx.text(
            text,
            color=COLORS["muted"],
            line_height="1.68",
            font_size={"base": "0.98rem", "md": "1.05rem"},
            max_width="860px",
            margin_x="auto" if centered else "0",
        ),
        width="100%",
        margin_bottom="2rem",
        text_align="center" if centered else "left",
    )


def route_pill(text: str, margin_top: str = "0") -> rx.Component:
    return rx.badge(
        text,
        variant="soft",
        color_scheme="green",
        radius="full",
        padding_x="0.65rem",
        padding_y="0.2rem",
        margin_top=margin_top,
        width="fit-content",
    )


def feature_card(icon_tag: str, title: str, copy: str, route_hint: str = "") -> rx.Component:
    return rx.box(
        rx.box(
            rx.icon(tag=icon_tag, size=20, color=COLORS["green_soft"]),
            width="48px",
            height="48px",
            border_radius="16px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.15)",
            border=f"1px solid {COLORS['border']}",
            margin_bottom="1rem",
        ),
        rx.heading(title, size="5", margin_bottom="0.55rem", letter_spacing="-0.02em"),
        rx.text(copy, color=COLORS["muted"], line_height="1.58", font_size="0.95rem"),
        rx.cond(route_hint != "", route_pill(route_hint, margin_top="0.9rem")),
        padding="1.4rem",
        min_height="220px",
        width="100%",
        **CARD_STYLE,
    )


def metric_card(value: str, label: str) -> rx.Component:
    return rx.box(
        rx.heading(
            value,
            size="8",
            color=COLORS["green_soft"],
            letter_spacing="-0.05em",
            margin_bottom="0.35rem",
        ),
        rx.text(label, color=COLORS["muted"], line_height="1.45", size="2"),
        padding="1.2rem",
        border_radius="22px",
        bg="rgba(255,255,255,0.075)",
        border=f"1px solid {COLORS['border']}",
        height="100%",
    )


def role_card(role_name: str, summary: str, points: list[str]) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag="shield", size=20, color=COLORS["green_soft"]),
                width="42px",
                height="42px",
                border_radius="14px",
                display="grid",
                place_items="center",
                bg="rgba(22, 199, 132, 0.15)",
                border=f"1px solid {COLORS['border']}",
            ),
            rx.heading(role_name, size="6", color=COLORS["green_soft"]),
            spacing="3",
            align="center",
            margin_bottom="0.7rem",
        ),
        rx.text(summary, color=COLORS["muted"], line_height="1.58", margin_bottom="1rem"),
        rx.vstack(
            *[
                rx.hstack(
                    rx.icon(tag="badge_check", size=16, color=COLORS["green_soft"]),
                    rx.text(point, color=COLORS["muted"], size="2"),
                    spacing="2",
                    align="start",
                    width="100%",
                )
                for point in points
            ],
            spacing="2",
            align="stretch",
            width="100%",
        ),
        padding={"base": "1.2rem", "md": "1.5rem"},
        border_radius="28px",
        bg="rgba(255,255,255,0.07)",
        border=f"1px solid {COLORS['border']}",
        height="100%",
    )


def _button_link(label: str, href: str, primary: bool = True, width: str = "auto") -> rx.Component:
    return rx.link(
        rx.button(
            rx.hstack(
                rx.text(label),
                rx.icon(tag="arrow_right", size=15),
                spacing="2",
                align="center",
            ),
            width=width,
            **(BUTTON_PRIMARY_STYLE if primary else BUTTON_SECONDARY_STYLE),
        ),
        href=href,
        width=width,
    )


def _hero_bullet(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(tag="badge_check", size=15, color=COLORS["green_soft"]),
            width="26px",
            height="26px",
            border_radius="999px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.16)",
            border=f"1px solid {COLORS['border']}",
            flex_shrink="0",
        ),
        rx.text(text, color=COLORS["muted"], font_size="0.95rem", line_height="1.45"),
        spacing="2",
        align="center",
        width="100%",
    )


def _mini_stat(title: str, value: str) -> rx.Component:
    return rx.box(
        rx.text(title, color=COLORS["soft"], size="1"),
        rx.heading(value, size="5", color=COLORS["green_soft"], margin_top="0.2rem"),
        padding="0.85rem",
        border_radius="16px",
        bg="rgba(255,255,255,0.055)",
        border=f"1px solid {COLORS['border']}",
    )


def _dashboard_mockup() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.32)"),
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.32)"),
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.32)"),
                    spacing="2",
                    align="center",
                ),
                rx.badge("Vista ADMIN en tiempo real", color_scheme="green", variant="soft", radius="full"),
                width="100%",
                justify="between",
                align="center",
                padding="1rem 1rem 0.8rem 1rem",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            rx.vstack(
                rx.grid(
                    _mini_stat("ATS activos", "128"),
                    _mini_stat("Alto riesgo", "27%"),
                    _mini_stat("PDF versionados", "362"),
                    columns={"base": "1", "sm": "3"},
                    spacing="2",
                    width="100%",
                ),
                rx.box(
                    rx.hstack(
                        rx.text("Seguimiento por estado", size="2", color=COLORS["muted"]),
                        rx.text("Cumplimiento 78%", size="2", color=COLORS["green_soft"], font_weight="700"),
                        justify="between",
                        align="center",
                        width="100%",
                        margin_bottom="0.45rem",
                    ),
                    rx.box(
                        rx.box(
                            width="78%",
                            height="100%",
                            border_radius="999px",
                            bg=f"linear-gradient(90deg, {COLORS['green']}, {COLORS['green_neon']})",
                        ),
                        width="100%",
                        height="8px",
                        border_radius="999px",
                        bg="rgba(255,255,255,0.12)",
                    ),
                    padding="0.9rem",
                    border_radius="16px",
                    bg="rgba(255,255,255,0.055)",
                    border=f"1px solid {COLORS['border']}",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Formato ATS", color=COLORS["muted"], size="2"),
                        rx.text("31 tareas", color=COLORS["green_soft"], size="2", font_weight="700"),
                        width="100%",
                        justify="between",
                    ),
                    rx.hstack(
                        rx.text("Documentos PDF", color=COLORS["muted"], size="2"),
                        rx.text("11 pendientes", color=COLORS["green_soft"], size="2", font_weight="700"),
                        width="100%",
                        justify="between",
                    ),
                    rx.hstack(
                        rx.text("Dashboard", color=COLORS["muted"], size="2"),
                        rx.text("Actualizado hoy", color=COLORS["green_soft"], size="2", font_weight="700"),
                        width="100%",
                        justify="between",
                    ),
                    spacing="2",
                    padding="0.9rem",
                    border_radius="16px",
                    bg="rgba(255,255,255,0.055)",
                    border=f"1px solid {COLORS['border']}",
                    width="100%",
                ),
                spacing="2",
                width="100%",
                padding="1rem",
            ),
            border_radius="26px",
            overflow="hidden",
            bg="rgba(3, 16, 10, 0.84)",
            border=f"1px solid {COLORS['border']}",
            width="100%",
        ),
        padding="1rem",
        border_radius="34px",
        bg=(
            "radial-gradient(circle at 20% 0%, rgba(57, 255, 156, 0.2), transparent 48%), "
            "linear-gradient(145deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02))"
        ),
        border=f"1px solid {COLORS['border']}",
        box_shadow="0 32px 95px rgba(10, 84, 53, 0.34), 0 24px 70px rgba(0,0,0,0.32)",
    )


def landing_navbar() -> rx.Component:
    desktop_links = rx.hstack(
        rx.link("Reto", href="#reto", color=COLORS["muted"], _hover={"color": COLORS["green_soft"]}),
        rx.link("Plataforma", href="#plataforma", color=COLORS["muted"], _hover={"color": COLORS["green_soft"]}),
        rx.link("Modulos", href="#modulos", color=COLORS["muted"], _hover={"color": COLORS["green_soft"]}),
        rx.link("Metricas", href="#metricas", color=COLORS["muted"], _hover={"color": COLORS["green_soft"]}),
        rx.link("Roles", href="#roles", color=COLORS["muted"], _hover={"color": COLORS["green_soft"]}),
        spacing="4",
        display={"base": "none", "md": "flex"},
        align="center",
        font_size="0.92rem",
    )

    mobile_links = rx.hstack(
        rx.link("Reto", href="#reto"),
        rx.link("Plataforma", href="#plataforma"),
        rx.link("Modulos", href="#modulos"),
        rx.link("Metricas", href="#metricas"),
        rx.link("Roles", href="#roles"),
        display={"base": "flex", "md": "none"},
        width="100%",
        overflow_x="auto",
        white_space="nowrap",
        spacing="3",
        padding_bottom="0.35rem",
        color=COLORS["muted"],
        font_size="0.88rem",
    )

    return rx.box(
        _container(
            rx.vstack(
                rx.hstack(
                    rx.link(
                        rx.hstack(
                            app_brand(show_text=False, logo_size="44px"),
                            rx.vstack(
                                rx.text("App ATS SST", font_weight="800", letter_spacing="-0.03em", line_height="1.0"),
                                rx.text("Plataforma web operativa", color=COLORS["soft"], size="1"),
                                spacing="0",
                                align="start",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        href="#top",
                    ),
                    desktop_links,
                    rx.hstack(
                        rx.link(
                            rx.button("Ver modulos", **BUTTON_SECONDARY_STYLE),
                            href="#modulos",
                            display={"base": "none", "sm": "inline"},
                        ),
                        rx.link(rx.button("Entrar al sistema", **BUTTON_PRIMARY_STYLE), href="/login"),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    justify="between",
                    spacing="4",
                ),
                mobile_links,
                spacing="2",
                width="100%",
                align="stretch",
            )
        ),
        position="sticky",
        top="0",
        z_index="40",
        bg="rgba(3, 16, 10, 0.82)",
        backdrop_filter="blur(12px)",
        border_bottom=f"1px solid {COLORS['border']}",
        padding_y="0.85rem",
    )


def hero_section() -> rx.Component:
    highlights = rx.grid(
        _hero_bullet("Digitaliza el ATS por fases con trazabilidad completa."),
        _hero_bullet("Relaciona paso, peligro y control en un flujo unico."),
        _hero_bullet("Genera PDF versionados y evidencia operativa."),
        _hero_bullet("Mide gestion SST por rol, estado y periodo."),
        columns={"base": "1", "sm": "2"},
        spacing="2",
        width="100%",
        margin_top="1.2rem",
    )

    trust_row = rx.grid(
        _mini_stat("Control por roles", "ADMIN / SISO"),
        _mini_stat("Flujo ATS", "7 fases"),
        _mini_stat("Documentacion", "PDF + historial"),
        columns={"base": "1", "md": "3"},
        spacing="3",
        width="100%",
        margin_top="1.6rem",
    )

    return rx.box(
        _container(
            rx.grid(
                rx.box(
                    rx.hstack(
                        rx.box(width="9px", height="9px", border_radius="999px", bg=COLORS["green_neon"]),
                        rx.text("App web ATS SST", font_weight="700", font_size="0.88rem"),
                        spacing="2",
                        align="center",
                        color=COLORS["green_soft"],
                        bg="rgba(22, 199, 132, 0.13)",
                        border=f"1px solid {COLORS['border']}",
                        border_radius="999px",
                        padding="0.5rem 0.85rem",
                        width="fit-content",
                        margin_bottom="1.25rem",
                    ),
                    rx.heading(
                        "Controla el ATS con trazabilidad real, PDF versionado y metricas utiles.",
                        size={"base": "8", "md": "9"},
                        line_height="0.96",
                        letter_spacing="-0.06em",
                        margin_bottom="0.95rem",
                        max_width="780px",
                    ),
                    rx.text(
                        (
                            "Centraliza la operacion SST en una sola plataforma: registro estructurado, "
                            "documentacion auditable, seguimiento por roles y dashboard para decisiones claras."
                        ),
                        color=COLORS["muted"],
                        line_height="1.68",
                        font_size={"base": "1rem", "md": "1.1rem"},
                        max_width="760px",
                    ),
                    highlights,
                    rx.hstack(
                        _button_link("Entrar al sistema", "/login", primary=True),
                        _button_link("Ver funcionalidades", "#modulos", primary=False),
                        spacing="3",
                        width="100%",
                        flex_wrap="wrap",
                        margin_top="1.6rem",
                    ),
                    trust_row,
                    width="100%",
                ),
                _dashboard_mockup(),
                columns={"base": "1", "lg": "2"},
                spacing={"base": "6", "lg": "8"},
                align_items="center",
            )
        ),
        id="top",
        padding_y={"base": "3.2rem", "md": "4.8rem"},
        width="100%",
    )


def challenge_section() -> rx.Component:
    return section_shell(
        section_heading(
            "El reto actual",
            "Sin estructura digital, el ATS se vuelve pesado y dificil de controlar.",
            (
                "La informacion existe, pero suele quedar dispersa en documentos y seguimientos manuales. "
                "Eso afecta lectura rapida, control documental y visibilidad gerencial."
            ),
        ),
        rx.grid(
            feature_card(
                "folders",
                "Registros dispersos",
                "Datos, firmas y evidencias quedan en varios frentes y cuesta consolidarlos.",
            ),
            feature_card(
                "triangle_alert",
                "Riesgo poco visible",
                "Sin una matriz clara paso-peligro-control, el analisis pierde foco operativo.",
            ),
            feature_card(
                "eye",
                "Seguimiento limitado",
                "Sin metricas, la direccion no ve avance real por equipo, periodo o riesgo.",
            ),
            columns={"base": "1", "md": "2", "xl": "3"},
            spacing="4",
            width="100%",
        ),
        section_id="reto",
        tone="soft",
    )


def platform_section() -> rx.Component:
    def flow_step(step: str, title: str, desc: str, route: str) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.box(
                    step,
                    width="42px",
                    height="42px",
                    border_radius="14px",
                    display="grid",
                    place_items="center",
                    font_weight="800",
                    color="#032015",
                    bg=f"linear-gradient(135deg, {COLORS['green']}, {COLORS['green_neon']})",
                    flex_shrink="0",
                ),
                rx.box(
                    rx.heading(title, size="4", margin_bottom="0.25rem"),
                    rx.text(desc, size="2", color=COLORS["soft"], line_height="1.45"),
                    width="100%",
                ),
                route_pill(route),
                width="100%",
                align="center",
                spacing="3",
                flex_wrap={"base": "wrap", "sm": "nowrap"},
            ),
            padding="1rem",
            border_radius="20px",
            bg="rgba(255,255,255,0.06)",
            border=f"1px solid {COLORS['border']}",
            width="100%",
        )

    return section_shell(
        rx.grid(
            rx.box(
                section_heading(
                    "Que resuelve la plataforma",
                    "Un flujo web claro para crear, cerrar, documentar y analizar ATS.",
                    (
                        "El equipo SISO registra y mantiene trazabilidad del proceso. "
                        "El rol ADMIN monitorea avance, riesgos y productividad desde el dashboard."
                    ),
                ),
                rx.vstack(
                    _hero_bullet("Autenticacion y control de acceso por roles activos."),
                    _hero_bullet("Formulario ATS por fases con datos y firmas."),
                    _hero_bullet("Catalogos para estandarizar tipos, peligros y controles."),
                    _hero_bullet("PDF con versionado, trazabilidad y consulta centralizada."),
                    spacing="2",
                    width="100%",
                ),
                padding="1.5rem",
                border_radius="24px",
                bg="rgba(3, 16, 10, 0.55)",
                border=f"1px solid {COLORS['border']}",
                height="100%",
            ),
            rx.vstack(
                flow_step("1", "Login y rol", "Ingreso por perfil ADMIN o SISO.", "/login"),
                flow_step("2", "Formato ATS", "Registro operativo por fases y evidencias.", "/ats/formato"),
                flow_step("3", "Documento PDF", "Generacion y versionado del documento ATS.", "/ats/documentos"),
                flow_step("4", "Dashboard", "Analitica para control SST y decisiones.", "/admin/dashboard"),
                spacing="3",
                width="100%",
            ),
            columns={"base": "1", "xl": "2"},
            spacing="4",
            align_items="stretch",
            width="100%",
            padding={"base": "1rem", "md": "1.5rem"},
            border_radius="32px",
            bg="linear-gradient(145deg, rgba(22, 199, 132, 0.12), rgba(255,255,255,0.045))",
            border=f"1px solid {COLORS['border']}",
            box_shadow="0 24px 72px rgba(0, 0, 0, 0.34)",
        ),
        section_id="plataforma",
        tone="panel",
    )


def modules_section() -> rx.Component:
    return section_shell(
        section_heading(
            "Modulos principales",
            "Todo el ciclo ATS dentro de una experiencia unica y consistente.",
            "Cada modulo responde a un punto critico del proceso operativo y documental.",
        ),
        rx.grid(
            feature_card(
                "clipboard_check",
                "Formato ATS por fases",
                "Captura datos generales, tareas, peligros, controles, observaciones y cierre.",
                "/ats/formato",
            ),
            feature_card(
                "route",
                "Matriz paso-peligro-control",
                "Relacion directa entre cada paso, sus peligros y medidas de control aplicadas.",
                "Trazabilidad real",
            ),
            feature_card(
                "users",
                "Trabajadores y firmas",
                "Integracion con catalogo de personal, snapshot historico y firma operativa.",
                "Evidencia operativa",
            ),
            feature_card(
                "file_text",
                "Documentos PDF",
                "Busqueda, generacion, descarga y control de historial de versiones.",
                "/ats/documentos",
            ),
            feature_card(
                "layout_dashboard",
                "Dashboard administrativo",
                "KPIs y analitica por estado, tipo de riesgo, usuario y periodos.",
                "/admin/dashboard",
            ),
            feature_card(
                "shield",
                "Control por ownership",
                "ADMIN ve toda la operacion; SISO trabaja sobre sus ATS autorizados.",
                "ADMIN / SISO",
            ),
            columns={"base": "1", "md": "2", "xl": "3"},
            spacing="4",
            width="100%",
        ),
        section_id="modulos",
        tone="base",
    )


def metrics_section() -> rx.Component:
    return section_shell(
        section_heading(
            "Metricas y analitica",
            "Del registro operativo a decisiones con datos medibles.",
            (
                "El dashboard transforma informacion ATS en indicadores accionables, "
                "con lectura rapida para seguimiento diario y control gerencial."
            ),
        ),
        rx.grid(
            metric_card("7", "Fases estructuradas para gestionar el ATS."),
            metric_card("100%", "Trazabilidad entre tarea, peligro y control."),
            metric_card("2", "Roles para separar operacion y administracion."),
            metric_card("1", "Fuente unificada de ATS, PDF y firmas."),
            columns={"base": "1", "sm": "2", "xl": "4"},
            spacing="4",
            width="100%",
        ),
        rx.grid(
            feature_card(
                "pie_chart",
                "Alto riesgo vs no alto riesgo",
                "Identifica proporcion y cambios por periodo de analisis.",
            ),
            feature_card(
                "bar_chart_3",
                "Top peligros y controles",
                "Prioriza acciones segun frecuencia y concentracion de riesgo.",
            ),
            feature_card(
                "line_chart",
                "Tendencia mensual",
                "Monitorea evolucion operativa para intervencion temprana.",
            ),
            columns={"base": "1", "md": "3"},
            spacing="4",
            width="100%",
            margin_top="1rem",
        ),
        section_id="metricas",
        tone="soft",
    )


def roles_section() -> rx.Component:
    return section_shell(
        section_heading(
            "Roles SISO y ADMIN",
            "Control operativo y visibilidad administrativa, cada uno en su lugar.",
            "La experiencia de uso se adapta al perfil para mantener orden, seguridad y trazabilidad.",
        ),
        rx.grid(
            role_card(
                "Rol SISO",
                "Gestiona la ejecucion del ATS de punta a punta.",
                [
                    "Crea y actualiza ATS por fases.",
                    "Registra peligros, controles, trabajadores y firmas.",
                    "Consulta y genera documentos PDF de su gestion.",
                ],
            ),
            role_card(
                "Rol ADMIN",
                "Supervisa la operacion y direcciona decisiones SST.",
                [
                    "Visualiza toda la operacion en el dashboard.",
                    "Analiza datos por estado, riesgo, usuario y periodo.",
                    "Mantiene control global sobre cumplimiento operativo.",
                ],
            ),
            columns={"base": "1", "md": "2"},
            spacing="4",
            width="100%",
        ),
        section_id="roles",
        tone="panel",
    )


def cta_section() -> rx.Component:
    return rx.box(
        _container(
            rx.box(
                section_heading(
                    "CTA final",
                    "Empieza a gestionar ATS con trazabilidad, versionado y control operativo.",
                    (
                        "Ingresa al sistema para centralizar tu proceso SST: registro por fases, "
                        "documentos PDF versionados y metricas reales para seguimiento continuo."
                    ),
                    centered=True,
                ),
                rx.hstack(
                    _button_link("Entrar al sistema", "/login", primary=True),
                    _button_link("Gestionar ATS", "/ats/formato", primary=False),
                    _button_link("Ver documentos", "/ats/documentos", primary=False),
                    spacing="3",
                    flex_wrap="wrap",
                    justify="center",
                    width="100%",
                ),
                rx.hstack(
                    route_pill("Trazabilidad"),
                    route_pill("PDF versionado"),
                    route_pill("Metricas reales"),
                    route_pill("Control por roles"),
                    spacing="2",
                    flex_wrap="wrap",
                    justify="center",
                    margin_top="1.15rem",
                    width="100%",
                ),
                width="100%",
                padding={"base": "2rem 1rem", "md": "4rem 1.8rem"},
                border_radius="40px",
                bg=(
                    "radial-gradient(circle at 50% 0%, rgba(57, 255, 156, 0.25), transparent 46%), "
                    "linear-gradient(145deg, rgba(22, 199, 132, 0.17), rgba(255,255,255,0.05))"
                ),
                border=f"1px solid {COLORS['border']}",
                box_shadow="0 30px 94px rgba(10, 84, 53, 0.34), 0 24px 70px rgba(0,0,0,0.3)",
            )
        ),
        id="login",
        padding_y={"base": "4.2rem", "md": "5.4rem"},
        width="100%",
    )


def landing_footer() -> rx.Component:
    return rx.box(
        _container(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        f"(c) {datetime.now().year} App ATS SST",
                        color=COLORS["soft"],
                        font_size="0.9rem",
                        font_weight="700",
                    ),
                    rx.text(
                        "Plataforma web para gestion operativa de Analisis de Trabajo Seguro.",
                        color=COLORS["soft"],
                        font_size="0.9rem",
                    ),
                    width="100%",
                    justify="between",
                    align="center",
                    spacing="3",
                    flex_wrap="wrap",
                ),
                rx.hstack(
                    route_pill("ATS"),
                    route_pill("Documentos"),
                    route_pill("Firmas"),
                    route_pill("Dashboard"),
                    spacing="2",
                    flex_wrap="wrap",
                    width="100%",
                    justify="start",
                ),
                spacing="3",
                width="100%",
                align="stretch",
            )
        ),
        border_top=f"1px solid {COLORS['border']}",
        padding_y="1.5rem",
        width="100%",
        bg="rgba(0, 0, 0, 0.15)",
    )


def landing_page() -> rx.Component:
    return rx.box(
        landing_navbar(),
        hero_section(),
        challenge_section(),
        platform_section(),
        modules_section(),
        metrics_section(),
        roles_section(),
        cta_section(),
        landing_footer(),
        **PAGE_BG_STYLE,
        custom_attrs={"style": "scroll-behavior: smooth;"},
    )
