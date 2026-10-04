"""Tests for the fail-closed synchronous numeric menu PCM playback seam."""
from dataclasses import replace
import unittest
from unittest.mock import Mock, patch

from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch
from gate14_audiohooks_menu_playback import (
    Gate14MenuPcmPlaybackError,
    MenuPcmPlaybackSummary,
    play_audiohooks_menu_pcm,
)


def decoded(*, slot: int | None) -> DecodedMenuPcmDispatch:
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


class Gate14MenuPcmPlaybackTests(unittest.TestCase):
    @patch("gate14_audiohooks_menu_playback.decode_audiohooks_menu_pcm")
    def test_non_silent_result_is_delivered_once_and_only_adapter_completion_is_promoted(
        self,
        decode,
    ):
        item = decoded(slot=6)
        decode.return_value = item
        backend = Mock()
        backend.play.return_value = True

        summary = play_audiohooks_menu_pcm(b"canonical-placeholder", 17, 0, backend)

        decode.assert_called_once_with(b"canonical-placeholder", 17, 0)
        backend.play.assert_called_once_with(item)
        self.assertEqual(summary.sample_slot, 6)
        self.assertTrue(summary.backend_invoked)
        self.assertTrue(summary.adapter_delivery_completed)
        self.assertTrue(summary.numeric_routing_recovered)
        self.assertTrue(summary.sample_decode_recovered)
        self.assertFalse(summary.semantic_event_binding_recovered)
        self.assertFalse(summary.sample_meaning_recovered)
        self.assertFalse(summary.audible_windows_verified)
        self.assertFalse(summary.login_menu_audio_integrated)

    @patch("gate14_audiohooks_menu_playback.decode_audiohooks_menu_pcm")
    def test_silent_route_never_requires_or_invokes_backend(self, decode):
        decode.return_value = decoded(slot=None)
        backend = Mock()

        summary = play_audiohooks_menu_pcm(b"canonical-placeholder", 7, 0, backend)

        backend.play.assert_not_called()
        self.assertIsNone(summary.sample_slot)
        self.assertFalse(summary.backend_invoked)
        self.assertFalse(summary.adapter_delivery_completed)

        # A backend is also unnecessary for an original numeric no-sound route.
        summary_without_backend = play_audiohooks_menu_pcm(
            b"canonical-placeholder", 7, 0, None
        )
        self.assertFalse(summary_without_backend.backend_invoked)

    @patch("gate14_audiohooks_menu_playback.decode_audiohooks_menu_pcm")
    def test_non_silent_route_requires_exact_true_backend_completion(self, decode):
        decode.return_value = decoded(slot=6)
        for result in (None, False, 1):
            with self.subTest(result=result):
                backend = Mock()
                backend.play.return_value = result
                with self.assertRaisesRegex(
                    Gate14MenuPcmPlaybackError,
                    "exact synchronous completion",
                ):
                    play_audiohooks_menu_pcm(
                        b"canonical-placeholder", 17, 0, backend
                    )

        with self.assertRaisesRegex(
            Gate14MenuPcmPlaybackError,
            "requires a backend",
        ):
            play_audiohooks_menu_pcm(b"canonical-placeholder", 17, 0, None)

        with self.assertRaisesRegex(
            Gate14MenuPcmPlaybackError,
            "requires a backend",
        ):
            play_audiohooks_menu_pcm(
                b"canonical-placeholder", 17, 0, object()
            )

    @patch("gate14_audiohooks_menu_playback.decode_audiohooks_menu_pcm")
    def test_backend_exception_is_wrapped_without_completion_claim(self, decode):
        decode.return_value = decoded(slot=6)
        backend = Mock()
        backend.play.side_effect = OSError("device failure")

        with self.assertRaisesRegex(
            Gate14MenuPcmPlaybackError,
            "OSError: device failure",
        ):
            play_audiohooks_menu_pcm(b"canonical-placeholder", 17, 0, backend)

    def test_summary_invariants_forbid_semantic_audible_or_integration_promotion(self):
        summary = MenuPcmPlaybackSummary(
            event_id=17,
            state_value=0,
            sample_slot=6,
            backend_invoked=True,
            adapter_delivery_completed=True,
        )
        for field in (
            "semantic_event_binding_recovered",
            "sample_meaning_recovered",
            "audible_windows_verified",
            "login_menu_audio_integrated",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14MenuPcmPlaybackError,
                    "cannot promote",
                ):
                    replace(summary, **{field: True})

        with self.assertRaisesRegex(
            Gate14MenuPcmPlaybackError,
            "silent numeric route",
        ):
            MenuPcmPlaybackSummary(
                event_id=7,
                state_value=0,
                sample_slot=None,
                backend_invoked=True,
                adapter_delivery_completed=False,
            )


if __name__ == "__main__":
    unittest.main()
