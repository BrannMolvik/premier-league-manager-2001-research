"""Normal Tk PResults source single-user Start return is guarded and transactional."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from front_end_state import FrontEndScreen
from original_game_host import OriginalGameTkHost,OriginalGameHostError
from original_postresults_432505_single_user_return import (
    SourceOriginalSingleUserStartMenuReturn,
    source_original_432505_single_user_startmenu_plan,
)


def source_args():
    return dict(
        original_reached_post_presults_432505=True,
        original_global_date_9847fc=0x2000123,
        original_reached_user_pointer_4139d0=0x1000,
        original_875680_settings_owner_pointer=0,
        original_4290f0_eax_at_43254c=1,
        original_516010_al_at_432559=1,
        original_registered_manager_count_8755e4=1,
        original_413ac0_update_completed=True,
    )


def host():
    h=object.__new__(OriginalGameTkHost)
    screen=SimpleNamespace(screen=FrontEndScreen.MANAGEMENT)
    def return_to_start():
        screen.screen=FrontEndScreen.START_MENU
    session=SimpleNamespace(navigation=screen,
                            source_accepted_return_to_start_menu=Mock(side_effect=return_to_start))
    h.presenter=SimpleNamespace(session=session,hierarchy=object())
    h._original_match_input_owner=lambda:None
    h.pmenu_popup_active=True
    h.management_presenter=object()
    h._squad_drag_source=object()
    h.management_header_state=SimpleNamespace(set_selected=Mock())
    h.first_screen_animation=None
    h.redraw=Mock()
    h.last_status='before'
    return h


class OriginalPostResultsReturnTkTests(TestCase):
    def test_4325df_source_receipt_enters_original_frontend_without_bottom_click(self):
        h=host()
        src=source_original_432505_single_user_startmenu_plan(**source_args())
        h.apply_source_original_postresults_single_user_startmenu(src)
        self.assertEqual(h.presenter.session.navigation.screen,FrontEndScreen.START_MENU)
        h.presenter.session.source_accepted_return_to_start_menu.assert_called_once()
        self.assertFalse(h.pmenu_popup_active)
        self.assertIsNone(h.management_presenter)
        self.assertIsNone(h._squad_drag_source)
        self.assertIsNone(h.presenter.hierarchy)
        h.management_header_state.set_selected.assert_called_once_with(False)
        h.redraw.assert_called_once()
        self.assertIn('4325DF',h.last_status)

    def test_nonmatching_native_source_or_active_match_does_not_change_gui(self):
        h=host()
        src=source_original_432505_single_user_startmenu_plan(**source_args())
        h._original_match_input_owner=lambda:'prematch'
        with self.assertRaises(OriginalGameHostError):
            h.apply_source_original_postresults_single_user_startmenu(src)
        self.assertEqual(h.presenter.session.navigation.screen,FrontEndScreen.MANAGEMENT)
        h.presenter.session.source_accepted_return_to_start_menu.assert_not_called()
        h.redraw.assert_not_called()
        h._original_match_input_owner=lambda:None
        for bad in (None,object(),dict()):
            with self.subTest(bad=type(bad).__name__),self.assertRaises(OriginalGameHostError):
                h.apply_source_original_postresults_single_user_startmenu(bad)
        self.assertEqual(h.presenter.session.navigation.screen,FrontEndScreen.MANAGEMENT)

    def test_typed_receipt_must_not_replace_original_4325df_source_guards(self):
        h=host()
        fake=SourceOriginalSingleUserStartMenuReturn(
            0x2000123,0x1000,2)
        with self.assertRaises(OriginalGameHostError):
            h.apply_source_original_postresults_single_user_startmenu(fake)
        h.presenter.session.navigation.screen=FrontEndScreen.TEAM_SELECT
        good=source_original_432505_single_user_startmenu_plan(**source_args())
        with self.assertRaises(OriginalGameHostError):
            h.apply_source_original_postresults_single_user_startmenu(good)
        h.redraw.assert_not_called()
