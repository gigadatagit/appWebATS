from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(
    route="/sst/dashboard/energias-peligrosas",
    title="Dashboard Energias Peligrosas | SST",
    on_load=SSTAnalyticsState.load_energias_dashboard,
)
def energias_peligrosas_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard energias peligrosas",
        sst_dashboard_content(),
        subtitle="Analitica de permisos para energias peligrosas y controles asociados.",
        current_route="/sst/dashboard/energias-peligrosas",
    )
