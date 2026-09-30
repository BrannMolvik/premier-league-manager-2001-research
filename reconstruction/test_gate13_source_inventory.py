import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from gate13_source_inventory import (
    EXPECTED_BGROUND_PATH,
    ISO9660_SECTOR_BYTES,
    MODE1_RAW_SECTOR_BYTES,
    MODE1_SYNC,
    candidate_reason,
    catalog_iso_image,
    convert_mode1_2352_to_iso,
    inventory_iso_image,
    inventory_zip,
    is_mode1_2352_image,
    load_explicit_path_file,
    normalize_member,
    parse_7z_slt,
    report_for_source,
)

from test_iso9660_reader import build_joliet_iso


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


    @staticmethod
    def _mode1_sector(payload: bytes, mode: int = 1) -> bytes:
        if len(payload) != ISO9660_SECTOR_BYTES:
            raise ValueError("payload must be exactly one ISO sector")
        header = MODE1_SYNC + b"\x00\x02\x00" + bytes([mode])
        tail = b"\x00" * (MODE1_RAW_SECTOR_BYTES - len(header) - len(payload))
        return header + payload + tail

    def test_mode1_2352_conversion_extracts_exact_2048_payloads(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            raw = root / "game.bin"
            iso = root / "game.iso"
            first = bytes((index % 251 for index in range(ISO9660_SECTOR_BYTES)))
            second = bytes(((index + 17) % 251 for index in range(ISO9660_SECTOR_BYTES)))
            raw.write_bytes(self._mode1_sector(first) + self._mode1_sector(second))

            self.assertTrue(is_mode1_2352_image(raw))
            sectors = convert_mode1_2352_to_iso(raw, iso)

            self.assertEqual(sectors, 2)
            self.assertEqual(iso.read_bytes(), first + second)

    def test_mode1_2352_conversion_rejects_non_mode1_sector(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            raw = root / "game.bin"
            iso = root / "game.iso"
            payload = b"X" * ISO9660_SECTOR_BYTES
            raw.write_bytes(
                self._mode1_sector(payload)
                + self._mode1_sector(payload, mode=2)
            )

            self.assertTrue(is_mode1_2352_image(raw))
            with self.assertRaises(ValueError):
                convert_mode1_2352_to_iso(raw, iso)

    def test_builtin_iso_reader_inventories_and_extracts_candidate(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            payload = build_joliet_iso(iso)
            out = root / "out"

            catalog = catalog_iso_image(iso)
            records, warnings = inventory_iso_image(iso, out)

            self.assertEqual(warnings, [])
            self.assertEqual(
                [(record.path, record.size) for record in catalog],
                [("FM2001_Art/Generic/bground.444", len(payload))],
            )
            self.assertEqual(
                [record.path for record in records],
                ["FM2001_Art/Generic/bground.444"],
            )
            self.assertEqual(records[0].source_layer, "iso9660-extracted")
            self.assertEqual(records[0].sha256, __import__("hashlib").sha256(payload).hexdigest())
            self.assertEqual(
                (out / "FM2001_Art" / "Generic" / "bground.444").read_bytes(),
                payload,
            )

    def test_deep_zip_mode1_inventory_no_longer_requires_7zip(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            build_joliet_iso(iso)
            iso_bytes = iso.read_bytes()
            raw = b"".join(
                self._mode1_sector(
                    iso_bytes[offset:offset + ISO9660_SECTOR_BYTES]
                )
                for offset in range(0, len(iso_bytes), ISO9660_SECTOR_BYTES)
            )
            archive = root / "source.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("disc/game.bin", raw)

            report = report_for_source(archive, deep=True)

            self.assertEqual(report["nested_disc_images"], ["disc/game.bin"])
            self.assertEqual(report["disc_file_count"], 1)
            self.assertEqual(
                [record["path"] for record in report["disc_files"]],
                ["FM2001_Art/Generic/bground.444"],
            )
            self.assertEqual(report["disc_files"][0]["size"], len(b"\x20\x03\x58\x02gate13-joliet"))
            self.assertGreater(report["disc_files"][0]["extent"], 0)
            self.assertEqual(
                [record["path"] for record in report["candidates"]],
                ["FM2001_Art/Generic/bground.444"],
            )
            self.assertEqual(
                report["candidates"][0]["source_layer"],
                "iso9660-listing",
            )
            self.assertTrue(
                any("MODE1/2352" in warning for warning in report["warnings"])
            )
            self.assertFalse(
                any("7-Zip was not found" in warning for warning in report["warnings"])
            )

    def test_explicit_opaque_iso_path_can_be_selected_and_extracted(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            payload = build_joliet_iso(iso)
            out = root / "out"

            records, warnings = inventory_iso_image(
                iso,
                out,
                {"FM2001_Art/Generic/bground.444"},
            )

            self.assertEqual(warnings, [])
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].candidate_reason, "explicit-path")
            self.assertEqual(
                (out / "FM2001_Art" / "Generic" / "bground.444").read_bytes(),
                payload,
            )

    def test_report_records_explicit_paths_for_reproducibility(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            build_joliet_iso(iso)

            report = report_for_source(
                iso,
                explicit_paths={"FM2001_Art/Generic/bground.444"},
            )

            self.assertEqual(
                report["explicit_paths"],
                ["FM2001_Art/Generic/bground.444"],
            )
            self.assertEqual(
                report["candidates"][0]["candidate_reason"],
                "explicit-path",
            )

    def test_only_explicit_stages_no_other_heuristic_candidates(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            payload = build_joliet_iso(iso)
            selected = root / "selected"
            none = root / "none"

            records, warnings = inventory_iso_image(
                iso, selected,
                {"FM2001_Art/Generic/bground.444"},
                only_explicit=True,
            )
            self.assertEqual(warnings, [])
            self.assertEqual([item.path for item in records],
                             ["FM2001_Art/Generic/bground.444"])
            self.assertEqual((selected / "FM2001_Art/Generic/bground.444").read_bytes(), payload)

            records, _ = inventory_iso_image(
                iso, none, {"Unrelated/unknown.dat"}, only_explicit=True
            )
            self.assertEqual(records, [])
            self.assertFalse(none.exists())

    def test_only_explicit_requires_a_nonempty_selection(self):
        with tempfile.TemporaryDirectory() as temp_name:
            iso = Path(temp_name) / "fixture.iso"
            build_joliet_iso(iso)
            with self.assertRaisesRegex(ValueError, "requires at least one"):
                report_for_source(iso, only_explicit=True)

    def test_only_explicit_report_retains_catalog_but_limits_candidates(self):
        with tempfile.TemporaryDirectory() as temp_name:
            iso = Path(temp_name) / "fixture.iso"
            build_joliet_iso(iso)
            report = report_for_source(
                iso, explicit_paths={"Unrelated/unknown.dat"},
                only_explicit=True,
            )
            self.assertEqual(report["disc_file_count"], 1)
            self.assertEqual(report["candidates"], [])
            self.assertTrue(report["only_explicit"])
            self.assertTrue(any("Explicit disc path was not found" in x
                                for x in report["warnings"]))

    def test_missing_explicit_disc_path_warns(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            iso = root / "fixture.iso"
            build_joliet_iso(iso)

            report = report_for_source(
                iso,
                explicit_paths={"FM2001_Art/Unknown/layout.bin"},
            )

            self.assertTrue(
                any(
                    "Explicit disc path was not found: FM2001_Art/Unknown/layout.bin"
                    in warning
                    for warning in report["warnings"]
                )
            )

    def test_explicit_path_file_ignores_comments_and_normalizes(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "paths.txt"
            path.write_text(
                "# selected Gate 13 resources\n"
                "\\FM2001_Art\\Generic\\bground.444\n"
                "\n"
                "Data/UI/PStartMenu.dat\n",
                encoding="utf-8",
            )

            paths = load_explicit_path_file(path)

            self.assertEqual(
                paths,
                {
                    "FM2001_Art/Generic/bground.444",
                    "Data/UI/PStartMenu.dat",
                },
            )

    def test_mode1_detector_rejects_nonintegral_or_bad_sync_image(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            nonintegral = root / "short.bin"
            nonintegral.write_bytes(b"not-a-sector")
            self.assertFalse(is_mode1_2352_image(nonintegral))

            bad_sync = root / "bad.bin"
            bad_sync.write_bytes(b"\x00" * MODE1_RAW_SECTOR_BYTES)
            self.assertFalse(is_mode1_2352_image(bad_sync))


if __name__ == "__main__":
    unittest.main()
