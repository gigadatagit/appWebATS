from __future__ import annotations

from dataclasses import dataclass

from ..sst_formats import SST_FORMATS, SSTFormat, get_sst_format, template_exists


@dataclass(frozen=True)
class DocumentFormatConfig:
    code: str
    name: str
    template_path: str
    storage_prefix: str
    generation_enabled: bool
    main_table: str
    document_table: str
    document_parent_column: str
    header_code: str
    header_version: str
    header_effective_date: str


DOCUMENT_FORMAT_CONFIGS: tuple[DocumentFormatConfig, ...] = tuple(
    DocumentFormatConfig(
        code=item.code,
        name=item.name,
        template_path=item.template_path,
        storage_prefix=item.code.lower(),
        generation_enabled=item.document_generation_enabled,
        main_table=item.main_table,
        document_table=item.document_table,
        document_parent_column=item.document_parent_column,
        header_code=item.header_code,
        header_version=item.header_version,
        header_effective_date=item.header_effective_date,
    )
    for item in SST_FORMATS
)


def get_document_format_config(code: str) -> DocumentFormatConfig | None:
    item: SSTFormat | None = get_sst_format(code)
    if item is None:
        return None
    return DocumentFormatConfig(
        code=item.code,
        name=item.name,
        template_path=item.template_path,
        storage_prefix=item.code.lower(),
        generation_enabled=item.document_generation_enabled and template_exists(item.code),
        main_table=item.main_table,
        document_table=item.document_table,
        document_parent_column=item.document_parent_column,
        header_code=item.header_code,
        header_version=item.header_version,
        header_effective_date=item.header_effective_date,
    )
