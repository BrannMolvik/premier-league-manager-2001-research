"""Regression for the opt-in FastView surface on the source-backed host."""
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

import original_game_host
from original_game_host import OriginalGameTkHost


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

    def test_host_method_has_no_hidden_gameplay_or_navigation_trigger(self):
        source = inspect.getsource(
            OriginalGameTkHost.present_completed_match_fastview
        )
        for forbidden in (
            "play_user_fixture",
            "match_simulation",
            "match_calculator",
            "presenter.session",
            "navigation",
            "on_click(",
            "source_accepted_pmenu",
        ):
            self.assertNotIn(forbidden, source)

        host_source = Path(original_game_host.__file__).read_text(encoding="utf-8")
        self.assertEqual(
            host_source.count("present_completed_match_fastview("),
            1,
        )


if __name__ == "__main__":
    unittest.main()
