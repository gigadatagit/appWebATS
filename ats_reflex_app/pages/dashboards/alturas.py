from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(
    route="/sst/dashboard/alturas",
    title="Dashboard Alturas | SST",
    on_load=SSTAnalyticsState.load_alturas_dashboard,
)
def alturas_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard trabajo en alturas",
        sst_dashboard_content(),
        subtitle="Analitica de permisos de trabajo seguro en alturas.",
        current_route="/sst/dashboard/alturas",
    )
