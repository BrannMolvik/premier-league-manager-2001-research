import unittest
from types import SimpleNamespace
from unittest.mock import patch
from original_fixtures_pager import (
    fixtures_page_controls, fixtures_page_press, OriginalFixturesPagerArt,
)


class FixturesPagerTests(unittest.TestCase):
    def test_exact_geometry_native_events_and_disabled_bounds(self):
        left, right = fixtures_page_controls(0, 20)
        self.assertEqual((left.rect, right.rect), ((351,213,27,18),(721,213,27,18)))
        self.assertEqual((left.event_id, right.event_id), (39,40))
        self.assertEqual((left.frame,right.frame),(3,0))
        self.assertIsNone(fixtures_page_press((left,right),351,213))
        self.assertEqual(fixtures_page_press((left,right),721,213),right)
        self.assertEqual(tuple(c.frame for c in fixtures_page_controls(8,20)),(0,3))

    def test_descriptor_f_four_frames_priority_and_capture_guard(self):
        for flags, frame in ((0x183,0),(0x18B,2),(0x193,1),(0x19B,1),(0x199,3)):
            right=fixtures_page_controls(0,20,{-1:0x183,1:flags})[1]
            self.assertEqual(right.frame, frame if flags & 2 else 1)
        controls=fixtures_page_controls(0,20,{-1:0x183,1:0x193})
        self.assertIsNone(fixtures_page_press(controls,721,213))
        self.assertEqual(fixtures_page_controls(8,20,{-1:0x183,1:0x19B})[1].frame,3)

    def test_half_open_bounds_and_no_guessed_short_league_geometry(self):
        controls=fixtures_page_controls(0,20)
        for point in ((720,213),(748,213),(721,212),(721,231)):
            self.assertIsNone(fixtures_page_press(controls,*point))
        self.assertIsNotNone(fixtures_page_press(controls,747,230))
        for offset,count in ((True,20),(-1,20),(9,20),(0,11)):
            with self.assertRaises(ValueError): fixtures_page_controls(offset,count)

    def test_host_sends_native_events_on_press_not_release(self):
        from original_game_host import OriginalGameTkHost
        from test_original_game_host import presenter, FakeRoot, FakeTk
        from front_end_state import FrontEndScreen
        live=presenter(); host=OriginalGameTkHost(live,FakeRoot(),FakeTk)
        live.session.navigation.screen=FrontEndScreen.MANAGEMENT
        host.fixtures_pager_art=OriginalFixturesPagerArt((b'\0'*(27*18*4),)*4,(b'\0'*(27*18*4),)*4)
        calls=[]
        panel=SimpleNamespace(panel_class='PLeagueFixtures',league_fixtures=SimpleNamespace(member_club_ids=tuple(range(20))))
        owner=SimpleNamespace(league_fixtures_column_offset=0,snapshot=lambda:panel)
        def accepted(direction):
            calls.append(direction)
            owner.league_fixtures_column_offset=8 if direction==1 else 0
            return SimpleNamespace(column_offset=owner.league_fixtures_column_offset)
        owner.source_accepted_league_fixtures_page=accepted
        host.management_presenter=owner
        with patch('original_game_host.build_management_canvas_frame',return_value=SimpleNamespace(presentation=panel)),patch.object(host,'redraw'):
            host.on_click(SimpleNamespace(x=722,y=214))
            self.assertEqual(calls,[1])
            self.assertEqual(owner.league_fixtures_column_offset,8)
            host.on_script_arrow_release(None)
            self.assertEqual(calls,[1])
            host.on_click(SimpleNamespace(x=352,y=214))
            self.assertEqual(calls,[1,-1])

    def test_real_host_ordinary_press_release_hover_and_modal_guard(self):
        from original_game_host import OriginalGameTkHost
        from test_original_game_host import (
            presenter, FakeRoot, FakeTk, management_factory,
            fake_pmenu_render, fake_squad_top_resources,
            fake_squad_row_text_resources,
        )
        live=presenter()
        pixels=bytes((1,2,3,255))*27*18
        art=OriginalFixturesPagerArt((pixels,)*4,(pixels,)*4)
        with patch('original_game_host.build_management_pmenu_render',side_effect=lambda *_:fake_pmenu_render()):
            host=OriginalGameTkHost(live,FakeRoot(),FakeTk,
                management_presenter_factory=management_factory,
                management_pmenu_resources=object(),
                squad_top_resources=fake_squad_top_resources(),
                squad_row_text_resources=fake_squad_row_text_resources())
            host.on_click(SimpleNamespace(x=141,y=512)); live.choose_club(12)
            host.on_click(SimpleNamespace(x=426,y=301))
            host.management_presenter.navigate(0x25C)
            # Synthetic source bridge has four clubs; qualify only this test's
            # control window. Real-Windows route validates actual twenty clubs.
            host.fixtures_pager_art=art
            controls=fixtures_page_controls(0,20)
            with patch.object(host,'_fixtures_page_controls',return_value=controls), patch.object(host,'redraw'):
                host.on_fixtures_pager_motion(SimpleNamespace(x=722,y=214))
                self.assertTrue(host.fixtures_pager_flags[1]&8)
                host.on_fixtures_pager_leave(None)
                self.assertFalse(host.fixtures_pager_flags[1]&8)
                host.fixtures_pager_flags[1]|=0x10
                host.on_script_arrow_release(None)
                self.assertFalse(host.fixtures_pager_flags[1]&0x10)
        host.active_pmatchinfo_art=object()
        self.assertEqual(host._fixtures_page_controls(),())


if __name__=='__main__': unittest.main()
