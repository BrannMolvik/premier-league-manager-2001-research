import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from gate13_asset_import import (
    AssetImportError,
    add_manifest_row,
    destination_relative,
    import_original_asset,
    validate_source_relative,
    verify_selection_inventory,
)


MANIFEST = """# Original Asset Manifest

| Repository path | Original source path | Source SHA-256 | Form | Conversion/provenance notes |
| --- | --- | --- | --- | --- |
| _None imported yet_ |  |  |  |  |

Forms:
"""


class Gate13AssetImportTests(unittest.TestCase):
    def test_destination_preserves_original_relative_path_under_source_tree(self):
        self.assertEqual(
            destination_relative("FM2001_Art/Generic/menu.444").as_posix(),
            "original_assets/source/FM2001_Art/Generic/menu.444",
        )

    def test_rejects_raw_source_containers(self):
        with self.assertRaises(AssetImportError):
            validate_source_relative("disc/FAMG2001.bin")
        with self.assertRaises(AssetImportError):
            validate_source_relative("source.zip")

    def test_manifest_first_import_replaces_none_row(self):
        text = add_manifest_row(
            MANIFEST,
            repository_path="original_assets/source/FM2001_Art/Generic/menu.444",
            source_path="FM2001_Art/Generic/menu.444",
            sha256="a" * 64,
            notes="Gate 13 source asset.",
        )
        self.assertNotIn("_None imported yet_", text)
        self.assertIn(
            "| original_assets/source/FM2001_Art/Generic/menu.444 | "
            "FM2001_Art/Generic/menu.444 | " + "a" * 64 + " | original |",
            text,
        )

    def test_import_copies_bytes_and_updates_manifest(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staging = root / "staging"
            repo = root / "repo"
            source = staging / "FM2001_Art" / "Generic" / "menu-logo.png"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"authorized-original")
            manifest = repo / "original_assets" / "MANIFEST.md"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(MANIFEST, encoding="utf-8")

            destination, digest = import_original_asset(
                staging_root=staging,
                source_relative="FM2001_Art/Generic/menu-logo.png",
                repo_root=repo,
                notes="Gate 13 test import.",
            )

            imported = repo / destination
            self.assertEqual(imported.read_bytes(), b"authorized-original")
            self.assertEqual(len(digest), 64)
            manifest_text = manifest.read_text(encoding="utf-8")
            self.assertIn(destination.as_posix(), manifest_text)
            self.assertIn(digest, manifest_text)

    def test_report_verified_import_retains_original_provenance(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staging = root / "staging"
            repo = root / "repo"
            path = "FM2001_Art/Buttons/original.png"
            source = staging / path
            source.parent.mkdir(parents=True)
            source.write_bytes(b"authorized-source-bytes")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            report_path = root / "selected.json"
            report_path.write_text(json.dumps({
                "source_sha256": "a" * 64,
                "unresolved_explicit_paths": [],
                "candidates": [{
                    "path": path,
                    "size": source.stat().st_size,
                    "sha256": digest,
                    "source_layer": "iso9660-extracted",
                }],
            }), encoding="utf-8")
            manifest = repo / "original_assets" / "MANIFEST.md"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(MANIFEST, encoding="utf-8")
            dest, recorded = import_original_asset(
                staging_root=staging,
                source_relative=path,
                repo_root=repo,
                notes="Verified original UI asset.",
                inventory_report=report_path,
            )
            self.assertEqual(recorded, digest)
            self.assertEqual((repo / dest).read_bytes(), source.read_bytes())
            self.assertIn(
                "Source archive SHA-256: " + "a" * 64,
                manifest.read_text(encoding="utf-8"),
            )

    def test_import_rejects_changed_staged_bytes_and_ambiguous_sources(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staging = root / "staging"
            repo = root / "repo"
            path = "FM2001_Art/Buttons/original.png"
            source = staging / path
            source.parent.mkdir(parents=True)
            source.write_bytes(b"tampered")
            digest = hashlib.sha256(b"untampered").hexdigest()
            report_path = root / "selected.json"
            candidate = {
                "path": path,
                "size": len(b"untampered"),
                "sha256": digest,
                "source_layer": "iso9660-extracted",
            }
            report = {
                "unresolved_explicit_paths": [],
                "candidates": [candidate],
            }
            report_path.write_text(json.dumps(report), encoding="utf-8")
            manifest = repo / "original_assets" / "MANIFEST.md"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(MANIFEST, encoding="utf-8")
            with self.assertRaisesRegex(AssetImportError, "differ"):
                import_original_asset(
                    staging_root=staging, source_relative=path,
                    repo_root=repo, notes="Must fail.", inventory_report=report_path,
                )
            report["candidates"] = [candidate, candidate]
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(AssetImportError, "exactly one"):
                import_original_asset(
                    staging_root=staging, source_relative=path,
                    repo_root=repo, notes="Must fail.", inventory_report=report_path,
                )
            self.assertFalse((repo / "original_assets/source" / path).exists())
            self.assertEqual(manifest.read_text(encoding="utf-8"), MANIFEST)

    def test_opaque_ui_bin_import_requires_report_and_rejects_raw_disc(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staging = root / "staging"
            repo = root / "repo"
            path = "UI/opaque.bin"
            source = staging / path
            source.parent.mkdir(parents=True)
            source.write_bytes(b"legitimate-layout-data")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            report_path = root / "selected.json"
            candidate = {
                "path": path, "size": source.stat().st_size,
                "sha256": digest, "source_layer": "zip-extracted",
            }
            report = {
                "unresolved_explicit_paths": [],
                "candidates": [candidate],
                "zip_files": [{
                    "path": path, "size": source.stat().st_size,
                    "is_disc_image": False,
                }],
            }
            report_path.write_text(json.dumps(report), encoding="utf-8")
            manifest = repo / "original_assets" / "MANIFEST.md"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(MANIFEST, encoding="utf-8")
            with self.assertRaises(AssetImportError):
                import_original_asset(
                    staging_root=staging, source_relative=path,
                    repo_root=repo, notes="No report.",
                )
            report["zip_files"][0]["is_disc_image"] = True
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(AssetImportError, "not a disc image"):
                import_original_asset(
                    staging_root=staging, source_relative=path,
                    repo_root=repo, notes="Disc impersonation.",
                    inventory_report=report_path,
                )
            report["zip_files"][0]["is_disc_image"] = False
            report_path.write_text(json.dumps(report), encoding="utf-8")
            dest, result_digest = import_original_asset(
                staging_root=staging, source_relative=path,
                repo_root=repo, notes="Verified opaque original UI data.",
                inventory_report=report_path,
            )
            self.assertEqual(result_digest, digest)
            self.assertEqual((repo / dest).read_bytes(), b"legitimate-layout-data")

    def test_partial_selection_report_blocks_import(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            report_path = root / "selected.json"
            report_path.write_text(json.dumps({
                "unresolved_explicit_paths": ["UI/missing.dat"],
                "candidates": [{
                    "path": "UI/known.png", "size": 3,
                    "sha256": hashlib.sha256(b"abc").hexdigest(),
                    "source_layer": "zip-extracted",
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(AssetImportError, "partial"):
                verify_selection_inventory(
                    report_path, source_relative="UI/known.png",
                    staged_sha256=hashlib.sha256(b"abc").hexdigest(),
                    staged_size=3,
                )

    def test_wrong_bground_is_rejected_before_copy(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staging = root / "staging"
            repo = root / "repo"
            source = staging / "FM2001_Art" / "Generic" / "bground.444"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"not-the-original")
            manifest = repo / "original_assets" / "MANIFEST.md"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(MANIFEST, encoding="utf-8")

            with self.assertRaises(AssetImportError):
                import_original_asset(
                    staging_root=staging,
                    source_relative="FM2001_Art/Generic/bground.444",
                    repo_root=repo,
                    notes="Must fail.",
                )

            self.assertFalse(
                (repo / "original_assets/source/FM2001_Art/Generic/bground.444").exists()
            )


if __name__ == "__main__":
    unittest.main()
