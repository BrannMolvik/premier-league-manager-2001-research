from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from gate13_first_screen_manifest_readiness import (
    FirstScreenManifestReadinessError,
    assert_first_screen_manifest_ready,
    parse_manifest_asset_rows,
)
from gate13_first_screen_selection import ExpectedSource


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


class FirstScreenManifestReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "original_assets").mkdir()
        self.assets = (
            ExpectedSource("FM2001_Art/Generic/a.444", digest(b"a")),
            ExpectedSource("Fonts/test.fnt", digest(b"font")),
        )

    def tearDown(self):
        self.temp.cleanup()

    def _write_asset(self, source: str, data: bytes):
        path = self.root / "original_assets" / "source" / Path(source)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _write_manifest(self, rows):
        header = (
            "# Original Asset Manifest\n\n"
            "| Repository path | Original source path | Source SHA-256 | Form | "
            "Conversion/provenance notes |\n"
            "| --- | --- | --- | --- | --- |\n"
        )
        text = header + "".join(
            f"| {repository} | {source} | {source_hash} | {form} | test |\n"
            for repository, source, source_hash, form in rows
        )
        (self.root / "original_assets" / "MANIFEST.md").write_text(
            text, encoding="utf-8"
        )

    def _complete_rows(self):
        return [
            (
                f"original_assets/source/{self.assets[0].path}",
                self.assets[0].path,
                self.assets[0].sha256,
                "original",
            ),
            (
                f"original_assets/source/{self.assets[1].path}",
                self.assets[1].path,
                self.assets[1].sha256,
                "original",
            ),
        ]

    def test_complete_manifest_and_bytes_pass(self):
        self._write_asset(self.assets[0].path, b"a")
        self._write_asset(self.assets[1].path, b"font")
        self._write_manifest(self._complete_rows())

        self.assertEqual(
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            ),
            (
                f"original_assets/source/{self.assets[0].path}",
                f"original_assets/source/{self.assets[1].path}",
            ),
        )

    def test_missing_pinned_asset_fails_closed(self):
        self._write_asset(self.assets[0].path, b"a")
        self._write_manifest(self._complete_rows()[:1])

        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "not imported"
        ):
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            )

    def test_manifest_hash_must_equal_pinned_source_receipt(self):
        self._write_asset(self.assets[0].path, b"a")
        self._write_asset(self.assets[1].path, b"font")
        rows = self._complete_rows()
        rows[0] = (rows[0][0], rows[0][1], "0" * 64, rows[0][3])
        self._write_manifest(rows)

        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "source SHA-256"
        ):
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            )

    def test_tracked_bytes_must_still_match_pinned_source_hash(self):
        self._write_asset(self.assets[0].path, b"changed")
        self._write_asset(self.assets[1].path, b"font")
        self._write_manifest(self._complete_rows())

        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "Tracked bytes"
        ):
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            )

    def test_import_destination_path_is_not_replaceable(self):
        self._write_asset(self.assets[0].path, b"a")
        self._write_asset(self.assets[1].path, b"font")
        rows = self._complete_rows()
        rows[0] = (
            "original_assets/source/wrong/a.444",
            rows[0][1],
            rows[0][2],
            rows[0][3],
        )
        self._write_manifest(rows)

        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "repository path disagrees"
        ):
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            )

    def test_pinned_source_copy_must_be_manifested_as_original(self):
        self._write_asset(self.assets[0].path, b"a")
        self._write_asset(self.assets[1].path, b"font")
        rows = self._complete_rows()
        rows[0] = (rows[0][0], rows[0][1], rows[0][2], "converted")
        self._write_manifest(rows)

        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "byte-identical original"
        ):
            assert_first_screen_manifest_ready(
                self.root, expected_assets=self.assets
            )

    def test_duplicate_source_or_repository_rows_are_rejected(self):
        rows = self._complete_rows()
        duplicate_source = rows + [
            (
                "original_assets/source/elsewhere/a.444",
                rows[0][1],
                rows[0][2],
                "original",
            )
        ]
        self._write_manifest(duplicate_source)
        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "Duplicate manifest source"
        ):
            parse_manifest_asset_rows(
                (self.root / "original_assets" / "MANIFEST.md").read_text(
                    encoding="utf-8"
                )
            )

        duplicate_repository = rows + [
            (
                rows[0][0],
                "other/source.444",
                rows[0][2],
                "original",
            )
        ]
        self._write_manifest(duplicate_repository)
        with self.assertRaisesRegex(
            FirstScreenManifestReadinessError, "Duplicate manifest repository"
        ):
            parse_manifest_asset_rows(
                (self.root / "original_assets" / "MANIFEST.md").read_text(
                    encoding="utf-8"
                )
            )


if __name__ == "__main__":
    unittest.main()
