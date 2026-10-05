from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from original_management_header import (
    HEADER_ADVANCE_MASK,
    HEADER_CAPTION_ENGLISH_INDEX,
    HEADER_CAPTION_GLOBAL_VA,
    HEADER_CAPTION_RECT,
    HEADER_CAPTION_STYLE,
    HEADER_CAPTION_TEXT,
    HEADER_COMPOUND_RECT,
    HEADER_ENABLED_MASK,
    HEADER_FONT_OBJECT_VA,
    HEADER_FONT_SOURCE_PATH,
    HEADER_LEFT_GROUP_LENGTHS,
    HEADER_LEFT_RECT,
    HEADER_LEFT_RESOURCE,
    HEADER_RIGHT_GROUP_LENGTHS,
    HEADER_RIGHT_RECT,
    HEADER_RIGHT_RESOURCE,
    HEADER_SELECTED_MASK,
    OriginalManagementHeaderError,
    OriginalManagementHeaderFrame,
    OriginalManagementHeaderResources,
    OriginalManagementHeaderState,
    management_header_caption_overlay,
    management_header_group_for_flags,
    management_header_left_source_row,
    management_header_overlays,
    management_header_right_source_row,
)


class FakeHeaderFont:
    def measure_text(self, text):
        if text != "MENU":
            raise AssertionError(text)
        return 20

    def render_text_alpha(self, text):
        if text != "MENU":
            raise AssertionError(text)
        return SimpleNamespace(width=20, height=5, alpha=bytes([255]) * 100)


def resources(font=None):
    left_rgba = bytearray(30 * 4845 * 4)
    right_rgba = bytearray(70 * 380 * 4)
    return OriginalManagementHeaderResources(
        EA444DecodedImage(30, 4845, bytes(left_rgba), 0, 0),
        EA444DecodedImage(70, 380, bytes(right_rgba), 0, 0),
        FakeHeaderFont() if font is None else font,
    )


class OriginalManagementHeaderTests(unittest.TestCase):
    def test_fixed_source_geometry_resource_and_caption_identity(self):
        self.assertEqual(HEADER_COMPOUND_RECT, (599, 0, 100, 95))
        self.assertEqual(HEADER_LEFT_RECT, (599, 0, 30, 95))
        self.assertEqual(HEADER_RIGHT_RECT, (629, 0, 70, 95))
        self.assertEqual(HEADER_CAPTION_RECT, (631, 62, 70, 30))
        self.assertEqual(HEADER_CAPTION_STYLE, 10)
        self.assertEqual(HEADER_LEFT_RESOURCE.frame_count, 51)
        self.assertEqual(HEADER_RIGHT_RESOURCE.frame_count, 4)
        self.assertEqual(HEADER_LEFT_GROUP_LENGTHS, (26, 1, 0))
        self.assertEqual(HEADER_RIGHT_GROUP_LENGTHS, (2, 1, 1))
        self.assertEqual(
            HEADER_LEFT_RESOURCE.sha256,
            "867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69",
        )
        self.assertEqual(
            HEADER_RIGHT_RESOURCE.sha256,
            "710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb",
        )
        self.assertEqual(HEADER_FONT_SOURCE_PATH, "Fonts/Zurich_XCn_BT_24pixel.fnt")
        self.assertEqual(HEADER_FONT_OBJECT_VA, 0x8B0760)
        self.assertEqual(HEADER_CAPTION_GLOBAL_VA, 0x9820F4)
        self.assertEqual(HEADER_CAPTION_ENGLISH_INDEX, 2497)
        self.assertEqual(HEADER_CAPTION_TEXT, "MENU")

    def test_three_state_selector_matches_shared_source_bits(self):
        self.assertEqual(management_header_group_for_flags(0), 2)
        self.assertEqual(management_header_group_for_flags(HEADER_ENABLED_MASK), 0)
        self.assertEqual(
            management_header_group_for_flags(HEADER_ENABLED_MASK | HEADER_SELECTED_MASK),
            1,
        )

    def test_physical_source_row_mappings_are_bounded(self):
        self.assertEqual(management_header_left_source_row(0, 0), 0)
        self.assertEqual(management_header_left_source_row(0, 25), 25)
        self.assertEqual(management_header_left_source_row(1, 0), 50)
        self.assertIsNone(management_header_left_source_row(2, 0))
        self.assertEqual(
            [management_header_right_source_row(group, 0) for group in range(3)],
            [0, 2, 3],
        )
        self.assertEqual(management_header_right_source_row(0, 1), 1)

    def test_live_hover_advances_and_retreats_without_wall_clock_timer(self):
        state = OriginalManagementHeaderState()
        self.assertEqual(state.source_frame(), OriginalManagementHeaderFrame(0, 0))
        state.set_pointer_inside(True)
        self.assertTrue(state.flags & HEADER_ADVANCE_MASK)
        for _ in range(25):
            self.assertTrue(state.update())
        self.assertEqual(state.source_frame(), OriginalManagementHeaderFrame(25, 1))
        self.assertFalse(state.pending())
        state.set_pointer_inside(False)
        self.assertTrue(state.update())
        self.assertEqual(state.source_frame(), OriginalManagementHeaderFrame(24, 0))

    def test_selected_and_disabled_source_states(self):
        state = OriginalManagementHeaderState()
        state.set_selected(True)
        self.assertTrue(state.update())
        self.assertEqual(state.source_frame(), OriginalManagementHeaderFrame(50, 2))
        self.assertFalse(state.pending())

        state.set_selected(False)
        state.set_enabled(False)
        self.assertTrue(state.update())
        self.assertEqual(state.source_frame(), OriginalManagementHeaderFrame(None, 3))
        self.assertEqual(
            [(item.role, item.source_row) for item in management_header_overlays(
                resources(), state.source_frame()
            )],
            [("right_state", 3)],
        )

    def test_frame_contract_rejects_out_of_atlas_rows(self):
        for left, right in ((-1, 0), (51, 0), (0, -1), (0, 4)):
            with self.assertRaises(OriginalManagementHeaderError):
                OriginalManagementHeaderFrame(left, right)
        self.assertEqual(
            OriginalManagementHeaderFrame(50, 3),
            OriginalManagementHeaderFrame(left_source_row=50, right_source_row=3),
        )
        self.assertEqual(OriginalManagementHeaderFrame(None, 3).left_source_row, None)

    def test_overlay_crop_uses_exact_95px_physical_atlas_rows(self):
        left_rgba = bytearray(30 * 4845 * 4)
        right_rgba = bytearray(70 * 380 * 4)
        left_offset = (17 * 95 * 30) * 4
        right_offset = (2 * 95 * 70) * 4
        left_rgba[left_offset:left_offset + 4] = b"\x01\x02\x03\x04"
        right_rgba[right_offset:right_offset + 4] = b"\x05\x06\x07\x08"

        staged = OriginalManagementHeaderResources(
            EA444DecodedImage(30, 4845, bytes(left_rgba), 0, 0),
            EA444DecodedImage(70, 380, bytes(right_rgba), 0, 0),
            FakeHeaderFont(),
        )
        overlays = management_header_overlays(
            staged,
            OriginalManagementHeaderFrame(17, 2),
        )
        self.assertEqual(
            [(item.role, item.source_row, (item.x, item.y, item.width, item.height))
             for item in overlays],
            [
                ("left_anim", 17, HEADER_LEFT_RECT),
                ("right_state", 2, HEADER_RIGHT_RECT),
            ],
        )
        self.assertEqual(overlays[0].rgba[:4], b"\x01\x02\x03\x04")
        self.assertEqual(overlays[1].rgba[:4], b"\x05\x06\x07\x08")
        self.assertEqual(len(overlays[0].rgba), 30 * 95 * 4)
        self.assertEqual(len(overlays[1].rgba), 70 * 95 * 4)

    def test_menu_caption_uses_recovered_rect_style_and_white_endpoint(self):
        overlay = management_header_caption_overlay(resources())
        self.assertEqual(overlay.text, "MENU")
        self.assertEqual((overlay.x, overlay.y), (681, 62))
        self.assertEqual((overlay.width, overlay.height), (20, 5))
        self.assertEqual(overlay.native_color_16, 0xFFFF)
        self.assertEqual(overlay.rgba[:4], b"\xff\xff\xff\xff")
        self.assertEqual(len(overlay.rgba), 20 * 5 * 4)
        with self.assertRaises(OriginalManagementHeaderError):
            management_header_caption_overlay(resources(), text="Menu")


if __name__ == "__main__":
    unittest.main()
