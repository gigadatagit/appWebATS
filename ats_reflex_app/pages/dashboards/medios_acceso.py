from __future__ import annotations

import reflex as rx

from ...components.dashboards.sst_dashboard import sst_dashboard_content
from ...state import SSTAnalyticsState
from ...template import protected_page


@rx.page(
    route="/sst/dashboard/medios-acceso",
    title="Dashboard Medios de Acceso | SST",
    on_load=SSTAnalyticsState.load_medios_acceso_dashboard,
)
def medios_acceso_dashboard_page() -> rx.Component:
    return protected_page(
        "Dashboard medios de acceso",
        sst_dashboard_content(),
        subtitle="Analitica de listas de chequeo asociadas a permisos de alturas.",
        current_route="/sst/dashboard/medios-acceso",
    )
