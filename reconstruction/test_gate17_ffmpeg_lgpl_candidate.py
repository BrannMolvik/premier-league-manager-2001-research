"""Tests for the pinned LGPL FFmpeg migration candidate audit."""
from __future__ import annotations

from hashlib import sha256
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

import gate17_ffmpeg_lgpl_candidate as candidate
from gate17_ffmpeg_lgpl_candidate import (
    LgplFfmpegCandidateError,
    validate_archive_identity,
    validate_codec_capabilities,
    validate_ffprobe_version_output,
    validate_synthetic_probe_output,
    validate_version_output,
)


VERSION = """ffmpeg version n9.0.2-22-g46d8f462ee-20261003 Copyright
built with gcc
configuration: --enable-version3 --enable-static --disable-debug
"""
FFPROBE_VERSION = """ffprobe version n9.0.2-22-g46d8f462ee-20261003 Copyright
built with gcc
configuration: --enable-version3 --enable-static --disable-debug
"""
SYNTHETIC_PROBE = """{
  "streams": [
    {
      "codec_type": "video",
      "codec_name": "h264",
      "pix_fmt": "yuv420p",
      "width": 320,
      "height": 480,
      "avg_frame_rate": "25/1",
      "nb_read_frames": "25"
    },
    {
      "codec_type": "audio",
      "codec_name": "aac",
      "sample_rate": "22050",
      "channels": 2
    }
  ],
  "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2"}
}"""

DECODERS = """
 V....D eatgq               Electronic Arts TGQ video
 V....D h264                 H.264 / AVC / MPEG-4 AVC
"""
ENCODERS = """
 V..... h264_mf              H.264 via MediaFoundation
 A..... aac                  AAC (Advanced Audio Coding)
"""


class Gate17LgplFfmpegCandidateTests(unittest.TestCase):
    def test_version_rejects_gpl_and_x264_flags(self):
        result = validate_version_output(VERSION)
        self.assertEqual(result["forbidden_configuration_flags_present"], [])

        for flag in candidate.FORBIDDEN_CONFIGURATION_FLAGS:
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(
                    LgplFfmpegCandidateError,
                    "unexpectedly enables",
                ):
                    validate_version_output(
                        VERSION.replace(
                            "--disable-debug",
                            f"--disable-debug {flag}",
                        )
                    )

    def test_version_requires_pinned_source_revision(self):
        with self.assertRaisesRegex(
            LgplFfmpegCandidateError,
            "pinned source revision",
        ):
            validate_version_output(
                VERSION.replace(candidate.EXPECTED_VERSION_TOKEN, "different")
            )

    def test_ffprobe_version_requires_same_pinned_source_revision(self):
        result = validate_ffprobe_version_output(FFPROBE_VERSION)
        self.assertIn(candidate.EXPECTED_VERSION_TOKEN, result["ffprobe_version_line"])

        with self.assertRaisesRegex(
            LgplFfmpegCandidateError,
            "pinned source revision",
        ):
            validate_ffprobe_version_output(
                FFPROBE_VERSION.replace(candidate.EXPECTED_VERSION_TOKEN, "different")
            )

    def test_synthetic_probe_requires_exact_startup_output_shape(self):
        result = validate_synthetic_probe_output(SYNTHETIC_PROBE)
        self.assertTrue(result["synthetic_probe_verified"])
        self.assertEqual(result["synthetic_probe_pixel_format"], "yuv420p")

        with self.assertRaisesRegex(
            LgplFfmpegCandidateError,
            "video geometry/codec",
        ):
            validate_synthetic_probe_output(
                SYNTHETIC_PROBE.replace('"pix_fmt": "yuv420p"', '"pix_fmt": "nv12"')
            )

    def test_codec_probe_requires_tgq_h264_mf_and_aac(self):
        result = validate_codec_capabilities(
            decoders_text=DECODERS,
            encoders_text=ENCODERS,
        )
        self.assertTrue(result["all_required_codecs_present"])

        with self.assertRaisesRegex(
            LgplFfmpegCandidateError,
            "lacks required",
        ):
            validate_codec_capabilities(
                decoders_text=DECODERS.replace("eatgq", "other"),
                encoders_text=ENCODERS,
            )

    def test_archive_identity_requires_exact_sha_and_materials(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / candidate.ARCHIVE_NAME
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("candidate/bin/ffmpeg.exe", b"fake")
                zf.writestr("candidate/bin/ffprobe.exe", b"fake-probe")
                zf.writestr("candidate/LICENSE.txt", b"L" * 200)
            actual = sha256(archive.read_bytes()).hexdigest()

            with patch.object(candidate, "ARCHIVE_SHA256", actual):
                result = validate_archive_identity(archive)
            self.assertEqual(result["archive_sha256"], actual)
            self.assertTrue(result["ffmpeg_member"].endswith("/bin/ffmpeg.exe"))
            self.assertTrue(result["ffprobe_member"].endswith("/bin/ffprobe.exe"))
            self.assertTrue(result["license_member"].endswith("/LICENSE.txt"))

    def test_archive_identity_rejects_digest_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "candidate.zip"
            archive.write_bytes(b"wrong")
            with self.assertRaisesRegex(
                LgplFfmpegCandidateError,
                "SHA-256 mismatch",
            ):
                validate_archive_identity(archive)


if __name__ == "__main__":
    unittest.main()
