from base64 import b64decode
from dataclasses import replace
from unittest.mock import Mock, patch
import unittest

from ea444_decoder import EA444DecodedImage
from front_end_state import FrontEndScreen
from original_game_host import OriginalGameTkHost, _decode_generated_rgba_png
from original_management_header import management_header_overlays
import test_original_game_host as fixtures


class HeaderLayerUpdateTests(unittest.TestCase):
    def host(self):
        resources = fixtures.fake_management_header_resources()
        def stack(width, count):
            return EA444DecodedImage(width, count * 95,
                b''.join(bytes((i, i + 1, i + 2, 255)) * (width * 95)
                         for i in range(count)), 0, 0)
        resources = replace(resources, left_anim=stack(30, 51), right_state=stack(70, 4))
        host = OriginalGameTkHost(fixtures.presenter(), fixtures.FakeRoot(), fixtures.FakeTk,
                                  management_header_resources=resources)
        host.presenter.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = Mock()
        host.canvas.delete('all')
        host._draw_management_header()
        return host

    def test_whole_hover_cycle_updates_exact_pixels_without_game_snapshot_or_canvas_rebuild(self):
        host = self.host()
        items_before = dict(host._management_header_items)
        deletes_before = host.canvas.delete_count
        references_before = len(host._photos)
        frames = []
        with patch.object(host, 'redraw') as redraw:
            for inside in (True, False, True, False):
                host.management_header_state.set_pointer_inside(inside)
                host._schedule_management_header_update()
                steps = 0
                while host.root.values.get('idle'):
                    host.root.run_idle()
                    steps += 1
                    self.assertLess(steps, 60)
                    state = host.management_header_state.source_frame()
                    frames.append((state.left_source_row, state.right_source_row))
                    for overlay in management_header_overlays(host.management_header_resources, state):
                        item, rect = host._management_header_items[overlay.role]
                        x, y, values = host.canvas.images[item - 1]
                        self.assertEqual((x, y, overlay.width, overlay.height), rect)
                        self.assertEqual(_decode_generated_rgba_png(b64decode(values['image'].data)),
                                         (overlay.width, overlay.height, overlay.rgba))
                self.assertFalse(host.management_header_state.pending())
            redraw.assert_not_called()
            host.management_presenter.snapshot.assert_not_called()
        self.assertGreater(len(set(frames)), 10)
        self.assertEqual(host._management_header_items, items_before)
        self.assertEqual(host.canvas.delete_count, deletes_before)
        self.assertEqual(len(host.canvas.images), 3)
        self.assertEqual(len(host._photos), references_before)

    def test_changed_resource_or_owner_set_falls_back_to_full_draw(self):
        for change in ('resources', 'owner'):
            host = self.host()
            if change == 'resources':
                host.management_header_resources = replace(host.management_header_resources)
            else:
                host._management_header_items.pop('left_anim')
            host.management_header_state.set_pointer_inside(True)
            with patch.object(host, 'redraw') as redraw:
                host._advance_management_header()
                redraw.assert_called_once_with()

    def test_other_screen_ignores_pending_management_animation(self):
        host = self.host()
        host.management_header_state.set_pointer_inside(True)
        host.presenter.session.navigation.screen = FrontEndScreen.START_MENU
        with patch.object(host, 'redraw') as redraw:
            host._advance_management_header()
            redraw.assert_not_called()
        self.assertEqual(host.canvas.itemconfigure_count, 0)


if __name__ == '__main__':
    unittest.main()
