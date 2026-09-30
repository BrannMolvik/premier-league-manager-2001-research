import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from gate13_source_inventory import (
    EXPECTED_BGROUND_PATH,
    EXPECTED_BGROUND_BYTES,
    ISO9660_SECTOR_BYTES,
    MODE1_RAW_SECTOR_BYTES,
    MODE1_SYNC,
    StagingCollisionError,
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

    def test_rejects_parent_and_drive_prefixed_archive_paths(self):
        with self.assertRaisesRegex(ValueError, "Parent traversal"):
            normalize_member("../outside.bin")
        with self.assertRaisesRegex(ValueError, "Parent traversal"):
            normalize_member(r"Folder\\..\\outside.bin")
        with self.assertRaisesRegex(ValueError, "Drive-prefixed"):
            normalize_member(r"C:\\outside.bin")

    def test_nested_zip_path_traversal_fails_before_staging(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            source = root / "bad-source.zip"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("../../escaped.bin", b"bad")
            with self.assertRaisesRegex(ValueError, "Parent traversal"):
                report_for_source(source, deep=True)
            self.assertFalse((root.parent / "escaped.bin").exists())

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

    def test_loose_zip_exact_only_stages_only_requested_opaque_path(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            archive = root / "source.zip"
            staged = root / "staged"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("UI/OpaquePanel.bin", b"verified-test-only")
                zf.writestr("FM2001_Art/Generic/other.png", b"not-selected")
            report = report_for_source(
                archive,
                explicit_paths={"UI/OpaquePanel.bin"},
                extract_candidates_to=staged,
                only_explicit=True,
            )

            self.assertEqual(report["source_kind"], "zip")
            self.assertEqual(
                [item["path"] for item in report["candidates"]],
                ["UI/OpaquePanel.bin"],
            )
            self.assertEqual(
                report["candidates"][0]["candidate_reason"],
                "explicit-path",
            )
            self.assertEqual(
                report["candidates"][0]["source_layer"],
                "zip-extracted",
            )
            self.assertEqual(
                (staged / "UI/OpaquePanel.bin").read_bytes(),
                b"verified-test-only",
            )
            self.assertFalse(
                (staged / "FM2001_Art/Generic/other.png").exists()
            )
            self.assertFalse(report["warnings"])

    def test_deep_mixed_zip_exact_only_keeps_loose_selection_and_disc_catalog(self):
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
            staged = root / "staged"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("UI/opaque.dat", b"staged-original-fixture")
                zf.writestr("disc/game.bin", raw)
            with patch(
                "gate13_source_inventory.inventory_zip", wraps=inventory_zip
            ) as zip_spy:
                report = report_for_source(
                    archive,
                    deep=True,
                    only_explicit=True,
                    explicit_paths={"UI/opaque.dat"},
                    extract_candidates_to=staged,
                )
            zip_spy.assert_called_once()
            self.assertEqual(report["nested_disc_images"], ["disc/game.bin"])
            self.assertEqual(report["disc_file_count"], 1)
            self.assertEqual(
                [item["path"] for item in report["candidates"]],
                ["UI/opaque.dat"],
            )
            self.assertEqual(
                (staged / "UI/opaque.dat").read_bytes(),
                b"staged-original-fixture",
            )
            self.assertFalse(
                (staged / "FM2001_Art/Generic/bground.444").exists()
            )

    def test_unmatched_loose_zip_selection_warns(self):
        with tempfile.TemporaryDirectory() as temp_name:
            archive = Path(temp_name) / "source.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("UI/real.dat", b"test")
            report = report_for_source(
                archive,
                explicit_paths={"UI/missing.dat"},
                only_explicit=True,
            )
            self.assertEqual(report["candidates"], [])
            self.assertTrue(
                any(
                    "Explicit disc path was not found: UI/missing.dat" in warning
                    for warning in report["warnings"]
                )
            )

    def test_report_captures_entire_outer_zip_catalog_not_only_candidates(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            archive = root / "source.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("FM2001_Art/Generic/logo.png", b"front-end")
                zf.writestr("Opaque/A.dat", b"not-a-hint")
                zf.writestr("disc/game.bin", b"raw-disc-placeholder")
            report = report_for_source(archive)
            self.assertEqual(report["zip_file_count"], 3)
            self.assertEqual(
                [(item["path"], item["size"], item["is_disc_image"])
                 for item in report["zip_files"]],
                [
                    ("FM2001_Art/Generic/logo.png", 9, False),
                    ("Opaque/A.dat", 10, False),
                    ("disc/game.bin", 20, True),
                ],
            )
            self.assertEqual(report["disc_file_count"], 0)
            self.assertEqual(len(report["candidates"]), 1)

    def test_deep_outer_zip_catalog_does_not_duplicate_disc_member_listing(self):
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
                zf.writestr("Data/opaque", b"fixture")
                zf.writestr("disc/game.bin", raw)
            report = report_for_source(archive, deep=True)
            self.assertEqual(report["zip_file_count"], 2)
            self.assertEqual(report["zip_files"][0]["path"], "Data/opaque")
            self.assertEqual(report["zip_files"][1]["path"], "disc/game.bin")
            self.assertTrue(report["zip_files"][1]["is_disc_image"])
            self.assertEqual(report["disc_file_count"], 1)

    def test_case_insensitive_duplicate_zip_paths_fail_before_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            archive = root / "source.zip"
            staged = root / "staged"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("UI/Panel.dat", b"first")
                zf.writestr("ui/panel.dat", b"SECOND")
            with self.assertRaisesRegex(
                StagingCollisionError, "Duplicate Gate-13 staging path"
            ):
                report_for_source(
                    archive,
                    explicit_paths={"UI/Panel.dat"},
                    extract_candidates_to=staged,
                    only_explicit=True,
                )
            self.assertEqual((staged / "UI/Panel.dat").read_bytes(), b"first")
            self.assertFalse((staged / "ui/panel.dat").exists())

    def test_selected_loose_and_nested_disc_path_collision_is_fatal(self):
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
            staged = root / "staged"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("FM2001_Art/Generic/bground.444", b"outer-layer")
                zf.writestr("disc/game.bin", raw)
            with self.assertRaisesRegex(
                StagingCollisionError, "Duplicate Gate-13 staging path"
            ):
                report_for_source(
                    archive,
                    deep=True,
                    only_explicit=True,
                    explicit_paths={"FM2001_Art/Generic/bground.444"},
                    extract_candidates_to=staged,
                )
            self.assertEqual(
                (staged / "FM2001_Art/Generic/bground.444").read_bytes(),
                b"outer-layer",
            )

    def test_preexisting_staged_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            archive = root / "source.zip"
            staged = root / "staged"
            target = staged / "UI" / "Panel.dat"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"prior-work")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("UI/Panel.dat", b"new-content")
            with self.assertRaises(StagingCollisionError):
                report_for_source(
                    archive,
                    only_explicit=True,
                    explicit_paths={"UI/Panel.dat"},
                    extract_candidates_to=staged,
                )
            self.assertEqual(target.read_bytes(), b"prior-work")

    def test_nested_image_cannot_be_selected_as_menu_asset(self):
        with tempfile.TemporaryDirectory() as temp_name:
            archive = Path(temp_name) / "source.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("disc/game.bin", b"raw-disc-placeholder")
            with self.assertRaisesRegex(ValueError, "Disc-image containers"):
                report_for_source(
                    archive,
                    explicit_paths={"disc/game.bin"},
                    only_explicit=True,
                )

    def test_original_background_expected_byte_count_is_recorded(self):
        with tempfile.TemporaryDirectory() as temp_name:
            iso = Path(temp_name) / "fixture.iso"
            build_joliet_iso(iso)
            report = report_for_source(iso)

        self.assertEqual(EXPECTED_BGROUND_BYTES, 222_616)
        self.assertEqual(report["expected_bground"]["size_bytes"], 222_616)
        self.assertTrue(
            any(
                "bground.444 size is" in warning and "222616" in warning
                for warning in report["warnings"]
            )
        )

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
