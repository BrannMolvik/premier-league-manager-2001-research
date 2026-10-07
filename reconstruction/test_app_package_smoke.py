import shutil
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
        ffmpeg = root / app.PACKAGED_FFMPEG_RELATIVE_PATH
        ffmpeg.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg.write_bytes(b"packaged-ffmpeg")

        canonical_bundle = (
            Path(__file__).resolve().parents[1]
            / app.PSTARTMENU_DERIVATIVE_RELATIVE
        )
        staged_bundle = root / app.PSTARTMENU_DERIVATIVE_RELATIVE
        staged_bundle.mkdir(parents=True, exist_ok=True)
        for name in ("manifest.json", "payload.bin.xz"):
            shutil.copyfile(
                canonical_bundle / name,
                staged_bundle / name,
            )
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
            self.assertEqual(
                report["pstartmenu_manifest_sha256"],
                app.PSTARTMENU_DERIVATIVE_MANIFEST_SHA256,
            )
            self.assertTrue(report["pstartmenu_presenter_build_passed"])
            self.assertEqual(report["pstartmenu_presenter_screen"], "pstartmenu")
            self.assertFalse(report["settings_surface_present"])
            self.assertEqual(report["original_menu_control_ids"], [1, 2, 3, 4])
            self.assertTrue(report["external_game_data_required"])

    def test_smoke_rejects_nonoriginal_default_menu_controls(self):
        from dataclasses import replace
        from original_game_host import build_original_game_presenter

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, _manifest = self._layout(root)
            presenter = build_original_game_presenter(root / '__no_game_data__')
            native_snapshot = presenter.snapshot()
            invalid_snapshot = replace(
                native_snapshot,
                controls=native_snapshot.controls + (native_snapshot.controls[-1],),
            )
            with (
                patch('app.application_root', return_value=root),
                patch('app.bundled_source_root', return_value=source),
                patch('app.build_original_game_presenter', return_value=presenter),
                patch.object(type(presenter), 'snapshot', return_value=invalid_snapshot),
                self.assertRaisesRegex(RuntimeError, 'four-control baseline differs'),
            ):
                app.package_smoke_report()

    def test_package_smoke_rejects_crlf_pstartmenu_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, _manifest = self._layout(root)
            derivative_manifest = (
                root
                / app.PSTARTMENU_DERIVATIVE_RELATIVE
                / "manifest.json"
            )
            raw = derivative_manifest.read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            derivative_manifest.write_bytes(
                raw[:-1] + b"\r\n"
            )
            with (
                patch("app.application_root", return_value=root),
                patch("app.bundled_source_root", return_value=source),
                self.assertRaisesRegex(
                    RuntimeError,
                    "exact-byte verification.*pinned receipt",
                ),
            ):
                app.package_smoke_report()

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
