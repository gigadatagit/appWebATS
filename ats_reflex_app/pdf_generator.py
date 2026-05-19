from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from typing import Any


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 40
LINE_HEIGHT = 14
FONT_SIZE = 10
MAX_CHARS_PER_LINE = 105
MAX_LINES_PER_PAGE = 52


def _safe_text(value: Any) -> str:
    text = str(value or "").strip()
    return " ".join(text.split())


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_line(line: str) -> list[str]:
    raw = _safe_text(line)
    if raw == "":
        return [""]
    return wrap(raw, width=MAX_CHARS_PER_LINE, replace_whitespace=False, drop_whitespace=False) or [raw]


def _build_lines(context: dict[str, Any]) -> list[str]:
    ats = context.get("ats", {})
    apoyos = context.get("apoyos", [])
    certificados = context.get("certificados", [])
    peligros = context.get("peligros", [])
    pasos = context.get("pasos", [])
    trabajadores = context.get("trabajadores", [])
    firmas_finales = context.get("firmas_finales", [])

    lines: list[str] = []
    lines.append("FORMATO ATS - DOCUMENTO GENERADO")
    lines.append("")
    lines.append(f"Codigo ATS: {_safe_text(ats.get('codigo_publico'))}")
    lines.append(f"Empresa/Persona: {_safe_text(ats.get('empresa_persona_ejecuta'))}")
    lines.append(f"Fecha elaboracion: {_safe_text(ats.get('fecha_elaboracion'))}")
    lines.append(f"Ciudad: {_safe_text(ats.get('ciudad'))}")
    lines.append(f"Area/Lugar: {_safe_text(ats.get('area_lugar'))}")
    lines.append(f"Numero ATS: {_safe_text(ats.get('numero_ats'))}")
    lines.append(f"Tipo ATS: {_safe_text(ats.get('tipo_ats'))}")
    lines.append(f"Duracion actividad: {_safe_text(ats.get('duracion_actividad'))}")
    lines.append(f"Actividad alto riesgo: {_safe_text(ats.get('actividad_alto_riesgo'))}")
    lines.append("")
    lines.append("Descripcion de la actividad:")
    lines.extend(_wrap_line(_safe_text(ats.get("descripcion_actividad"))))
    lines.append("")

    lines.append("Informacion de apoyo:")
    if apoyos:
        for item in apoyos:
            nombre = _safe_text(item.get("nombre"))
            extra = _safe_text(item.get("descripcion_otro"))
            suffix = f" (Otro: {extra})" if extra else ""
            lines.extend(_wrap_line(f"- {nombre}{suffix}"))
    else:
        lines.append("- Sin datos")
    lines.append("")

    lines.append("Certificados asociados:")
    if certificados:
        for item in certificados:
            nombre = _safe_text(item.get("nombre"))
            extra = _safe_text(item.get("descripcion_otro"))
            suffix = f" (Otro: {extra})" if extra else ""
            lines.extend(_wrap_line(f"- {nombre}{suffix}"))
    else:
        lines.append("- Sin datos")
    lines.append("")

    lines.append("Peligros y riesgos identificados:")
    if peligros:
        for item in peligros:
            numero = _safe_text(item.get("numero_visual"))
            nombre = _safe_text(item.get("nombre"))
            extra = _safe_text(item.get("descripcion_otro"))
            suffix = f" (Detalle: {extra})" if extra else ""
            lines.extend(_wrap_line(f"- P{numero} - {nombre}{suffix}"))
    else:
        lines.append("- Sin datos")
    lines.append("")

    lines.append("Paso a paso de la actividad:")
    if pasos:
        for paso in pasos:
            numero = _safe_text(paso.get("numero_paso"))
            lines.append(f"Paso {numero}")
            lines.extend(_wrap_line(f"  Descripcion: {_safe_text(paso.get('descripcion_paso'))}"))
            lines.extend(_wrap_line(f"  Peligros asociados: {_safe_text(paso.get('peligros_asociados'))}"))
            lines.extend(
                _wrap_line(
                    f"  Controles: {_safe_text(paso.get('controles_aplicados'))}"
                )
            )
            lines.append("")
    else:
        lines.append("- Sin datos")
        lines.append("")

    lines.append("Trabajadores relacionados:")
    if trabajadores:
        for item in trabajadores:
            nombre = _safe_text(item.get("nombre_trabajador"))
            documento = _safe_text(item.get("numero_documento"))
            cargo = _safe_text(item.get("cargo_trabajador"))
            firma = "SI" if _safe_text(item.get("firma_base64")) else "NO"
            lines.extend(_wrap_line(f"- {nombre} | Doc: {documento} | Cargo: {cargo} | Firma: {firma}"))
    else:
        lines.append("- Sin datos")
    lines.append("")

    lines.append("Observaciones:")
    lines.extend(_wrap_line(_safe_text(context.get("observaciones"))))
    lines.append("")

    lines.append("Firmas finales:")
    if firmas_finales:
        for item in firmas_finales:
            tipo = _safe_text(item.get("firma_tipo_nombre"))
            nombre = _safe_text(item.get("nombre_completo"))
            cargo = _safe_text(item.get("cargo"))
            firma = "SI" if _safe_text(item.get("firma_base64")) else "NO"
            lines.extend(_wrap_line(f"- {tipo}: {nombre} | Cargo: {cargo} | Firma: {firma}"))
    else:
        lines.append("- Sin datos")

    return lines


def _paginate(lines: list[str]) -> list[list[str]]:
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        wrapped = _wrap_line(line)
        for chunk in wrapped:
            if len(current) >= MAX_LINES_PER_PAGE:
                pages.append(current)
                current = []
            current.append(chunk)
    if current:
        pages.append(current)
    return pages or [["Documento sin contenido"]]


def _page_stream(lines: list[str]) -> bytes:
    y = PAGE_HEIGHT - MARGIN
    commands = [
        "BT",
        f"/F1 {FONT_SIZE} Tf",
        f"{LINE_HEIGHT} TL",
        f"1 0 0 1 {MARGIN} {y} Tm",
    ]
    for line in lines:
        commands.append(f"({_escape_pdf_text(line)}) Tj")
        commands.append("T*")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1", errors="replace")


def generate_ats_pdf(context: dict[str, Any], output_path: Path) -> Path:
    lines = _build_lines(context)
    pages = _paginate(lines)
    streams = [_page_stream(page_lines) for page_lines in pages]

    object_bytes: dict[int, bytes] = {}
    object_id = 1

    catalog_id = object_id
    object_id += 1
    pages_id = object_id
    object_id += 1
    font_id = object_id
    object_id += 1

    page_ids: list[int] = []
    content_ids: list[int] = []
    for _ in streams:
        page_ids.append(object_id)
        object_id += 1
        content_ids.append(object_id)
        object_id += 1

    object_bytes[catalog_id] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    object_bytes[pages_id] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode("ascii")
    object_bytes[font_id] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    for page_id, content_id, stream in zip(page_ids, content_ids, streams, strict=True):
        object_bytes[page_id] = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        object_bytes[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"\nendstream"
        )

    output = bytearray()
    output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    max_object = max(object_bytes.keys())
    for idx in range(1, max_object + 1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode("ascii"))
        output.extend(object_bytes[idx])
        output.extend(b"\nendobj\n")

    xref_pos = len(output)
    output.extend(f"xref\n0 {max_object + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for idx in range(1, max_object + 1):
        output.extend(f"{offsets[idx]:010d} 00000 n \n".encode("ascii"))

    output.extend(
        (
            f"trailer\n<< /Size {max_object + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        ).encode("ascii")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(output))
    return output_path
