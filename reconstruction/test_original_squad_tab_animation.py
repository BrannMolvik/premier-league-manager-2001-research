from base64 import b64decode
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

from front_end_state import FrontEndScreen
from original_game_host import OriginalGameTkHost, _decode_generated_rgba_png
from original_management_shell import SQUAD_PANEL_CODE
from original_squad_resources import squad_view_transition
from original_squad_tab_animation import OriginalSquadTabAnimation, OriginalSquadTabState
from original_squad_top_controls import build_fresh_squad_top_render, OriginalSquadTopControlsError
from test_original_squad_top_controls import fixture_resources
import test_original_game_host as fixtures


class SquadTabStateTests(unittest.TestCase):
    def test_native_lengths_are_eleven_one_one_not_first_screen_button_lengths(self):
        animation = OriginalSquadTabAnimation()
        self.assertEqual(animation.frames(), (11, 0, 0))
        for control, x in ((3, 37), (4, 113), (5, 189)):
            animation = OriginalSquadTabAnimation()
            animation.observe((x, 171))
            forward = []
            for _ in range(12):
                animation.update()
                forward.append(animation.states[control].source_frame)
            self.assertEqual(forward, [11] * 12 if control == 3 else list(range(1, 11)) + [10, 10])
            self.assertFalse(animation.pending())
            animation.observe(None)
            backward = []
            for _ in range(12):
                animation.update()
                backward.append(animation.states[control].source_frame)
            self.assertEqual(backward, [11] * 12 if control == 3 else list(range(9, -1, -1)) + [0, 0])
            self.assertFalse(animation.pending())

    def test_native_half_open_parent_transformed_containment_and_three_pixel_gaps(self):
        for x, y, target in ((37, 171, 3), (109, 195, 3), (110, 180, None),
                              (112, 180, None), (113, 171, 4), (185, 195, 4),
                              (186, 180, None), (189, 171, 5), (261, 195, 5),
                              (262, 180, None), (113, 170, None), (113, 196, None)):
            animation = OriginalSquadTabAnimation()
            animation.observe((x, y))
            inside = [control for control, state in animation.states.items() if state.flags & 8]
            self.assertEqual(inside, [] if target is None else [target])

    def test_group_transition_rescales_before_hover_and_disabled_uses_physical_row22(self):
        state = OriginalSquadTabState(flags=0x818B, subframe=10)
        state.update()
        self.assertEqual((state.group, state.subframe, state.source_frame), (1, 0, 11))
        state.flags = 0x189
        state.update()
        self.assertEqual((state.group, state.subframe, state.source_frame), (2, 0, 22))
        state.flags = 0x18B
        state.update()
        self.assertEqual((state.group, state.subframe, state.source_frame), (0, 1, 1))
        with self.assertRaisesRegex(ValueError, 'group/subframe'):
            OriginalSquadTabState(group=1, subframe=1).update()

    def test_all_children_receive_the_update(self):
        animation = OriginalSquadTabAnimation()
        animation.states[4].set_pointer_inside(True)
        animation.states[5].set_pointer_inside(True)
        animation.update()
        self.assertEqual(animation.frames(), (11, 1, 1))

    def test_combined_renderer_accepts_live_hover_but_not_unproven_view_state(self):
        resources = fixture_resources()
        rendered = build_fresh_squad_top_render(resources, source_frames=(11, 7, 10))
        buttons = [o for o in rendered.overlays if o.role == 'button']
        self.assertEqual([o.source_index for o in buttons], [11, 7, 10])
        text = [o for o in rendered.overlays if o.role == 'text']
        self.assertEqual([o.native_color_16 for o in text], [0, 0xffff, 0xffff])
        for frames in ((0, 11, 0), (11, 22, 0), (11, True, 0), (11, 0), [11, 0, 0]):
            with self.assertRaisesRegex(OriginalSquadTopControlsError, 'combined-view'):
                build_fresh_squad_top_render(resources, source_frames=frames)


class SquadTabHostTests(unittest.TestCase):
    def host(self):
        host = OriginalGameTkHost(fixtures.presenter(), fixtures.FakeRoot(), fixtures.FakeTk,
                                 squad_top_resources=fixture_resources())
        host.presenter.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = Mock(selected_child_id=SQUAD_PANEL_CODE, squad_view_control_id=3)
        host.canvas.delete('all')
        host._photos = []
        host._draw_squad_top_controls(SimpleNamespace(presentation=SimpleNamespace(
            panel_class='PSquadScreen', squad_view_transition=squad_view_transition(3))))
        return host

    def test_live_hover_in_place_uses_existing_idle_pass_without_snapshot_timer_or_redraw(self):
        host = self.host()
        items = {key: pair[0] for key, pair in host._squad_tab_items.items()}
        deletes, refs = host.canvas.delete_count, len(host._photos)
        forward = []
        with patch.object(host, 'redraw') as redraw, patch.object(host.root, 'after') as timer:
            for pointer in ((113, 171), (-1, -1), (189, 171), (-1, -1)):
                host.on_fixtures_pager_motion(SimpleNamespace(x=pointer[0], y=pointer[1]))
                passes = 0
                while host.root.values.get('idle'):
                    host.root.run_idle()
                    passes += 1
                    self.assertLessEqual(passes, 10)
                    forward.append(host._squad_tab_animation.frames())
                    for control, (item, source) in host._squad_tab_items.items():
                        _x, _y, values = host.canvas.images[item - 1]
                        w, h, pixels = _decode_generated_rgba_png(b64decode(values['image'].data))
                        self.assertEqual((w, h), (73, 25))
                        self.assertEqual(pixels, bytes((source, source, source, 255)) * (73 * 25))
                self.assertEqual(passes, 10)
            redraw.assert_not_called()
            timer.assert_not_called()
            host.management_presenter.snapshot.assert_not_called()
        self.assertIn((11, 10, 0), forward)
        self.assertIn((11, 0, 10), forward)
        self.assertEqual(host._squad_tab_animation.frames(), (11, 0, 0))
        self.assertEqual({key: pair[0] for key, pair in host._squad_tab_items.items()}, items)
        self.assertEqual(host.canvas.delete_count, deletes)
        self.assertEqual(len(host._photos), refs)
        self.assertEqual(len(host.canvas.images), 6)

    def test_popup_modal_other_panel_and_other_screen_do_not_update_hidden_tabs(self):
        for guard in ('popup', 'modal', 'panel', 'screen', 'view'):
            host = self.host()
            host._squad_tab_animation.observe((113, 171))
            if guard == 'popup': host.pmenu_popup_active = True
            if guard == 'modal': host.active_pmatchinfo_art = object()
            if guard == 'panel': host.management_presenter.selected_child_id = -1
            if guard == 'view': host.management_presenter.squad_view_control_id = 4
            if guard == 'screen': host.presenter.session.navigation.screen = FrontEndScreen.START_MENU
            with patch.object(host, 'redraw') as redraw:
                host._advance_management_header()
                redraw.assert_not_called()
            self.assertEqual(host._squad_tab_animation.frames(), (11, 0, 0))
            self.assertEqual(host.canvas.itemconfigure_count, 0)
            host.management_presenter.snapshot.assert_not_called()

    def test_replaced_resource_or_missing_item_requires_full_redraw(self):
        for change in ('resource', 'item'):
            host = self.host()
            if change == 'resource': host.squad_top_resources = fixture_resources()
            else: host._squad_tab_items.pop(5)
            host._squad_tab_animation.observe((113, 171))
            with patch.object(host, 'redraw') as redraw:
                host._advance_management_header()
                redraw.assert_called_once_with()

    def test_header_and_tabs_share_one_scheduled_pass_and_both_advance(self):
        host = self.host()
        host.management_header_resources = fixtures.fake_management_header_resources()
        host._draw_management_header()
        host.management_header_state.set_pointer_inside(True)
        host._squad_tab_animation.observe((113, 171))
        before = host.management_header_state.source_frame()
        host._schedule_management_header_update()
        host._schedule_management_header_update()
        self.assertEqual(len(host.root.values['idle']), 1)
        with patch.object(host, 'redraw') as redraw:
            host.root.run_idle()
            redraw.assert_not_called()
        self.assertNotEqual(host.management_header_state.source_frame(), before)
        self.assertEqual(host._squad_tab_animation.frames(), (11, 1, 0))
        self.assertEqual(len(host.root.values['idle']), 1)
        host.management_presenter.snapshot.assert_not_called()

    def test_full_draw_preserves_hover_frame_and_no_item_belongs_to_non_squad_panel(self):
        host = self.host()
        host._squad_tab_animation.observe((113, 171))
        host._squad_tab_animation.update()
        host.canvas.delete('all')
        host._draw_squad_top_controls(SimpleNamespace(presentation=SimpleNamespace(
            panel_class='PSquadScreen', squad_view_transition=squad_view_transition(3))))
        self.assertEqual(host._squad_tab_items[4][1], 1)
        host._draw_squad_top_controls(SimpleNamespace(presentation=SimpleNamespace(panel_class='PLeagueTables')))
        self.assertEqual(host._squad_tab_items, {})
        self.assertIsNone(host._squad_tab_draw_resources)


if __name__ == '__main__':
    unittest.main()
