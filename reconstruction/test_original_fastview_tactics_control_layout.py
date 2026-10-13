"""Exact native modal layout tests; private original executable is opt-in."""
import os
from pathlib import Path
from struct import pack
import unittest

from original_fastview_tactics_control_layout import (
    NATIVE_TACTICS_PANEL_RECT,
    NATIVE_AUXILIARY_PLAYER_ROW_FAMILIES,
    NATIVE_AUXILIARY_EVENT_FIELD_OFFSET,
    NATIVE_FIRST_AUXILIARY_ROW_SIZE,
    NATIVE_FIRST_AUXILIARY_SOURCE_TEXT_BUFFER_FIRST_OFFSET,
    NATIVE_FIRST_AUXILIARY_SOURCE_TEXT_BUFFER_STRIDE,
    NATIVE_FIRST_AUXILIARY_TEXT_RESOURCE_OWNER_VA,
    NATIVE_SECOND_AUXILIARY_DIMENSIONS_OWNER_VA,
    NATIVE_SECOND_AUXILIARY_DIMENSIONS_OFFSETS,
    NATIVE_SECOND_AUXILIARY_RECT_WRAPPER,
    original_fastview_auxiliary_player_row_controls,
    OriginalFastViewTacticsAuxiliaryRowControl,
    NATIVE_FASTVIEW_MODAL_SIZE,
    NATIVE_ARROW_IMAGE_SIZE,
    NATIVE_ARROW_FRAME_SIZE,
    NATIVE_TACTICS_PLAYER_ROWS,
    original_fastview_arrow_frame_word_for_native_flags,
    NATIVE_FASTVIEW_ARROW_FRAME_FLAG_MASK,
    NATIVE_HUMAN_PLAYER_ARROW_PARENT_OFFSETS,
    NATIVE_HUMAN_PLAYER_ARROW_EVENT_BASES,
    NATIVE_HUMAN_PLAYER_ARROW_EVENT_FIELD_OFFSET,
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

    def test_all_forty_four_arrow_art_objects_have_exact_native_event_id(self):
        self.assertEqual(NATIVE_HUMAN_PLAYER_ARROW_PARENT_OFFSETS,
                         (0x1CF4, 0x2038, 0x34D8, 0x3CEC))
        self.assertEqual(NATIVE_HUMAN_PLAYER_ARROW_EVENT_BASES,
                         (0x246E8E, 0x247276, 0x2466BE, 0x246AA6))
        self.assertEqual(NATIVE_HUMAN_PLAYER_ARROW_EVENT_FIELD_OFFSET, 0x20)
        arrows = original_fastview_player_arrow_positions()
        for row in range(11):
            for v in range(4):
                with self.subTest(row=row, variant=v):
                    arrow = arrows[4 * row + v]
                    self.assertEqual(
                        arrow.source_original_native_event_id,
                        NATIVE_HUMAN_PLAYER_ARROW_EVENT_BASES[v] + row
                    )
                    self.assertEqual(
                        arrow.source_original_parent_offset,
                        NATIVE_HUMAN_PLAYER_ARROW_PARENT_OFFSETS[v] + 0x4C * row
                    )
        for arrow in original_fastview_bottom_arrow_positions():
            self.assertIsNone(arrow.source_original_native_event_id)
            self.assertIsNone(arrow.source_original_parent_offset)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_native_four_arrow_child_origins_and_high_event_source_writers(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites = (
            (0x527FC6, "8d be f4 1c 00 00"), # row0 first arrow child +0x1cf4
            (0x52800D, "8d be 38 20 00 00"), # second +0x2038
            (0x5281F9, "8d 9e d8 34 00 00"), # third +0x34d8
            (0x5282D7, "8d 9e ec 3c 00 00"), # fourth +0x3cec
            (0x52E2FB, "be ae 77 88 00"),    # true source ID base
            (0x52E34C, "8d 96 e0 f6 9b ff"),# arrow0 base from source ESIs
            (0x52E352, "8d 8e c8 fa 9b ff"),# arrow1
            (0x52E32C, "8d 96 10 ef 9b ff"),# arrow2
            (0x52E332, "8d 8e f8 f2 9b ff"),# arrow3
            (0x52E359, "89 97 08 e0 ff ff"),# arrow0 ID field at +0x1d14
            (0x52E35F, "89 8f 4c e3 ff ff"),# arrow1 ID field at +0x2058
            (0x52E344, "89 97 ec f7 ff ff"),# arrow2 ID field at +0x34f8
            (0x52E34A, "89 0f"),            # arrow3 ID field at +0x3d0c
            (0x52E36E, "83 c7 4c"),        # native 0x4c sprite array stride
            (0x52E371, "83 fa 0b"),        # 11 full source rows
        )
        for va, hexdump in sites:
            with self.subTest(va=hex(va)):
                expected = bytes.fromhex(hexdump)
                self.assertEqual(pe.read(va, len(expected)), expected)

    def test_original_native_arrow_frame_selects_word_using_bit_two_only(self):
        self.assertEqual(NATIVE_FASTVIEW_ARROW_FRAME_FLAG_MASK, 4)
        for value in (0, 1, 2, 3, 8, 0xFFFF_FFFB):
            with self.subTest(flags=value):
                self.assertEqual(original_fastview_arrow_frame_word_for_native_flags(
                    value, 0x1234, 0xABCD), 0x1234)
        for value in (4, 5, 6, 7, 12, 0xFFFF_FFFF):
            with self.subTest(flags=value):
                self.assertEqual(original_fastview_arrow_frame_word_for_native_flags(
                    value, 0x1234, 0xABCD), 0xABCD)

    def test_original_native_arrow_frame_refuses_invented_signed_or_nonword_state(self):
        for bad in (True, False, -1, 2**32, None, "4"):
            with self.subTest(flags=repr(bad)), self.assertRaises(ValueError):
                original_fastview_arrow_frame_word_for_native_flags(bad, 0, 1)
        for bad in (True, -1, 65536, None, "0"):
            with self.subTest(frame=repr(bad)), self.assertRaises(ValueError):
                original_fastview_arrow_frame_word_for_native_flags(4, 0, bad)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original EXE source not mounted")
    def test_private_source_arrow_frame_word_selection_from_actual_native_flags(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source_sites = (
            (0x651E49, "e8 52 fd ff ff"),     # child calls original 0x651BA0 base
            (0x651E5A, "89 4e 34"),           # stores child selector metadata
            (0x651E62, "89 56 38"),
            (0x651E6A, "89 46 3c"),
            (0x651E72, "66 89 4e 44"),        # true candidate frame WORD
            (0x651E7B, "66 89 56 46"),        # alternate frame WORD
            (0x651E7F, "66 89 46 40"),
            (0x651E83, "66 89 4e 42"),
            (0x651F43, "e8 48 d6 ff ff"),     # 0x651F40 reads source bit2 getter
            (0x651F4C, "66 8b 46 46"),        # flag true returns +0x46
            (0x651F52, "66 8b 46 44"),        # flag false returns +0x44
            (0x651F6A, "66 89 41 44"),        # original frame setter
            (0x651F6E, "66 89 51 46"),
            (0x651F72, "e8 89 d6 ff ff"),     # requests redraw, 0x64f600
            (0x64F590, "8b 41 18"),           # source flags DWORD +0x18
            (0x64F593, "c1 e8 02"),
            (0x64F596, "83 e0 01"),
            (0x64F600, "8b c1"),              # base refresh routine
            (0x64F602, "8b 48 24"),
            (0x64F60D, "e8 3e 3d 00 00"),     # 0x653350 redraw path
        )
        for address, encoded in source_sites:
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



class NativeFastViewRemainingRowControlsTests(unittest.TestCase):
    """Evidence for the 22 other row widgets, not fabricated arrow artwork."""

    def test_complete_original_two_other_row_families(self):
        expected = (
            (0x23D65A, 0x1A34, 0x40, 80, 0x6503F0),
            (0x8877AE, 0x263C, 0x44, 133, 0x5D71A0),
        )
        self.assertEqual(NATIVE_AUXILIARY_PLAYER_ROW_FAMILIES, expected)
        self.assertEqual(NATIVE_AUXILIARY_EVENT_FIELD_OFFSET, 0x20)
        controls = original_fastview_auxiliary_player_row_controls()
        self.assertEqual(len(controls), 22)
        for row in range(11):
            left, right = controls[row * 2:row * 2 + 2]
            self.assertEqual((left.source_row, right.source_row), (row, row))
            self.assertEqual((left.source_event_id, right.source_event_id),
                             (0x23D65A + row, 0x8877AE + row))
            self.assertEqual((left.parent_offset, right.parent_offset),
                             (0x1A34 + 0x40 * row, 0x263C + 0x44 * row))
            self.assertEqual((left.native_x, right.native_x), (80, 133))
            self.assertEqual((left.native_y, right.native_y), (278 + 17 * row,) * 2)
            self.assertEqual((left.source_constructor_va, right.source_constructor_va),
                             (0x6503F0, 0x5D71A0))
            self.assertFalse(left.artwork_identity_verified)
            self.assertFalse(right.artwork_identity_verified)
        with self.assertRaises(ValueError):
            OriginalFastViewTacticsAuxiliaryRowControl(
                0x8877AE, 0, 0x263C, 133, 278, 0x5D71A0,
                artwork_identity_verified=True)
        with self.assertRaises(ValueError):
            OriginalFastViewTacticsAuxiliaryRowControl(
                0x8877AE, 11, 0x263C, 133, 278, 0x5D71A0)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Authenticated private executable not mounted")
    def test_all_22_original_native_x_y_and_actual_constructor_callees(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        # Every call-site independently retrieved from original native
        # 0x527C00..0x52B000 constructor, NOT synthesized from the port.
        source_call_sites = (
            (0x527FBE, 0x5280D8),
            (0x5283AC, 0x5284D2),
            (0x5287BA, 0x5288EC),
            (0x528BE3, 0x528D15),
            (0x52900C, 0x52913E),
            (0x52943B, 0x529576),
            (0x529879, 0x5299BD),
            (0x529CC3, 0x529E0A),
            (0x52A116, 0x52A260),
            (0x52A56C, 0x52A6B6),
            (0x52A9C2, 0x52AB0C),
        )
        self.assertEqual(len(source_call_sites), 11)
        for row, (first, second) in enumerate(source_call_sites):
            y = 278 + row * 17
            with self.subTest(row=row, family="virtual_0x1A34"):
                self.assertEqual(
                    pe.read(first - 9, 7),
                    b"\x68" + pack("<I", y) + b"\x6a\x50"
                )
                self.assertEqual(
                    pe.read(first, 5),
                    b"\xe8" + pack("<i", 0x6503F0 - first - 5)
                )
            with self.subTest(row=row, family="byte_status_0x263C"):
                self.assertEqual(
                    pe.read(second - 12, 10),
                    b"\x68" + pack("<I", y) + b"\x68" + pack("<I", 133)
                )
                self.assertEqual(
                    pe.read(second, 5),
                    b"\xe8" + pack("<i", 0x5D71A0 - second - 5)
                )
        # Last-family source child event writer at screen+0x265C
        # and the other family uses distinct child vtable+8 registration.
        self.assertEqual(pe.read(0x52E2F5, 6),
                         bytes.fromhex("8d 8b 5c 26 00 00"))
        self.assertEqual(pe.read(0x52E2A9, 6),
                         bytes.fromhex("8d ab 34 1a 00 00"))
        self.assertEqual(pe.read(0x52E31B, 6),
                         bytes.fromhex("8d 8e ac 5e 9b ff"))
        self.assertEqual(pe.read(0x52E323, 5),
                         bytes.fromhex("8b cd ff 50 08"))



class NativeFastViewSourceSizedAuxiliaryRectangleTests(unittest.TestCase):
    """Keep exact native rect provenance without guessing a click acceptance."""

    def test_all_original_explicit_rects_and_dynamic_owner_fail_closed(self):
        self.assertEqual(NATIVE_FIRST_AUXILIARY_ROW_SIZE, (40, 16))
        self.assertEqual(NATIVE_SECOND_AUXILIARY_DIMENSIONS_OWNER_VA, 0x877820)
        self.assertEqual(NATIVE_SECOND_AUXILIARY_DIMENSIONS_OFFSETS, (0x14, 0x18))
        self.assertEqual(NATIVE_SECOND_AUXILIARY_RECT_WRAPPER, 0x651A50)
        controls = original_fastview_auxiliary_player_row_controls()
        for row in range(11):
            fixed, dynamic = controls[2*row:2*row+2]
            with self.subTest(row=row):
                self.assertEqual(
                    fixed.native_source_rect_from_original_dimensions(),
                    (80, 278 + 17*row, 40, 16)
                )
                with self.assertRaises(ValueError):
                    dynamic.native_source_rect_from_original_dimensions()
                # These are caller-supplied original owner fields, not
                # reconstructed assumptions about the global bitmap resource.
                self.assertEqual(
                    dynamic.native_source_rect_from_original_dimensions(
                        original_resource_dimensions=(16, 16)
                    ), (133, 278 + 17*row, 16, 16))
                with self.assertRaises(ValueError):
                    fixed.native_source_rect_from_original_dimensions(
                        original_resource_dimensions=(40, 16))

        dynamic = controls[1]
        for invalid in (None, (0, 16), (16, 0), (True, 16),
                        (16, False), (-1, 16), (0x100000000, 1),
                        (16.0, 16), [16, 16], (16,), (16, 16, 16),
                        ("16", 16)):
            with self.subTest(dimensions=repr(invalid)), self.assertRaises(ValueError):
                dynamic.native_source_rect_from_original_dimensions(
                    original_resource_dimensions=invalid)

    def test_each_first_auxiliary_row_uses_real_screen_text_pointer(self):
        self.assertEqual(NATIVE_FIRST_AUXILIARY_SOURCE_TEXT_BUFFER_FIRST_OFFSET, 0x374)
        self.assertEqual(NATIVE_FIRST_AUXILIARY_SOURCE_TEXT_BUFFER_STRIDE, 0x20)
        self.assertEqual(NATIVE_FIRST_AUXILIARY_TEXT_RESOURCE_OWNER_VA, 0x87BEA0)
        controls = original_fastview_auxiliary_player_row_controls()
        for row in range(11):
            first, second = controls[2*row:2*row+2]
            with self.subTest(row=row):
                self.assertEqual(first.native_original_text_buffer_offset,
                                 0x374+0x20*row)
                self.assertEqual(first.native_original_text_resource_owner_va,
                                 0x87BEA0)
                self.assertIsNone(second.native_original_text_buffer_offset)
                self.assertIsNone(second.native_original_text_resource_owner_va)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Authenticated original executable is not mounted")
    def test_original_all_eleven_text_pointer_source_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        first_call_sites = (
            0x527FBE, 0x5283AC, 0x5287BA, 0x528BE3, 0x52900C,
            0x52943B, 0x529879, 0x529CC3, 0x52A116, 0x52A56C,
            0x52A9C2,
        )
        for row, va in enumerate(first_call_sites):
            with self.subTest(row=row):
                self.assertEqual(
                    pe.read(va-0x1B, 6),
                    b"\\x8d\\x86" + pack("<I", 0x374 + 0x20*row)
                )
                self.assertEqual(
                    pe.read(va-18, 5),
                    b"\\x68" + pack("<I", 0x87BEA0)
                )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Authenticated original executable is not mounted")
    def test_all_fixed_row_40x16_and_dynamic_rect_source_chain(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        first_call_sites = (
            0x527FBE, 0x5283AC, 0x5287BA, 0x528BE3, 0x52900C,
            0x52943B, 0x529879, 0x529CC3, 0x52A116, 0x52A56C,
            0x52A9C2,
        )
        for row, va in enumerate(first_call_sites):
            with self.subTest(row=row):
                y = 278+17*row
                self.assertEqual(
                    pe.read(va-13, 11),
                    b"\x6a\x10\x6a\x28\x68" + pack("<I", y) + b"\x6a\x50"
                )
        for va, data in (
            (0x650465, "e8 16 ef ff ff"),   # first control to base rectangle
            (0x5280C7, "68 20 78 87 00"), # second's actual resource arg3
            (0x5280C2, "68 40 78 87 00"), # distinct fourth argument
            (0x5D71AD, "68 60 79 87 00"), # native event owner argument
            (0x651A50, "8b 44 24 0c"),   # resource pointer from arg3
            (0x651A57, "8b 48 18 8b 50 14"),  # height, width from owner
            (0x651A78, "e8 03 d9 ff ff"), # dynamic dims to base rectangle
        ):
            with self.subTest(va=hex(va)):
                expected = bytes.fromhex(data)
                self.assertEqual(pe.read(va, len(expected)), expected)

if __name__ == "__main__":
    unittest.main()
