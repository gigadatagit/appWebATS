from __future__ import annotations

import unittest

from ats_reflex_app.state.dashboard_state import DashboardState
from ats_reflex_app.state.sst_analytics_state import SSTAnalyticsState
from ats_reflex_app.styles import DASHBOARD_GREEN_DARK, DASHBOARD_GREEN_LIGHT, DASHBOARD_GREEN_SCALE


class DashboardGreenPaletteTests(unittest.TestCase):
    def test_sst_charts_use_only_the_shared_green_scale(self):
        rows = [{"label": f"Formato {index}", "total": index} for index in range(len(DASHBOARD_GREEN_SCALE))]

        colored_rows = SSTAnalyticsState._apply_palette(rows)

        self.assertEqual([row["fill"] for row in colored_rows], list(DASHBOARD_GREEN_SCALE))
        self.assertNotIn("#0284c7", DASHBOARD_GREEN_SCALE)
        self.assertNotIn("#7c3aed", DASHBOARD_GREEN_SCALE)

    def test_shared_gradient_exposes_dark_and_light_endpoints(self):
        self.assertEqual(DASHBOARD_GREEN_DARK, DASHBOARD_GREEN_SCALE[0])
        self.assertEqual(DASHBOARD_GREEN_LIGHT, DASHBOARD_GREEN_SCALE[-1])
        self.assertGreaterEqual(len(set(DASHBOARD_GREEN_SCALE)), 6)

        pie_rows = DashboardState._build_alto_riesgo_pie(alto=8, no_alto=3)
        self.assertEqual([row["fill"] for row in pie_rows], [DASHBOARD_GREEN_DARK, DASHBOARD_GREEN_LIGHT])


if __name__ == "__main__":
    unittest.main()
