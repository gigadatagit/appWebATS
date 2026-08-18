from __future__ import annotations

import reflex as rx

from ...components.documentos.sst_documentos import documentos_sst_content
from ...state import SSTDocumentsState
from ...template import protected_page


@rx.page(route="/sst/documentos", title="Documentos SST", on_load=SSTDocumentsState.load_documents_page_data)
def sst_documentos_page() -> rx.Component:
    return protected_page(
        "Documentos SST",
        documentos_sst_content(),
        subtitle="Historial documental consolidado por formato SST.",
        current_route="/sst/documentos",
    )
