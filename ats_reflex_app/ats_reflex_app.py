from __future__ import annotations

import reflex as rx

from .config import get_database_url, is_sqlite_url
from .db_bootstrap import ensure_database
from . import models  # noqa: F401
from .pages import home, login, ats_form, ats_documentos, admin_dashboard  # noqa: F401

if is_sqlite_url(get_database_url()):
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
