from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class SSTFormat:
    code: str
    name: str
    short_name: str
    dashboard_route: str
    icon: str
    summary_view: str
    main_table: str
    document_table: str
    document_parent_column: str
    template_path: str
    header_code: str
    header_version: str
    header_effective_date: str
    document_generation_enabled: bool = True


SST_FORMATS: tuple[SSTFormat, ...] = (
    SSTFormat(
        code="ATS",
        name="Analisis de Trabajo Seguro",
        short_name="ATS",
        dashboard_route="/admin/dashboard",
        icon="clipboard_check",
        summary_view="vw_sst_ats_resumen",
        main_table="ats",
        document_table="ats_documento",
        document_parent_column="ats_id",
        template_path="templates/ats/template.html",
        header_code="FO-ATS-12",
        header_version="Original",
        header_effective_date="05/01/2026",
    ),
    SSTFormat(
        code="PREOPERACIONAL_MAQUINARIA",
        name="Preoperacional de maquinaria",
        short_name="Preoperacionales",
        dashboard_route="/sst/dashboard/preoperacionales",
        icon="tractor",
        summary_view="vw_sst_preoperacional_maquinaria_resumen",
        main_table="preoperacional_maquinaria",
        document_table="preoperacional_maquinaria_documento",
        document_parent_column="preoperacional_maquinaria_id",
        template_path="templates/preoperacional_maquinaria/template.html",
        header_code="FO-PPS-11",
        header_version="Original",
        header_effective_date="02/01/2025",
    ),
    SSTFormat(
        code="TRABAJO_ALTURAS",
        name="Permiso de trabajo en alturas",
        short_name="Alturas",
        dashboard_route="/sst/dashboard/alturas",
        icon="mountain",
        summary_view="vw_sst_permiso_alturas_resumen",
        main_table="permiso_trabajo_alturas",
        document_table="permiso_trabajo_alturas_documento",
        document_parent_column="permiso_trabajo_alturas_id",
        template_path="templates/trabajo_alturas/template.html",
        header_code="MZ-TSA-10",
        header_version="Original",
        header_effective_date="02/05/2023",
    ),
    SSTFormat(
        code="MEDIO_ACCESO",
        name="Lista de chequeo de medios de acceso",
        short_name="Medios de acceso",
        dashboard_route="/sst/dashboard/medios-acceso",
        icon="waves_ladder",
        summary_view="vw_sst_lista_medio_acceso_resumen",
        main_table="lista_chequeo_medio_acceso",
        document_table="lista_chequeo_medio_acceso_documento",
        document_parent_column="lista_chequeo_medio_acceso_id",
        template_path="templates/medios_acceso/template.html",
        header_code="MZ-TSA-10",
        header_version="Original",
        header_effective_date="02/05/2023",
    ),
    SSTFormat(
        code="ENERGIAS_PELIGROSAS",
        name="Permiso de energias peligrosas",
        short_name="Energias",
        dashboard_route="/sst/dashboard/energias-peligrosas",
        icon="zap",
        summary_view="vw_sst_permiso_energias_resumen",
        main_table="permiso_trabajo_energias_peligrosas",
        document_table="permiso_trabajo_energias_peligrosas_documento",
        document_parent_column="permiso_trabajo_energias_peligrosas_id",
        template_path="templates/energias_peligrosas/template.html",
        header_code="MZ-HTRE-11",
        header_version="Original",
        header_effective_date="02/05/2024",
    ),
    SSTFormat(
        code="TRABAJO_CALIENTE",
        name="Permiso de trabajo seguro en caliente",
        short_name="Trabajo caliente",
        dashboard_route="/sst/dashboard/trabajo-caliente",
        icon="flame",
        summary_view="vw_sst_permiso_caliente_resumen",
        main_table="permiso_trabajo_caliente",
        document_table="permiso_trabajo_caliente_documento",
        document_parent_column="permiso_trabajo_caliente_id",
        template_path="templates/trabajo_caliente/template.html",
        header_code="FO-PTC-10",
        header_version="Original",
        header_effective_date="01/01/2025",
    ),
)

SST_FORMAT_BY_CODE: dict[str, SSTFormat] = {item.code: item for item in SST_FORMATS}


def get_sst_format(code: str) -> SSTFormat | None:
    return SST_FORMAT_BY_CODE.get(str(code or "").strip().upper())


def sst_format_options(include_all: bool = True) -> list[dict]:
    options: list[dict] = []
    if include_all:
        options.append({"id": "TODOS", "label": "Todos los formatos"})
    options.extend({"id": item.code, "label": item.short_name} for item in SST_FORMATS)
    return options


def template_exists(format_code: str) -> bool:
    item = get_sst_format(format_code)
    if item is None:
        return False
    return (PROJECT_ROOT / item.template_path).is_file()
