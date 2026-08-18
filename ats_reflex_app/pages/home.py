from __future__ import annotations

import reflex as rx

from ..components.landing_home import landing_page
from ..state import SessionState


@rx.page(route="/", title="Inicio | SST", on_load=SessionState.redirect_authenticated_home)
def home_page() -> rx.Component:
    return landing_page()
