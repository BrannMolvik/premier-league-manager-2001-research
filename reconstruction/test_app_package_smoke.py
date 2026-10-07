from hashlib import sha256
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from startup_media_profile_marker import (
    PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH,
    candidate_profile_marker_payload,
)


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
            self.assertTrue(report["settings_surface_present"])
            self.assertEqual(report["settings_default_profile"], "Original")
            self.assertTrue(report["settings_default_fullscreen"])
            self.assertEqual(report["startup_media_video_encoder"], "libx264")
            self.assertFalse(report["startup_media_profile_marker_present"])
            self.assertFalse(report["startup_media_candidate_only"])
            self.assertFalse(report["startup_media_production_runtime_switched"])
            self.assertTrue(report["external_game_data_required"])

    def test_package_smoke_reports_hash_bound_candidate_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, _manifest = self._layout(root)
            ffmpeg = root / app.PACKAGED_FFMPEG_RELATIVE_PATH
            marker = root / PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH
            payload = candidate_profile_marker_payload(
                ffmpeg_sha256=sha256(ffmpeg.read_bytes()).hexdigest(),
                build_proof_sha256="1" * 64,
                roundtrip_proof_sha256="2" * 64,
                source_commit="46d8f462eeb87ee1f704d8c44a0ee24fca471ad1",
            )
            marker.write_text(json.dumps(payload), encoding="utf-8")
            with (
                patch("app.application_root", return_value=root),
                patch("app.bundled_source_root", return_value=source),
            ):
                report = app.package_smoke_report()

        self.assertEqual(report["startup_media_video_encoder"], "h264_mf")
        self.assertTrue(report["startup_media_profile_marker_present"])
        self.assertTrue(report["startup_media_candidate_only"])
        self.assertFalse(report["startup_media_production_runtime_switched"])

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
