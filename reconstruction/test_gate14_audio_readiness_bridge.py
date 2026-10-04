"""Tests for the strict Windows-audio to Gate-14 readiness bridge."""
import unittest
from unittest.mock import patch

from gate14_audio_readiness_bridge import (
    apply_validated_windows_menu_audio_receipt,
)
from gate14_readiness import (
    Gate14ReadinessError,
    canonical_gate14_readiness,
)
from gate14_windows_menu_audio_receipt import Gate14WindowsMenuAudioReceiptError


def validated_result() -> dict:
    return {
        "passed": True,
        "source_bank_verified": True,
        "deterministic_numeric_route_replay_verified": True,
        "prior_human_audibility_receipt_accepted": True,
        "audible_windows_verified": True,
        "new_device_audibility_replayed": False,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "modern_ui_event_equivalence_recovered": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
    }


class Gate14AudioReadinessBridgeTests(unittest.TestCase):
    @patch("gate14_audio_readiness_bridge.validate_windows_menu_audio_receipt")
    def test_strict_validation_advances_only_audible_windows_capability(self, validate):
        validate.return_value = validated_result()
        before = canonical_gate14_readiness()
        receipt = {"private": "schema-1-receipt"}
        bank = b"canonical-private-bank"

        after = apply_validated_windows_menu_audio_receipt(before, receipt, bank)

        validate.assert_called_once_with(receipt, bank)
        self.assertFalse(before.audible_windows_verified)
        self.assertTrue(after.audible_windows_verified)
        self.assertEqual(
            after.audio_event_binding_recovered,
            before.audio_event_binding_recovered,
        )
        self.assertEqual(
            after.login_menu_audio_integrated,
            before.login_menu_audio_integrated,
        )
        self.assertEqual(
            after.complete_fastview_frame_recovered,
            before.complete_fastview_frame_recovered,
        )
        self.assertFalse(after.criterion_original_audio_integrated)
        self.assertFalse(after.gate14_ready)
        self.assertIn("audio_event_binding", after.blockers)
        self.assertNotIn("audible_windows_output", after.blockers)
        self.assertIn("login_menu_audio_integration", after.blockers)

    @patch("gate14_audio_readiness_bridge.validate_windows_menu_audio_receipt")
    def test_bridge_rejects_validator_output_that_promotes_semantics(self, validate):
        promoted = validated_result()
        promoted["semantic_event_binding_recovered"] = True
        validate.return_value = promoted

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "semantic_event_binding_recovered must be false",
        ):
            apply_validated_windows_menu_audio_receipt(
                canonical_gate14_readiness(),
                {"receipt": True},
                b"bank",
            )

    @patch("gate14_audio_readiness_bridge.validate_windows_menu_audio_receipt")
    def test_bridge_rejects_incomplete_validation_result(self, validate):
        incomplete = validated_result()
        incomplete["audible_windows_verified"] = False
        validate.return_value = incomplete

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "audible_windows_verified must be true",
        ):
            apply_validated_windows_menu_audio_receipt(
                canonical_gate14_readiness(),
                {"receipt": True},
                b"bank",
            )

    @patch("gate14_audio_readiness_bridge.validate_windows_menu_audio_receipt")
    def test_strict_receipt_failure_is_wrapped_as_readiness_failure(self, validate):
        validate.side_effect = Gate14WindowsMenuAudioReceiptError("bad receipt")

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "rejected Windows menu-audio evidence",
        ):
            apply_validated_windows_menu_audio_receipt(
                canonical_gate14_readiness(),
                {"receipt": False},
                b"bank",
            )

    def test_bridge_requires_exact_readiness_type(self):
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "requires exact Gate14ReadinessEvidence",
        ):
            apply_validated_windows_menu_audio_receipt(
                object(),
                {"receipt": True},
                b"bank",
            )


if __name__ == "__main__":
    unittest.main()
