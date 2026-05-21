from __future__ import annotations

from datetime import datetime

import reflex as rx

from .brand import app_brand

COLORS = {
    "bg_base": "#04110b",
    "bg_soft": "#071a12",
    "bg_panel": "#0b2117",
    "card": "rgba(255, 255, 255, 0.06)",
    "card_strong": "rgba(255, 255, 255, 0.10)",
    "border": "rgba(167, 243, 208, 0.22)",
    "text": "#f4fff8",
    "muted": "#bed9ca",
    "soft": "#81a895",
    "green": "#16c784",
    "green_dark": "#087f4f",
    "green_soft": "#a7f3d0",
    "green_neon": "#39ff9c",
    "lime": "#c6f86d",
}

SECTION_STYLE = {
    "width": "100%",
    "padding_y": {"base": "3.8rem", "md": "5.6rem"},
}

CARD_STYLE = {
    "bg": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "22px",
    "box_shadow": "0 20px 55px rgba(0, 0, 0, 0.28)",
    "backdrop_filter": "blur(8px)",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-5px)",
        "bg": COLORS["card_strong"],
        "border_color": "rgba(167, 243, 208, 0.36)",
    },
}

BUTTON_PRIMARY_STYLE = {
    "bg": f"linear-gradient(135deg, {COLORS['green_neon']}, {COLORS['green']})",
    "color": "#032015",
    "border_radius": "999px",
    "padding_x": "1.2rem",
    "padding_y": "0.9rem",
    "font_weight": "700",
    "box_shadow": "0 18px 48px rgba(22, 199, 132, 0.35)",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": "0 24px 62px rgba(22, 199, 132, 0.42)",
    },
    "_active": {"transform": "translateY(1px)"},
}

BUTTON_SECONDARY_STYLE = {
    "bg": "rgba(255, 255, 255, 0.08)",
    "color": COLORS["text"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "999px",
    "padding_x": "1.2rem",
    "padding_y": "0.9rem",
    "font_weight": "700",
    "transition": "all 180ms ease",
    "_hover": {
        "transform": "translateY(-2px)",
        "bg": "rgba(255, 255, 255, 0.14)",
        "border_color": "rgba(167, 243, 208, 0.40)",
    },
    "_active": {"transform": "translateY(1px)"},
}

PAGE_BG_STYLE = {
    "min_height": "100vh",
    "color": COLORS["text"],
    "bg": (
        "radial-gradient(circle at top left, rgba(22, 199, 132, 0.22), transparent 38%), "
        "radial-gradient(circle at 86% 8%, rgba(198, 248, 109, 0.12), transparent 34%), "
        "linear-gradient(135deg, #03100a 0%, #06170f 42%, #0b2117 100%)"
    ),
}


def _container(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children,
        width="100%",
        max_width="1180px",
        margin_x="auto",
        padding_x={"base": "1rem", "sm": "1.25rem", "lg": "1.5rem"},
    )


def _section_heading(kicker: str, title: str, text: str) -> rx.Component:
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
        ),
        rx.text(
            text,
            color=COLORS["muted"],
            line_height="1.75",
            font_size={"base": "0.98rem", "md": "1.05rem"},
            max_width="850px",
        ),
        width="100%",
        margin_bottom="2rem",
    )


def _route_pill(text: str) -> rx.Component:
    return rx.badge(
        text,
        variant="soft",
        color_scheme="green",
        radius="full",
        padding_x="0.65rem",
        padding_y="0.2rem",
        margin_top="0.9rem",
    )


def _feature_card(icon_tag: str, title: str, copy: str, route_hint: str = "") -> rx.Component:
    return rx.box(
        rx.box(
            rx.icon(tag=icon_tag, size=20, color=COLORS["green_soft"]),
            width="48px",
            height="48px",
            border_radius="16px",
            display="grid",
            place_items="center",
            bg="rgba(22, 199, 132, 0.14)",
            border=f"1px solid {COLORS['border']}",
            margin_bottom="1rem",
        ),
        rx.heading(title, size="5", margin_bottom="0.6rem", letter_spacing="-0.02em"),
        rx.text(copy, color=COLORS["muted"], line_height="1.6", font_size="0.95rem"),
        rx.cond(route_hint != "", _route_pill(route_hint)),
        padding="1.35rem",
        min_height="220px",
        **CARD_STYLE,
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
        font_size="0.93rem",
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
                        rx.link(rx.button("Iniciar sesion", **BUTTON_PRIMARY_STYLE), href="/login"),
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
        bg="rgba(3, 16, 10, 0.78)",
        backdrop_filter="blur(12px)",
        border_bottom=f"1px solid {COLORS['border']}",
        padding_y="0.9rem",
    )


def hero_section() -> rx.Component:
    trust_row = rx.grid(
        _feature_card(
            "clipboard_check",
            "ATS por fases",
            "Flujo guiado para registrar informacion completa y consistente.",
        ),
        _feature_card(
            "file_text",
            "PDF versionado",
            "Generacion documental con historial y respaldo seguro.",
        ),
        _feature_card(
            "layout_dashboard",
            "Dashboard SST",
            "Metricas por estado, riesgo, usuario, peligro, control y periodo.",
        ),
        columns={"base": "1", "md": "3"},
        spacing="3",
        width="100%",
        margin_top="1.5rem",
    )

    visual = rx.box(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.35)"),
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.35)"),
                    rx.box(width="10px", height="10px", border_radius="999px", bg="rgba(255,255,255,0.35)"),
                    spacing="2",
                    align="center",
                ),
                rx.badge("Dashboard ADMIN", color_scheme="green", variant="soft", radius="full"),
                width="100%",
                justify="between",
                align="center",
                padding="1rem 1rem 0.85rem 1rem",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            rx.box(
                rx.grid(
                    rx.box(
                        rx.text("Total ATS", color=COLORS["soft"], size="2"),
                        rx.heading("128", size="8"),
                        padding="0.9rem",
                        border_radius="16px",
                        bg="rgba(255,255,255,0.06)",
                        border=f"1px solid {COLORS['border']}",
                    ),
                    rx.box(
                        rx.text("% alto riesgo", color=COLORS["soft"], size="2"),
                        rx.heading("27", size="8", color=COLORS["green_soft"]),
                        padding="0.9rem",
                        border_radius="16px",
                        bg="rgba(255,255,255,0.06)",
                        border=f"1px solid {COLORS['border']}",
                    ),
                    columns={"base": "1", "sm": "2"},
                    spacing="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.box(
                        rx.hstack(
                            rx.text("ATS por estado", color=COLORS["muted"], size="2"),
                            rx.text("Activo", color=COLORS["green_soft"], size="2", font_weight="700"),
                            width="100%",
                            justify="between",
                            align="center",
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
                            bg="rgba(255,255,255,0.10)",
                            margin_top="0.5rem",
                        ),
                        padding="0.9rem",
                        border_radius="16px",
                        bg="rgba(255,255,255,0.06)",
                        border=f"1px solid {COLORS['border']}",
                        width="100%",
                    ),
                    rx.box(
                        rx.hstack(
                            rx.text("Tendencia mensual", color=COLORS["muted"], size="2"),
                            rx.text("Seguimiento", color=COLORS["green_soft"], size="2", font_weight="700"),
                            width="100%",
                            justify="between",
                            align="center",
                        ),
                        rx.box(
                            rx.box(
                                width="66%",
                                height="100%",
                                border_radius="999px",
                                bg=f"linear-gradient(90deg, {COLORS['green']}, {COLORS['lime']})",
                            ),
                            width="100%",
                            height="8px",
                            border_radius="999px",
                            bg="rgba(255,255,255,0.10)",
                            margin_top="0.5rem",
                        ),
                        padding="0.9rem",
                        border_radius="16px",
                        bg="rgba(255,255,255,0.06)",
                        border=f"1px solid {COLORS['border']}",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                    margin_top="0.8rem",
                ),
                padding="1rem",
                width="100%",
            ),
            border_radius="26px",
            overflow="hidden",
            bg="rgba(3, 16, 10, 0.85)",
            border=f"1px solid {COLORS['border']}",
            width="100%",
        ),
        padding="1rem",
        border_radius="34px",
        bg="linear-gradient(145deg, rgba(255,255,255,0.16), rgba(255,255,255,0.03))",
        border=f"1px solid {COLORS['border']}",
        box_shadow="0 26px 90px rgba(22, 199, 132, 0.24), 0 22px 65px rgba(0,0,0,0.32)",
    )

    return rx.box(
        _container(
            rx.grid(
                rx.box(
                    rx.hstack(
                        rx.box(width="9px", height="9px", border_radius="999px", bg=COLORS["green_neon"]),
                        rx.text("Plataforma web operativa para ATS/SST", font_weight="700", font_size="0.88rem"),
                        spacing="2",
                        align="center",
                        color=COLORS["green_soft"],
                        bg="rgba(22, 199, 132, 0.12)",
                        border=f"1px solid {COLORS['border']}",
                        border_radius="999px",
                        padding="0.5rem 0.85rem",
                        width="fit-content",
                        margin_bottom="1.25rem",
                    ),
                    rx.heading(
                        "Digitaliza el ATS de principio a fin con trazabilidad real.",
                        size={"base": "8", "md": "9"},
                        line_height="0.98",
                        letter_spacing="-0.06em",
                        margin_bottom="1rem",
                        max_width="760px",
                    ),
                    rx.text(
                        (
                            "App ATS SST convierte el Análisis de Trabajo Seguro en un flujo web claro, "
                            "medible y auditable: crea ATS por fases, relaciona actividades con peligros y "
                            "controles, registra trabajadores y firmas, genera PDF versionados y visualiza "
                            "indicadores desde un dashboard administrativo."
                        ),
                        color=COLORS["muted"],
                        line_height="1.72",
                        font_size={"base": "1rem", "md": "1.18rem"},
                        max_width="760px",
                    ),
                    rx.hstack(
                        _button_link("Entrar al sistema", "/login", primary=True),
                        rx.link(rx.button("Conocer la plataforma", **BUTTON_SECONDARY_STYLE), href="#plataforma"),
                        spacing="3",
                        width="100%",
                        flex_wrap="wrap",
                        margin_top="1.5rem",
                    ),
                    trust_row,
                    width="100%",
                ),
                visual,
                columns={"base": "1", "lg": "2"},
                spacing={"base": "6", "lg": "8"},
                align_items="center",
            )
        ),
        id="top",
        padding_y={"base": "3rem", "md": "4.2rem"},
        width="100%",
    )


def challenge_section() -> rx.Component:
    return rx.box(
        _container(
            _section_heading(
                "El reto",
                "El ATS deja de ser solo un formato cuando se convierte en informacion accionable.",
                (
                    "En muchos procesos SST, los registros quedan dispersos, son dificiles de consultar "
                    "y no siempre se transforman en datos utiles. Esta App Web centraliza el ciclo operativo "
                    "del ATS para mejorar trazabilidad, control documental y toma de decisiones."
                ),
            ),
            rx.grid(
                _feature_card(
                    "folders",
                    "Registros dispersos",
                    "La informacion del ATS puede quedar repartida entre formatos, archivos, firmas, evidencias y seguimientos manuales.",
                ),
                _feature_card(
                    "triangle_alert",
                    "Riesgos dificiles de leer",
                    "Sin una estructura paso-peligro-control, es mas complejo entender que se va a hacer, que puede fallar y como se controla.",
                ),
                _feature_card(
                    "eye",
                    "Poca visibilidad gerencial",
                    "Cuando los ATS no alimentan metricas, el equipo administrativo pierde capacidad de seguimiento por usuario, periodo y tipo de riesgo.",
                ),
                columns={"base": "1", "md": "2", "xl": "3"},
                spacing="3",
            ),
        ),
        id="reto",
        **SECTION_STYLE,
    )


def platform_section() -> rx.Component:
    def flow_step(step: str, title: str, desc: str, route: str) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.box(
                    step,
                    width="40px",
                    height="40px",
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
                rx.badge(route, variant="soft", color_scheme="green", radius="full"),
                width="100%",
                align="center",
                spacing="3",
                flex_wrap={"base": "wrap", "sm": "nowrap"},
            ),
            padding="1rem",
            border_radius="20px",
            bg="rgba(255,255,255,0.06)",
            border=f"1px solid {COLORS['border']}",
        )

    return rx.box(
        _container(
            rx.grid(
                rx.box(
                    rx.text(
                        "La plataforma",
                        color=COLORS["green_soft"],
                        text_transform="uppercase",
                        letter_spacing="0.16em",
                        font_weight="800",
                        font_size="0.75rem",
                        margin_bottom="0.75rem",
                    ),
                    rx.heading(
                        "Un flujo web para crear, cerrar, documentar y analizar ATS.",
                        size={"base": "7", "md": "8"},
                        line_height="1.04",
                        letter_spacing="-0.04em",
                    ),
                    rx.text(
                        (
                            "La App Web esta disenada para que el equipo SISO registre el ATS con persistencia "
                            "en base de datos, mientras el rol ADMIN puede consultar indicadores y controlar la "
                            "operacion desde el dashboard."
                        ),
                        color=COLORS["muted"],
                        line_height="1.75",
                        margin_top="1rem",
                    ),
                    rx.vstack(
                        rx.hstack(rx.icon(tag="badge_check", size=16, color=COLORS["green_soft"]), rx.text("Autenticacion con control de acceso por rol: ADMIN y SISO."), spacing="2", align="start"),
                        rx.hstack(rx.icon(tag="badge_check", size=16, color=COLORS["green_soft"]), rx.text("Formulario ATS por secciones con datos generales, peligros, pasos, trabajadores, observaciones y firmas."), spacing="2", align="start"),
                        rx.hstack(rx.icon(tag="badge_check", size=16, color=COLORS["green_soft"]), rx.text("Catalogos activos para estandarizar tipos de ATS, peligros, controles, trabajadores y firmas."), spacing="2", align="start"),
                        rx.hstack(rx.icon(tag="badge_check", size=16, color=COLORS["green_soft"]), rx.text("Generacion de PDF desde plantilla, almacenamiento privado, URL firmada e historial versionado."), spacing="2", align="start"),
                        spacing="3",
                        margin_top="1rem",
                        color=COLORS["muted"],
                        line_height="1.55",
                    ),
                    padding="1.5rem",
                    border_radius="24px",
                    bg="rgba(3, 16, 10, 0.58)",
                    border=f"1px solid {COLORS['border']}",
                ),
                rx.vstack(
                    flow_step("1", "Login y rol", "El usuario inicia sesion y la aplicacion redirige segun su perfil: ADMIN o SISO.", "/login"),
                    flow_step("2", "Formato ATS", "El SISO crea el ATS en estado borrador y completa el flujo por fases.", "/ats/formato"),
                    flow_step("3", "Documento PDF", "Se valida la informacion, se genera el PDF y queda historial por versiones.", "/ats/documentos"),
                    flow_step("4", "Dashboard", "El ADMIN visualiza KPIs, graficos, filtros y tendencias para seguimiento SST.", "/admin/dashboard"),
                    spacing="3",
                    width="100%",
                ),
                columns={"base": "1", "xl": "2"},
                spacing="4",
                align_items="stretch",
                padding={"base": "1rem", "md": "1.6rem"},
                border_radius="32px",
                bg="linear-gradient(145deg, rgba(22, 199, 132, 0.12), rgba(255,255,255,0.05))",
                border=f"1px solid {COLORS['border']}",
                box_shadow="0 22px 65px rgba(0, 0, 0, 0.32)",
            )
        ),
        id="plataforma",
        **SECTION_STYLE,
    )


def modules_section() -> rx.Component:
    return rx.box(
        _container(
            _section_heading(
                "Modulos principales",
                "Todo el ciclo del ATS en una plataforma web centralizada.",
                (
                    "La landing destaca lo que ya esta implementado en la App Web: creacion de ATS, "
                    "gestion documental, dashboard administrativo y control por roles, evitando prometer "
                    "funcionalidades que pertenecen a futuras etapas."
                ),
            ),
            rx.grid(
                _feature_card(
                    "clipboard_check",
                    "Formato ATS por fases",
                    "Captura datos generales, actividad, alto riesgo, peligros, pasos, controles, trabajadores, observaciones y firmas finales.",
                    "/ats/formato",
                ),
                _feature_card(
                    "route",
                    "Matriz paso-peligro-control",
                    "Por cada paso se registran peligros asociados y por cada peligro se agregan uno o varios controles para trazabilidad real.",
                    "Riesgo-control trazable",
                ),
                _feature_card(
                    "users",
                    "Trabajadores y firmas",
                    "Los trabajadores se importan desde catalogo maestro, se conserva snapshot historico y se registra firma digital.",
                    "Evidencia operativa",
                ),
                _feature_card(
                    "file_text",
                    "Documentos PDF",
                    "Busca ATS, genera PDF desde plantilla, descarga el documento y conserva historial versionado.",
                    "/ats/documentos",
                ),
                _feature_card(
                    "layout_dashboard",
                    "Dashboard administrativo",
                    "Visualiza KPIs, graficos y tablas por estado, tipo, usuario SISO, peligros, controles, alto riesgo y tendencia mensual.",
                    "/admin/dashboard",
                ),
                _feature_card(
                    "shield",
                    "Control por ownership",
                    "El ADMIN consulta toda la operacion; el SISO crea, edita y consulta unicamente los ATS asociados a su usuario.",
                    "ADMIN / SISO",
                ),
                columns={"base": "1", "md": "2", "xl": "3"},
                spacing="3",
            ),
        ),
        id="modulos",
        **SECTION_STYLE,
    )


def metrics_section() -> rx.Component:
    metric_card_style = {
        "padding": "1.25rem",
        "border_radius": "22px",
        "bg": "rgba(255,255,255,0.065)",
        "border": f"1px solid {COLORS['border']}",
    }

    def metric(value: str, text: str) -> rx.Component:
        return rx.box(
            rx.heading(value, size="8", color=COLORS["green_soft"], letter_spacing="-0.05em", margin_bottom="0.4rem"),
            rx.text(text, color=COLORS["muted"], line_height="1.45", size="2"),
            **metric_card_style,
        )

    return rx.box(
        _container(
            _section_heading(
                "Metricas y analitica",
                "Convierte los ATS en datos SST medibles, auditables y accionables.",
                (
                    "El dashboard administrativo permite pasar del registro operativo al seguimiento visual, "
                    "con filtros por empleado SISO y rango de fechas para analizar la gestion desde diferentes angulos."
                ),
            ),
            rx.grid(
                metric("7", "Fases para estructurar el proceso de creacion y cierre del ATS."),
                metric("100%", "Enfocado en trazabilidad por actividad, peligro y control."),
                metric("2", "Roles principales para separar operacion y administracion."),
                metric("1", "Fuente central para documentos, firmas e indicadores ATS."),
                columns={"base": "1", "sm": "2", "xl": "4"},
                spacing="3",
            ),
            rx.grid(
                _feature_card(
                    "pie_chart",
                    "Alto riesgo vs no alto riesgo",
                    "Permite entender la proporcion de ATS clasificados como alto riesgo y comparar comportamiento por periodo.",
                ),
                _feature_card(
                    "bar_chart_3",
                    "Top peligros y controles",
                    "Identifica los peligros y controles mas frecuentes para priorizar acciones preventivas.",
                ),
                _feature_card(
                    "line_chart",
                    "Tendencia mensual",
                    "Visualiza la evolucion de ATS en el tiempo para seguimiento operativo y administrativo.",
                ),
                columns={"base": "1", "md": "3"},
                spacing="3",
                margin_top="1rem",
            ),
        ),
        id="metricas",
        **SECTION_STYLE,
    )


def roles_section() -> rx.Component:
    role_card = {
        "padding": {"base": "1.2rem", "md": "1.6rem"},
        "border_radius": "28px",
        "bg": "rgba(255,255,255,0.065)",
        "border": f"1px solid {COLORS['border']}",
    }

    return rx.box(
        _container(
            _section_heading(
                "Control por roles",
                "Una experiencia diferenciada para operacion y administracion.",
                (
                    "La plataforma esta pensada para proteger la informacion y mantener el control operativo: "
                    "cada usuario accede a lo que corresponde segun su rol y perfil interno activo."
                ),
            ),
            rx.grid(
                rx.box(
                    rx.heading("Rol SISO", size="6", color=COLORS["green_soft"], margin_bottom="0.75rem"),
                    rx.text(
                        "Crea, edita y consulta sus ATS. Completa el formato, gestiona peligros y controles, "
                        "registra trabajadores, firmas y accede al modulo de documentos para generar el PDF correspondiente.",
                        color=COLORS["muted"],
                        line_height="1.65",
                    ),
                    **role_card,
                ),
                rx.box(
                    rx.heading("Rol ADMIN", size="6", color=COLORS["green_soft"], margin_bottom="0.75rem"),
                    rx.text(
                        "Cuenta con acceso total a la operacion y al dashboard administrativo para analizar ATS por "
                        "usuario, fechas, estado, tipo, alto riesgo, peligros, controles y tendencia mensual.",
                        color=COLORS["muted"],
                        line_height="1.65",
                    ),
                    **role_card,
                ),
                columns={"base": "1", "md": "2"},
                spacing="3",
            ),
        ),
        id="roles",
        **SECTION_STYLE,
    )


def cta_section() -> rx.Component:
    return rx.box(
        _container(
            rx.box(
                rx.box(
                    rx.text(
                        "Acceso al sistema",
                        color=COLORS["green_soft"],
                        text_transform="uppercase",
                        letter_spacing="0.16em",
                        font_weight="800",
                        font_size="0.75rem",
                        margin_bottom="0.75rem",
                    ),
                    rx.heading(
                        "Gestiona ATS con trazabilidad, documentos versionados y metricas reales.",
                        size={"base": "7", "md": "8"},
                        line_height="1.04",
                        letter_spacing="-0.04em",
                        margin_bottom="0.9rem",
                    ),
                    rx.text(
                        "Ingresa a la App Web para crear nuevos ATS, consultar documentos generados y visualizar informacion clave para la gestion SST desde una plataforma centralizada.",
                        color=COLORS["muted"],
                        line_height="1.7",
                        font_size={"base": "1rem", "md": "1.06rem"},
                        margin_bottom="1.35rem",
                        max_width="800px",
                        margin_x="auto",
                    ),
                    rx.hstack(
                        _button_link("Entrar al sistema", "/login", primary=True),
                        rx.link(rx.button("Gestionar ATS", **BUTTON_SECONDARY_STYLE), href="/ats/formato"),
                        rx.link(rx.button("Generar documentos", **BUTTON_SECONDARY_STYLE), href="/ats/documentos"),
                        spacing="3",
                        flex_wrap="wrap",
                        justify="center",
                        width="100%",
                    ),
                    width="100%",
                    text_align="center",
                ),
                width="100%",
                padding={"base": "2rem 1rem", "md": "4rem 1.75rem"},
                border_radius="40px",
                bg=(
                    "radial-gradient(circle at 50% 0%, rgba(57, 255, 156, 0.24), transparent 45%), "
                    "linear-gradient(145deg, rgba(22, 199, 132, 0.17), rgba(255,255,255,0.055))"
                ),
                border=f"1px solid {COLORS['border']}",
                box_shadow="0 26px 90px rgba(22, 199, 132, 0.24), 0 22px 65px rgba(0,0,0,0.32)",
            )
        ),
        id="login",
        padding_y={"base": "3.8rem", "md": "5rem"},
        width="100%",
    )


def landing_footer() -> rx.Component:
    return rx.box(
        _container(
            rx.hstack(
                rx.text(
                    f"(c) {datetime.now().year} App ATS SST. Plataforma web para gestion operativa de Analisis de Trabajo Seguro.",
                    color=COLORS["soft"],
                    font_size="0.9rem",
                ),
                rx.text(
                    "ATS - Documentos - Firmas - Dashboard",
                    color=COLORS["soft"],
                    font_size="0.9rem",
                ),
                width="100%",
                justify="between",
                align="center",
                spacing="3",
                flex_wrap="wrap",
            )
        ),
        border_top=f"1px solid {COLORS['border']}",
        padding_y="1.4rem",
        width="100%",
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
