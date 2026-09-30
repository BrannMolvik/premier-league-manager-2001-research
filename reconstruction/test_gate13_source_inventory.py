import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from gate13_source_inventory import (
    EXPECTED_BGROUND_PATH,
    candidate_reason,
    inventory_zip,
    normalize_member,
    parse_7z_slt,
    report_for_source,
)


class Gate13SourceInventoryTests(unittest.TestCase):
    def test_normalizes_disc_style_separators(self):
        self.assertEqual(
            normalize_member(r"\\FM2001_Art\\Generic\\bground.444"),
            "FM2001_Art/Generic/bground.444",
        )

    def test_known_background_is_always_candidate(self):
        self.assertEqual(
            candidate_reason(EXPECTED_BGROUND_PATH),
            "known-gate13-path",
        )

    def test_generic_directory_is_inventoried_without_guessing_names(self):
        self.assertEqual(
            candidate_reason("FM2001_Art/Generic/opaque_resource.444"),
            "generic-front-end-directory",
        )

    def test_direct_zip_candidate_is_hashed_and_nested_image_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "source.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "FM2001_Art/Generic/menu-logo.png",
                    b"menu-logo",
                )
                archive.writestr("disc/game.iso", b"not-a-real-image")

            records, nested, warnings = inventory_zip(path)

        self.assertEqual([record.path for record in records], [
            "FM2001_Art/Generic/menu-logo.png"
        ])
        self.assertEqual(records[0].size, len(b"menu-logo"))
        self.assertIsNotNone(records[0].sha256)
        self.assertEqual(nested, ["disc/game.iso"])
        self.assertEqual(warnings, [])

    def test_zip_with_only_disc_image_marks_deep_inspection_dependency(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "source.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("disc/game.bin", b"disc")

            report = report_for_source(path)

        self.assertEqual(report["source_kind"], "zip")
        self.assertEqual(report["nested_disc_images"], ["disc/game.bin"])
        self.assertEqual(report["candidates"], [])
        self.assertTrue(
            any("nested disc image" in warning for warning in report["warnings"])
        )

    def test_7z_slt_parser_returns_file_records_not_archive_header(self):
        text = """Path = game.iso
Type = Iso
Physical Size = 123

----------
Path = FM2001_Art
Folder = +
Size = 0

Path = FM2001_Art/Generic/bground.444
Size = 42
Packed Size = 42

Path = FMV/PREMINTRO.TGQ
Size = 99
Packed Size = 99
"""
        entries = parse_7z_slt(text)
        self.assertEqual(
            [entry["Path"] for entry in entries],
            [
                "FM2001_Art",
                "FM2001_Art/Generic/bground.444",
                "FMV/PREMINTRO.TGQ",
            ],
        )


if __name__ == "__main__":
    unittest.main()
