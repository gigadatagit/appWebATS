from __future__ import annotations

import unittest
from pathlib import Path

from ats_reflex_app.state.session_state import SessionState


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NavigationRouteTests(unittest.TestCase):
    def setUp(self):
        self.state = SessionState(_reflex_internal_init=True)

    def test_authenticated_home_routes_admin_to_dashboard(self):
        self.state.current_user_role_codigo = " ADMIN "

        self.assertEqual(self.state._resolve_authenticated_home_route(), "/sst/dashboard")

    def test_authenticated_home_routes_siso_to_documents(self):
        self.state.current_user_role_codigo = " siso "

        self.assertEqual(self.state._resolve_authenticated_home_route(), "/sst/documentos")

    def test_authenticated_home_routes_future_roles_to_documents(self):
        self.state.current_user_role_codigo = "AUDITOR"

        self.assertEqual(self.state._resolve_authenticated_home_route(), "/sst/documentos")

    def test_legacy_ats_form_route_depends_on_authentication(self):
        self.assertEqual(self.state._resolve_legacy_ats_form_route(), "/login")

        self.state.is_authenticated = True

        self.assertEqual(self.state._resolve_legacy_ats_form_route(), "/sst/documentos")

    def test_sidebar_does_not_expose_ats_form(self):
        source = (PROJECT_ROOT / "ats_reflex_app" / "components" / "sidebar.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn('sidebar_link("Formato ATS"', source)
        self.assertNotIn('sidebar_link("Formato ATS", "/ats/formato"', source)

    def test_public_ats_card_routes_to_documents(self):
        source = (
            PROJECT_ROOT / "ats_reflex_app" / "components" / "landing_home.py"
        ).read_text(encoding="utf-8")

        ats_card = source[source.index('"ATS",') : source.index('"Preoperacionales",')]
        self.assertIn('"/sst/documentos"', ats_card)
        self.assertNotIn('"/ats/formato"', ats_card)

    def test_legacy_ats_page_only_renders_redirect_feedback(self):
        source = (PROJECT_ROOT / "ats_reflex_app" / "pages" / "ats_form.py").read_text(
            encoding="utf-8"
        )
        page_source = source[source.index('@rx.page(route="/ats/formato"') :]

        self.assertIn("SessionState.redirect_legacy_ats_form", page_source)
        self.assertNotIn("AtsFormState.load_initial_data", page_source)
        self.assertNotIn("section_selector()", page_source)
        self.assertNotIn("current_section()", page_source)


if __name__ == "__main__":
    unittest.main()
