"""Tests for strict Gate-14 Windows menu-audio receipt validation."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch
from gate14_windows_menu_audio_receipt import (
    Gate14WindowsMenuAudioReceiptError,
    _require_private_validation_output,
    main as receipt_main,
    validate_windows_menu_audio_receipt,
)


def decoded(*, slot: int | None = 6) -> DecodedMenuPcmDispatch:
    if slot is None:
        return DecodedMenuPcmDispatch(
            event_id=7,
            state_value=0,
            sample_slot=None,
            sample_rate=None,
            channels=None,
            pcm_samples=None,
            pcm_sha256=None,
        )
    return DecodedMenuPcmDispatch(
        event_id=17,
        state_value=0,
        sample_slot=slot,
        sample_rate=22050,
        channels=1,
        pcm_samples=(100, -100, 200),
        pcm_sha256="a" * 64,
    )


def strict_receipt(raw: bytes) -> dict:
    return {
        "schema_version": 1,
        "passed": True,
        "platform_system": "Windows",
        "platform": "Windows-11-test",
        "python_version": "3.12.test",
        "source_bank": {
            "filename": "menus.bnk",
            "size_bytes": len(raw),
            "sha256": sha256(raw).hexdigest(),
        },
        "numeric_route": {
            "event_id": 17,
            "state_value": 0,
            "sample_slot": 6,
        },
        "decoded_pcm": {
            "sample_rate": 22050,
            "channels": 1,
            "sample_count": 3,
            "sha256": "a" * 64,
        },
        "playback_backend": {
            "class": "WindowsMemoryWaveMenuPcmBackend",
            "memory_flag": 4,
        },
        "adapter_delivery_completed": True,
        "human_audibility_confirmation": True,
        "audible_windows_verified": True,
        "numeric_routing_recovered": True,
        "sample_decode_recovered": True,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "modern_ui_event_equivalence_recovered": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
        "evidence_limit": "synthetic bounded receipt",
    }


class Gate14WindowsMenuAudioReceiptTests(unittest.TestCase):
    def setUp(self):
        self.raw = b"synthetic-menus-bank"
        self.identity = {
            "size_bytes": len(self.raw),
            "sha256": sha256(self.raw).hexdigest(),
        }

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_accepts_exact_schema_and_replays_numeric_route_and_pcm(self, replay):
        replay.return_value = decoded()
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            validation = validate_windows_menu_audio_receipt(
                strict_receipt(self.raw),
                self.raw,
            )

        replay.assert_called_once_with(self.raw, 17, 0)
        self.assertTrue(validation["passed"])
        self.assertTrue(validation["source_bank_verified"])
        self.assertTrue(validation["deterministic_numeric_route_replay_verified"])
        self.assertEqual(
            validation["numeric_route"],
            {"event_id": 17, "state_value": 0, "sample_slot": 6},
        )
        self.assertEqual(
            validation["decoded_pcm"],
            {
                "sample_rate": 22050,
                "channels": 1,
                "sample_count": 3,
                "sha256": "a" * 64,
            },
        )
        self.assertTrue(validation["prior_human_audibility_receipt_accepted"])
        self.assertTrue(validation["audible_windows_verified"])
        self.assertFalse(validation["new_device_audibility_replayed"])
        self.assertFalse(validation["semantic_event_binding_recovered"])
        self.assertFalse(validation["sample_meaning_recovered"])
        self.assertFalse(validation["modern_ui_event_equivalence_recovered"])
        self.assertFalse(validation["login_menu_audio_integrated"])
        self.assertFalse(validation["gate14_complete"])

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_rejects_source_route_and_pcm_drift(self, replay):
        replay.return_value = decoded()

        cases = []
        source = strict_receipt(self.raw)
        source["source_bank"]["sha256"] = "b" * 64
        cases.append((source, "source_bank differs"))

        route = strict_receipt(self.raw)
        route["numeric_route"]["sample_slot"] = 7
        cases.append((route, "numeric route differs"))

        pcm = strict_receipt(self.raw)
        pcm["decoded_pcm"]["sha256"] = "b" * 64
        cases.append((pcm, "decoded PCM differs"))

        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            for receipt, message in cases:
                with self.subTest(message=message):
                    with self.assertRaisesRegex(
                        Gate14WindowsMenuAudioReceiptError,
                        message,
                    ):
                        validate_windows_menu_audio_receipt(receipt, self.raw)

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_semantic_promotion_or_schema_expansion_fails_closed(self, replay):
        replay.return_value = decoded()
        promoted = strict_receipt(self.raw)
        promoted["semantic_event_binding_recovered"] = True

        expanded = strict_receipt(self.raw)
        expanded["semantic_event_name"] = "invented"

        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "semantic_event_binding_recovered must be exactly false",
            ):
                validate_windows_menu_audio_receipt(promoted, self.raw)

            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "schema keys differ",
            ):
                validate_windows_menu_audio_receipt(expanded, self.raw)

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_requires_windows_claim_canonical_backend_and_snd_memory(self, replay):
        replay.return_value = decoded()
        non_windows = strict_receipt(self.raw)
        non_windows["platform_system"] = "Linux"

        wrong_class = strict_receipt(self.raw)
        wrong_class["playback_backend"]["class"] = "SyntheticBackend"

        wrong_flag = strict_receipt(self.raw)
        wrong_flag["playback_backend"]["memory_flag"] = 0

        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            for receipt, message in (
                (non_windows, "Windows platform"),
                (wrong_class, "backend class"),
                (wrong_flag, "SND_MEMORY"),
            ):
                with self.subTest(message=message):
                    with self.assertRaisesRegex(
                        Gate14WindowsMenuAudioReceiptError,
                        message,
                    ):
                        validate_windows_menu_audio_receipt(receipt, self.raw)

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_replay_must_remain_non_silent(self, replay):
        replay.return_value = decoded(slot=None)
        receipt = strict_receipt(self.raw)
        receipt["numeric_route"] = {
            "event_id": 7,
            "state_value": 0,
            "sample_slot": 6,
        }

        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "replays to silence",
            ):
                validate_windows_menu_audio_receipt(receipt, self.raw)

    def test_noncanonical_bank_fails_before_replay(self):
        with patch(
            "gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm"
        ) as replay:
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "canonical source identity",
            ):
                validate_windows_menu_audio_receipt(
                    strict_receipt(self.raw),
                    self.raw,
                )
            replay.assert_not_called()

    def test_private_validation_output_must_be_outside_git_and_new(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "outside Git",
            ):
                _require_private_validation_output(
                    root / "validation.json",
                    repository_root=root,
                )

            outside = Path(temp) / "private" / "validation.json"
            checked = _require_private_validation_output(
                outside,
                repository_root=root,
            )
            self.assertEqual(checked, outside.resolve())
            checked.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "do not overwrite",
            ):
                _require_private_validation_output(
                    outside,
                    repository_root=root,
                )

    def test_cli_writes_only_strict_private_validation_result(self):
        validation = {
            "schema_version": 1,
            "passed": True,
            "deterministic_numeric_route_replay_verified": True,
            "audible_windows_verified": True,
            "new_device_audibility_replayed": False,
            "semantic_event_binding_recovered": False,
            "login_menu_audio_integrated": False,
            "gate14_complete": False,
        }
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "menus.bnk"
            source.write_bytes(self.raw)
            receipt_path = Path(temp) / "receipt.json"
            receipt_path.write_text(
                json.dumps(strict_receipt(self.raw)),
                encoding="utf-8",
            )
            output = Path(temp) / "private" / "validation.json"
            argv = [
                "gate14_windows_menu_audio_receipt.py",
                str(source),
                "--receipt",
                str(receipt_path),
                "--output-validation",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_windows_menu_audio_receipt.validate_windows_menu_audio_receipt",
                    return_value=validation,
                ) as validate,
            ):
                self.assertEqual(receipt_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted, validation)
            validate.assert_called_once()
            self.assertEqual(validate.call_args.args[1], self.raw)


if __name__ == "__main__":
    unittest.main()
