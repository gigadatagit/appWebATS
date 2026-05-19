from __future__ import annotations

import reflex as rx

from ..styles import (
    CARD_STYLE,
    FOCUS_VISIBLE_STYLE,
    GREEN,
    GREEN_DARK,
    GREEN_SOFT,
    INTERACTIVE_TRANSITION,
    STEP_PENDING,
    STEPPER_TRACK_BG,
    STEP_VISITED_BG,
    STEP_VISITED_TEXT,
)


def metric_card(title: str, value, subtitle: str = "") -> rx.Component:
    return rx.box(
        rx.text(title, color="#64748b", size="2"),
        rx.heading(value, size="8", color=GREEN),
        #rx.cond(bool(subtitle), rx.text(subtitle, size="2", color="#94a3b8")),
        rx.cond(subtitle, rx.text(subtitle, size="2", color="#94a3b8")),
        **CARD_STYLE,
        width="100%",
    )


def section_card(title: str, description: str, on_click=None, active=False, icon_tag: str = "list_checks") -> rx.Component:
    return rx.button(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag=icon_tag, size=16, color=rx.cond(active, GREEN_DARK, "#64748b")),
                    rx.text(title, font_weight="700", color=rx.cond(active, GREEN_DARK, "#0f172a")),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.cond(
                    active,
                    rx.badge("Actual", color_scheme="green", variant="soft"),
                ),
                width="100%",
                align="center",
            ),
            rx.text(description, size="2", color="#475569"),
            align="start",
            spacing="2",
            width="100%",
        ),
        on_click=on_click,
        width="100%",
        height="100%",
        min_height="110px",
        justify="start",
        padding="1rem",
        white_space="normal",
        bg=rx.cond(active, GREEN_SOFT, "white"),
        color="#0f172a",
        border=rx.cond(active, f"2px solid {GREEN}", "1px solid #e2e8f0"),
        border_radius="16px",
        transition=INTERACTIVE_TRANSITION,
        _hover={"bg": "#f8fafc"},
        _focus_visible=FOCUS_VISIBLE_STYLE,
        box_shadow=rx.cond(active, "0 8px 20px rgba(34, 197, 94, 0.12)", "none"),
    )


def workflow_step_chip(
    step_number: int,
    title: str,
    status: str = "pending",
    on_click=None,
) -> rx.Component:
    is_current = status == "current"
    is_visited = status == "visited"
    return rx.button(
        rx.hstack(
            rx.box(
                step_number,
                width="26px",
                height="26px",
                border_radius="999px",
                display="flex",
                align_items="center",
                justify_content="center",
                font_weight="700",
                font_size="0.8rem",
                bg=rx.cond(is_current, GREEN, rx.cond(is_visited, STEP_VISITED_BG, "white")),
                color=rx.cond(is_current, "white", rx.cond(is_visited, STEP_VISITED_TEXT, STEP_PENDING)),
                border=rx.cond(is_current, f"1px solid {GREEN}", "1px solid #cbd5e1"),
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(title, font_weight=rx.cond(is_current, "700", "600"), size="2"),
                rx.text(
                    rx.cond(is_current, "Actual", rx.cond(is_visited, "Recorrido", "Pendiente")),
                    size="1",
                    color=rx.cond(is_current, GREEN_DARK, rx.cond(is_visited, STEP_VISITED_TEXT, STEP_PENDING)),
                    text_transform="uppercase",
                    letter_spacing="0.06em",
                ),
                spacing="0",
                align="start",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        on_click=on_click,
        variant="ghost",
        justify="start",
        width="240px",
        min_width="240px",
        border_radius="12px",
        border=rx.cond(is_current, f"1px solid {GREEN}", "1px solid transparent"),
        bg=rx.cond(is_current, GREEN_SOFT, STEPPER_TRACK_BG),
        transition=INTERACTIVE_TRANSITION,
        _hover={"bg": "#eef2f7"},
        _focus_visible=FOCUS_VISIBLE_STYLE,
        padding="0.5rem 0.6rem",
    )


def workflow_step_card(
    step_number: int,
    title: str,
    description: str,
    status: str = "pending",
    on_click=None,
    icon_tag: str = "list_checks",
) -> rx.Component:
    is_current = status == "current"
    is_visited = status == "visited"
    return rx.button(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        tag=icon_tag,
                        size=16,
                        color=rx.cond(is_current, GREEN_DARK, rx.cond(is_visited, STEP_VISITED_TEXT, "#64748b")),
                    ),
                    rx.text(f"{step_number}. {title}", font_weight="700"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.badge(
                    rx.cond(is_current, "Actual", rx.cond(is_visited, "Recorrido", "Pendiente")),
                    variant="soft",
                    color_scheme=rx.cond(is_current, "green", "gray"),
                ),
                width="100%",
                align="center",
            ),
            rx.text(description, size="2", color="#475569"),
            align="start",
            spacing="2",
            width="100%",
        ),
        on_click=on_click,
        width="100%",
        min_height="112px",
        justify="start",
        padding="1rem",
        white_space="normal",
        bg=rx.cond(is_current, GREEN_SOFT, rx.cond(is_visited, STEPPER_TRACK_BG, "white")),
        color="#0f172a",
        border=rx.cond(is_current, f"2px solid {GREEN}", "1px solid #e2e8f0"),
        border_radius="16px",
        transition=INTERACTIVE_TRANSITION,
        _hover={"bg": "#f8fafc"},
        _focus_visible=FOCUS_VISIBLE_STYLE,
        box_shadow=rx.cond(is_current, "0 8px 20px rgba(34, 197, 94, 0.12)", "none"),
    )
