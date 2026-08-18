from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(route="/sst/dashboard", title="Dashboard SST", on_load=SSTAnalyticsState.load_global_dashboard)
def sst_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard global SST",
        sst_dashboard_content(),
        subtitle="Analitica consolidada de formatos SST, documentos, cierres y origen de captura.",
        current_route="/sst/dashboard",
    )
