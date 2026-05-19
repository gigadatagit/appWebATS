from __future__ import annotations

import reflex as rx

from ..components.cards import workflow_step_card, workflow_step_chip
from ..components.signature_canvas import signature_canvas
from ..state import AtsFormState
from ..template import protected_page
from ..styles import (
    CARD_STYLE,
    CHECKLIST_GRID_STYLE,
    CHECKLIST_ITEM_STYLE,
    EMPTY_STATE_STYLE,
    FIELD_LABEL_STYLE,
    FORM_ITEM_CARD_STYLE,
    FORM_BLOCK_HEADER_STYLE,
    FORM_BLOCK_HELPER_STYLE,
    FORM_BLOCK_STYLE,
    FORM_BLOCK_TITLE_STYLE,
    GREEN,
    INFO_SURFACE_STYLE,
    PRIMARY_BUTTON_STYLE,
    STEP_ACTION_BAR_STYLE,
)


def _step_status(step_number: int):
    return rx.cond(
        AtsFormState.current_step == step_number,
        "current",
        rx.cond(AtsFormState.current_step > step_number, "visited", "pending"),
    )


def _flow_action_bar(*buttons: rx.Component) -> rx.Component:
    return rx.box(
        rx.hstack(
            *buttons,
            spacing="2",
            flex_wrap="wrap",
            width="100%",
            justify={"base": "start", "md": "end"},
            align="center",
        ),
        **STEP_ACTION_BAR_STYLE,
    )


def _action_prev(on_click, label: str = "Anterior") -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(tag="arrow_left", size=15),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        on_click=on_click,
        variant="soft",
        color_scheme="gray",
    )


def _action_save(label: str, on_click, icon_tag: str = "save") -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon_tag, size=15),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        on_click=on_click,
        variant="soft",
        color_scheme="blue",
    )


def _action_continue(label: str, on_click, icon_tag: str = "arrow_right") -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.text(label),
            rx.icon(tag=icon_tag, size=15),
            spacing="2",
            align="center",
        ),
        on_click=on_click,
        **PRIMARY_BUTTON_STYLE,
    )


def _field_label(label: str, required: bool = False, optional: bool = False) -> rx.Component:
    children = [rx.text(label, **FIELD_LABEL_STYLE)]
    if required:
        children.append(rx.badge("Obligatorio", variant="soft", color_scheme="red"))
    elif optional:
        children.append(rx.badge("Opcional", variant="soft", color_scheme="gray"))
    return rx.hstack(
        *children,
        spacing="2",
        align="center",
        width="100%",
    )


def _form_block(
    title: str,
    helper_text: str,
    *children: rx.Component,
    icon_tag: str = "layout_list",
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag=icon_tag, size=16, color=GREEN),
                    rx.text(title, **FORM_BLOCK_TITLE_STYLE),
                    spacing="2",
                    align="center",
                ),
                #width="100%",
                **FORM_BLOCK_HEADER_STYLE,
            ),
            rx.cond(helper_text != "", rx.text(helper_text, **FORM_BLOCK_HELPER_STYLE)),
            *children,
            spacing="3",
            align="stretch",
            width="100%",
        ),
        **FORM_BLOCK_STYLE,
    )


def _section_heading(title: str, description: str, step_label: str, icon_tag: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.hstack(
                rx.icon(tag=icon_tag, size=18, color=GREEN),
                rx.heading(title, size="6"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.badge(step_label, variant="soft", color_scheme="green"),
            width="100%",
            align="center",
        ),
        rx.text(
            description,
            color="#64748b",
            size="2",
            width="100%",
        ),
        spacing="2",
        align="stretch",
        width="100%",
    )


def _empty_state(message: str) -> rx.Component:
    return rx.box(
        rx.text(message, color="#64748b", size="2"),
        **EMPTY_STATE_STYLE,
    )


def section_selector() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="route", size=18, color=GREEN),
                rx.heading("Flujo ATS", size="5"),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.text(
                "Avance visual por fases del formulario. 'Recorrido' indica navegación en pantalla, no guardado definitivo.",
                color="#64748b",
                size="2",
                width="100%",
            ),
            rx.box(
                rx.hstack(
                    workflow_step_chip(1, "Identificación", status=_step_status(1), on_click=AtsFormState.set_step(1)),
                    workflow_step_chip(
                        2,
                        "Peligros",
                        status=_step_status(2),
                        on_click=[AtsFormState.load_peligros_for_current_ats, AtsFormState.set_step(2)],
                    ),
                    workflow_step_chip(
                        3,
                        "Paso a paso",
                        status=_step_status(3),
                        on_click=[AtsFormState.load_pasos_for_current_ats, AtsFormState.set_step(3)],
                    ),
                    workflow_step_chip(
                        4,
                        "Trabajadores",
                        status=_step_status(4),
                        on_click=[AtsFormState.load_trabajadores_for_current_ats, AtsFormState.set_step(4)],
                    ),
                    workflow_step_chip(
                        5,
                        "Observaciones",
                        status=_step_status(5),
                        on_click=[AtsFormState.load_observaciones_for_current_ats, AtsFormState.set_step(5)],
                    ),
                    workflow_step_chip(
                        6,
                        "Firmas",
                        status=_step_status(6),
                        on_click=[AtsFormState.load_firmas_finales_for_current_ats, AtsFormState.set_step(6)],
                    ),
                    workflow_step_chip(7, "Documento", status=_step_status(7), on_click=AtsFormState.set_step(7)),
                    spacing="2",
                    width="max-content",
                ),
                width="100%",
                overflow_x="auto",
                padding_bottom="0.25rem",
            ),
            rx.grid(
                workflow_step_card(
                    1,
                    "Identificación",
                    "Datos generales del ATS",
                    status=_step_status(1),
                    on_click=AtsFormState.set_step(1),
                    icon_tag="clipboard_list",
                ),
                workflow_step_card(
                    2,
                    "Peligros",
                    "Checklist de riesgos",
                    status=_step_status(2),
                    on_click=[AtsFormState.load_peligros_for_current_ats, AtsFormState.set_step(2)],
                    icon_tag="triangle_alert",
                ),
                workflow_step_card(
                    3,
                    "Paso a paso",
                    "Pasos y controles",
                    status=_step_status(3),
                    on_click=[AtsFormState.load_pasos_for_current_ats, AtsFormState.set_step(3)],
                    icon_tag="route",
                ),
                workflow_step_card(
                    4,
                    "Trabajadores",
                    "Personal relacionado",
                    status=_step_status(4),
                    on_click=[AtsFormState.load_trabajadores_for_current_ats, AtsFormState.set_step(4)],
                    icon_tag="users",
                ),
                workflow_step_card(
                    5,
                    "Observaciones",
                    "Notas del ATS",
                    status=_step_status(5),
                    on_click=[AtsFormState.load_observaciones_for_current_ats, AtsFormState.set_step(5)],
                    icon_tag="message_square",
                ),
                workflow_step_card(
                    6,
                    "Firmas",
                    "Cierre del formato",
                    status=_step_status(6),
                    on_click=[AtsFormState.load_firmas_finales_for_current_ats, AtsFormState.set_step(6)],
                    icon_tag="signature",
                ),
                workflow_step_card(
                    7,
                    "Documento",
                    "PDF del ATS",
                    status=_step_status(7),
                    on_click=AtsFormState.set_step(7),
                    icon_tag="file_check",
                ),
                columns={"base": "1", "xl": "2"},
                spacing="3",
                width="100%",
            ),
            spacing="3",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def identificacion_general_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="clipboard_list", size=18, color=GREEN),
                    rx.heading("Identificación General", size="6"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.badge("Paso 1 de 7", color_scheme="green", variant="soft"),
                width="100%",
                align="center",
            ),
            rx.text(
                "Completa la base del ATS y luego continúa con riesgos, pasos, trabajadores, observaciones y firmas.",
                color="#64748b",
                size="2",
                width="100%",
            ),
            _form_block(
                "Datos base del ATS",
                "Información principal del formato y referencia de identificación.",
                rx.cond(
                    AtsFormState.ats_id == 0,
                    rx.box(
                        rx.vstack(
                            rx.text("¿Ya tienes un ATS guardado?", font_weight="600", size="2"),
                            rx.text("Puedes cargarlo por código para editarlo sin perder información.", size="2", color="#64748b"),
                            rx.hstack(
                                rx.input(
                                    placeholder="Ingrese código ATS (ej: ATS-12345678)",
                                    value=AtsFormState.load_codigo_input,
                                    on_change=AtsFormState.set_load_codigo_input,
                                    width="100%",
                                ),
                                rx.button(
                                    rx.hstack(rx.icon(tag="search", size=15), rx.text("Cargar ATS"), spacing="2", align="center"),
                                    on_click=AtsFormState.load_ats_by_codigo(AtsFormState.load_codigo_input),
                                    color_scheme="blue",
                                ),
                                spacing="2",
                                width="100%",
                                flex_wrap="wrap",
                            ),
                            spacing="2",
                            align="stretch",
                            width="100%",
                        ),
                        **INFO_SURFACE_STYLE,
                    ),
                ),
                rx.cond(
                    AtsFormState.ats_id > 0,
                    rx.box(
                        rx.vstack(
                            _field_label("Código ATS cargado", optional=True),
                            rx.input(
                                value=AtsFormState.codigo_publico,
                                read_only=True,
                                width="100%",
                            ),
                            spacing="2",
                            align="stretch",
                        ),
                        **INFO_SURFACE_STYLE,
                    ),
                ),
                rx.grid(
                    rx.box(
                        _field_label("Empresa / Persona ejecuta", required=True),
                        rx.input(
                            placeholder="Ingrese nombre...",
                            value=AtsFormState.empresa_persona_ejecuta,
                            on_change=AtsFormState.set_empresa_persona_ejecuta,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("Fecha elaboración", required=True),
                        rx.input(
                            type="date",
                            value=AtsFormState.fecha_elaboracion,
                            on_change=AtsFormState.set_fecha_elaboracion,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("Ciudad", required=True),
                        rx.input(
                            placeholder="Ingrese ciudad...",
                            value=AtsFormState.ciudad,
                            on_change=AtsFormState.set_ciudad,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("Área / Lugar", required=True),
                        rx.input(
                            placeholder="Ingrese área o lugar...",
                            value=AtsFormState.area_lugar,
                            on_change=AtsFormState.set_area_lugar,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("ATS N°", optional=True),
                        rx.input(
                            placeholder="Ingrese número ATS...",
                            value=AtsFormState.numero_ats,
                            on_change=AtsFormState.set_numero_ats,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("Tipo ATS", required=True),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecciona tipo ATS", width="100%"),
                            rx.select.content(
                                rx.foreach(
                                    AtsFormState.tipos_ats,
                                    lambda tipo: rx.select.item(
                                        tipo["nombre"],
                                        value=tipo["id"].to_string(),
                                    ),
                                )
                            ),
                            value=rx.cond(AtsFormState.tipo_ats_id > 0, AtsFormState.tipo_ats_id.to_string(), ""),
                            on_change=AtsFormState.set_tipo_ats_id_from_select,
                            width="100%",
                        ),
                    ),
                    columns={"base": "1", "md": "2"},
                    spacing="4",
                    width="100%",
                ),
                icon_tag="file_text",
            ),
            _form_block(
                "Contexto de la actividad",
                "Describe qué se realizará y en qué condiciones de riesgo.",
                rx.grid(
                    rx.box(
                        _field_label("Duración de la actividad", required=True),
                        rx.input(
                            placeholder="Ingrese duración...",
                            value=AtsFormState.duracion_actividad,
                            on_change=AtsFormState.set_duracion_actividad,
                            width="100%",
                        ),
                    ),
                    rx.box(
                        _field_label("Clasificación de riesgo", optional=True),
                        rx.box(
                            rx.checkbox(
                                "Actividad de alto riesgo",
                                checked=AtsFormState.actividad_alto_riesgo,
                                on_change=AtsFormState.set_actividad_alto_riesgo,
                            ),
                            **INFO_SURFACE_STYLE,
                        ),
                    ),
                    columns={"base": "1", "md": "2"},
                    spacing="4",
                    width="100%",
                ),
                rx.box(
                    _field_label("Descripción de la actividad", required=True),
                    rx.text_area(
                        placeholder="Describa la actividad con el mayor detalle posible...",
                        value=AtsFormState.descripcion_actividad,
                        on_change=AtsFormState.set_descripcion_actividad,
                        width="100%",
                        min_height="180px",
                    ),
                    width="100%",
                ),
                icon_tag="clipboard_pen",
            ),
            _form_block(
                "Información de apoyo",
                "Marca los apoyos requeridos para ejecutar el ATS de manera segura.",
                rx.box(
                    rx.foreach(
                        AtsFormState.apoyos_catalogo,
                        lambda item: rx.box(
                            rx.vstack(
                                rx.checkbox(
                                    item["nombre"],
                                    checked=AtsFormState.apoyos_seleccionados.contains(item["id"]),
                                    on_change=lambda checked: AtsFormState.set_apoyo_checked(item["id"], checked),
                                ),
                                rx.cond(
                                    item["permite_descripcion_libre"] & AtsFormState.apoyos_seleccionados.contains(item["id"]),
                                    rx.box(
                                        _field_label("Descripción de otro apoyo", optional=True),
                                        rx.text_area(
                                            placeholder="Describe el apoyo adicional...",
                                            value=item["descripcion_otro"],
                                            on_change=lambda value: AtsFormState.set_apoyo_descripcion_otro(item["id"], value),
                                            min_height="100px",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                spacing="2",
                                align="stretch",
                                width="100%",
                            ),
                            **CHECKLIST_ITEM_STYLE,
                        ),
                    ),
                    **CHECKLIST_GRID_STYLE,
                ),
                icon_tag="list_checks",
            ),
            _form_block(
                "Certificados requeridos",
                "Selecciona certificaciones exigidas para la ejecución de la actividad.",
                rx.box(
                    rx.foreach(
                        AtsFormState.certificados_catalogo,
                        lambda item: rx.box(
                            rx.vstack(
                                rx.checkbox(
                                    item["nombre"],
                                    checked=AtsFormState.certificados_seleccionados.contains(item["id"]),
                                    on_change=lambda checked: AtsFormState.set_certificado_checked(item["id"], checked),
                                ),
                                rx.cond(
                                    item["permite_descripcion_libre"]
                                    & AtsFormState.certificados_seleccionados.contains(item["id"]),
                                    rx.box(
                                        _field_label("Descripción de otro certificado", optional=True),
                                        rx.text_area(
                                            placeholder="Describe el certificado adicional...",
                                            value=item["descripcion_otro"],
                                            on_change=lambda value: AtsFormState.set_certificado_descripcion_otro(item["id"], value),
                                            min_height="100px",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                spacing="2",
                                align="stretch",
                                width="100%",
                            ),
                            **CHECKLIST_ITEM_STYLE,
                        ),
                    ),
                    **CHECKLIST_GRID_STYLE,
                ),
                icon_tag="badge_check",
            ),
            _form_block(
                "Observaciones",
                "Notas adicionales relevantes para el equipo y la revisión posterior.",
                rx.box(
                    _field_label("Observaciones generales", optional=True),
                    rx.text_area(
                        placeholder="Agrega observaciones relevantes del ATS...",
                        value=AtsFormState.observaciones,
                        on_change=AtsFormState.set_observaciones,
                        width="100%",
                        min_height="140px",
                    ),
                    width="100%",
                ),
                icon_tag="message_square",
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                rx.button(
                    rx.hstack(
                        rx.icon(tag="rotate_ccw", size=15),
                        rx.text("Nuevo"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=AtsFormState.reset_form,
                    variant="soft",
                ),
                _action_continue("Guardar y continuar", AtsFormState.save_identificacion_general),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def peligros_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            _section_heading(
                "Peligros y riesgos identificados",
                "Selecciona peligros y registra detalles adicionales donde aplique.",
                "Paso 2 de 7",
                "triangle_alert",
            ),
            rx.cond(
                AtsFormState.ats_id <= 0,
                rx.callout(
                    "Primero guarda la Identificacion General para habilitar esta seccion.",
                    color_scheme="orange",
                    icon="triangle_alert",
                ),
            ),
            _form_block(
                "Checklist de peligros",
                "Marca los riesgos detectados. El guardado mantiene el comportamiento actual.",
                rx.hstack(
                    rx.badge("Peligros seleccionados", variant="soft", color_scheme="orange"),
                    rx.badge(AtsFormState.peligros_seleccionados_count.to_string(), color_scheme="orange"),
                    spacing="2",
                    width="100%",
                    align="center",
                ),
                rx.box(
                    rx.text("Puedes completar descripcion adicional solo cuando aplique.", size="2", color="#64748b"),
                    **INFO_SURFACE_STYLE,
                ),
                rx.grid(
                    rx.foreach(
                        AtsFormState.peligros_catalogo,
                        lambda peligro: rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.checkbox(
                                        checked=peligro["seleccionado"],
                                        on_change=lambda checked: AtsFormState.set_peligro_checked(peligro["id"], checked),
                                    ),
                                    rx.badge(peligro["numero"].to_string(), color_scheme="orange", variant="soft"),
                                    rx.text(peligro["nombre"], size="3", font_weight="600"),
                                    align="center",
                                    spacing="3",
                                    width="100%",
                                ),
                                rx.cond(
                                    peligro["permite_descripcion_libre"] & peligro["seleccionado"],
                                    rx.box(
                                        _field_label("Descripcion adicional", optional=True),
                                        rx.text_area(
                                            placeholder="Describe el peligro identificado...",
                                            value=peligro["descripcion_otro"],
                                            on_change=lambda value: AtsFormState.set_peligro_descripcion_otro(
                                                peligro["id"], value
                                            ),
                                            min_height="110px",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                spacing="3",
                                align="stretch",
                                width="100%",
                            ),
                            **CHECKLIST_ITEM_STYLE,
                        ),
                    ),
                    columns={"base": "1", "md": "2"},
                    spacing="3",
                    width="100%",
                ),
                icon_tag="triangle_alert",
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                _action_prev(AtsFormState.prev_step),
                _action_save("Guardar", AtsFormState.save_peligros_riesgos),
                _action_continue("Guardar y continuar", AtsFormState.save_peligros_riesgos_y_continuar),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def pasos_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            _section_heading(
                "Paso a paso de la actividad",
                "Crea pasos y asocia peligros con uno o varios controles por cada relacion.",
                "Paso 3 de 7",
                "route",
            ),
            rx.cond(
                AtsFormState.ats_id <= 0,
                rx.callout(
                    "Primero guarda la identificacion general del ATS.",
                    color_scheme="orange",
                    icon="triangle_alert",
                ),
            ),
            _form_block(
                "Detalle de pasos, peligros y controles",
                "Busca peligros por ID o nombre y asigna uno o varios controles por cada peligro del paso.",
                rx.hstack(
                    rx.badge("Pasos creados", variant="soft", color_scheme="green"),
                    rx.badge(AtsFormState.pasos_actividad_count.to_string(), color_scheme="green"),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="plus", size=15),
                            rx.text("Agregar paso"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=AtsFormState.add_paso_actividad,
                        color_scheme="green",
                        variant="soft",
                    ),
                    spacing="3",
                    width="100%",
                    align="center",
                    flex_wrap="wrap",
                ),
                rx.cond(
                    AtsFormState.pasos_actividad_count <= 0,
                    _empty_state("Aun no hay pasos. Agrega al menos uno para continuar."),
                ),
                rx.vstack(
                    rx.foreach(
                        AtsFormState.pasos_actividad,
                        lambda paso: rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.badge("Paso " + paso["numero_paso"].to_string(), color_scheme="green"),
                                    rx.spacer(),
                                    rx.button(
                                        "Eliminar paso",
                                        on_click=AtsFormState.remove_paso_actividad(paso["uid"]),
                                        variant="soft",
                                        color_scheme="red",
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                                rx.box(
                                    _field_label("Descripcion del paso", required=True),
                                    rx.text_area(
                                        placeholder="Describe la actividad de este paso...",
                                        value=paso["descripcion_paso"],
                                        on_change=lambda value: AtsFormState.set_paso_descripcion(paso["uid"], value),
                                        min_height="120px",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                rx.box(
                                    _field_label("Peligros asociados", required=True),
                                    rx.hstack(
                                        rx.button(
                                            rx.hstack(
                                                rx.icon(tag="search", size=15),
                                                rx.text("Buscar y agregar peligro"),
                                                spacing="2",
                                                align="center",
                                            ),
                                            on_click=AtsFormState.open_paso3_peligro_modal(paso["uid"]),
                                            variant="soft",
                                            color_scheme="orange",
                                        ),
                                        rx.text(
                                            "Cada peligro debe tener uno o varios controles.",
                                            size="2",
                                            color="#64748b",
                                        ),
                                        width="100%",
                                        align="center",
                                        spacing="3",
                                        flex_wrap="wrap",
                                    ),
                                    rx.cond(
                                        paso["peligros"].length() <= 0,
                                        _empty_state("Sin peligros asociados en este paso."),
                                    ),
                                    rx.vstack(
                                        rx.foreach(
                                            paso["peligros"],
                                            lambda peligro: rx.box(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.badge(
                                                            "P" + peligro["peligro_numero"].to_string(),
                                                            variant="soft",
                                                            color_scheme="orange",
                                                        ),
                                                        rx.text(peligro["peligro_nombre"], font_weight="600"),
                                                        rx.spacer(),
                                                        rx.button(
                                                            "Quitar",
                                                            on_click=AtsFormState.remove_peligro_from_paso(
                                                                paso["uid"], peligro["uid"]
                                                            ),
                                                            variant="soft",
                                                            color_scheme="red",
                                                        ),
                                                        width="100%",
                                                        align="center",
                                                        spacing="2",
                                                        flex_wrap="wrap",
                                                    ),
                                                    rx.box(
                                                        _field_label("Controles aplicables", required=True),
                                                        rx.hstack(
                                                            rx.button(
                                                                rx.hstack(
                                                                    rx.icon(tag="plus", size=15),
                                                                    rx.text("Agregar control"),
                                                                    spacing="2",
                                                                    align="center",
                                                                ),
                                                                on_click=AtsFormState.add_control_to_paso_peligro(
                                                                    paso["uid"], peligro["uid"]
                                                                ),
                                                                variant="soft",
                                                                color_scheme="blue",
                                                            ),
                                                            rx.text(
                                                                "Agrega uno o varios controles para este peligro.",
                                                                size="2",
                                                                color="#64748b",
                                                            ),
                                                            width="100%",
                                                            align="center",
                                                            spacing="3",
                                                            flex_wrap="wrap",
                                                        ),
                                                        rx.cond(
                                                            peligro["controls"].length() <= 0,
                                                            _empty_state("Este peligro no tiene controles asociados."),
                                                        ),
                                                        rx.vstack(
                                                            rx.foreach(
                                                                peligro["controls"],
                                                                lambda control: rx.box(
                                                                    rx.vstack(
                                                                        rx.hstack(
                                                                            rx.badge(
                                                                                "Control",
                                                                                variant="soft",
                                                                                color_scheme="blue",
                                                                            ),
                                                                            rx.spacer(),
                                                                            rx.button(
                                                                                "Quitar control",
                                                                                on_click=AtsFormState.remove_control_from_paso_peligro(
                                                                                    paso["uid"], peligro["uid"], control["uid"]
                                                                                ),
                                                                                variant="soft",
                                                                                color_scheme="red",
                                                                            ),
                                                                            width="100%",
                                                                            align="center",
                                                                            spacing="2",
                                                                            flex_wrap="wrap",
                                                                        ),
                                                                        rx.select.root(
                                                                            rx.select.trigger(
                                                                                placeholder="Selecciona un control",
                                                                                width="100%",
                                                                            ),
                                                                            rx.select.content(
                                                                                rx.foreach(
                                                                                    AtsFormState.controles_catalogo_options,
                                                                                    lambda item: rx.select.item(
                                                                                        item["label"],
                                                                                        value=item["value"],
                                                                                    ),
                                                                                )
                                                                            ),
                                                                            value=rx.cond(
                                                                                control["control_id"] > 0,
                                                                                control["control_id"].to_string(),
                                                                                "",
                                                                            ),
                                                                            on_change=lambda value: AtsFormState.set_paso_peligro_control(
                                                                                paso["uid"], peligro["uid"], control["uid"], value
                                                                            ),
                                                                            width="100%",
                                                                        ),
                                                                        rx.cond(
                                                                            (control["control_id"] > 0)
                                                                            & (control["control_id"] == AtsFormState.control_otro_id),
                                                                            rx.box(
                                                                                _field_label("Control aplicado (OTROS)", required=True),
                                                                                rx.text_area(
                                                                                    placeholder="Escribe el control aplicado...",
                                                                                    value=control["control_aplicado"],
                                                                                    on_change=lambda value: AtsFormState.set_paso_peligro_control_aplicado(
                                                                                        paso["uid"], peligro["uid"], control["uid"], value
                                                                                    ),
                                                                                    min_height="90px",
                                                                                    width="100%",
                                                                                ),
                                                                                width="100%",
                                                                            ),
                                                                            rx.cond(
                                                                                control["control_id"] > 0,
                                                                                rx.box(
                                                                                    rx.text(
                                                                                        "Snapshot control: ",
                                                                                        control["control_aplicado"],
                                                                                        size="2",
                                                                                        color="#475569",
                                                                                    ),
                                                                                    **INFO_SURFACE_STYLE,
                                                                                ),
                                                                            ),
                                                                        ),
                                                                        spacing="3",
                                                                        align="stretch",
                                                                    ),
                                                                    **INFO_SURFACE_STYLE,
                                                                ),
                                                            ),
                                                            spacing="3",
                                                            width="100%",
                                                        ),
                                                        width="100%",
                                                    ),
                                                    spacing="3",
                                                    align="stretch",
                                                ),
                                                **CHECKLIST_ITEM_STYLE,
                                            ),
                                        ),
                                        spacing="3",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                spacing="4",
                                align="stretch",
                            ),
                            **FORM_ITEM_CARD_STYLE,
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                icon_tag="route",
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.vstack(
                        rx.dialog.title("Agregar peligros al paso"),
                        rx.text(
                            "Busca por ID o nombre del peligro y agregalo al paso actual.",
                            color="#64748b",
                            size="2",
                        ),
                        rx.input(
                            placeholder="Ejemplo: P3 o caida",
                            value=AtsFormState.paso3_peligro_search,
                            on_change=AtsFormState.set_paso3_peligro_search,
                            width="100%",
                        ),
                        rx.cond(
                            AtsFormState.paso3_peligros_filtrados.length() <= 0,
                            _empty_state("No hay peligros disponibles con ese filtro."),
                        ),
                        rx.box(
                            rx.vstack(
                                rx.foreach(
                                    AtsFormState.paso3_peligros_filtrados,
                                    lambda item: rx.hstack(
                                        rx.hstack(
                                            rx.badge("P" + item["numero"].to_string(), color_scheme="orange", variant="soft"),
                                            rx.text(item["nombre"]),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.spacer(),
                                        rx.button(
                                            "Agregar",
                                            on_click=AtsFormState.add_peligro_to_paso(item["id"]),
                                            variant="soft",
                                            color_scheme="green",
                                        ),
                                        width="100%",
                                        align="center",
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            max_height="320px",
                            overflow_y="auto",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button("Cancelar", on_click=AtsFormState.close_paso3_peligro_modal, variant="soft"),
                            rx.button("Finalizar", on_click=AtsFormState.close_paso3_peligro_modal, **PRIMARY_BUTTON_STYLE),
                            width="100%",
                            justify="end",
                            spacing="2",
                        ),
                        spacing="3",
                        align="stretch",
                    ),
                    max_width="720px",
                ),
                open=AtsFormState.paso3_peligro_modal_open,
                on_open_change=AtsFormState.set_paso3_peligro_modal_open,
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                _action_prev(AtsFormState.prev_step),
                _action_save("Guardar", AtsFormState.save_pasos_actividad),
                _action_continue("Guardar y continuar", AtsFormState.save_pasos_actividad_y_continuar),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def trabajadores_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            _section_heading(
                "Trabajadores relacionados",
                "Importa personal desde el catalogo maestro y conserva la firma digital.",
                "Paso 4 de 7",
                "users",
            ),
            rx.cond(
                AtsFormState.ats_id <= 0,
                rx.callout(
                    "Primero guarda la identificacion general del ATS.",
                    color_scheme="orange",
                    icon="triangle_alert",
                ),
            ),
            _form_block(
                "Equipo participante",
                "Los datos de nombre, documento y cargo se cargan desde catalogo y quedan en snapshot.",
                rx.hstack(
                    rx.badge("Trabajadores", variant="soft", color_scheme="green"),
                    rx.badge(AtsFormState.trabajadores_actividad_count.to_string(), color_scheme="green"),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="download", size=15),
                            rx.text("Importar trabajador"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=AtsFormState.open_trabajador_import_modal,
                        color_scheme="green",
                        variant="soft",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                    flex_wrap="wrap",
                ),
                rx.cond(
                    AtsFormState.trabajadores_actividad_count <= 0,
                    _empty_state("Aun no hay trabajadores. Importa al menos uno para continuar."),
                ),
                rx.vstack(
                    rx.foreach(
                        AtsFormState.trabajadores_actividad,
                        lambda trabajador: rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.badge("Trabajador " + trabajador["numero_orden"].to_string(), color_scheme="green"),
                                    rx.spacer(),
                                    rx.button(
                                        "Eliminar",
                                        on_click=AtsFormState.remove_trabajador_actividad(trabajador["uid"]),
                                        variant="soft",
                                        color_scheme="red",
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                                rx.grid(
                                    rx.box(
                                        _field_label("Nombre completo (snapshot)", required=True),
                                        rx.input(
                                            value=trabajador["nombre_trabajador"],
                                            read_only=True,
                                            width="100%",
                                        ),
                                    ),
                                    rx.box(
                                        _field_label("Numero de documento (snapshot)", required=True),
                                        rx.input(
                                            value=trabajador["numero_documento"],
                                            read_only=True,
                                            width="100%",
                                        ),
                                    ),
                                    rx.box(
                                        _field_label("Cargo (snapshot)", optional=True),
                                        rx.input(
                                            value=trabajador["cargo_trabajador"],
                                            read_only=True,
                                            width="100%",
                                        ),
                                    ),
                                    columns={"base": "1", "md": "3"},
                                    spacing="4",
                                    width="100%",
                                ),
                                rx.box(
                                    _field_label("Firma digital", required=True),
                                    rx.box(
                                        signature_canvas(
                                            pen_color="#0f172a",
                                            background_color="#ffffff",
                                            clear_on_resize=False,
                                            canvas_props={
                                                "className": "ats-signature-canvas",
                                                "width": 1200,
                                                "height": 440,
                                                "style": {
                                                    "width": "100%",
                                                    "height": "100%",
                                                    "background": "#ffffff",
                                                    "touchAction": "none",
                                                    "cursor": "crosshair",
                                                    "display": "block",
                                                },
                                            },
                                        ),
                                        border="1px solid #cbd5e1",
                                        border_radius="12px",
                                        overflow="hidden",
                                        width="100%",
                                        height="220px",
                                        bg="white",
                                    ),
                                    rx.hstack(
                                        rx.text("La firma se captura automaticamente al guardar trabajadores.", size="2", color="#475569"),
                                        rx.spacer(),
                                        rx.button(
                                            "Limpiar",
                                            on_click=rx.call_script(
                                                """
(() => {
  const trigger = (typeof event !== "undefined" && event?.target) ? event.target : document.activeElement;
  const root = trigger ? trigger.closest(".ats-signature-root") : null;
  const card = trigger ? trigger.closest(".ats-trabajador-card") : null;
  const canvas = root ? root.querySelector("canvas") : null;
  if (!canvas) return "";
  const ctx = canvas.getContext("2d");
  if (!ctx) return "";
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (card) {
    card.setAttribute("data-firma-actual", "");
  }
  return "";
})()
                                                """
                                            ),
                                            variant="soft",
                                        ),
                                        spacing="3",
                                        width="100%",
                                        flex_wrap="wrap",
                                        align="center",
                                    ),
                                    rx.cond(
                                        trabajador["firma_base64"] != "",
                                        rx.box(
                                            rx.text("Firma guardada actualmente", size="2", color="#16a34a"),
                                            rx.image(
                                                src=trabajador["firma_base64"],
                                                width="100%",
                                                max_width="420px",
                                                border="1px solid #e2e8f0",
                                                border_radius="10px",
                                                bg="white",
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                    class_name="ats-signature-root",
                                ),
                                spacing="4",
                                align="stretch",
                            ),
                            **FORM_ITEM_CARD_STYLE,
                            class_name="ats-trabajador-card",
                            custom_attrs={
                                "data-trabajador-uid": trabajador["uid"],
                                "data-firma-actual": trabajador["firma_base64"],
                            },
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                icon_tag="users",
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.vstack(
                        rx.dialog.title("Importar trabajador"),
                        rx.text(
                            "Busca por nombre o documento y selecciona uno o varios.",
                            size="2",
                            color="#64748b",
                        ),
                        rx.input(
                            placeholder="Buscar trabajador...",
                            value=AtsFormState.trabajador_import_search,
                            on_change=AtsFormState.set_trabajador_import_search,
                            width="100%",
                        ),
                        rx.cond(
                            AtsFormState.trabajadores_importables_filtrados.length() <= 0,
                            _empty_state("No hay resultados para esta busqueda."),
                        ),
                        rx.box(
                            rx.vstack(
                                rx.foreach(
                                    AtsFormState.trabajadores_importables_filtrados,
                                    lambda item: rx.box(
                                        rx.hstack(
                                            rx.checkbox(
                                                checked=item["seleccionado"],
                                                on_change=lambda checked: AtsFormState.toggle_trabajador_import_selection(
                                                    item["id"], checked
                                                ),
                                            ),
                                            rx.vstack(
                                                rx.text(item["nombre_completo"], font_weight="600"),
                                                rx.text("Doc: ", item["numero_documento"], size="2", color="#64748b"),
                                                rx.text("Cargo: ", item["cargo"], size="2", color="#64748b"),
                                                spacing="1",
                                                align="start",
                                            ),
                                            width="100%",
                                            align="start",
                                            spacing="3",
                                        ),
                                        **CHECKLIST_ITEM_STYLE,
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            max_height="340px",
                            overflow_y="auto",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button("Cancelar", on_click=AtsFormState.close_trabajador_import_modal, variant="soft"),
                            rx.button(
                                "Importar / Agregar",
                                on_click=AtsFormState.import_trabajadores_seleccionados,
                                **PRIMARY_BUTTON_STYLE,
                            ),
                            width="100%",
                            justify="end",
                            spacing="2",
                        ),
                        spacing="3",
                        align="stretch",
                    ),
                    max_width="760px",
                ),
                open=AtsFormState.trabajador_import_modal_open,
                on_open_change=AtsFormState.set_trabajador_import_modal_open,
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                _action_prev(AtsFormState.prev_step),
                _action_save(
                    "Guardar",
                    rx.call_script(
                        """
(() => {
  const cards = Array.from(document.querySelectorAll(".ats-trabajador-card"));

  const buildCanvasData = (canvas) => {
    const withWhiteBackground = document.createElement("canvas");
    withWhiteBackground.width = canvas.width;
    withWhiteBackground.height = canvas.height;
    const ctx = withWhiteBackground.getContext("2d");
    if (!ctx) return { data: "", blank: "" };
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, withWhiteBackground.width, withWhiteBackground.height);
    ctx.drawImage(canvas, 0, 0);
    const data = withWhiteBackground.toDataURL("image/png");

    const blank = document.createElement("canvas");
    blank.width = canvas.width;
    blank.height = canvas.height;
    const blankCtx = blank.getContext("2d");
    if (!blankCtx) return { data, blank: "" };
    blankCtx.fillStyle = "#ffffff";
    blankCtx.fillRect(0, 0, blank.width, blank.height);
    const blankData = blank.toDataURL("image/png");
    return { data, blank: blankData };
  };

  const rows = cards
    .map((card) => {
      const uid = card.getAttribute("data-trabajador-uid") || "";
      if (!uid) return null;
      const current = card.getAttribute("data-firma-actual") || "";
      const canvas = card.querySelector("canvas");
      if (!canvas) return { uid, firma_base64: current };

      const parsed = buildCanvasData(canvas);
      const isBlank = parsed.data === "" || parsed.data === parsed.blank;
      return { uid, firma_base64: isBlank ? current : parsed.data };
    })
    .filter((row) => row !== null);

  return JSON.stringify(rows);
})()
                        """,
                        callback=AtsFormState.save_trabajadores_actividad_with_signatures,
                    ),
                ),
                _action_continue(
                    "Guardar y continuar",
                    rx.call_script(
                        """
(() => {
  const cards = Array.from(document.querySelectorAll(".ats-trabajador-card"));

  const buildCanvasData = (canvas) => {
    const withWhiteBackground = document.createElement("canvas");
    withWhiteBackground.width = canvas.width;
    withWhiteBackground.height = canvas.height;
    const ctx = withWhiteBackground.getContext("2d");
    if (!ctx) return { data: "", blank: "" };
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, withWhiteBackground.width, withWhiteBackground.height);
    ctx.drawImage(canvas, 0, 0);
    const data = withWhiteBackground.toDataURL("image/png");

    const blank = document.createElement("canvas");
    blank.width = canvas.width;
    blank.height = canvas.height;
    const blankCtx = blank.getContext("2d");
    if (!blankCtx) return { data, blank: "" };
    blankCtx.fillStyle = "#ffffff";
    blankCtx.fillRect(0, 0, blank.width, blank.height);
    const blankData = blank.toDataURL("image/png");
    return { data, blank: blankData };
  };

  const rows = cards
    .map((card) => {
      const uid = card.getAttribute("data-trabajador-uid") || "";
      if (!uid) return null;
      const current = card.getAttribute("data-firma-actual") || "";
      const canvas = card.querySelector("canvas");
      if (!canvas) return { uid, firma_base64: current };

      const parsed = buildCanvasData(canvas);
      const isBlank = parsed.data === "" || parsed.data === parsed.blank;
      return { uid, firma_base64: isBlank ? current : parsed.data };
    })
    .filter((row) => row !== null);

  return JSON.stringify(rows);
})()
                        """,
                        callback=AtsFormState.save_trabajadores_actividad_with_signatures_y_continuar,
                    ),
                ),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def observaciones_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            _section_heading(
                "Observaciones",
                "Registra notas finales del ATS para seguimiento interno.",
                "Paso 5 de 7",
                "message_square",
            ),
            rx.cond(
                AtsFormState.ats_id <= 0,
                rx.callout(
                    "Primero guarda la identificacion general del ATS.",
                    color_scheme="orange",
                    icon="triangle_alert",
                ),
            ),
            _form_block(
                "Notas y observaciones",
                "Este texto se mantiene en la misma base de datos del ATS actual.",
                rx.box(
                    _field_label("Observaciones", optional=True),
                    rx.text_area(
                        placeholder="Escribe observaciones...",
                        value=AtsFormState.observaciones,
                        on_change=AtsFormState.set_observaciones,
                        width="100%",
                        min_height="220px",
                    ),
                    width="100%",
                ),
                icon_tag="message_square",
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                _action_prev(AtsFormState.prev_step),
                _action_save("Guardar", AtsFormState.save_observaciones),
                _action_continue("Guardar y continuar", AtsFormState.save_observaciones_y_continuar),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def firmas_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            _section_heading(
                "Firmas finales",
                "Captura la informacion de Autoriza, Supervisa y Ejecuta.",
                "Paso 6 de 7",
                "signature",
            ),
            rx.cond(
                AtsFormState.ats_id <= 0,
                rx.callout(
                    "Primero guarda la identificacion general del ATS.",
                    color_scheme="orange",
                    icon="triangle_alert",
                ),
            ),
            _form_block(
                "Registro de responsables",
                "Completa los datos y firma digital de cada rol configurado.",
                rx.hstack(
                    rx.badge("Firmas configuradas", variant="soft", color_scheme="green"),
                    rx.badge(AtsFormState.firmas_finales_count.to_string(), color_scheme="green"),
                    spacing="2",
                    width="100%",
                    align="center",
                ),
                rx.cond(
                    AtsFormState.firmas_finales_count <= 0,
                    _empty_state("No hay tipos de firma activos en catalogo."),
                ),
                rx.grid(
                    rx.foreach(
                        AtsFormState.firmas_finales,
                        lambda firma: rx.box(
                            rx.vstack(
                                rx.badge(firma["firma_tipo_nombre"], color_scheme="green", variant="soft"),
                                rx.box(
                                    _field_label("Nombre completo", required=True),
                                    rx.input(
                                        placeholder="Nombre completo",
                                        value=firma["nombre_completo"],
                                        on_change=lambda value: AtsFormState.set_firma_final_nombre(firma["uid"], value),
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                rx.box(
                                    _field_label("Cargo", optional=True),
                                    rx.input(
                                        placeholder="Cargo",
                                        value=firma["cargo"],
                                        on_change=lambda value: AtsFormState.set_firma_final_cargo(firma["uid"], value),
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                rx.box(
                                    _field_label("Firma digital", required=True),
                                    rx.box(
                                        signature_canvas(
                                            pen_color="#0f172a",
                                            background_color="#ffffff",
                                            clear_on_resize=False,
                                            canvas_props={
                                                "className": "ats-firma-final-canvas",
                                                "width": 1200,
                                                "height": 420,
                                                "style": {
                                                    "width": "100%",
                                                    "height": "100%",
                                                    "background": "#ffffff",
                                                    "touchAction": "none",
                                                    "cursor": "crosshair",
                                                    "display": "block",
                                                },
                                            },
                                        ),
                                        border="1px solid #cbd5e1",
                                        border_radius="12px",
                                        overflow="hidden",
                                        width="100%",
                                        height="210px",
                                        bg="white",
                                    ),
                                    rx.hstack(
                                        rx.text("La firma se captura automaticamente al guardar.", size="2", color="#475569"),
                                        rx.spacer(),
                                        rx.button(
                                            "Limpiar",
                                            on_click=rx.call_script(
                                                """
(() => {
  const trigger = (typeof event !== "undefined" && event?.target) ? event.target : document.activeElement;
  const root = trigger ? trigger.closest(".ats-firma-final-root") : null;
  const card = trigger ? trigger.closest(".ats-firma-final-card") : null;
  const canvas = root ? root.querySelector("canvas") : null;
  if (!canvas) return "";
  const ctx = canvas.getContext("2d");
  if (!ctx) return "";
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (card) {
    card.setAttribute("data-firma-actual", "");
  }
  return "";
})()
                                                """
                                            ),
                                            variant="soft",
                                        ),
                                        spacing="2",
                                        width="100%",
                                        align="center",
                                    ),
                                    rx.cond(
                                        firma["firma_base64"] != "",
                                        rx.box(
                                            rx.text("Firma guardada actualmente", size="2", color="#16a34a"),
                                            rx.image(
                                                src=firma["firma_base64"],
                                                width="100%",
                                                max_width="340px",
                                                border="1px solid #e2e8f0",
                                                border_radius="10px",
                                                bg="white",
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                    class_name="ats-firma-final-root",
                                ),
                                spacing="3",
                                width="100%",
                                align="stretch",
                            ),
                            **FORM_ITEM_CARD_STYLE,
                            class_name="ats-firma-final-card",
                            custom_attrs={
                                "data-firma-uid": firma["uid"],
                                "data-firma-actual": firma["firma_base64"],
                            },
                        ),
                    ),
                    columns={"base": "1", "lg": "3"},
                    spacing="4",
                    width="100%",
                ),
                icon_tag="signature",
            ),
            rx.cond(AtsFormState.form_error != "", rx.callout(AtsFormState.form_error, color_scheme="red", icon="triangle_alert")),
            rx.cond(AtsFormState.form_success != "", rx.callout(AtsFormState.form_success, color_scheme="green", icon="circle_check")),
            _flow_action_bar(
                _action_prev(AtsFormState.prev_step),
                _action_save(
                    "Guardar",
                    rx.call_script(
                        """
(() => {
  const cards = Array.from(document.querySelectorAll(".ats-firma-final-card"));

  const buildCanvasData = (canvas) => {
    const withWhiteBackground = document.createElement("canvas");
    withWhiteBackground.width = canvas.width;
    withWhiteBackground.height = canvas.height;
    const ctx = withWhiteBackground.getContext("2d");
    if (!ctx) return { data: "", blank: "" };
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, withWhiteBackground.width, withWhiteBackground.height);
    ctx.drawImage(canvas, 0, 0);
    const data = withWhiteBackground.toDataURL("image/png");

    const blank = document.createElement("canvas");
    blank.width = canvas.width;
    blank.height = canvas.height;
    const blankCtx = blank.getContext("2d");
    if (!blankCtx) return { data, blank: "" };
    blankCtx.fillStyle = "#ffffff";
    blankCtx.fillRect(0, 0, blank.width, blank.height);
    const blankData = blank.toDataURL("image/png");
    return { data, blank: blankData };
  };

  const rows = cards
    .map((card) => {
      const uid = card.getAttribute("data-firma-uid") || "";
      if (!uid) return null;
      const current = card.getAttribute("data-firma-actual") || "";
      const canvas = card.querySelector("canvas");
      if (!canvas) return { uid, firma_base64: current };
      const parsed = buildCanvasData(canvas);
      const isBlank = parsed.data === "" || parsed.data === parsed.blank;
      return { uid, firma_base64: isBlank ? current : parsed.data };
    })
    .filter((row) => row !== null);

  return JSON.stringify(rows);
})()
                        """,
                        callback=AtsFormState.save_firmas_finales_with_signatures,
                    ),
                ),
                _action_continue(
                    "Guardar y continuar",
                    rx.call_script(
                        """
(() => {
  const cards = Array.from(document.querySelectorAll(".ats-firma-final-card"));

  const buildCanvasData = (canvas) => {
    const withWhiteBackground = document.createElement("canvas");
    withWhiteBackground.width = canvas.width;
    withWhiteBackground.height = canvas.height;
    const ctx = withWhiteBackground.getContext("2d");
    if (!ctx) return { data: "", blank: "" };
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, withWhiteBackground.width, withWhiteBackground.height);
    ctx.drawImage(canvas, 0, 0);
    const data = withWhiteBackground.toDataURL("image/png");

    const blank = document.createElement("canvas");
    blank.width = canvas.width;
    blank.height = canvas.height;
    const blankCtx = blank.getContext("2d");
    if (!blankCtx) return { data, blank: "" };
    blankCtx.fillStyle = "#ffffff";
    blankCtx.fillRect(0, 0, blank.width, blank.height);
    const blankData = blank.toDataURL("image/png");
    return { data, blank: blankData };
  };

  const rows = cards
    .map((card) => {
      const uid = card.getAttribute("data-firma-uid") || "";
      if (!uid) return null;
      const current = card.getAttribute("data-firma-actual") || "";
      const canvas = card.querySelector("canvas");
      if (!canvas) return { uid, firma_base64: current };
      const parsed = buildCanvasData(canvas);
      const isBlank = parsed.data === "" || parsed.data === parsed.blank;
      return { uid, firma_base64: isBlank ? current : parsed.data };
    })
    .filter((row) => row !== null);

  return JSON.stringify(rows);
})()
                        """,
                        callback=AtsFormState.save_firmas_finales_with_signatures_y_continuar,
                    ),
                ),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def documento_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Creación de documento", size="6"),
            rx.text(
                "Esta sección queda enlazada a la futura generación PDF basada en el ATS guardado.",
                color="#64748b",
            ),
            rx.cond(
                AtsFormState.codigo_publico != "",
                rx.badge("ATS actual: " + AtsFormState.codigo_publico, color_scheme="green", size="3"),
            ),
            _flow_action_bar(
                _action_prev(AtsFormState.set_step(1), label="Volver a identificación"),
                _action_continue("Ir a documentos", rx.redirect("/ats/documentos"), icon_tag="external_link"),
            ),
            spacing="4",
            align="stretch",
        ),
        **CARD_STYLE,
        width="100%",
    )


def current_section() -> rx.Component:
    return rx.match(
        AtsFormState.current_step,
        (1, identificacion_general_section()),
        (2, peligros_section()),
        (3, pasos_section()),
        (4, trabajadores_section()),
        (5, observaciones_section()),
        (6, firmas_section()),
        (7, documento_section()),
        identificacion_general_section(),
    )


@rx.page(route="/ats/formato", title="Formato ATS", on_load=AtsFormState.load_initial_data)
def ats_form_page() -> rx.Component:
    content = rx.vstack(
        section_selector(),
        current_section(),
        rx.box(
            rx.heading("ATS recientes", size="5"),
            rx.text("Esto ya viene conectado a la base SQLite.", color="#64748b"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Código"),
                        rx.table.column_header_cell("Empresa"),
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell("Estado"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AtsFormState.ats_recientes,
                        lambda row: rx.table.row(
                            rx.table.cell(row["codigo_publico"]),
                            rx.table.cell(row["empresa_persona_ejecuta"]),
                            rx.table.cell(row["fecha_elaboracion"]),
                            rx.table.cell(row["estado"]),
                        ),
                    )
                ),
                width="100%",
            ),
            **CARD_STYLE,
            width="100%",
        ),
        width="100%",
        align="stretch",
        spacing="4",
    )
    return protected_page(
        "Formato ATS",
        content,
        subtitle="Completa el flujo por fases y guarda cada sección para avanzar con control.",
        current_route="/ats/formato",
    )
