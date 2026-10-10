"""Regression for the opt-in FastView surface on the source-backed host."""
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

import original_game_host
from original_game_host import OriginalGameHostError, OriginalGameTkHost


class Gate14FastViewHostSurfaceTests(unittest.TestCase):
    def test_host_forwards_existing_presentation_without_navigation_or_simulation(self):
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.root = object()
        host.tk = object()
        host.last_fastview_window = None
        host.last_status = "before"
        presentation = object()
        opened = object()

        with patch.object(
            original_game_host,
            "open_human_fastview_tk_window",
            return_value=opened,
        ) as open_window:
            result = host.present_completed_match_fastview(presentation)

        self.assertIs(result, opened)
        self.assertIs(host.last_fastview_window, opened)
        self.assertIn("partial FastView", host.last_status)
        self.assertIn("trigger remains unrecovered", host.last_status)
        open_window.assert_called_once_with(
            presentation,
            host.tk,
            host.root,
        )

    def test_source_mode_dispatch_opens_fastview_only_for_native_mode_2(self):
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.last_status = "before"
        presentation = object()
        opened = object()

        with patch.object(
            host,
            "present_completed_match_fastview",
            return_value=opened,
        ) as open_fastview:
            result = host.present_completed_match_by_source_mode(
                presentation,
                2,
            )

        self.assertIs(result, opened)
        open_fastview.assert_called_once_with(presentation)

    def test_source_mode_dispatch_keeps_quick_match_wrapper_free(self):
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.last_status = "before"
        presentation = object()

        with patch.object(host, "present_completed_match_fastview") as open_fastview:
            result = host.present_completed_match_by_source_mode(
                presentation,
                3,
            )

        self.assertIsNone(result)
        self.assertIn("no presentation wrapper", host.last_status)
        open_fastview.assert_not_called()

    def test_source_mode_dispatch_refuses_fastview_substitution_for_3d_modes(self):
        presentation = object()
        for mode in (0, 1):
            with self.subTest(mode=mode):
                host = OriginalGameTkHost.__new__(OriginalGameTkHost)
                host.last_status = "before"
                with patch.object(
                    host,
                    "present_completed_match_fastview",
                ) as open_fastview:
                    with self.assertRaisesRegex(
                        OriginalGameHostError,
                        "3D presentation wrapper",
                    ):
                        host.present_completed_match_by_source_mode(
                            presentation,
                            mode,
                        )
                open_fastview.assert_not_called()

    def test_host_method_has_no_hidden_gameplay_or_navigation_trigger(self):
        methods = (
            inspect.getsource(
                OriginalGameTkHost.present_completed_match_fastview
            ),
            inspect.getsource(
                OriginalGameTkHost.present_completed_match_by_source_mode
            ),
        )
        for source in methods:
            for forbidden in (
                "play_user_fixture",
                "match_simulation",
                "match_calculator",
                "self.presenter",
                "self.on_click",
                "source_accepted_pmenu_action(",
            ):
                self.assertNotIn(forbidden, source)

        host_source = Path(original_game_host.__file__).read_text(encoding="utf-8")
        # R1 now source-qualifies one match-completion dispatch from the
        # asynchronous PResults/Quick Match owner. The original declaration is
        # the other occurrence; no arbitrary management click may dispatch.
        self.assertEqual(
            host_source.count("present_completed_match_by_source_mode("),
            2,
        )
        completed = inspect.getsource(
            OriginalGameTkHost._poll_original_management_turn
        )
        self.assertIn(
            "self.present_completed_match_by_source_mode(outcome, auxiliary)",
            completed,
        )
        self.assertNotIn(
            "self.present_completed_match_by_source_mode(",
            inspect.getsource(OriginalGameTkHost.on_click),
        )
        self.assertEqual(
            host_source.count("present_completed_match_fastview("),
            2,
        )


if __name__ == "__main__":
    unittest.main()
