from __future__ import annotations

import reflex as rx

from ..state import SSTDocumentsState


@rx.page(
    route="/ats/documentos",
    title="Documentos ATS",
    on_load=SSTDocumentsState.redirect_legacy_ats_documents,
)
def ats_documentos_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Redirigiendo a Documentos SST...", color="#64748b"),
            spacing="3",
            align="center",
        ),
        min_height="100vh",
        width="100%",
    )
