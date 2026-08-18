from __future__ import annotations

import reflex as rx

from ..styles import (
    BRAND_LOGO_ASSET_PATH,
    BRAND_MARK_STYLE,
    BRAND_SUBTITLE_STYLE,
    BRAND_TITLE_STYLE,
)


def app_brand(
    compact: bool = False,
    show_text: bool = True,
    subtitle: str = "",
    title: str = "GIGATech SST",
    logo_size: str | None = None,
) -> rx.Component:
    resolved_logo_size = logo_size or ("32px" if compact else "40px")
    return rx.hstack(
        rx.box(
            rx.image(
                src=BRAND_LOGO_ASSET_PATH,
                alt="Logo de GIGATech SST",
                width="100%",
                height="100%",
                object_fit="contain",
            ),
            width=resolved_logo_size,
            height=resolved_logo_size,
            **BRAND_MARK_STYLE,
        ),
        rx.cond(
            show_text,
            rx.vstack(
                rx.text(title, **BRAND_TITLE_STYLE),
                rx.cond(subtitle != "", rx.text(subtitle, **BRAND_SUBTITLE_STYLE)),
                spacing="0",
                align="start",
                line_height="1.1",
            ),
        ),
        spacing="2",
        align="center",
    )
