"""Tests for the opt-in production first-screen audio evidence hook."""
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock, patch

from gate14_live_first_screen_audio import Gate14LiveFirstScreenAudioError
from original_game_host import OriginalGameHostError, run_original_game_ui


class FakeRoot:
    def __init__(self, order):
        self.order = order

    def mainloop(self):
        self.order.append("mainloop")


class BoundAudioHostHookTests(unittest.TestCase):
    def test_callback_runs_after_mainloop_with_exact_retained_binding(self):
        order = []
        root = FakeRoot(order)
        tk_module = SimpleNamespace(Tk=lambda: root)
        host = SimpleNamespace(first_screen_audio_binding=None)
        binding = object()
        callback = Mock(side_effect=lambda *_args: order.append("callback"))

        with (
            patch.dict(sys.modules, {"tkinter": tk_module}),
            patch("original_game_host.timed_stage", side_effect=lambda *_a, **_k: nullcontext()),
            patch("original_game_host.play_configured_startup_media"),
            patch("original_game_host.build_original_game_presenter", return_value=object()),
            patch("original_game_host.OriginalGameTkHost", return_value=host),
            patch(
                "original_game_host.install_live_first_screen_audio",
                return_value=binding,
            ) as install,
        ):
            run_original_game_ui(
                Path("C:/FM2001"),
                source_root=Path("C:/source"),
                first_screen_audio_audit_callback=callback,
            )

        self.assertEqual(order, ["mainloop", "callback"])
        self.assertIs(host.first_screen_audio_binding, binding)
        install.assert_called_once_with(host, Path("C:/FM2001"))
        callback.assert_called_once_with(host, binding)

    def test_audio_install_failure_is_retained_as_none_for_audit(self):
        order = []
        root = FakeRoot(order)
        tk_module = SimpleNamespace(Tk=lambda: root)
        host = SimpleNamespace(first_screen_audio_binding=object())
        callback = Mock()

        with (
            patch.dict(sys.modules, {"tkinter": tk_module}),
            patch("original_game_host.timed_stage", side_effect=lambda *_a, **_k: nullcontext()),
            patch("original_game_host.play_configured_startup_media"),
            patch("original_game_host.build_original_game_presenter", return_value=object()),
            patch("original_game_host.OriginalGameTkHost", return_value=host),
            patch(
                "original_game_host.install_live_first_screen_audio",
                side_effect=Gate14LiveFirstScreenAudioError("missing audio"),
            ),
            patch("original_game_host.print"),
        ):
            run_original_game_ui(
                Path("C:/FM2001"),
                source_root=Path("C:/source"),
                first_screen_audio_audit_callback=callback,
            )

        self.assertIsNone(host.first_screen_audio_binding)
        callback.assert_called_once_with(host, None)

    def test_non_callable_audit_hook_fails_before_runtime_launch(self):
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "must be callable",
        ):
            run_original_game_ui(
                Path("C:/FM2001"),
                first_screen_audio_audit_callback=object(),
            )


if __name__ == "__main__":
    unittest.main()
