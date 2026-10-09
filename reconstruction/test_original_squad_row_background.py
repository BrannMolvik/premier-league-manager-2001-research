from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from front_end_state import FrontEndScreen
from original_squad_presenter import build_squad_row_viewport
from original_squad_resources import squad_view_transition
from original_squad_row_background import (
    SQUAD_CELL_NORMAL_RGB, SQUAD_CELL_HOVER_RGB,
    SQUAD_ROW_INITIAL_PICTURE_FLAGS, build_squad_row_backgrounds,
    squad_cell_frame, squad_row_at_point,
)
import test_original_squad_presenter as squad_fixtures


class SquadBackgroundTests(unittest.TestCase):
    def view(self, slots=(0, None, 1)):
        source = squad_fixtures.OriginalSquadPresenterTests()
        return build_squad_row_viewport(tuple(None if i is None else source.row(i) for i in slots))

    def test_canonical_descriptor5_uses_only_normal_and_enabled_hover(self):
        self.assertEqual(SQUAD_ROW_INITIAL_PICTURE_FLAGS, 0x183)
        self.assertEqual(SQUAD_CELL_NORMAL_RGB, (57, 130, 171))
        self.assertEqual(SQUAD_CELL_HOVER_RGB, (16, 95, 162))
        for flags in range(1024):
            expected = 2 if flags & 2 and flags & 8 else 0
            self.assertEqual(squad_cell_frame(flags), expected)
            self.assertEqual(squad_cell_frame(flags | 0x8000), expected)
        for bad in (True, -1, 1.0, 0x100000000):
            with self.assertRaises(ValueError):
                squad_cell_frame(bad)

    def test_exact_three_cells_holes_and_both_parent_transforms(self):
        actual = build_squad_row_backgrounds(self.view(), self.view((2,)))
        self.assertEqual([row.key for row in actual], [(0, 0), (0, 2), (1, 0)])
        self.assertEqual(actual[0].cells, ((38, 234, 22, 14),
            (65, 234, 38, 14), (108, 234, 154, 14)))
        self.assertEqual(actual[1].row_origin, (37, 267))
        self.assertEqual(actual[2].cells, tuple((x + 381, y, w, h)
            for x, y, w, h in actual[0].cells))
        self.assertIsNone(squad_row_at_point(actual, 50, 251))

    def test_main_and_scf_union_is_half_open_not_bounding_box(self):
        rows = build_squad_row_backgrounds(self.view((0,)))
        for x, y in ((37, 233), (262, 249), (276, 233), (364, 249)):
            self.assertEqual(squad_row_at_point(rows, x, y), (0, 0))
        for x, y in ((36, 233), (263, 240), (275, 240), (365, 240), (50, 250), (50, 232)):
            self.assertIsNone(squad_row_at_point(rows, x, y))

    def test_rejects_non_source_geometry_and_does_not_infer_from_name_colour(self):
        first = self.view((0,))
        differently_selected = replace(first, rows=(replace(first.rows[0],
            display_name_rgb=(217, 210, 62)),))
        self.assertEqual(build_squad_row_backgrounds(first),
                         build_squad_row_backgrounds(differently_selected))
        for bad in (SimpleNamespace(rows=first.rows), replace(first, rows=(
                replace(first.rows[0], y=155),)), replace(first, rows=first.rows * 2)):
            with self.assertRaises(ValueError):
                build_squad_row_backgrounds(bad)

    def host(self):
        from original_game_host import OriginalGameTkHost
        from test_original_game_host import presenter, FakeRoot, FakeTk
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        host.presenter.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.canvas.delete('all')
        frame = SimpleNamespace(presentation=SimpleNamespace(
            panel_class='PSquadScreen', squad_view_transition=squad_view_transition(3),
            squad=self.view(), paired_squad=None))
        self.assertEqual(host._draw_squad_backgrounds(frame), 6)
        return host, frame

    def test_motion_updates_only_cells_without_snapshot_redraw_or_reference_leak(self):
        host, _ = self.host()
        initial_refs = len(host._photos)
        before = host.canvas.delete_count
        with patch.object(host, 'redraw') as redraw, \
                patch.object(host, '_schedule_management_header_update'):
            for _ in range(200):
                host.on_fixtures_pager_motion(SimpleNamespace(x=100, y=240))
            self.assertEqual(host._squad_background_hover, (0, 0))
            self.assertEqual(host.canvas.itemconfigure_count, 3)
            host.on_fixtures_pager_motion(SimpleNamespace(x=300, y=274))
            self.assertEqual(host._squad_background_hover, (0, 2))
            self.assertEqual(host.canvas.itemconfigure_count, 9)
            host.on_fixtures_pager_leave(None)
            self.assertIsNone(host._squad_background_hover)
            self.assertEqual(host.canvas.itemconfigure_count, 12)
            redraw.assert_not_called()
        self.assertEqual(len(host._photos), initial_refs)
        self.assertEqual(host.canvas.delete_count, before)

    def test_hover_does_not_mutate_membership_or_persist_game_flags(self):
        host, frame = self.host()
        before = frame.presentation.squad
        host._update_squad_background_hover(100, 240)
        self.assertIs(frame.presentation.squad, before)
        self.assertEqual(frame.presentation.squad, self.view())

    def test_popup_modal_startup_and_other_panel_do_not_keep_live_targets(self):
        host, frame = self.host()
        host._update_squad_background_hover(100, 240)
        host._startup_media_active = True
        host.on_fixtures_pager_leave(None)
        self.assertEqual(host._squad_background_hover, (0, 0))
        host._startup_media_active = False
        for attr in ('pmenu_popup_active', 'active_pmatchinfo_art'):
            setattr(host, attr, True)
            host._update_squad_background_hover(100, 240)
            self.assertIsNone(host._squad_background_hover)
            setattr(host, attr, False if attr == 'pmenu_popup_active' else None)
            host._update_squad_background_hover(100, 240)
        frame.presentation.panel_class = 'PLeagueFixtures'
        self.assertEqual(host._draw_squad_backgrounds(frame), 0)
        self.assertEqual(host._squad_background_items, {})
        host._update_squad_background_hover(100, 240)
        self.assertIsNone(host._squad_background_hover)

    def test_return_to_first_screen_discards_background_item_ids(self):
        host, _ = self.host()
        host._update_squad_background_hover(100, 240)
        host.presenter.session.navigation.screen = FrontEndScreen.START_MENU
        host.redraw()
        self.assertEqual(host._squad_background_items, {})
        host.on_fixtures_pager_motion(SimpleNamespace(x=100, y=240))
        self.assertIsNone(host._squad_background_hover)


if __name__ == '__main__':
    unittest.main()
