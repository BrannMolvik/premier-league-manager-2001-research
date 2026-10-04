"""Tests for the bounded Gate-14 audible-receipt readiness bridge."""
import unittest

from gate14_audio_readiness_bridge import (
    apply_verified_windows_menu_audio_receipt,
)
from gate14_readiness import Gate14ReadinessError, canonical_gate14_readiness
from gate14_windows_menu_audio_receipt import VerifiedWindowsMenuAudioReceipt


def verified_receipt() -> VerifiedWindowsMenuAudioReceipt:
    return VerifiedWindowsMenuAudioReceipt(
        event_id=17,
        state_value=0,
        sample_slot=6,
        sample_rate=22050,
        channels=1,
        sample_count=3,
        pcm_sha256="a" * 64,
        platform="Windows-11",
        python_version="3.12",
        playback_backend_class="WindowsMemoryWaveMenuPcmBackend",
        playback_memory_flag=4,
    )


class Gate14AudioReadinessBridgeTests(unittest.TestCase):
    def test_validated_receipt_advances_only_audible_windows_evidence(self):
        before = canonical_gate14_readiness()
        after = apply_verified_windows_menu_audio_receipt(
            before,
            verified_receipt(),
        )

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
        self.assertFalse(after.audio_event_binding_recovered)
        self.assertFalse(after.login_menu_audio_integrated)
        self.assertFalse(after.criterion_original_audio_integrated)
        self.assertFalse(after.gate14_ready)
        self.assertNotIn("audible_windows_output", after.blockers)
        self.assertIn("audio_event_binding", after.blockers)
        self.assertIn("login_menu_audio_integration", after.blockers)

    def test_bridge_rejects_unvalidated_objects(self):
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "replay-validated",
        ):
            apply_verified_windows_menu_audio_receipt(
                canonical_gate14_readiness(),
                object(),
            )


if __name__ == "__main__":
    unittest.main()
