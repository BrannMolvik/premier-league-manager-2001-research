from __future__ import annotations

from hashlib import sha256
import unittest

from gate14_font_blend_source_trace import Native16PixelMasks
from gate14_native_rgb_pack import pack_native_rgb16
from gate14_prematch_child_rasters import PrematchChildRaster, PrematchChildRasterLedger
from gate14_prematch_native16_compositor import (
    compose_prematch_native16_frame,
    prematch_native16_compositor_contract,
)
from gate14_prematch_compositor_source import PREMATCH_SELECTOR_CAPTION_STYLE
from original_front_end_layout import OriginalRect


MASKS_565 = Native16PixelMasks(red=0xF800, green=0x07E0, blue=0x001F)


def hidden_child(index: int) -> PrematchChildRaster:
    return PrematchChildRaster(
        child_index=index,
        role=f"hidden_{index}",
        visible=False,
        rect=None,
        rgba=None,
        rgba_sha256=None,
        source_identity=None,
    )


def visible_child(index: int, rgba: bytes, *, role="visible", rect=None, **kwargs):
    if rect is None:
        rect = OriginalRect(0, 0, len(rgba) // 4, 1)
    return PrematchChildRaster(
        child_index=index,
        role=role,
        visible=True,
        rect=rect,
        rgba=rgba,
        rgba_sha256=sha256(rgba).hexdigest(),
        source_identity=f"synthetic:{index}",
        **kwargs,
    )


def ledger_with(*children: PrematchChildRaster) -> PrematchChildRasterLedger:
    items = [hidden_child(index) for index in range(182)]
    for child in children:
        items[child.child_index] = child
    return PrematchChildRasterLedger(children=tuple(items))


def pixel16(frame, x=0, y=0):
    offset = (y * 800 + x) * 2
    return frame.pixels_le[offset] | (frame.pixels_le[offset + 1] << 8)


class PrematchNative16CompositorTests(unittest.TestCase):
    def test_opaque_picture_writes_rgb_even_when_modern_alpha_is_zero(self):
        child = visible_child(0, bytes((255, 0, 0, 0)))
        frame = compose_prematch_native16_frame(
            ledger_with(child),
            masks=MASKS_565,
        )
        self.assertEqual(pixel16(frame), 0xF800)
        self.assertEqual(frame.picture_child_count, 1)
        self.assertEqual(frame.visible_child_count, 1)

    def test_keyed_picture_skips_alpha_zero_and_native_color_key_pixels(self):
        rgba = bytes(
            (
                1, 2, 3, 0,
                255, 0, 255, 255,
                0, 255, 0, 255,
            )
        )
        child = visible_child(10, rgba, rect=OriginalRect(0, 0, 3, 1))
        frame = compose_prematch_native16_frame(
            ledger_with(child),
            masks=MASKS_565,
        )
        self.assertEqual(pixel16(frame, 0), 0)
        self.assertEqual(pixel16(frame, 1), 0)
        self.assertEqual(pixel16(frame, 2), 0x07E0)

    def test_text_child_uses_native_white_font_blend(self):
        child = visible_child(3, bytes((255, 255, 255, 255)))
        frame = compose_prematch_native16_frame(
            ledger_with(child),
            masks=MASKS_565,
        )
        self.assertEqual(pixel16(frame), 0xFFFF)
        self.assertEqual(frame.text_child_count, 1)

    def test_later_text_blends_over_earlier_picture_in_native_child_order(self):
        picture = visible_child(0, bytes((255, 0, 0, 255)))
        text = visible_child(3, bytes((255, 255, 255, 128)))
        frame = compose_prematch_native16_frame(
            ledger_with(picture, text),
            masks=MASKS_565,
        )
        expected = 0xF800
        # Source primitive uses mask-local integer arithmetic with alpha=128.
        inverse = 128
        for mask in (MASKS_565.red, MASKS_565.green, MASKS_565.blue):
            blended = (
                (expected & mask) * inverse
                + (0xFFFF & mask) * 128
            ) >> 8
            expected = (expected & (~mask & 0xFFFF)) | (blended & mask)
        self.assertEqual(pixel16(frame), expected)

    def test_selector_draws_opaque_frame_then_centered_caption_plane(self):
        frame_rgba = bytes((0, 0, 255, 0))
        selector = visible_child(
            178,
            frame_rgba,
            rect=OriginalRect(0, 0, 1, 1),
            caption_text="X",
            caption_alpha=bytes((255,)),
            caption_alpha_sha256=sha256(bytes((255,))).hexdigest(),
            caption_size=(1, 1),
            caption_origin=(0, 0),
            caption_native_color_16=0x0000,
            caption_native_style=PREMATCH_SELECTOR_CAPTION_STYLE,
        )
        frame = compose_prematch_native16_frame(
            ledger_with(selector),
            masks=MASKS_565,
        )
        self.assertEqual(pixel16(frame), 0x0000)
        self.assertEqual(frame.selector_child_count, 1)

    def test_contract_promotes_only_native16_flattening(self):
        contract = prematch_native16_compositor_contract()
        self.assertTrue(contract["picture_write_modes_source_closed"])
        self.assertTrue(contract["text_packed16_blend_reused"])
        self.assertTrue(contract["selector_frame_then_caption_order_source_closed"])
        self.assertTrue(contract["flattened_native16_frame_available"])
        self.assertFalse(contract["runtime_masks_observed_from_original"])
        self.assertFalse(contract["packed16_to_modern_rgba_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_pack_helper_agrees_with_known_synthetic_565_endpoints(self):
        self.assertEqual(pack_native_rgb16(255, 0, 0, MASKS_565), 0xF800)
        self.assertEqual(pack_native_rgb16(0, 255, 0, MASKS_565), 0x07E0)
        self.assertEqual(pack_native_rgb16(0, 0, 255, MASKS_565), 0x001F)


if __name__ == "__main__":
    unittest.main()
