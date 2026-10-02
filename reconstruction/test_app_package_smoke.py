import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app


class AppPackageSmokeTests(unittest.TestCase):
    def _layout(self, root: Path):
        source = root / "original_assets" / "source"
        for relative in app.PACKAGE_SMOKE_REQUIRED:
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"asset")
        manifest = root / "original_assets" / "MANIFEST.md"
        manifest.write_text("provenance", encoding="utf-8")
        return source, manifest

    def test_package_smoke_requires_assets_and_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, manifest = self._layout(root)
            with (
                patch("app.application_root", return_value=root),
                patch("app.bundled_source_root", return_value=source),
            ):
                report = app.package_smoke_report()
            self.assertTrue(report["passed"])
            self.assertEqual(report["provenance_manifest"], str(manifest))
            self.assertTrue(report["external_game_data_required"])

    def test_package_smoke_fails_when_provenance_manifest_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, manifest = self._layout(root)
            manifest.unlink()
            with (
                patch("app.application_root", return_value=root),
                patch("app.bundled_source_root", return_value=source),
                self.assertRaisesRegex(RuntimeError, "MANIFEST.md"),
            ):
                app.package_smoke_report()


if __name__ == "__main__":
    unittest.main()
