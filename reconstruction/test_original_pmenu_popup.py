import unittest
from types import SimpleNamespace
from unittest.mock import patch
from original_pmenu_popup import pmenu_open_press, pmenu_app_pointer_dismiss


class PMenuPopupTests(unittest.TestCase):
    def test_exact_native_open_control_and_repeat_gate(self):
        for point in ((599, 0), (698, 94)):
            self.assertTrue(pmenu_open_press(*point, active=False))
            self.assertFalse(pmenu_open_press(*point, active=True))
        for point in ((598, 0), (699, 0), (599, -1), (599, 95)):
            self.assertFalse(pmenu_open_press(*point, active=False))

    def test_exact_application_dismissal_guards(self):
        self.assertTrue(pmenu_app_pointer_dismiss(523, 214))
        self.assertFalse(pmenu_app_pointer_dismiss(524, 214))
        self.assertTrue(pmenu_app_pointer_dismiss(701, 95))
        self.assertFalse(pmenu_app_pointer_dismiss(700, 95))
        self.assertFalse(pmenu_app_pointer_dismiss(701, 96))

    def test_popup_initially_closed_source_open_and_pointer_dismiss(self):
        from original_game_host import OriginalGameTkHost
        from test_original_game_host import presenter, FakeTk, FakeRoot
        from front_end_state import FrontEndScreen
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk)
        self.assertFalse(host.pmenu_popup_active)
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = object()
        with patch('original_game_host.build_management_canvas_frame'), patch.object(host, 'redraw'):
            host.on_click(SimpleNamespace(x=600, y=1))
            self.assertTrue(host.pmenu_popup_active)
            with patch.object(host, '_fixtures_page_controls', return_value=()):
                host.on_fixtures_pager_motion(SimpleNamespace(x=523, y=214))
            self.assertFalse(host.pmenu_popup_active)

    def test_popup_owns_input_and_cannot_open_hidden_fixture_report(self):
        from original_game_host import OriginalGameTkHost
        from test_original_game_host import presenter, FakeTk, FakeRoot
        from front_end_state import FrontEndScreen
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk)
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.pmenu_popup_active = True
        with patch.object(host, 'apply_source_accepted_fixture_match_info') as report:
            host.on_fixture_report_press(SimpleNamespace(x=722, y=240))
            report.assert_not_called()
            self.assertIn('PMenu popup owns input', host.last_status)


if __name__ == '__main__':
    unittest.main()
