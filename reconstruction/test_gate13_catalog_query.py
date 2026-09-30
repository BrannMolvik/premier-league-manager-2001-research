import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate13_catalog_query import main, query_disc_files, summarize_disc_files


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
