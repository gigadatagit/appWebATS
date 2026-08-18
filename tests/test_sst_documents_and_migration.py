from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from ats_reflex_app.access_control import AuthContext
from ats_reflex_app.services.analytics_sst import SSTDashboardFilters, _build_registros_where
from ats_reflex_app.services.documentos.html_documents import fetch_generation_candidates


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeMappingsResult:
    def __init__(self, rows: list[dict]):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class RecordingSession:
    def __init__(self, rows: list[dict]):
        self.rows = rows
        self.statements: list[str] = []
        self.params: list[dict] = []

    def execute(self, statement, params=None):
        self.statements.append(str(statement))
        self.params.append(dict(params or {}))
        return FakeMappingsResult(self.rows)


class DashboardCloseDateMigrationTests(unittest.TestCase):
    def test_migration_targets_all_close_date_dashboard_views(self):
        migration = (PROJECT_ROOT / "sql" / "03_dashboard_fecha_cierre.sql").read_text(
            encoding="utf-8"
        )
        expected_targets = {
            "vw_sst_preoperacional_maquinaria_resumen": "pm",
            "vw_sst_permiso_alturas_resumen": "pta",
            "vw_sst_lista_medio_acceso_resumen": "lc",
            "vw_sst_permiso_energias_resumen": "ptep",
            "vw_sst_permiso_caliente_resumen": "ptc",
        }

        self.assertIn("BEGIN;", migration)
        self.assertIn("COMMIT;", migration)
        self.assertIn("CREATE OR REPLACE VIEW public.%I", migration)
        self.assertIn("fecha_cierre AS fecha_principal", migration)
        self.assertNotIn("vw_sst_ats_resumen", migration)
        for view_name, source_alias in expected_targets.items():
            self.assertIn(f"('{view_name}', '{source_alias}')", migration)

    def test_migration_is_guarded_for_first_and_repeated_execution(self):
        migration = (PROJECT_ROOT / "sql" / "03_dashboard_fecha_cierre.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("to_regclass", migration)
        self.assertIn("pg_get_viewdef", migration)
        self.assertIn("IF current_definition ~*", migration)
        self.assertIn("CONTINUE;", migration)
        self.assertIn("fecha_inspeccion", migration)

    def test_dashboard_date_range_filters_the_migrated_principal_date(self):
        where_sql, params = _build_registros_where(
            SSTDashboardFilters(
                fecha_inicio=date(2026, 8, 1),
                fecha_fin=date(2026, 8, 31),
                selected_format_code="ENERGIAS_PELIGROSAS",
            ),
            current_user_id=10,
            role_code="ADMIN",
        )

        self.assertIn("r.fecha_principal >= :fecha_inicio", where_sql)
        self.assertIn("r.fecha_principal <= :fecha_fin", where_sql)
        self.assertEqual(params["fecha_inicio"], date(2026, 8, 1))
        self.assertEqual(params["fecha_fin"], date(2026, 8, 31))


class SearchableGenerationRecordTests(unittest.TestCase):
    def test_generation_search_includes_location_and_returns_structured_candidate(self):
        session = RecordingSession(
            [
                {
                    "registro_id": 31,
                    "codigo_publico": "ELE-031",
                    "ats_codigo_publico": "ATS-004",
                    "fecha_principal": "2026-08-18",
                    "actividad": "Bloqueo electrico",
                    "ubicacion": "Subestacion norte",
                }
            ]
        )
        auth = AuthContext("auth", 10, "ADMIN", True)

        rows = fetch_generation_candidates(
            session,
            auth_context=auth,
            format_code="ENERGIAS_PELIGROSAS",
            search_query="subestacion",
        )

        self.assertIn("LOWER(COALESCE(r.ubicacion, '')) LIKE :term", session.statements[0])
        self.assertEqual(session.params[0]["term"], "%subestacion%")
        self.assertEqual(
            rows[0]["label"],
            "ELE-031 | 2026-08-18 | Bloqueo electrico | Subestacion norte",
        )
        self.assertEqual(rows[0]["fecha_principal"], "2026-08-18")
        self.assertEqual(rows[0]["actividad"], "Bloqueo electrico")
        self.assertEqual(rows[0]["ubicacion"], "Subestacion norte")


class UnifiedDocumentsRouteTests(unittest.TestCase):
    def test_legacy_ats_route_only_redirects_to_sst_documents(self):
        legacy_page = (
            PROJECT_ROOT / "ats_reflex_app" / "pages" / "ats_documentos.py"
        ).read_text(encoding="utf-8")
        state_source = (
            PROJECT_ROOT / "ats_reflex_app" / "state" / "sst_documents_state.py"
        ).read_text(encoding="utf-8")

        self.assertIn("redirect_legacy_ats_documents", legacy_page)
        self.assertNotIn("documentos_sst_content", legacy_page)
        self.assertIn('rx.redirect("/sst/documentos")', state_source)

    def test_generation_card_has_no_duplicate_open_or_download_buttons(self):
        component_source = (
            PROJECT_ROOT
            / "ats_reflex_app"
            / "components"
            / "documentos"
            / "sst_documentos.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn('"Abrir HTML"', component_source)
        self.assertNotIn('"Descargar HTML"', component_source)
        self.assertIn('_link_button("Abrir"', component_source)
        self.assertIn('_link_button("Descargar"', component_source)
        self.assertIn("rx.popover.root", component_source)
        self.assertIn("rx.popover.content", component_source)
        self.assertIn("rx.popover.close", component_source)
        self.assertIn("_generation_candidate_option", component_source)
        self.assertNotIn("datalist", component_source)
        self.assertNotIn("ats_compat", component_source)

    def test_combobox_state_tracks_and_clears_structured_selection(self):
        state_source = (
            PROJECT_ROOT / "ats_reflex_app" / "state" / "sst_documents_state.py"
        ).read_text(encoding="utf-8")

        self.assertIn("selected_record_code", state_source)
        self.assertIn("selected_record_label", state_source)
        self.assertIn("generation_search_error", state_source)
        self.assertIn("select_generation_candidate", state_source)
        self.assertNotIn("_candidate_id_for_label", state_source)


if __name__ == "__main__":
    unittest.main()
