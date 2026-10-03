"""Tests for exact source-proven FastView resource path resolution."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate14_fastview_resource_catalog import (
    TARGETS,
    main,
    require_source_resolved_fastview_resources,
    resolve_fastview_resources,
    resolved_paths,
)


def complete_report() -> dict:
    disc_files = []
    candidates = []
    for index, target in enumerate(reversed(TARGETS), start=1):
        disc_files.append(
            {
                "path": target.source_path,
                "size": target.size_bytes,
                "extent": 100 + index,
            }
        )
        candidates.append({"path": target.source_path, "sha256": target.sha256})
    return {
        "source_sha256": "source",
        "disc_files": disc_files,
        "candidates": candidates,
    }


class Gate14FastViewResourceCatalogTests(unittest.TestCase):
    def test_all_source_proven_targets_resolve_by_exact_full_path(self):
        catalog = resolve_fastview_resources(complete_report())

        self.assertEqual(catalog["schema_version"], 2)
        self.assertEqual(catalog["resource_count"], 11)
        self.assertEqual(catalog["resolved_count"], 11)
        self.assertTrue(catalog["all_paths_source_resolved"])
        self.assertEqual(
            [item["source_path"] for item in catalog["resources"]],
            [target.source_path for target in TARGETS],
        )
        first = catalog["resources"][0]["resolved"]
        self.assertEqual(first["path"], TARGETS[0].source_path)
        self.assertEqual(first["observed_sha256"], TARGETS[0].sha256)
        self.assertEqual(
            first["executable_string_va"], TARGETS[0].executable_string_va
        )

    def test_team_bars_are_fastview_team_not_possession_figures(self):
        bars = TARGETS[:3]
        self.assertEqual([item.component for item in bars], ["FastViewTeam"] * 3)
        self.assertTrue(all("not a PossessionFigures control" in item.proven_role for item in bars))

    def test_team_name_grids_are_exact_fastview_team_targets(self):
        grids = TARGETS[3:7]
        self.assertEqual(
            [item.basename for item in grids],
            [
                "team_name_grid.444",
                "team_name_grid_2.444",
                "team_name_grid_3.444",
                "team_name_grid_4.444",
            ],
        )
        self.assertEqual([item.component for item in grids], ["FastViewTeam"] * 4)
        self.assertTrue(all(item.width == 259 and item.height == 16 for item in grids))

    def test_duplicate_pitch_normal_basename_does_not_ambiguate_exact_fastview_path(self):
        report = complete_report()
        report["disc_files"].append(
            {
                "path": "FM2001_Art/Generic/match_report/pitch_normal.444",
                "size": 15932,
                "extent": 999,
            }
        )
        catalog = resolve_fastview_resources(report)
        normal = next(
            item
            for item in catalog["resources"]
            if item["basename"] == "pitch_normal.444"
        )

        self.assertEqual(normal["status"], "resolved")
        self.assertEqual(
            normal["resolved"]["path"],
            "FM2001_Art/FastView/pitch_normal.444",
        )
        self.assertEqual(
            normal["basename_matches"],
            [
                "FM2001_Art/FastView/pitch_normal.444",
                "FM2001_Art/Generic/match_report/pitch_normal.444",
            ],
        )

    def test_same_basename_elsewhere_cannot_substitute_for_missing_source_path(self):
        report = complete_report()
        target = TARGETS[-1]
        report["disc_files"] = [
            item
            for item in report["disc_files"]
            if item["path"] != target.source_path
        ]
        report["disc_files"].append(
            {
                "path": "FM2001_Art/Generic/match_report/pitch_normal.444",
                "size": target.size_bytes,
                "extent": 999,
            }
        )

        catalog = resolve_fastview_resources(report)
        normal = catalog["resources"][-1]
        self.assertEqual(normal["status"], "missing")
        with self.assertRaisesRegex(ValueError, "pitch_normal.444=missing"):
            require_source_resolved_fastview_resources(catalog)

    def test_size_or_observed_hash_mismatch_fails_closed(self):
        report = complete_report()
        report["disc_files"][0]["size"] += 1
        catalog = resolve_fastview_resources(report)
        self.assertEqual(catalog["resources"][-1]["status"], "size_mismatch")

        report = complete_report()
        target = TARGETS[0]
        report["candidates"] = [
            {**item, "sha256": "0" * 64}
            if item["path"] == target.source_path
            else item
            for item in report["candidates"]
        ]
        catalog = resolve_fastview_resources(report)
        self.assertEqual(catalog["resources"][0]["status"], "hash_mismatch")

    def test_fidelity_boundary_does_not_claim_timing_or_side_orientation(self):
        catalog = resolve_fastview_resources(complete_report())
        boundary = catalog["fidelity_boundary"]
        self.assertTrue(boundary["exact_source_paths_source_proven"])
        self.assertTrue(boundary["possession_figures_bar_association_rejected"])
        self.assertFalse(boundary["layout_geometry_recovered"])
        self.assertFalse(boundary["side0_screen_orientation_recovered"])
        self.assertFalse(boundary["territory_update_cadence_recovered"])

    def test_cli_paths_only_emits_deterministic_target_order(self):
        with tempfile.TemporaryDirectory() as temp_name:
            report_path = Path(temp_name) / "report.json"
            report_path.write_text(
                json.dumps(complete_report()), encoding="utf-8"
            )
            output = io.StringIO()
            with patch(
                "sys.argv",
                [
                    "gate14_fastview_resource_catalog.py",
                    str(report_path),
                    "--paths-only",
                ],
            ):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)

        self.assertEqual(
            output.getvalue().splitlines(),
            [target.source_path for target in TARGETS],
        )


if __name__ == "__main__":
    unittest.main()
