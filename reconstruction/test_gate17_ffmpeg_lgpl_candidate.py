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
    validate_version_output,
)


VERSION = """ffmpeg version n9.0.2-22-g46d8f462ee-20261003 Copyright
built with gcc
configuration: --enable-version3 --enable-static --disable-debug
"""
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
                zf.writestr("candidate/LICENSE.txt", b"L" * 200)
            actual = sha256(archive.read_bytes()).hexdigest()

            with patch.object(candidate, "ARCHIVE_SHA256", actual):
                result = validate_archive_identity(archive)
            self.assertEqual(result["archive_sha256"], actual)
            self.assertTrue(result["ffmpeg_member"].endswith("/bin/ffmpeg.exe"))
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
