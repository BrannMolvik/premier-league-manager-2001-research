"""Tests for the exact-original minimal FFmpeg Gate-17 proof producer."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate17_ffmpeg_original_tgq_proof import (
    MinimalFfmpegOriginalTgqError,
    audit_exact_original_tgq_conversion,
    validate_conversion_result,
)
from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE


def _sha(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _conversion_result() -> dict:
    return {
        "passed": True,
        "profile": {
            "video_encoder": "h264_mf",
            "video_codec": "h264",
            "audio_encoder": "aac",
            "audio_codec": "aac",
            "output_width": 640,
            "output_height": 480,
            "video_filter": "scale=640:480:flags=neighbor",
        },
        "outputs": [
            {
                "source_path": spec.source_path,
                "source_sha256": spec.source_sha256,
                "source_size_bytes": spec.size_bytes,
                "video_codec": "h264",
                "pixel_format": "yuv420p",
                "video_width": 640,
                "video_height": 480,
                "frame_rate": 25,
                "decoded_video_frames": spec.decoded_video_frames,
                "audio_codec": "aac",
                "audio_sample_rate": 22050,
                "audio_channels": 2,
                "container": "mp4",
                "converted_sha256": ("%064x" % (index + 1)),
                "converted_size_bytes": 1000 + index,
            }
            for index, spec in enumerate(ORIGINAL_STARTUP_MEDIA_SEQUENCE)
        ],
    }


class Gate17OriginalTgqProofTests(unittest.TestCase):
    def fixture(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        private = root / "private"
        private.mkdir()
        ffmpeg = private / "ffmpeg.exe"
        ffprobe = private / "ffprobe.exe"
        ffmpeg.write_bytes(b"ffmpeg-minimal")
        ffprobe.write_bytes(b"ffprobe-minimal")
        build = private / "build-proof.json"
        build_payload = {
            "schema_version": 1,
            "audit_kind": "gate17_minimal_ffmpeg_build",
            "passed": True,
            "ffmpeg_sha256": _sha(ffmpeg.read_bytes()),
            "ffprobe_sha256": _sha(ffprobe.read_bytes()),
            "build_verified": True,
            "synthetic_roundtrip_verified": False,
            "exact_original_tgq_verified": False,
            "external_windows11_playback_verified": False,
            "source_material_complete": False,
            "production_migration_ready": False,
            "legal_compliance_claimed": False,
        }
        build.write_text(json.dumps(build_payload), encoding="utf-8")
        roundtrip = private / "roundtrip-proof.json"
        roundtrip_payload = {
            "schema_version": 1,
            "audit_kind": "gate17_minimal_ffmpeg_synthetic_roundtrip",
            "passed": True,
            "build_proof_sha256": _sha(build.read_bytes()),
            "build_proof_ffmpeg_sha256": _sha(ffmpeg.read_bytes()),
            "build_proof_ffprobe_sha256": _sha(ffprobe.read_bytes()),
            "build_verified": True,
            "synthetic_roundtrip_verified": True,
            "exact_original_tgq_verified": False,
            "external_windows11_playback_verified": False,
            "source_material_complete": False,
            "production_migration_ready": False,
            "legal_compliance_claimed": False,
        }
        roundtrip.write_text(json.dumps(roundtrip_payload), encoding="utf-8")
        return repo, private, ffmpeg, ffprobe, build, roundtrip

    def test_success_binds_exact_conversion_to_both_prior_proofs(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, private, ffmpeg, ffprobe, build, roundtrip = self.fixture(temp)
            conversion_receipt = private / "conversion.json"
            final_receipt = private / "gate17-original.json"
            conversion = _conversion_result()

            def fake_convert(**kwargs):
                Path(kwargs["receipt_path"]).write_text(
                    json.dumps(conversion), encoding="utf-8"
                )
                return conversion

            with patch(
                "gate17_ffmpeg_original_tgq_proof.convert_and_receipt_startup_media",
                side_effect=fake_convert,
            ):
                result = audit_exact_original_tgq_conversion(
                    repo_root=repo,
                    source_root=private / "game",
                    output_root=private / "converted",
                    conversion_receipt=conversion_receipt,
                    output_receipt=final_receipt,
                    ffmpeg_exe=ffmpeg,
                    ffprobe_exe=ffprobe,
                    build_proof=build,
                    roundtrip_proof=roundtrip,
                )

            self.assertTrue(result["passed"])
            self.assertTrue(result["build_verified"])
            self.assertTrue(result["synthetic_roundtrip_verified"])
            self.assertTrue(result["exact_original_tgq_verified"])
            self.assertFalse(result["external_windows11_playback_verified"])
            self.assertFalse(result["source_material_complete"])
            self.assertFalse(result["production_migration_ready"])
            self.assertFalse(result["legal_compliance_claimed"])
            self.assertEqual(len(result["exact_original_outputs"]), 2)
            self.assertTrue(final_receipt.is_file())

    def test_tampered_helper_is_rejected_before_private_conversion(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, private, ffmpeg, ffprobe, build, roundtrip = self.fixture(temp)
            ffmpeg.write_bytes(b"tampered")
            with patch(
                "gate17_ffmpeg_original_tgq_proof.convert_and_receipt_startup_media"
            ) as convert:
                with self.assertRaisesRegex(
                    MinimalFfmpegOriginalTgqError, "differs from build proof"
                ):
                    audit_exact_original_tgq_conversion(
                        repo_root=repo,
                        source_root=private / "game",
                        output_root=private / "converted",
                        conversion_receipt=private / "conversion.json",
                        output_receipt=private / "gate17-original.json",
                        ffmpeg_exe=ffmpeg,
                        ffprobe_exe=ffprobe,
                        build_proof=build,
                        roundtrip_proof=roundtrip,
                    )
            convert.assert_not_called()

    def test_roundtrip_must_bind_exact_build_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, private, ffmpeg, ffprobe, build, roundtrip = self.fixture(temp)
            payload = json.loads(roundtrip.read_text(encoding="utf-8"))
            payload["build_proof_sha256"] = "0" * 64
            roundtrip.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                MinimalFfmpegOriginalTgqError, "different build proof"
            ):
                audit_exact_original_tgq_conversion(
                    repo_root=repo,
                    source_root=private / "game",
                    output_root=private / "converted",
                    conversion_receipt=private / "conversion.json",
                    output_receipt=private / "gate17-original.json",
                    ffmpeg_exe=ffmpeg,
                    ffprobe_exe=ffprobe,
                    build_proof=build,
                    roundtrip_proof=roundtrip,
                )

    def test_conversion_result_requires_exact_original_sequence(self):
        payload = _conversion_result()
        payload["outputs"][1]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            MinimalFfmpegOriginalTgqError, "differs from exact contract"
        ):
            validate_conversion_result(payload)

    def test_final_receipt_cannot_be_written_inside_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, private, ffmpeg, ffprobe, build, roundtrip = self.fixture(temp)
            with self.assertRaisesRegex(
                MinimalFfmpegOriginalTgqError, "outside the Git repository"
            ):
                audit_exact_original_tgq_conversion(
                    repo_root=repo,
                    source_root=private / "game",
                    output_root=private / "converted",
                    conversion_receipt=private / "conversion.json",
                    output_receipt=repo / "private-proof.json",
                    ffmpeg_exe=ffmpeg,
                    ffprobe_exe=ffprobe,
                    build_proof=build,
                    roundtrip_proof=roundtrip,
                )


if __name__ == "__main__":
    unittest.main()
