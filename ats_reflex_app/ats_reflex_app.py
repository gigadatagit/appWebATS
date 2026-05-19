from __future__ import annotations

import reflex as rx

from .db_bootstrap import ensure_database
from . import models  # noqa: F401
from .pages import login, ats_form, ats_documentos, admin_dashboard  # noqa: F401

ensure_database()

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        scaling="100%",
        accent_color="green",
    ),
)
