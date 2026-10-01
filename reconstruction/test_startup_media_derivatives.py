"""Tests for verified private startup-media derivative loading."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from original_startup_media import OriginalStartupMediaSpec
from startup_media_derivatives import (
    StartupMediaDerivativeError,
    load_verified_startup_media_derivatives,
)


def spec(path: str, *, source_byte: bytes, frames: int, flag: bool):
    return OriginalStartupMediaSpec(
        source_path=path,
        source_sha256=sha256(source_byte).hexdigest(),
        size_bytes=len(source_byte),
        startup_callsite_va=0x5000 + frames,
        playback_wrapper_va=0x461E20,
        playback_flag_bit0=flag,
        video_width=320,
        video_height=480,
        frame_rate=25,
        decoded_video_frames=frames,
        audio_sample_rate=22_050,
        audio_channels=2,
    )


class StartupMediaDerivativeTests(unittest.TestCase):
    def fixture(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        private = root / "private"
        private.mkdir()

        specs = (
            spec("FMV/first.tgq", source_byte=b"first source", frames=7, flag=False),
            spec("FMV/second.tgq", source_byte=b"second source", frames=11, flag=True),
        )
        files = []
        outputs = []
        for sequence, item in enumerate(specs):
            path = private / f"converted-{sequence}.mp4"
            payload = f"converted-{sequence}-bytes".encode("ascii")
            path.write_bytes(payload)
            files.append(path)
            outputs.append({
                "sequence": sequence,
                "source_path": item.source_path,
                "source_sha256": item.source_sha256,
                "source_size_bytes": item.size_bytes,
                "startup_callsite_va": f"0x{item.startup_callsite_va:X}",
                "playback_wrapper_va": f"0x{item.playback_wrapper_va:X}",
                "playback_flag_bit0": item.playback_flag_bit0,
                "converted_path": str(path.resolve()),
                "converted_size_bytes": len(payload),
                "converted_sha256": sha256(payload).hexdigest(),
                "container": "mp4",
                "video_codec": "h264",
                "video_width": 320,
                "video_height": 480,
                "frame_rate": 25,
                "decoded_video_frames": item.decoded_video_frames,
                "pixel_format": "yuv420p",
                "audio_codec": "aac",
                "audio_sample_rate": 22_050,
                "audio_channels": 2,
            })

        receipt = private / "receipt.json"
        receipt_payload = {
            "schema_version": 1,
            "passed": True,
            "audit_kind": "private_original_startup_media_conversion",
            "ffmpeg_version": "ffmpeg version fixture",
            "ffprobe_version": "ffprobe version fixture",
            "profile": {
                "container": "mp4",
                "video_encoder": "libx264",
                "video_codec": "h264",
                "pixel_format": "yuv420p",
                "audio_encoder": "aac",
                "audio_codec": "aac",
            },
            "outputs": outputs,
            "fidelity_boundary": "fixture",
            "gate14_complete": False,
        }
        receipt.write_text(
            json.dumps(receipt_payload, indent=2) + "\n",
            encoding="utf-8",
        )
        return repo, private, receipt, receipt_payload, specs, tuple(files)

    def rewrite(self, receipt, payload):
        receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_verified_receipt_rehashes_derivatives_and_preserves_sequence(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, _payload, specs, files = self.fixture(temp)
            result = load_verified_startup_media_derivatives(
                receipt_path=receipt,
                repo_root=repo,
                specs=specs,
            )
            self.assertEqual([item.sequence for item in result], [0, 1])
            self.assertEqual([item.spec for item in result], list(specs))
            self.assertEqual([item.path for item in result], list(files))
            self.assertEqual(
                [item.spec.playback_flag_bit0 for item in result],
                [False, True],
            )
            self.assertEqual([item.container for item in result], ["mp4", "mp4"])

    def test_same_size_derivative_tamper_is_detected_by_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, _payload, specs, files = self.fixture(temp)
            original = files[1].read_bytes()
            files[1].write_bytes(b"x" * len(original))
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "converted bytes differ from receipt",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_reordered_or_changed_source_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, payload, specs, _files = self.fixture(temp)
            payload["outputs"][0], payload["outputs"][1] = (
                payload["outputs"][1],
                payload["outputs"][0],
            )
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "sequence|source_path",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_receipt_cannot_self_promote_gate14_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, payload, specs, _files = self.fixture(temp)
            payload["gate14_complete"] = True
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "completion boundary",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_derivative_or_receipt_inside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, private, receipt, payload, specs, _files = self.fixture(temp)
            inside = repo / "startup.mp4"
            inside.write_bytes(b"inside")
            payload["outputs"][0]["converted_path"] = str(inside.resolve())
            payload["outputs"][0]["converted_size_bytes"] = inside.stat().st_size
            payload["outputs"][0]["converted_sha256"] = sha256(
                inside.read_bytes()
            ).hexdigest()
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "outside the Git repository",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

            inside_receipt = repo / "receipt.json"
            inside_receipt.write_text(receipt.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "outside the Git repository",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=inside_receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_boolean_receipt_fields_require_json_booleans(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, payload, specs, _files = self.fixture(temp)
            payload["passed"] = 1
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "must be a boolean",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_integer_receipt_fields_reject_numeric_coercion(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, payload, specs, _files = self.fixture(temp)
            payload["outputs"][0]["video_width"] = 320.5
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "must be an integer",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )

    def test_duplicate_derivative_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, receipt, payload, specs, files = self.fixture(temp)
            payload["outputs"][1]["converted_path"] = str(files[0].resolve())
            payload["outputs"][1]["converted_size_bytes"] = files[0].stat().st_size
            payload["outputs"][1]["converted_sha256"] = sha256(
                files[0].read_bytes()
            ).hexdigest()
            self.rewrite(receipt, payload)
            with self.assertRaisesRegex(
                StartupMediaDerivativeError,
                "reuses one converted path",
            ):
                load_verified_startup_media_derivatives(
                    receipt_path=receipt,
                    repo_root=repo,
                    specs=specs,
                )


if __name__ == "__main__":
    unittest.main()
