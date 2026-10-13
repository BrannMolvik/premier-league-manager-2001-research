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
    NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_WIDTH,
    NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_X,
    NATIVE_RIGHT_VARIANT2_BOX_RESOURCE_PATH,
    NATIVE_HUMAN_TACTICS_SELECTOR_CONTROL_POSITIONS,
    NATIVE_HUMAN_TACTICS_SCROLLER_ART,
    NATIVE_HUMAN_TACTICS_SCROLLER_ATLAS_SIZE,
    NATIVE_HUMAN_TACTICS_SCROLLER_CROP_SIZE,
    NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_OWNER,
    NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_OWNER,
    NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_SOURCE_Y,
    NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_SOURCE_Y,
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
        self.assertEqual(NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_WIDTH, 124)
        self.assertEqual(NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_X, 544)
        self.assertEqual(NATIVE_RIGHT_VARIANT2_BOX_RESOURCE_PATH,
                         "FM2001_Art/Generic/GenericButtonsAndBars/name_input_box_7.444")

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
            self.assertEqual(group[3].resolved_native_x(original_box_width=124), 544)
            self.assertEqual(group[3].resolved_native_x(original_box_width=100), 520)
            with self.assertRaises(ValueError):
                group[3].resolved_native_x()
            self.assertEqual(group[0].resolved_native_x(), 69)
        self.assertEqual(tuple((a.native_x, a.native_y) for a in
                               original_fastview_bottom_arrow_positions()),
                         ((303, 481), (379, 481)))

    def test_all_eight_native_human_selector_positions(self):
        self.assertEqual(
            NATIVE_HUMAN_TACTICS_SELECTOR_CONTROL_POSITIONS,
            ((61, 576, 278), (62, 733, 278),
             (63, 576, 334), (64, 733, 334),
             (65, 576, 390), (66, 733, 390),
             (67, 576, 446), (68, 733, 446)),
        )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_eight_native_tactical_event_owner_and_coordinates(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        native_sites = (
            (61, 0x52AEE0, 0x52AF18, 576, 278),
            (62, 0x52AFCD, 0x52B00A, 733, 278),
            (63, 0x52B06E, 0x52B0A6, 576, 334),
            (64, 0x52B156, 0x52B191, 733, 334),
            (65, 0x52B1F2, 0x52B22A, 576, 390),
            (66, 0x52B2DA, 0x52B312, 733, 390),
            (67, 0x52B376, 0x52B3AE, 576, 446),
            (68, 0x52B45E, 0x52B496, 733, 446),
        )
        self.assertEqual(tuple((event, x, y) for event, _, _, x, y in native_sites),
                         NATIVE_HUMAN_TACTICS_SELECTOR_CONTROL_POSITIONS)
        for event, native_event_site, native_geometry_site, x, y in native_sites:
            with self.subTest(event=event):
                self.assertEqual(pe.read(native_event_site, 2), bytes([0x6A, event]))
                expected = bytes([0x68]) + pack("<I", y) + bytes([0x68]) + pack("<I", x)
                self.assertEqual(pe.read(native_geometry_site, len(expected)), expected)

    def test_native_selector_uses_original_scroller_art_not_player_arrows(self):
        self.assertEqual(NATIVE_HUMAN_TACTICS_SCROLLER_ART,
                         "FM2001_Art/Generic/GenericButtonsAndBars/scroller_hori.444")
        self.assertEqual(NATIVE_HUMAN_TACTICS_SCROLLER_ATLAS_SIZE, (100, 36))
        self.assertEqual(NATIVE_HUMAN_TACTICS_SCROLLER_CROP_SIZE, (25, 18))
        self.assertEqual((NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_OWNER,
                          NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_OWNER),
                         (0x947050, 0x947030))
        self.assertEqual((NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_SOURCE_Y,
                          NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_SOURCE_Y), (0, 18))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_native_selector_resource_loader_and_crop_not_arrow_substitution(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites = (
            (0x5F2C44, "68 18 50 83 00"),  # source scroller_hori filename
            (0x5F2C49, "b9 70 70 94 00"),  # actual filename loader owner
            (0x5F2C99, "6a 12 6a 19"),     # 18x25 crop
            (0x5F2CA1, "68 70 70 94 00"),  # same original resource owner
            (0x5F2CA6, "b9 50 70 94 00"),  # left button sprite owner
            (0x5F2CD9, "6a 12 6a 19"),     # same crop size, different source y
            (0x5F2CDD, "6a 12 6a 00"),     # variant source offset 18, x0
            (0x5F2CE1, "68 70 70 94 00"),
            (0x5F2CE6, "b9 30 70 94 00"),  # right button sprite owner
            (0x52AF24, "c7 47 2c 50 70 94 00"), # original selector left
            (0x52B016, "89 5f 2c"),        # selector right sprite pointer assigned
        )
        for address, encoded in sites:
            with self.subTest(address=hex(address)):
                expected = bytes.fromhex(encoded)
                self.assertEqual(pe.read(address, len(expected)), expected)

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
                    expected = bytes([0x68]) + pack("<I", owner)
                    if x is None:
                        expected += bytes([0x05]) + pack("<I", 420)
                    expected += bytes([0x68]) + pack("<I", y)
                    if x is None:
                        expected += bytes([0x50])
                    elif x < 128:
                        expected += bytes([0x6a]) + bytes([x])
                    else:
                        expected += bytes([0x68]) + pack("<I", x)
                    self.assertEqual(pe.read(va, len(expected)), expected)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_two_bottom_controls_both_popups_and_native_rect_writer(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for va, owner, x in ((0x52AE1D, 0x946E90, 303),
                             (0x52AE7A, 0x946E50, 379)):
            with self.subTest(control=hex(owner)):
                expected = bytes([0x68]) + pack("<I", owner) + bytes([0x68]) + pack("<I", 481) + bytes([0x68]) + pack("<I", x)
                self.assertEqual(pe.read(va, len(expected)), expected)
        for va in (0x527DFD, 0x52B746):
            # native 0x64F380 receives y=139 then x=20 and writes
            # [child+0x08/+0x0C] and derived right/bottom fields.
            self.assertEqual(pe.read(va, 7), bytes.fromhex("68 8b 00 00 00 6a 14"))
        # Source box owner 0x9472F0 records its native width at +0x14,
        # which is 0x947304; initial width is 124, not an inferred label width.
        self.assertEqual(pe.read(0x5F26B9, 8),
                         bytes.fromhex("6a 10 6a 7c 6a 00 6a 00"))
        self.assertEqual(pe.read(0x5F26C6, 5),
                         bytes.fromhex("b9 f0 72 94 00"))
        self.assertEqual(pe.read(0x64E58F, 6),
                         bytes.fromhex("89 5e 14 89 6e 18"))
        self.assertEqual(pe.read(0x52830F, 5),
                         bytes.fromhex("a1 04 73 94 00"))
        self.assertEqual(pe.read(0x64F38F, 0x25),
                         bytes.fromhex(
                             "89 48 08 03 ce 89 50 0c 89 48 10 8b 4c 24 14 "
                             "03 d1 8b 4c 24 18 89 50 14 8b 54 24 1c 85 c9 "
                             "89 48 28 89 50 1c 5e"))


if __name__ == "__main__":
    unittest.main()
