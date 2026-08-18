from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(
    route="/sst/dashboard/preoperacionales",
    title="Dashboard Preoperacionales | SST",
    on_load=SSTAnalyticsState.load_preoperacionales_dashboard,
)
def preoperacionales_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard preoperacionales",
        sst_dashboard_content(),
        subtitle="Analitica de inspecciones preoperacionales de maquinaria.",
        current_route="/sst/dashboard/preoperacionales",
    )
