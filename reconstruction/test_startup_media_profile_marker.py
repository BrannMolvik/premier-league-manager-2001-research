from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
)
from startup_media_profile_marker import (
    PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH,
    PackagedStartupMediaProfileError,
    candidate_profile_marker_payload,
    resolve_packaged_startup_media_profile,
)


class PackagedStartupMediaProfileTests(unittest.TestCase):
    def _valid_layout(self, root: Path):
        ffmpeg = root / "runtime_tools" / "ffmpeg.exe"
        ffmpeg.parent.mkdir(parents=True)
        ffmpeg.write_bytes(b"minimal-ffmpeg")
        payload = candidate_profile_marker_payload(
            ffmpeg_sha256=sha256(ffmpeg.read_bytes()).hexdigest(),
            build_proof_sha256="1" * 64,
            roundtrip_proof_sha256="2" * 64,
            source_commit="46d8f462eeb87ee1f704d8c44a0ee24fca471ad1",
        )
        marker = root / PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH
        marker.write_text(json.dumps(payload), encoding="utf-8")
        return ffmpeg, marker, payload

    def test_absent_marker_preserves_production_default(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg = root / "ffmpeg.exe"
            ffmpeg.write_bytes(b"production")
            profile, marker = resolve_packaged_startup_media_profile(root, ffmpeg)
        self.assertEqual(profile, DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE)
        self.assertIsNone(marker)

    def test_valid_candidate_marker_selects_h264_mf_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg, _marker, payload = self._valid_layout(root)
            profile, loaded = resolve_packaged_startup_media_profile(root, ffmpeg)
        self.assertEqual(
            profile,
            WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
        )
        self.assertEqual(profile.ffmpeg_video_encoder, "h264_mf")
        self.assertEqual(loaded, payload)
        self.assertFalse(loaded["production_runtime_switched"])

    def test_ffmpeg_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg, _marker, _payload = self._valid_layout(root)
            ffmpeg.write_bytes(b"tampered")
            with self.assertRaisesRegex(
                PackagedStartupMediaProfileError,
                "differs from candidate profile marker",
            ):
                resolve_packaged_startup_media_profile(root, ffmpeg)

    def test_marker_cannot_self_promote_production_switch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg, marker, payload = self._valid_layout(root)
            payload["production_runtime_switched"] = True
            marker.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                PackagedStartupMediaProfileError,
                "production_runtime_switched=false",
            ):
                resolve_packaged_startup_media_profile(root, ffmpeg)


if __name__ == "__main__":
    unittest.main()
