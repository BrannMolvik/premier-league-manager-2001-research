"""Tests for deterministic FastView resource path resolution."""
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
    require_unique_fastview_resources,
    resolve_fastview_resources,
    resolved_paths,
)


def complete_report() -> dict:
    disc_files = []
    for index, target in enumerate(reversed(TARGETS), start=1):
        disc_files.append(
            {
                "path": f"FM2001_Art/FastView/{target.basename}",
                "size": index * 10,
                "extent": 100 + index,
            }
        )
    return {
        "source_sha256": "source",
        "disc_files": disc_files,
        "candidates": [
            {
                "path": "fm2001_art/fastview/TEAM_BAR_1.444",
                "sha256": "a" * 64,
            }
        ],
    }


class Gate14FastViewResourceCatalogTests(unittest.TestCase):
    def test_all_persisted_targets_resolve_by_exact_basename_only(self):
        catalog = resolve_fastview_resources(complete_report())

        self.assertEqual(catalog["resource_count"], 7)
        self.assertEqual(catalog["resolved_count"], 7)
        self.assertTrue(catalog["all_paths_uniquely_resolved"])
        self.assertEqual(
            [item["basename"] for item in catalog["resources"]],
            [target.basename for target in TARGETS],
        )
        self.assertEqual(
            catalog["resources"][0]["resolved"]["path"],
            "FM2001_Art/FastView/team_bar_1.444",
        )
        self.assertEqual(catalog["resources"][0]["resolved"]["sha256"], "a" * 64)

    def test_substring_or_different_extension_does_not_count_as_match(self):
        report = complete_report()
        report["disc_files"] = [
            item
            for item in report["disc_files"]
            if not item["path"].endswith("pitch_left.444")
        ]
        report["disc_files"].extend(
            [
                {"path": "Other/not_pitch_left.444", "size": 1, "extent": 1},
                {"path": "Other/pitch_left.pcx", "size": 1, "extent": 2},
            ]
        )

        catalog = resolve_fastview_resources(report)

        left = next(
            item for item in catalog["resources"]
            if item["basename"] == "pitch_left.444"
        )
        self.assertEqual(left["status"], "missing")
        self.assertEqual(left["matches"], [])

    def test_duplicate_basename_in_two_directories_is_ambiguous_and_fails_closed(self):
        report = complete_report()
        report["disc_files"].append(
            {
                "path": "Duplicate/team_bar_2.444",
                "size": 99,
                "extent": 999,
            }
        )

        catalog = resolve_fastview_resources(report)
        target = next(
            item for item in catalog["resources"]
            if item["basename"] == "team_bar_2.444"
        )

        self.assertEqual(target["status"], "ambiguous")
        self.assertEqual(len(target["matches"]), 2)
        with self.assertRaisesRegex(ValueError, "team_bar_2.444=ambiguous"):
            require_unique_fastview_resources(catalog)

    def test_missing_target_fails_closed_for_exact_path_staging(self):
        report = complete_report()
        report["disc_files"] = report["disc_files"][:-1]
        catalog = resolve_fastview_resources(report)

        self.assertFalse(catalog["all_paths_uniquely_resolved"])
        with self.assertRaises(ValueError):
            resolved_paths(catalog)

    def test_fidelity_boundary_does_not_claim_geometry_orientation_or_thresholds(self):
        catalog = resolve_fastview_resources(complete_report())
        boundary = catalog["fidelity_boundary"]

        self.assertTrue(boundary["component_ownership_recovered"])
        self.assertTrue(boundary["asset_basenames_recovered"])
        self.assertFalse(boundary["layout_geometry_recovered"])
        self.assertFalse(boundary["side0_screen_orientation_recovered"])
        self.assertFalse(boundary["territory_thresholds_recovered"])

    def test_cli_paths_only_emits_deterministic_target_order(self):
        with tempfile.TemporaryDirectory() as temp_name:
            report_path = Path(temp_name) / "report.json"
            report_path.write_text(json.dumps(complete_report()), encoding="utf-8")
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
            [
                f"FM2001_Art/FastView/{target.basename}"
                for target in TARGETS
            ],
        )


if __name__ == "__main__":
    unittest.main()
