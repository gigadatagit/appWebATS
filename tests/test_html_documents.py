from __future__ import annotations

import base64
import unittest
from unittest.mock import patch

from ats_reflex_app.access_control import AuthContext
from ats_reflex_app.services.documentos import html_documents
from ats_reflex_app.services.documentos.html_documents import (
    GeneratedDocument,
    RenderedHtml,
    _base_context,
    generate_and_store_document,
    render_document_html,
    resolve_asset_data_uri,
    resolve_signature_data_uri,
)
from ats_reflex_app.storage_supabase import upload_html_bytes


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)
PNG_BASE64 = base64.b64encode(PNG_BYTES).decode("ascii")


def minimal_context(format_code: str, code: str = "DOC-UNIT-001") -> dict:
    return _base_context(
        format_code,
        {
            "id": 1,
            "codigo_publico": code,
            "ats_codigo_publico": "ATS-UNIT-001",
            "fecha_elaboracion": "2026-01-01",
            "fecha_inspeccion": "2026-01-01",
            "actividad": "Actividad de prueba",
            "observaciones": "Observacion <script>alert(1)</script>",
        },
    )


class HtmlRenderTests(unittest.TestCase):
    def test_minimal_ats_render_is_complete_and_escaped(self):
        context = minimal_context("ATS", "ATS-UNIT-001")

        rendered = render_document_html("ATS", context)
        text = rendered.html_bytes.decode("utf-8")

        self.assertIn("<!DOCTYPE html>", text)
        self.assertIn("ATS-UNIT-001", text)
        self.assertNotIn("{{", text)
        self.assertNotIn("{%", text)
        self.assertNotIn("<script>", text.lower())
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", text)

    def test_dynamic_ats_render_preserves_rows_and_signatures(self):
        context = minimal_context("ATS", "ATS-DYNAMIC-001")
        context["peligros"] = [
            {"numero_visual": 1, "nombre": "Caida", "descripcion_otro": ""},
            {"numero_visual": 2, "nombre": "Corte", "descripcion_otro": "Bordes"},
        ]
        context["pasos"] = [
            {
                "numero": 1,
                "descripcion": "Paso uno",
                "peligros": [
                    {
                        "numero": 1,
                        "nombre": "Caida",
                        "detalle": "",
                        "controles": ["Arnes", "Linea de vida"],
                    }
                ],
            },
            {
                "numero": 2,
                "descripcion": "Paso dos",
                "peligros": [
                    {
                        "numero": 2,
                        "nombre": "Corte",
                        "detalle": "Bordes",
                        "controles": ["Guantes anticorte"],
                    }
                ],
            },
        ]
        context["trabajadores"] = [
            {
                "numero_orden": 1,
                "nombre": "Ana Perez",
                "tipo_identificacion": "CC",
                "documento": "123",
                "cargo": "Operaria",
                "firma_base64": PNG_BASE64,
            },
            {
                "numero_orden": 2,
                "nombre": "Luis Gomez",
                "tipo_identificacion": "CC",
                "documento": "456",
                "cargo": "Supervisor",
                "firma_base64": "",
            },
        ]
        context["firmas"] = [
            {
                "tipo_codigo": "AUTORIZA",
                "tipo_nombre": "Autoriza",
                "nombre": "Coordinador",
                "cedula": "",
                "cargo": "SISO",
                "celular": "",
                "matricula": "",
                "firma_base64": f"data:image/png;base64,{PNG_BASE64}",
            }
        ]

        rendered = render_document_html("ATS", context)
        text = rendered.html_bytes.decode("utf-8")

        self.assertLess(text.index("Paso uno"), text.index("Paso dos"))
        self.assertIn("Arnes", text)
        self.assertIn("Linea de vida", text)
        self.assertIn("Guantes anticorte", text)
        self.assertIn("Ana Perez", text)
        self.assertIn("Luis Gomez", text)
        self.assertGreaterEqual(text.count("class=\"signature-image\""), 2)

    def test_all_templates_smoke_render(self):
        cases = [
            "ATS",
            "TRABAJO_ALTURAS",
            "TRABAJO_CALIENTE",
            "ENERGIAS_PELIGROSAS",
            "MEDIO_ACCESO",
            "PREOPERACIONAL_MAQUINARIA",
        ]
        for format_code in cases:
            with self.subTest(format_code=format_code):
                context = minimal_context(format_code, f"{format_code}-001")
                if format_code == "PREOPERACIONAL_MAQUINARIA":
                    context["general"]["maquina_nombre_snapshot"] = "Pulidora"
                    context["general"]["maquina_imagen_asset_path_snapshot"] = "maquinas/pulidora.png"
                if format_code == "MEDIO_ACCESO":
                    context["general"]["medio_acceso_nombre_snapshot"] = "Escalera"
                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")
                self.assertIn(f"{format_code}-001", text)
                self.assertNotIn("{{", text)
                self.assertNotIn("<script", text.lower())

    def test_checklist_templates_render_nonempty_items(self):
        cases = [
            "TRABAJO_ALTURAS",
            "TRABAJO_CALIENTE",
            "ENERGIAS_PELIGROSAS",
            "MEDIO_ACCESO",
            "PREOPERACIONAL_MAQUINARIA",
        ]
        for format_code in cases:
            with self.subTest(format_code=format_code):
                context = minimal_context(format_code, f"{format_code}-CHECKLIST-001")
                context["checklist_secciones"] = [
                    {
                        "codigo": "GENERAL",
                        "nombre": "Seccion de checklist de prueba",
                        "items": [
                            {
                                "numero_orden": 1,
                                "pregunta": "Elemento verificado en prueba",
                                "respuesta": "N/A",
                                "observacion": "Observacion de checklist de prueba",
                                "descripcion_otro": "",
                                "ayuda_texto": "",
                            }
                        ],
                    }
                ]

                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")

                self.assertIn("Seccion de checklist de prueba", text)
                self.assertIn("Elemento verificado en prueba", text)
                self.assertIn('<span class="check">X</span> N/A', text)
                self.assertIn("Observacion de checklist de prueba", text)
                self.assertNotIn("{{", text)
                self.assertNotIn("<script", text.lower())

    def test_section_titles_are_centered_globally(self):
        context = minimal_context("ATS", "ATS-CENTERED-TITLES-001")

        rendered = render_document_html("ATS", context)
        text = rendered.html_bytes.decode("utf-8")

        self.assertRegex(text, r"\.section-title\s*\{[^}]*text-align:\s*center;")

    def test_operational_templates_use_start_and_close_dates_without_inspection_date(self):
        cases = [
            "PREOPERACIONAL_MAQUINARIA",
            "TRABAJO_ALTURAS",
            "MEDIO_ACCESO",
            "ENERGIAS_PELIGROSAS",
            "TRABAJO_CALIENTE",
        ]
        for format_code in cases:
            with self.subTest(format_code=format_code):
                context = minimal_context(format_code, f"{format_code}-DATES-001")
                context["general"]["fecha_inicial"] = "2030-04-05"
                context["general"]["fecha_cierre"] = "2030-04-06"
                if format_code == "PREOPERACIONAL_MAQUINARIA":
                    context["general"]["maquina_nombre_snapshot"] = "Pulidora"
                if format_code == "MEDIO_ACCESO":
                    context["general"]["medio_acceso_nombre_snapshot"] = "Escalera"

                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")

                self.assertIn("Fecha de inicio / cierre", text)
                self.assertIn("2030-04-05 / 2030-04-06", text)
                self.assertNotIn("Fecha inspección", text)

    def test_document_warnings_are_retained_but_not_rendered_inside_html(self):
        context = minimal_context("ATS", "ATS-HIDDEN-WARNINGS-001")
        context["firmas"] = [
            {
                "tipo_codigo": "AUTORIZA",
                "tipo_nombre": "Autoriza",
                "nombre": "Responsable",
                "cedula": "",
                "cargo": "",
                "celular": "",
                "matricula": "",
                "firma_base64": "not-base64",
            }
        ]

        rendered = render_document_html("ATS", context)
        text = rendered.html_bytes.decode("utf-8")

        self.assertTrue(any("Base64" in warning for warning in rendered.warnings))
        self.assertNotIn("Advertencias de integridad documental", text)
        self.assertNotIn("La firma Base64 es invalida", text)
        self.assertNotIn('aria-label="Advertencias documentales"', text)

    def test_closure_templates_render_only_the_applicable_branch(self):
        cases = [
            ("TRABAJO_ALTURAS", "coordinador_cierre_firma_base64", "Firma coordinador cierre"),
            ("ENERGIAS_PELIGROSAS", "personal_sst_cierre_firma_base64", "Firma Personal SST"),
            ("TRABAJO_CALIENTE", "emisor_cierre_firma_base64", "Firma emisor cierre"),
        ]
        for format_code, closure_signature_key, closure_signature_label in cases:
            with self.subTest(format_code=format_code, branch="suspension"):
                context = minimal_context(format_code, f"{format_code}-SUSPENSION-001")
                context["cierre"] = {
                    "hubo_suspension": True,
                    "fecha_suspension": "2030-05-01",
                    "hora_suspension": "10:15",
                    "razones_suspension": "MOTIVO-SUSPENSION-PRUEBA",
                    "suspende_nombre": "RESPONSABLE-SUSPENSION",
                    "suspende_cargo": "Supervisor",
                    "suspende_firma_base64": PNG_BASE64,
                    "hora_cierre_real": "23:59",
                    closure_signature_key: PNG_BASE64,
                }

                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")

                self.assertIn('<div class="section-title">Suspensión</div>', text)
                self.assertIn("MOTIVO-SUSPENSION-PRUEBA", text)
                self.assertIn("Firma de suspensión", text)
                self.assertNotIn('<div class="section-title">Cierre</div>', text)
                self.assertNotIn("Hora de cierre real", text)
                self.assertNotIn(closure_signature_label, text)

            with self.subTest(format_code=format_code, branch="closure"):
                context = minimal_context(format_code, f"{format_code}-CLOSURE-001")
                context["cierre"] = {
                    "hubo_suspension": False,
                    "fecha_suspension": "2030-05-01",
                    "hora_suspension": "10:15",
                    "razones_suspension": "MOTIVO-SUSPENSION-OCULTO",
                    "suspende_nombre": "RESPONSABLE-SUSPENSION-OCULTO",
                    "suspende_firma_base64": PNG_BASE64,
                    "hora_cierre_real": "23:59",
                    closure_signature_key: PNG_BASE64,
                }

                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")

                self.assertIn('<div class="section-title">Cierre</div>', text)
                self.assertIn("Hora de cierre real", text)
                self.assertIn("23:59", text)
                self.assertIn(closure_signature_label, text)
                self.assertNotIn('<div class="section-title">Suspensión</div>', text)
                self.assertNotIn("MOTIVO-SUSPENSION-OCULTO", text)
                self.assertNotIn("Firma de suspensión", text)

    def test_closure_branch_without_signature_renders_placeholder(self):
        for format_code in ("TRABAJO_ALTURAS", "ENERGIAS_PELIGROSAS", "TRABAJO_CALIENTE"):
            with self.subTest(format_code=format_code):
                context = minimal_context(format_code, f"{format_code}-NO-CLOSURE-SIGNATURE-001")
                context["cierre"] = {"hubo_suspension": False, "hora_cierre_real": "17:30"}

                rendered = render_document_html(format_code, context)
                text = rendered.html_bytes.decode("utf-8")

                self.assertIn('<div class="section-title">Cierre</div>', text)
                self.assertIn("Firma no registrada", text)


class ResourceTests(unittest.TestCase):
    def test_rejects_unsafe_asset_path(self):
        result = resolve_asset_data_uri("../README.md")
        self.assertFalse(result.available)
        self.assertIn("salir del directorio assets", result.warning)

    def test_rejects_false_mime_asset(self):
        result = resolve_asset_data_uri("templates/README.md")
        self.assertFalse(result.available)
        self.assertIn("no es una imagen", result.warning)

    def test_rejects_corrupt_signature_base64(self):
        result = resolve_signature_data_uri("not-base64")
        self.assertFalse(result.available)
        self.assertIn("Base64", result.warning)

    def test_missing_required_logo_blocks_render(self):
        context = minimal_context("ATS", "ATS-NO-LOGO")
        with patch.object(html_documents, "LOGO_ASSET_PATH", "brand/no-existe.png"):
            with self.assertRaises(RuntimeError):
                render_document_html("ATS", context)


class FakeUploadBucket:
    def __init__(self, calls: list[dict]):
        self.calls = calls

    def upload(self, *, path, file, file_options):
        self.calls.append({"path": path, "file": file, "file_options": file_options})
        return {"path": path}


class FakeStorage:
    def __init__(self, calls: list[dict]):
        self.calls = calls

    def from_(self, bucket):
        self.calls.append({"bucket": bucket})
        return FakeUploadBucket(self.calls)


class FakeClient:
    def __init__(self, calls: list[dict]):
        self.storage = FakeStorage(calls)


class StorageTests(unittest.TestCase):
    def test_upload_html_uses_utf8_mime_and_no_upsert(self):
        calls: list[dict] = []
        with patch("ats_reflex_app.storage_supabase._build_service_supabase_client", return_value=FakeClient(calls)):
            path = upload_html_bytes("ATS-001/v1/ATS-001_v1.html", b"<!DOCTYPE html>")

        self.assertEqual(path, "ATS-001/v1/ATS-001_v1.html")
        upload_call = calls[-1]
        self.assertEqual(upload_call["file_options"]["content-type"], "text/html; charset=utf-8")
        self.assertEqual(upload_call["file_options"]["x-upsert"], "false")


class FakeScalarResult:
    def __init__(self, value=None):
        self.value = value

    def first(self):
        return None

    def scalar_one(self):
        return self.value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, *, fail_insert: bool = False):
        self.fail_insert = fail_insert
        self.committed = False
        self.rolled_back = False
        self.statements: list[str] = []
        self.params: list[dict] = []

    def get_bind(self):
        class Dialect:
            name = "sqlite"

        class Bind:
            dialect = Dialect()

        return Bind()

    def execute(self, statement, params=None):
        sql = str(statement)
        self.statements.append(sql)
        self.params.append(dict(params or {}))
        if "COALESCE(MAX(version)" in sql:
            return FakeScalarResult(0)
        if "INSERT INTO" in sql:
            if self.fail_insert:
                raise RuntimeError("insert failed")
            return FakeScalarResult(55)
        if "SELECT id FROM public.ats_estado" in sql:
            return FakeScalarResult(7)
        return FakeScalarResult(None)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class GenerateAndStoreTests(unittest.TestCase):
    def test_generate_uses_html_version_one_independent_from_old_documents(self):
        session = FakeSession()
        auth = AuthContext("auth", 10, "ADMIN", True)
        rendered = RenderedHtml(
            html_bytes=b"<!DOCTYPE html><html><body>ATS-GEN-001</body></html>",
            record_code="ATS-GEN-001",
            warnings=(),
        )
        with patch.object(html_documents, "build_document_context", return_value={}), patch.object(
            html_documents, "render_document_html", return_value=rendered
        ), patch.object(html_documents, "upload_html_bytes") as upload_mock:
            generated = generate_and_store_document(session, "ATS", 99, auth)

        self.assertIsInstance(generated, GeneratedDocument)
        self.assertEqual(generated.version, 1)
        self.assertEqual(generated.file_name, "ATS-GEN-001_v1.html")
        self.assertEqual(generated.storage_path, "ATS-GEN-001/v1/ATS-GEN-001_v1.html")
        upload_mock.assert_called_once_with(
            storage_path="ATS-GEN-001/v1/ATS-GEN-001_v1.html",
            html_bytes=rendered.html_bytes,
        )
        self.assertTrue(session.committed)
        self.assertFalse(session.rolled_back)
        self.assertTrue(any("UPPER(COALESCE(tipo_documento, '')) = 'HTML'" in sql for sql in session.statements))

    def test_uploaded_object_is_deleted_when_registering_fails(self):
        session = FakeSession(fail_insert=True)
        auth = AuthContext("auth", 10, "ADMIN", True)
        rendered = RenderedHtml(
            html_bytes=b"<!DOCTYPE html><html><body>ATS-ROLLBACK-001</body></html>",
            record_code="ATS-ROLLBACK-001",
            warnings=(),
        )
        with patch.object(html_documents, "build_document_context", return_value={}), patch.object(
            html_documents, "render_document_html", return_value=rendered
        ), patch.object(html_documents, "upload_html_bytes"), patch.object(
            html_documents, "delete_file_if_exists"
        ) as delete_mock, patch.object(html_documents.logger, "exception"):
            with self.assertRaises(RuntimeError):
                generate_and_store_document(session, "ATS", 99, auth)

        self.assertTrue(session.rolled_back)
        delete_mock.assert_called_once_with("ATS-ROLLBACK-001/v1/ATS-ROLLBACK-001_v1.html")


if __name__ == "__main__":
    unittest.main()
