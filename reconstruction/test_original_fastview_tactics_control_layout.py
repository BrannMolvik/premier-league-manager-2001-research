"""Exact native modal layout tests; private original executable is opt-in."""
import os
from pathlib import Path
from struct import pack
import unittest

from original_fastview_tactics_control_layout import (
    NATIVE_TACTICS_PANEL_RECT,
    NATIVE_FASTVIEW_MODAL_SIZE,
    NATIVE_ARROW_IMAGE_SIZE,
    NATIVE_ARROW_FRAME_SIZE,
    NATIVE_TACTICS_PLAYER_ROWS,
    NATIVE_RIGHT_VARIANT2_BASE_GLOBAL_VA,
    NATIVE_RIGHT_VARIANT2_X_ADDEND,
    original_fastview_player_arrow_positions,
    original_fastview_bottom_arrow_positions,
    OriginalFastViewTacticsArrowPosition,
)


class OriginalFastViewTacticsControlLayoutTests(unittest.TestCase):
    def test_two_native_popup_backgrounds_are_a_common_bounded_rectangle(self):
        self.assertEqual(NATIVE_FASTVIEW_MODAL_SIZE, (800, 600))
        self.assertEqual(NATIVE_TACTICS_PANEL_RECT, (20, 139, 760, 400))
        self.assertEqual(NATIVE_ARROW_IMAGE_SIZE, (11, 48))
        self.assertEqual(NATIVE_ARROW_FRAME_SIZE, (11, 16))
        self.assertEqual(NATIVE_TACTICS_PLAYER_ROWS, 11)

    def test_original_eleven_rows_and_dynamic_fourth_arrow_are_preserved(self):
        arrows = original_fastview_player_arrow_positions()
        self.assertEqual(len(arrows), 44)
        for row in range(11):
            group = arrows[4 * row:4 * row + 4]
            self.assertEqual([a.arrow_variant_index for a in group], [0, 1, 2, 3])
            self.assertEqual([a.native_y for a in group], [278 + 17 * row] * 4)
            self.assertEqual([a.native_x for a in group], [69, 120, 407, None])
            self.assertEqual(group[3].dynamic_x_global_va, NATIVE_RIGHT_VARIANT2_BASE_GLOBAL_VA)
            self.assertEqual(group[3].dynamic_x_addend, NATIVE_RIGHT_VARIANT2_X_ADDEND)
        self.assertEqual(tuple((a.native_x, a.native_y) for a in
                               original_fastview_bottom_arrow_positions()),
                         ((303, 481), (379, 481)))

    def test_unsupported_layout_claims_are_rejected(self):
        with self.assertRaises(ValueError):
            OriginalFastViewTacticsArrowPosition(0, 4, 69, 278)
        with self.assertRaises(ValueError):
            OriginalFastViewTacticsArrowPosition(0, 3, None, 278)
        with self.assertRaises(ValueError):
            OriginalFastViewTacticsArrowPosition(0, 3, 407, 278, 0x947304, 420)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_all_44_native_arrow_constructor_calls_recover_real_x_y(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        callsites = (
            (0x946E90, 69, (
                0x527FF7, 0x5283EC, 0x5287FD, 0x528C26, 0x52904F,
                0x529481, 0x5298C2, 0x529D0C, 0x52A162, 0x52A5B8, 0x52AA0E)),
            (0x946E50, 120, (
                0x52803E, 0x52843A, 0x52884E, 0x528C77, 0x5290A0,
                0x5294D5, 0x529919, 0x529D66, 0x52A1BC, 0x52A612, 0x52AA68)),
            (0x946E10, 407, (
                0x528231, 0x528635, 0x528A5E, 0x528E87, 0x5292B0,
                0x5296EB, 0x529B35, 0x529F85, 0x52A3DB, 0x52A831, 0x52AC7D)),
            (0x946DD0, None, (
                0x528314, 0x52871C, 0x528B45, 0x528F6E, 0x52939A,
                0x5297D8, 0x529C22, 0x52A075, 0x52A4CB, 0x52A921, 0x52AD6D)),
        )
        for owner, x, source_sites in callsites:
            for row, va in enumerate(source_sites):
                with self.subTest(owner=hex(owner), row=row):
                    y = 278 + 17 * row
                    expected = b"\\x68" + pack("<I", owner)
                    if x is None:
                        expected += b"\\x05" + pack("<I", 420)
                    expected += b"\\x68" + pack("<I", y)
                    if x is None:
                        expected += b"\\x50"
                    elif x < 128:
                        expected += b"\\x6a" + bytes([x])
                    else:
                        expected += b"\\x68" + pack("<I", x)
                    self.assertEqual(pe.read(va, len(expected)), expected)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_two_bottom_controls_both_popups_and_native_rect_writer(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for va, owner, x in ((0x52AE1D, 0x946E90, 303),
                             (0x52AE7A, 0x946E50, 379)):
            with self.subTest(control=hex(owner)):
                expected = b"\\x68" + pack("<I", owner) + b"\\x68" + pack("<I", 481) + b"\\x68" + pack("<I", x)
                self.assertEqual(pe.read(va, len(expected)), expected)
        for va in (0x527DFD, 0x52B746):
            # native 0x64F380 receives y=139 then x=20 and writes
            # [child+0x08/+0x0C] and derived right/bottom fields.
            self.assertEqual(pe.read(va, 7), bytes.fromhex("68 8b 00 00 00 6a 14"))
        self.assertEqual(pe.read(0x64F38F, 0x25),
                         bytes.fromhex(
                             "89 48 08 03 ce 89 50 0c 89 48 10 8b 4c 24 14 "
                             "03 d1 8b 4c 24 18 89 50 14 8b 54 24 1c 85 c9 "
                             "89 48 28 89 50 1c 5e"))


if __name__ == "__main__":
    unittest.main()
