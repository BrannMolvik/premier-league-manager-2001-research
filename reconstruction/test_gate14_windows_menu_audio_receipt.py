"""Tests for strict replay validation of Windows menu-audio receipts."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch
from gate14_windows_menu_audio_receipt import (
    Gate14WindowsMenuAudioReceiptError,
    VerifiedWindowsMenuAudioReceipt,
    load_and_validate_windows_menu_audio_receipt,
    validate_windows_menu_audio_receipt,
)


def decoded(*, slot: int | None = 6, pcm_sha: str = "a" * 64):
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
        pcm_sha256=pcm_sha,
    )


class Gate14WindowsMenuAudioReceiptTests(unittest.TestCase):
    def setUp(self):
        self.raw = b"synthetic-canonical-menus"
        self.identity = {
            "size_bytes": len(self.raw),
            "sha256": sha256(self.raw).hexdigest(),
        }
        self.receipt = {
            "schema_version": 1,
            "passed": True,
            "platform_system": "Windows",
            "platform": "Windows-11-test",
            "python_version": "3.12.test",
            "source_bank": {
                "filename": "menus.bnk",
                **self.identity,
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
            "evidence_limit": "bounded",
        }

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_valid_receipt_replays_canonical_source_route_and_pcm(self, decode):
        decode.return_value = decoded()
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            verified = validate_windows_menu_audio_receipt(
                self.receipt,
                self.raw,
            )

        decode.assert_called_once_with(self.raw, 17, 0)
        self.assertIsInstance(verified, VerifiedWindowsMenuAudioReceipt)
        self.assertEqual(verified.event_id, 17)
        self.assertEqual(verified.sample_slot, 6)
        self.assertEqual(verified.sample_count, 3)
        self.assertTrue(verified.source_identity_replayed)
        self.assertTrue(verified.numeric_route_replayed)
        self.assertTrue(verified.pcm_identity_replayed)
        self.assertTrue(verified.audible_windows_verified)
        self.assertFalse(verified.semantic_event_binding_recovered)
        self.assertFalse(verified.sample_meaning_recovered)
        self.assertFalse(verified.modern_ui_event_equivalence_recovered)
        self.assertFalse(verified.login_menu_audio_integrated)
        self.assertFalse(verified.gate14_complete)

    def test_receipt_flags_are_exact_and_cannot_promote_integration(self):
        for field, bad in (
            ("passed", False),
            ("adapter_delivery_completed", False),
            ("human_audibility_confirmation", False),
            ("audible_windows_verified", False),
            ("numeric_routing_recovered", False),
            ("sample_decode_recovered", False),
            ("semantic_event_binding_recovered", True),
            ("sample_meaning_recovered", True),
            ("modern_ui_event_equivalence_recovered", True),
            ("login_menu_audio_integrated", True),
            ("gate14_complete", True),
        ):
            with self.subTest(field=field):
                changed = json.loads(json.dumps(self.receipt))
                changed[field] = bad
                with patch.dict(
                    CANONICAL_FM2001_BANK_PROFILES,
                    {"menus.bnk": self.identity},
                ):
                    with self.assertRaisesRegex(
                        Gate14WindowsMenuAudioReceiptError,
                        f"receipt field {field}",
                    ):
                        validate_windows_menu_audio_receipt(
                            changed,
                            self.raw,
                        )

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_source_identity_is_replayed_not_trusted_from_receipt(self, decode):
        decode.return_value = decoded()
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "canonical source identity",
            ):
                validate_windows_menu_audio_receipt(
                    self.receipt,
                    self.raw + b"tampered",
                )

            tampered = json.loads(json.dumps(self.receipt))
            tampered["source_bank"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "source_bank does not match",
            ):
                validate_windows_menu_audio_receipt(
                    tampered,
                    self.raw,
                )
        decode.assert_not_called()

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_route_and_pcm_fields_must_match_canonical_replay(self, decode):
        decode.return_value = decoded()
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            wrong_slot = json.loads(json.dumps(self.receipt))
            wrong_slot["numeric_route"]["sample_slot"] = 7
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "sample slot differs",
            ):
                validate_windows_menu_audio_receipt(
                    wrong_slot,
                    self.raw,
                )

            wrong_pcm = json.loads(json.dumps(self.receipt))
            wrong_pcm["decoded_pcm"]["sha256"] = "b" * 64
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "decoded PCM identity differs",
            ):
                validate_windows_menu_audio_receipt(
                    wrong_pcm,
                    self.raw,
                )

    @patch("gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm")
    def test_original_no_sound_replay_invalidates_audible_receipt(self, decode):
        decode.return_value = decoded(slot=None)
        silent = json.loads(json.dumps(self.receipt))
        silent["numeric_route"] = {
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
                "no-sound path",
            ):
                validate_windows_menu_audio_receipt(
                    silent,
                    self.raw,
                )

    def test_load_helper_rejects_invalid_json_and_replays_valid_file(self):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioReceiptError,
                "could not read valid",
            ):
                load_and_validate_windows_menu_audio_receipt(
                    bad,
                    self.raw,
                )

            good = Path(temp) / "good.json"
            good.write_text(
                json.dumps(self.receipt),
                encoding="utf-8",
            )
            with (
                patch.dict(
                    CANONICAL_FM2001_BANK_PROFILES,
                    {"menus.bnk": self.identity},
                ),
                patch(
                    "gate14_windows_menu_audio_receipt.decode_audiohooks_menu_pcm",
                    return_value=decoded(),
                ),
            ):
                verified = load_and_validate_windows_menu_audio_receipt(
                    good,
                    self.raw,
                )
            self.assertEqual(verified.sample_slot, 6)

    def test_verified_object_invariants_reject_promoted_semantics(self):
        verified = VerifiedWindowsMenuAudioReceipt(
            event_id=17,
            state_value=0,
            sample_slot=6,
            sample_rate=22050,
            channels=1,
            sample_count=3,
            pcm_sha256="a" * 64,
            platform="Windows-11",
            python_version="3.12",
        )
        for field in (
            "semantic_event_binding_recovered",
            "sample_meaning_recovered",
            "modern_ui_event_equivalence_recovered",
            "login_menu_audio_integrated",
            "gate14_complete",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14WindowsMenuAudioReceiptError,
                    "cannot promote",
                ):
                    replace(verified, **{field: True})


if __name__ == "__main__":
    unittest.main()
