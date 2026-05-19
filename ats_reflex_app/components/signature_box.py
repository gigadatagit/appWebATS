from __future__ import annotations

import reflex as rx


def signature_placeholder(label: str = "Firma") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, font_weight="700"),
            rx.box(
                rx.text(
                    "Placeholder del componente de firma. Aquí irá el wrapper React/canvas en la siguiente fase.",
                    text_align="center",
                    color="#475569",
                    font_size="0.9rem",
                ),
                width="100%",
                min_height="160px",
                border="2px dashed #cbd5e1",
                border_radius="14px",
                bg="#f8fafc",
                display="flex",
                align_items="center",
                justify_content="center",
                padding="1rem",
            ),
            align="stretch",
            spacing="2",
            width="100%",
        )
    )
