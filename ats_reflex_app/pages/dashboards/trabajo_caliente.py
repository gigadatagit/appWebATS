from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(
    route="/sst/dashboard/trabajo-caliente",
    title="Dashboard Trabajo Caliente | SST",
    on_load=SSTAnalyticsState.load_trabajo_caliente_dashboard,
)
def trabajo_caliente_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard trabajo caliente",
        sst_dashboard_content(),
        subtitle="Analitica de permisos de trabajo seguro en caliente.",
        current_route="/sst/dashboard/trabajo-caliente",
    )
