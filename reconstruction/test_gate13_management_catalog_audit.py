import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gate13_management_catalog_audit import audit_management_catalog


class Gate13ManagementCatalogAuditTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "disc_files": [
                {"path": "FM2001_Art/Manager/home_background.444", "size": 100},
                {"path": "FM2001_Art/Squad/player_list_bar.444", "size": 101},
                {"path": "FM2001_Art/Tactics/formation_panel.444", "size": 102},
                {"path": "FM2001_Art/Season/fixtures_result_bar.444", "size": 103},
                {"path": "FM2001_Art/League/league_table_header.444", "size": 104},
                {"path": "FM2001_Art/Players/player_profile_info.444", "size": 105},
                {"path": "FM2001_Art/Transfers/contract_offer.444", "size": 106},
                {"path": "FM2001_Art/Finance/ticket_budget.444", "size": 107},
                {"path": "FM2001_Art/Mail/news_inbox.444", "size": 108},
                {"path": "FM2001_Art/Training/training_panel.444", "size": 109},
                {"path": "FM2001_Art/Scouting/scout_search.444", "size": 110},
                {"path": "FM2001_Art/Staff/youth_support.444", "size": 111},
                {"path": "FM2001_Art/Generic/team_choice/background.444", "size": 112},
                {"path": "FM2001_Art/Unrelated/texture.444", "size": 113},
            ],
            "zip_files": [
                {
                    "path": (
                        "F.A. Premier League Football Manager 2001/"
                        "famg2001.bin"
                    ),
                    "size": 631627248,
                    "is_disc_image": True,
                },
            ],
        }

    def test_groups_path_candidates_without_claiming_ui_binding(self):
        result = audit_management_catalog(self.report)

        groups = {item["surface"]: item for item in result["screen_queries"]}
        self.assertEqual(result["source_layer"], "disc")
        self.assertIn("filename/path discovery only", result["candidate_semantics"])

        expected_fragments = {
            "manager_home": "home_background.444",
            "squad": "player_list_bar.444",
            "tactics_team_selection": "formation_panel.444",
            "fixtures_results": "fixtures_result_bar.444",
            "league_table": "league_table_header.444",
            "player_profile": "player_profile_info.444",
            "transfers": "contract_offer.444",
            "finances": "ticket_budget.444",
            "messages_news": "news_inbox.444",
            "training": "training_panel.444",
            "scouting": "scout_search.444",
            "support_youth_leads": "youth_support.444",
            "main_menu_teamselect_reference": "team_choice/background.444",
        }
        for surface, fragment in expected_fragments.items():
            self.assertIn(surface, groups)
            self.assertFalse(groups[surface]["binding_proven"])
            self.assertTrue(
                any(fragment in row["path"] for row in groups[surface]["matches"]),
                surface,
            )

        every_path = {
            row["path"]
            for group in groups.values()
            for row in group["matches"]
        }
        self.assertNotIn("FM2001_Art/Unrelated/texture.444", every_path)

    def test_default_disc_layer_avoids_outer_wrapper_manager_false_positive(self):
        result = audit_management_catalog(self.report, surfaces=["manager_home"])
        group = result["screen_queries"][0]

        self.assertEqual(group["surface"], "manager_home")
        self.assertEqual(group["candidate_count"], 1)
        self.assertEqual(group["matches"][0]["source_layer"], "disc")
        self.assertEqual(
            group["matches"][0]["path"],
            "FM2001_Art/Manager/home_background.444",
        )

    def test_explicit_both_layers_keeps_outer_layer_visible(self):
        result = audit_management_catalog(
            self.report,
            layer="both",
            surfaces=["manager_home"],
        )
        group = result["screen_queries"][0]

        self.assertEqual(group["candidate_count"], 2)
        self.assertEqual(
            {row["source_layer"] for row in group["matches"]},
            {"disc", "zip"},
        )

    def test_unknown_surface_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown management catalog"):
            audit_management_catalog(self.report, surfaces=["invented_screen"])

    def test_cli_can_limit_to_one_surface(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "source.json"
            report_path.write_text(json.dumps(self.report), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "gate13_management_catalog_audit.py",
                    str(report_path),
                    "--surface",
                    "scouting",
                ],
                cwd=Path(__file__).parent,
                check=True,
                capture_output=True,
                text=True,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(len(payload["screen_queries"]), 1)
        self.assertEqual(payload["screen_queries"][0]["surface"], "scouting")
        self.assertFalse(payload["screen_queries"][0]["binding_proven"])


if __name__ == "__main__":
    unittest.main()
