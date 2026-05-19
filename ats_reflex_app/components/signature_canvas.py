from __future__ import annotations

from typing import Any

import reflex as rx


class SignatureCanvas(rx.NoSSRComponent):
    """Wrapper for react-signature-canvas."""

    library = "react-signature-canvas"
    tag = "SignatureCanvas"
    is_default = True

    pen_color: rx.Var[str]
    background_color: rx.Var[str]
    canvas_props: rx.Var[dict[str, Any]]
    clear_on_resize: rx.Var[bool]

    on_end: rx.EventHandler[lambda: []]


signature_canvas = SignatureCanvas.create
