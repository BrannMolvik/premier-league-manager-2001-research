"""Tests for the disjoint Gate-14 first-screen host audio wrapper."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from front_end_state import FrontEndScreen
from gate14_audiohooks_menu_playback import (
    Gate14MenuPcmPlaybackError,
    MenuPcmPlaybackSummary,
)
from gate14_first_screen_audio_binding import (
    LIVE_FIRST_SCREEN_NATIVE_GROUP,
    LIVE_FIRST_SCREEN_NATIVE_SUBFRAME,
    Gate14FirstScreenAudioBindingError,
    install_first_screen_press_audio,
)
from original_front_end_layout import PSTARTMENU_ACTIONS


class FakeCanvas:
    def __init__(self):
        self.bindings = {}

    def bind(self, sequence, handler):
        self.bindings[sequence] = handler


class FakeHost:
    def __init__(self, screen, order):
        self.canvas = FakeCanvas()
        self.presenter = SimpleNamespace(
            session=SimpleNamespace(
                navigation=SimpleNamespace(screen=screen)
            )
        )
        self.order = order

    def on_click(self, event):
        self.order.append("host")
        return "host-result"


def center(rect):
    return SimpleNamespace(
        x=rect.x + rect.width // 2,
        y=rect.y + rect.height // 2,
    )


class Gate14FirstScreenAudioBindingTests(unittest.TestCase):
    def test_live_host_fixed_frame_is_source_group0_subframe0(self):
        self.assertEqual(LIVE_FIRST_SCREEN_NATIVE_GROUP, 0)
        self.assertEqual(LIVE_FIRST_SCREEN_NATIVE_SUBFRAME, 0)

    def test_install_rebinds_button1_and_audio_runs_before_host_action(self):
        order = []
        host = FakeHost(FrontEndScreen.START_MENU, order)
        summary = MenuPcmPlaybackSummary(
            event_id=10,
            state_value=0,
            sample_slot=2,
            backend_invoked=True,
            adapter_delivery_completed=True,
        )

        with patch(
            "gate14_first_screen_audio_binding.play_verified_first_screen_action_press",
            side_effect=lambda *args, **kwargs: (order.append("audio"), summary)[1],
        ) as play:
            binding = install_first_screen_press_audio(host, b"bank", object())
            result = host.canvas.bindings["<Button-1>"](
                center(PSTARTMENU_ACTIONS[0].rect)
            )

        self.assertEqual(result, "host-result")
        self.assertEqual(order, ["audio", "host"])
        self.assertEqual(binding.audio_attempt_count, 1)
        self.assertEqual(binding.audio_success_count, 1)
        self.assertIs(binding.last_audio_summary, summary)
        self.assertIsNone(binding.last_audio_error)
        play.assert_called_once_with(
            b"bank",
            unittest.mock.ANY,
            native_group=0,
        )

    def test_non_action_first_screen_pixel_delegates_without_audio(self):
        order = []
        host = FakeHost(FrontEndScreen.START_MENU, order)
        with patch(
            "gate14_first_screen_audio_binding.play_verified_first_screen_action_press"
        ) as play:
            binding = install_first_screen_press_audio(host, b"bank", object())
            result = binding.on_click(SimpleNamespace(x=0, y=0))
        self.assertEqual(result, "host-result")
        self.assertEqual(order, ["host"])
        self.assertEqual(binding.audio_attempt_count, 0)
        play.assert_not_called()

    def test_management_click_delegates_without_first_screen_lookup_or_audio(self):
        order = []
        host = FakeHost(FrontEndScreen.MANAGEMENT, order)
        with patch(
            "gate14_first_screen_audio_binding.play_verified_first_screen_action_press"
        ) as play:
            binding = install_first_screen_press_audio(host, b"bank", object())
            result = binding.on_click(SimpleNamespace(x=181, y=478))
        self.assertEqual(result, "host-result")
        self.assertEqual(order, ["host"])
        play.assert_not_called()

    def test_expected_audio_failure_does_not_block_gameplay_click(self):
        order = []
        host = FakeHost(FrontEndScreen.START_MENU, order)
        with patch(
            "gate14_first_screen_audio_binding.play_verified_first_screen_action_press",
            side_effect=Gate14MenuPcmPlaybackError("device failed"),
        ):
            binding = install_first_screen_press_audio(host, b"bank", object())
            result = binding.on_click(center(PSTARTMENU_ACTIONS[0].rect))

        self.assertEqual(result, "host-result")
        self.assertEqual(order, ["host"])
        self.assertEqual(binding.audio_attempt_count, 1)
        self.assertEqual(binding.audio_success_count, 0)
        self.assertIn("device failed", binding.last_audio_error)
        self.assertIsNone(binding.last_audio_summary)

    def test_binding_keeps_hover_audibility_and_gate_integration_false(self):
        order = []
        host = FakeHost(FrontEndScreen.START_MENU, order)
        binding = install_first_screen_press_audio(host, b"bank", object())
        self.assertTrue(binding.press_binding_integrated)
        self.assertFalse(binding.hover_binding_integrated)
        self.assertFalse(binding.audible_windows_verified)
        self.assertFalse(binding.login_menu_audio_integrated)

    def test_double_install_fails_closed(self):
        order = []
        host = FakeHost(FrontEndScreen.START_MENU, order)
        binding = install_first_screen_press_audio(host, b"bank", object())
        with self.assertRaisesRegex(
            Gate14FirstScreenAudioBindingError,
            "already installed",
        ):
            binding.install()


if __name__ == "__main__":
    unittest.main()
