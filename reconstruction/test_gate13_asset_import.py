from pathlib import Path
import tempfile
import unittest

from gate13_asset_import import (
    AssetImportError,
    add_manifest_row,
    destination_relative,
    import_original_asset,
    validate_source_relative,
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
