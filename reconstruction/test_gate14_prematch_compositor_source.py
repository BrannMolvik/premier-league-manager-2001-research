from __future__ import annotations

import unittest

from gate14_prematch_child_rasters import PrematchChildRaster, PrematchChildRasterError
from gate14_prematch_compositor_source import (
    PREMATCH_DDBLT_KEYSRC,
    PREMATCH_DDBLT_WAIT,
    PREMATCH_KEYED_PICTURE_CHILD_INDICES,
    PREMATCH_OPAQUE_PICTURE_CHILD_INDICES,
    PREMATCH_PICTURE_CHILD_INDICES,
    PREMATCH_SELECTOR_CAPTION_STYLE,
    PREMATCH_SELECTOR_CHILD_INDICES,
    PREMATCH_TEXT_CHILD_INDICES,
    prematch_composition_source_contract,
    prematch_picture_write_mode,
    prematch_selector_caption_color16,
)
from original_front_end_layout import OriginalRect


class PrematchCompositorSourceTests(unittest.TestCase):
    def test_control_type_partition_covers_all_native_children(self):
        picture = set(PREMATCH_PICTURE_CHILD_INDICES)
        text = set(PREMATCH_TEXT_CHILD_INDICES)
        selectors = set(PREMATCH_SELECTOR_CHILD_INDICES)
        self.assertEqual(len(PREMATCH_KEYED_PICTURE_CHILD_INDICES), 72)
        self.assertEqual(len(PREMATCH_OPAQUE_PICTURE_CHILD_INDICES), 21)
        self.assertEqual(len(picture), 93)
        self.assertFalse(picture & text)
        self.assertFalse(picture & selectors)
        self.assertFalse(text & selectors)
        self.assertEqual(picture | text | selectors, set(range(182)))

    def test_picture_write_modes_match_source_style_split(self):
        for child_index in PREMATCH_KEYED_PICTURE_CHILD_INDICES:
            self.assertEqual(
                prematch_picture_write_mode(child_index),
                "source_color_key",
            )
        for child_index in PREMATCH_OPAQUE_PICTURE_CHILD_INDICES:
            self.assertEqual(prematch_picture_write_mode(child_index), "opaque")
        with self.assertRaises(ValueError):
            prematch_picture_write_mode(3)

    def test_source_contract_keeps_directdraw_flags_and_frame_fail_closed(self):
        contract = prematch_composition_source_contract()
        self.assertEqual(
            contract["keyed_style_flags"],
            PREMATCH_DDBLT_WAIT | PREMATCH_DDBLT_KEYSRC,
        )
        self.assertEqual(contract["opaque_style_flags"], PREMATCH_DDBLT_WAIT)
        self.assertEqual(contract["picture_alpha_endpoint"], 0x100)
        self.assertTrue(contract["text_requires_runtime_native_masks"])
        self.assertFalse(contract["fixed_rgb555_or_rgb565_claim"])
        self.assertFalse(contract["flattened_frame_available"])
        self.assertFalse(contract["gate14_complete"])

    def test_selector_caption_color_tracks_native_button_group(self):
        self.assertEqual(prematch_selector_caption_color16(0), 0xFFFF)
        self.assertEqual(prematch_selector_caption_color16(10), 0xFFFF)
        self.assertEqual(prematch_selector_caption_color16(11), 0x0000)
        self.assertEqual(prematch_selector_caption_color16(21), 0x0000)
        self.assertEqual(prematch_selector_caption_color16(22), 0xFFFF)

    def test_child_raster_accepts_complete_selector_caption_plane(self):
        alpha = bytes((0, 64, 255, 0))
        child = PrematchChildRaster(
            child_index=178,
            role="selector",
            visible=True,
            rect=OriginalRect(10, 20, 2, 2),
            rgba=bytes((1, 2, 3, 0) * 4),
            rgba_sha256="4c1b6f3ca847a04b4850c9c9d79a9bc2d85aa74fb59c7c0ee3c8d74a5ea40309",
            source_identity="selector_frame:0",
            caption_text="A",
            caption_alpha=alpha,
            caption_alpha_sha256="57f36c4033200e47411813d79b3a28406bb02c66efda4d15d162d62cd2d74866",
            caption_size=(2, 2),
            caption_origin=(10, 20),
            caption_native_color_16=0xFFFF,
            caption_native_style=PREMATCH_SELECTOR_CAPTION_STYLE,
        )
        self.assertEqual(child.caption_text, "A")

    def test_child_raster_rejects_partial_selector_caption_plane(self):
        with self.assertRaises(PrematchChildRasterError):
            PrematchChildRaster(
                child_index=178,
                role="selector",
                visible=True,
                rect=OriginalRect(10, 20, 1, 1),
                rgba=bytes((1, 2, 3, 255)),
                rgba_sha256="d77b3fb798a0968c1dca4fa26d3fe4d38d349ec0c276b9d8e494bbfa0dc3f10e",
                source_identity="selector_frame:0",
                caption_text="A",
            )


if __name__ == "__main__":
    unittest.main()
