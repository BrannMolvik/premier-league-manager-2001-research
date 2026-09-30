import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate13_catalog_query import (
    main,
    query_disc_files,
    query_source_files,
    summarize_disc_files,
    summarize_source_files,
)


REPORT = {
    "disc_files": [
        {"path": "FM2001_Art/Generic/bground.444", "size": 100, "extent": 20},
        {"path": "FM2001_Art/Buttons/start.pcx", "size": 200, "extent": 21},
        {"path": "Data/UI/PStartMenu.dat", "size": 300, "extent": 22},
        {"path": "Language/English.str", "size": 400, "extent": 23},
        {"path": "FMV/premintro.tgq", "size": 500, "extent": 24},
    ]
}


class Gate13CatalogQueryTests(unittest.TestCase):
    def test_contains_filters_case_insensitively(self):
        matches = query_disc_files(REPORT, contains=["pstart", "ui"])
        self.assertEqual(
            [item["path"] for item in matches],
            ["Data/UI/PStartMenu.dat"],
        )

    def test_suffix_and_top_level_filters_can_combine(self):
        matches = query_disc_files(
            REPORT,
            suffixes=["pcx", ".444"],
            top_level=["fm2001_art"],
        )
        self.assertEqual(
            [item["path"] for item in matches],
            [
                "FM2001_Art/Buttons/start.pcx",
                "FM2001_Art/Generic/bground.444",
            ],
        )

    def test_regex_can_find_opaque_screen_or_string_leads(self):
        matches = query_disc_files(
            REPORT,
            regex=r"(startmenu|english\.str)$",
        )
        self.assertEqual(
            [item["path"] for item in matches],
            ["Language/English.str"],
        )

    def test_paths_only_cli_emits_source_relative_paths(self):
        with tempfile.TemporaryDirectory() as temp_name:
            report_path = Path(temp_name) / "report.json"
            report_path.write_text(json.dumps(REPORT), encoding="utf-8")
            output = io.StringIO()
            with patch(
                "sys.argv",
                [
                    "gate13_catalog_query.py",
                    str(report_path),
                    "--contains",
                    "fm2001_art",
                    "--paths-only",
                ],
            ):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)

            self.assertEqual(
                output.getvalue().splitlines(),
                [
                    "FM2001_Art/Buttons/start.pcx",
                    "FM2001_Art/Generic/bground.444",
                ],
            )

    def test_source_query_includes_outer_zip_and_nested_disc_with_layers(self):
        mixed = {
            **REPORT,
            "zip_files": [
                {"path": "UI/LoosePanel.dat", "size": 5, "is_disc_image": False},
                {"path": "disc/source.bin", "size": 20, "is_disc_image": True},
            ],
        }
        matches = query_source_files(mixed, suffixes=["dat"])
        self.assertEqual(
            [(item["path"], item["source_layer"]) for item in matches],
            [
                ("Data/UI/PStartMenu.dat", "disc"),
                ("UI/LoosePanel.dat", "zip"),
            ],
        )
        self.assertEqual(
            [item["path"] for item in query_source_files(mixed, layer="zip")],
            ["disc/source.bin", "UI/LoosePanel.dat"],
        )
        summary = summarize_source_files(mixed)
        self.assertEqual(summary["disc"]["disc_file_count"], 5)
        self.assertEqual(summary["zip"]["zip_file_count"], 2)
        self.assertEqual(summary["zip"]["nested_disc_image_count"], 1)

    def test_paths_only_from_mixed_report_lists_both_layers_once(self):
        mixed = {
            "disc_files": [{"path": "UI/DiscPanel.dat", "extent": 18, "size": 1}],
            "zip_files": [{"path": "UI/LoosePanel.dat", "is_disc_image": False, "size": 2}],
        }
        with tempfile.TemporaryDirectory() as temp_name:
            report_path = Path(temp_name) / "mixed.json"
            report_path.write_text(json.dumps(mixed), encoding="utf-8")
            output = io.StringIO()
            with patch("sys.argv", [
                "gate13_catalog_query.py", str(report_path),
                "--suffix", "dat", "--paths-only",
            ]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)
            self.assertEqual(output.getvalue().splitlines(), [
                "UI/DiscPanel.dat", "UI/LoosePanel.dat",
            ])

    def test_duplicate_path_across_archive_layers_fails_closed_for_staging(self):
        mixed = {
            "disc_files": [{"path": "UI/Panel.dat", "extent": 18, "size": 1}],
            "zip_files": [{"path": "ui/panel.dat", "is_disc_image": False, "size": 2}],
        }
        with tempfile.TemporaryDirectory() as temp_name:
            report_path = Path(temp_name) / "mixed.json"
            report_path.write_text(json.dumps(mixed), encoding="utf-8")
            with patch("sys.argv", [
                "gate13_catalog_query.py", str(report_path), "--paths-only"
            ]):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as failed:
                        main()
            self.assertEqual(failed.exception.code, 2)

    def test_legacy_disc_only_report_remains_queryable(self):
        self.assertEqual(
            len(query_source_files(REPORT, suffixes=[".444"])), 1
        )
        self.assertEqual(summarize_source_files(REPORT)["zip"]["zip_file_count"], 0)

    def test_summary_counts_roots_and_suffixes(self):
        summary = summarize_disc_files(REPORT)
        self.assertEqual(summary["disc_file_count"], 5)
        self.assertEqual(
            summary["top_level_counts"],
            {"Data": 1, "FM2001_Art": 2, "FMV": 1, "Language": 1},
        )
        self.assertEqual(summary["suffix_counts"][".444"], 1)
        self.assertEqual(summary["suffix_counts"][".pcx"], 1)
        self.assertEqual(summary["suffix_counts"][".dat"], 1)
        self.assertEqual(summary["suffix_counts"][".str"], 1)
        self.assertEqual(summary["suffix_counts"][".tgq"], 1)


if __name__ == "__main__":
    unittest.main()
