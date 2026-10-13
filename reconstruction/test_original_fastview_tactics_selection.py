"""Tests only a source-verified subset of native human FastView tactics input."""
import struct
import unittest
import os
from pathlib import Path

from original_fastview_tactics_selection import (
    OriginalFastViewTacticsSelectionDraft,
    SOURCE_SELECTOR_RULES,
    SOURCE_SIDE_BUFFER_SIZE,
    SourceFastViewTacticsSelectionError,
    SOURCE_PLAYER_CONTROL_EVENT_FAMILIES,
    SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT,
    source_classify_fastview_player_control_event,
    source_fastview_native_base_dispatch_flags_allow_processing,
    source_fastview_first_callback_8877ae_row,
    source_fastview_guarded_status_allows_followup,
    SOURCE_HUMAN_TACTICS_VTABLE,
    SOURCE_NATIVE_EVENT_OWNER_REGISTRATION,
    SOURCE_NATIVE_BASE_INPUT_DISPATCH,
    SOURCE_NATIVE_CHILD_INPUT_DISPATCH,
    SOURCE_NATIVE_PARENT_CALLBACK_FIRST_SLOT,
    SOURCE_NATIVE_PARENT_CALLBACK_SECOND_SLOT,
    SOURCE_HUMAN_TACTICS_CALLBACK_FIRST,
    SOURCE_HUMAN_TACTICS_CALLBACK_SECOND,
    SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE,
    SOURCE_NATIVE_STATUS_BYTE_GETTER,
    SourceFastViewNativeCandidate,
    source_fastview_native_candidates_52f690,
    source_fastview_redraw_rows_52f690,
    source_fastview_6c2770_side_payload_value_only,
    SourceFastViewAuxChildInputOutcome,
    source_fastview_aux_child_input_outcome_651ac0,
    source_fastview_633020_result_when_original_list_empty,
    SOURCE_FASTVIEW_REPLACEMENT_COUNT_VISITOR_VA,
    SOURCE_FASTVIEW_REPLACEMENT_COUNT_VTABLE,
    SOURCE_FASTVIEW_REPLACEMENT_EDIT_VTABLE,
    SOURCE_FASTVIEW_REPLACEMENT_EDIT_FORWARD_METHOD_VA,
    SOURCE_FASTVIEW_REPLACEMENT_REPLAY_VISITOR_VA,
    SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH,
    source_fastview_original_staged_record_visitor_dispatch,
    OriginalFastViewStagedEditVisitorDispatch,
    source_fastview_633240_count_replacement_records,
    source_fastview_633020_result_without_replacement_records,
    source_fastview_staged_record_native_replay_method,
    SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE_METHODS,
    OriginalFastViewReplayMethodResolution,
    source_fastview_special_replay_record_branch,
    source_fastview_replacement_replay_branch_634b00,
    source_fastview_634b00_matched_chain_payload_value_only,
)


def source_draft(values=(1, 0, 0, 0)):
    words = list(range(70))
    words[0] = 22
    words[1:5] = values
    return OriginalFastViewTacticsSelectionDraft(struct.pack("<70I", *words))


class OriginalFastViewTacticsSelectionDraftTests(unittest.TestCase):
    def test_each_source_pair_cycles_only_its_exact_dword(self):
        for decrease, increase, index, low, high, _keys in SOURCE_SELECTOR_RULES:
            with self.subTest(decrease=decrease):
                values = [1, 0, 0, 0]
                values[index - 1] = low
                base = source_draft(tuple(values))
                down = base.with_original_selector_event_value_only(decrease)
                self.assertEqual(struct.unpack_from("<I", down.original_side_bytes, 4 * index)[0], high)
                self.assertEqual(down.original_side_bytes[:4 * index], base.original_side_bytes[:4 * index])
                self.assertEqual(down.original_side_bytes[4 * index + 4:], base.original_side_bytes[4 * index + 4:])
            with self.subTest(increase=increase):
                values = [1, 0, 0, 0]
                values[index - 1] = high
                base = source_draft(tuple(values))
                up = base.with_original_selector_event_value_only(increase)
                self.assertEqual(struct.unpack_from("<I", up.original_side_bytes, 4 * index)[0], low)
        self.assertEqual(len(source_draft().original_side_bytes), SOURCE_SIDE_BUFFER_SIZE)

    def test_all_four_midrange_changes_are_staged_without_mutating_original(self):
        original = source_draft((2, 1, 2, 1))
        self.assertEqual(original.source_four_values(), (2, 1, 2, 1))
        self.assertEqual(original.with_original_selector_event_value_only(62).source_four_values(), (3, 1, 2, 1))
        self.assertEqual(original.with_original_selector_event_value_only(64).source_four_values(), (2, 2, 2, 1))
        self.assertEqual(original.with_original_selector_event_value_only(66).source_four_values(), (2, 1, 3, 1))
        self.assertEqual(original.with_original_selector_event_value_only(68).source_four_values(), (2, 1, 2, 2))
        self.assertEqual(original.source_four_values(), (2, 1, 2, 1))

    def test_missing_source_contracts_fail_closed(self):
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            OriginalFastViewTacticsSelectionDraft(bytes(279))
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            OriginalFastViewTacticsSelectionDraft(bytearray(280))
        for event in (True, None, 1, 59, 60, 69, 0, -1):
            with self.subTest(event=event), self.assertRaises(SourceFastViewTacticsSelectionError):
                source_draft().with_original_selector_event_value_only(event)
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            source_draft((0, 0, 0, 0)).with_original_selector_event_value_only(61)
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            source_draft((1, 4, 0, 0)).with_original_selector_event_value_only(63)


    def test_exact_six_native_high_event_families_decode_all_sixty_six_controls(self):
        self.assertEqual(SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT, 11)
        self.assertEqual(len(SOURCE_PLAYER_CONTROL_EVENT_FAMILIES), 6)
        all_seen = set()
        for first, family in SOURCE_PLAYER_CONTROL_EVENT_FAMILIES:
            for row in range(11):
                event = first + row
                with self.subTest(event=hex(event)):
                    answer = source_classify_fastview_player_control_event(event)
                    self.assertEqual(answer.family, family)
                    self.assertEqual(answer.native_event_id, event)
                    self.assertEqual(answer.player_row_index, row)
                    self.assertNotIn(event, all_seen)
                    all_seen.add(event)
        self.assertEqual(len(all_seen), 66)


    def test_all_player_row_numeric_wraps_use_supplied_source_map_not_visible_row(self):
        base = [0] * 70
        base[0] = 22
        base[1:5] = (1, 0, 0, 0)
        base[42:53] = list(range(11))
        draft = OriginalFastViewTacticsSelectionDraft(struct.pack("<70I", *base))
        decrease, increase = 0x2466BE, 0x246AA6
        # Visible row0 maps to source player row10; do not assume identity.
        up = draft.with_original_player_row_step_value_only(
            increase, mapped_source_row=10
        )
        self.assertEqual(struct.unpack_from("<I", up.original_side_bytes, 52 * 4)[0], 0)
        self.assertEqual(struct.unpack_from("<I", draft.original_side_bytes, 52 * 4)[0], 10)
        down = draft.with_original_player_row_step_value_only(
            decrease + 10, mapped_source_row=0
        )
        self.assertEqual(struct.unpack_from("<I", down.original_side_bytes, 42 * 4)[0], 10)
        self.assertEqual(up.original_side_bytes[:52 * 4], draft.original_side_bytes[:52 * 4])
        self.assertEqual(down.original_side_bytes[43 * 4:], draft.original_side_bytes[43 * 4:])
        # Same source row can be targeted from a different visible row only
        # when the runtime mapping explicitly supplies it.
        for visible in range(11):
            with self.subTest(visible=visible):
                nxt = draft.with_original_player_row_step_value_only(
                    increase + visible, mapped_source_row=10 - visible
                )
                self.assertEqual(
                    struct.unpack_from("<I", nxt.original_side_bytes,
                                       (42 + 10 - visible) * 4)[0],
                    (10 - visible + 1) % 11
                )

    def test_player_row_mutations_fail_closed_without_live_row_mapping(self):
        base = [0] * 70
        base[1] = 1
        draft = OriginalFastViewTacticsSelectionDraft(struct.pack("<70I", *base))
        for bad_row in (True, False, None, -1, 11, 256, 1.0, "1"):
            with self.subTest(row=repr(bad_row)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                draft.with_original_player_row_step_value_only(
                    0x2466BE, mapped_source_row=bad_row
                )
        for wrong_event in (1, 61, 0x247276, 0x246E8E, 0x8877AE):
            with self.subTest(event=wrong_event), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                draft.with_original_player_row_step_value_only(
                    wrong_event, mapped_source_row=0
                )
        base[42] = 11
        bad = OriginalFastViewTacticsSelectionDraft(struct.pack("<70I", *base))
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            bad.with_original_player_row_step_value_only(
                0x2466BE, mapped_source_row=0
            )

    def test_nearby_unrecognized_or_noninteger_native_events_fail_closed(self):
        valid = {first + row
                 for first, _ in SOURCE_PLAYER_CONTROL_EVENT_FAMILIES
                 for row in range(11)}
        invalid = (None, True, False, 61, 62, 68, 0, -1, 4.0, "0x247276")
        for first, _ in SOURCE_PLAYER_CONTROL_EVENT_FAMILIES:
            invalid += (first - 1, first + 11)
        for event in invalid:
            if type(event) is int and event in valid:
                continue
            with self.subTest(event=repr(event)):
                with self.assertRaises(SourceFastViewTacticsSelectionError):
                    source_classify_fastview_player_control_event(event)



class NativeFastViewCallbackSourceBoundaryTests(unittest.TestCase):
    """Do not promote source callback branches into complete click semantics."""

    def test_all_eleven_first_callback_events_and_unrelated_accepted_events(self):
        self.assertEqual(SOURCE_NATIVE_EVENT_OWNER_REGISTRATION, 0x64F3C0)
        self.assertEqual(SOURCE_NATIVE_BASE_INPUT_DISPATCH, 0x64F7A0)
        self.assertEqual(SOURCE_NATIVE_CHILD_INPUT_DISPATCH, 0x651AC0)
        self.assertEqual(SOURCE_HUMAN_TACTICS_VTABLE, 0x7CACFC)
        self.assertEqual(SOURCE_NATIVE_PARENT_CALLBACK_FIRST_SLOT, 0x0C)
        self.assertEqual(SOURCE_NATIVE_PARENT_CALLBACK_SECOND_SLOT, 0x10)
        self.assertEqual(SOURCE_HUMAN_TACTICS_CALLBACK_FIRST, 0x52E3C0)
        self.assertEqual(SOURCE_HUMAN_TACTICS_CALLBACK_SECOND, 0x52E3F0)
        for row in range(11):
            self.assertEqual(
                source_fastview_first_callback_8877ae_row(
                    SOURCE_HUMAN_TACTICS_FIRST_CALLBACK_EVENT_BASE + row
                ), row
            )
        for other in (0, 1, 61, 68, 0x23D65A, 0x2466BE, 0x8877AD,
                      0x8877B9, 0xFFFFFFFF):
            self.assertIsNone(source_fastview_first_callback_8877ae_row(other))
        for bad in (True, False, None, -1, 0x100000000, "0x8877ae", 1.0):
            with self.subTest(bad=repr(bad)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_first_callback_8877ae_row(bad)

    def test_native_flags_must_pass_both_independent_preconditions(self):
        for f in (0x2, 0x3, 0x6, 0xA, 0xFFFFFFEF):
            with self.subTest(flags=hex(f)):
                self.assertTrue(source_fastview_native_base_dispatch_flags_allow_processing(f))
        for f in (0, 1, 4, 0x10, 0x12, 0x13, 0xFFFFFFFF):
            with self.subTest(flags=hex(f)):
                self.assertFalse(source_fastview_native_base_dispatch_flags_allow_processing(f))
        for bad in (True, False, None, -1, 2**32, "2", 2.0):
            with self.subTest(bad=repr(bad)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_native_base_dispatch_flags_allow_processing(bad)

    def test_status_byte_zero_only_necessary_not_sufficient_for_source_action(self):
        self.assertEqual(SOURCE_NATIVE_STATUS_BYTE_GETTER, 0x651AB0)
        self.assertTrue(source_fastview_guarded_status_allows_followup(0))
        for nonzero in (1, 2, 127, 255):
            self.assertFalse(source_fastview_guarded_status_allows_followup(nonzero))
        for bad in (True, False, -1, None, 256, 0.0, "0"):
            with self.subTest(bad=repr(bad)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_guarded_status_allows_followup(bad)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Owner-verified private original EXE not mounted")
    def test_original_pe_exact_native_dual_callback_and_status_gates(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source = (
            (0x64F3C0, "8b 44 24 04 8b 54 24 08 89 41 20 89 51 24 c2 08 00"),
            (0x52E3C0, "8b 44 24 04 8b 40 20 3d ae 77 88 00"),
            (0x52E3CE, "3d b9 77 88 00"),
            (0x52E3DA, "50 e8 b0 12 00 00"),
            (0x52E3E0, "b8 01 00 00 00 c2 08 00"),
            (0x64F7A5, "8b 46 18 8b c8 d1 e9 f6 c1 01"),
            (0x64F7B5, "c1 e8 04 a8 01"),
            (0x64F7C0, "8b 46 20"),
            (0x64F7D3, "8b 4e 24 53 56 8b 11 ff 52 0c"),
            (0x64F818, "53 56 8b 01 ff 50 10"),
            (0x651ADF, "ff 90 98 00 00 00"),
            (0x651AEC, "ff 92 9c 00 00 00"),
            (0x651AFA, "ff 50 20"),
            (0x651B3F, "8b 46 20 85 c0 74 12"),
            (0x651B4E, "8b 4e 24 55 56 8b 01 ff 50 10"),
            (0x651AB0, "8a 41 40 c3"),
            (0x52EBD6, "8d 8f 3c 26 00 00"),
            (0x52EBDC, "e8 cf 2e 12 00"),
            (0x52EBE1, "84 c0"),
            (0x52EBE3, "0f 85 b9 00 00 00"),
            (0x651B0B, "81 fb ff ff 00 00"),
            (0x651B13, "c6 46 40 01"),
            (0x651B1E, "c6 46 40 00"),
        )
        for va, code in source:
            with self.subTest(va=hex(va)):
                expected = bytes.fromhex(code)
                self.assertEqual(pe.read(va, len(expected)), expected)
        self.assertEqual(
            struct.unpack("<I", pe.read(SOURCE_HUMAN_TACTICS_VTABLE + 0x0C, 4))[0],
            SOURCE_HUMAN_TACTICS_CALLBACK_FIRST
        )
        self.assertEqual(
            struct.unpack("<I", pe.read(SOURCE_HUMAN_TACTICS_VTABLE + 0x10, 4))[0],
            SOURCE_HUMAN_TACTICS_CALLBACK_SECOND
        )


class NativeFastViewRefreshOriginalSourceTests(unittest.TestCase):
    """Source read-only roster/renderer control, not a played match."""

    @staticmethod
    def _fixture():
        source_map = tuple(range(16))
        enabled = [1] * 16
        enabled[12] = 0
        guards = [0] * 16
        guards[13] = 1
        return source_map, tuple(enabled), tuple(guards)

    def test_extra_candidates_start_after_original_first_eleven_and_keep_slot_order(self):
        mapping, enabled, guards = self._fixture()
        kwargs = dict(
            visible_row=0, source_club_roster_count=16,
            source_mapped_player_by_roster_slot=mapping,
            source_enabled_by_player_index=enabled,
            source_club_guard_by_player_index=guards,
        )
        self.assertEqual(
            source_fastview_native_candidates_52f690(
                source_current_row_bypass_byte=0, **kwargs),
            (SourceFastViewNativeCandidate(11, 11),
             SourceFastViewNativeCandidate(14, 14),
             SourceFastViewNativeCandidate(15, 15)),
        )
        # A nonzero native current-row bypass byte suppresses ONLY the
        # club guard check. It never overrides the enabled-byte gate.
        self.assertEqual(
            source_fastview_native_candidates_52f690(
                source_current_row_bypass_byte=1, **kwargs),
            (SourceFastViewNativeCandidate(11, 11),
             SourceFastViewNativeCandidate(13, 13),
             SourceFastViewNativeCandidate(14, 14),
             SourceFastViewNativeCandidate(15, 15)),
        )
        # The selected visible row has its own BYTE remap. Its club guard
        # nonzero also turns on the same bypass, independent of +0xB45.
        guards = list(guards)
        guards[0] = 1
        kwargs["source_club_guard_by_player_index"] = tuple(guards)
        self.assertEqual(
            source_fastview_native_candidates_52f690(
                source_current_row_bypass_byte=0, **kwargs),
            source_fastview_native_candidates_52f690(
                source_current_row_bypass_byte=1, **kwargs),
        )

    def test_actual_mapped_player_indices_not_source_slot_numbers(self):
        mapping = tuple(range(11)) + (15, 14, 13, 12, 11)
        enabled = tuple(1 if i in (11, 12, 13, 14, 15) else 0 for i in range(16))
        guards = (0,) * 16
        self.assertEqual(
            source_fastview_native_candidates_52f690(
                visible_row=0, source_club_roster_count=16,
                source_mapped_player_by_roster_slot=mapping,
                source_enabled_by_player_index=enabled,
                source_club_guard_by_player_index=guards,
                source_current_row_bypass_byte=0,
            ),
            tuple(SourceFastViewNativeCandidate(11 + i, 15 - i) for i in range(5)),
        )
        self.assertEqual(
            source_fastview_native_candidates_52f690(
                visible_row=0, source_club_roster_count=11,
                source_mapped_player_by_roster_slot=tuple(range(11)),
                source_enabled_by_player_index=(1,) * 11,
                source_club_guard_by_player_index=(0,) * 11,
                source_current_row_bypass_byte=0,
            ),
            (),
        )

    def test_redraw_all_vs_one_vs_no_rows_are_distinct_native_paths(self):
        kwargs = dict(visible_row=7, native_popup_selection=0)
        self.assertEqual(
            source_fastview_redraw_rows_52f690(
                native_redraw_all_mode_byte=0,
                native_mapped_player_triplet_flag=0, **kwargs), ())
        self.assertEqual(
            source_fastview_redraw_rows_52f690(
                native_redraw_all_mode_byte=0,
                native_mapped_player_triplet_flag=2, **kwargs), (7,))
        self.assertEqual(
            source_fastview_redraw_rows_52f690(
                native_redraw_all_mode_byte=1,
                native_mapped_player_triplet_flag=2, **kwargs), tuple(range(11)))
        self.assertEqual(
            source_fastview_redraw_rows_52f690(
                visible_row=7, native_popup_selection=11,
                native_redraw_all_mode_byte=0,
                native_mapped_player_triplet_flag=0), tuple(range(11)))

    def test_fail_closed_for_invalid_or_unproven_memory_snapshots(self):
        mapping, enabled, guards = self._fixture()
        kwargs = dict(
            visible_row=0, source_club_roster_count=16,
            source_mapped_player_by_roster_slot=mapping,
            source_enabled_by_player_index=enabled,
            source_club_guard_by_player_index=guards,
            source_current_row_bypass_byte=0,
        )
        invalid = (
            {"visible_row": True}, {"visible_row": 11},
            {"source_club_roster_count": 10},
            {"source_club_roster_count": 17},
            {"source_club_roster_count": True},
            {"source_current_row_bypass_byte": 256},
            {"source_mapped_player_by_roster_slot": list(mapping)},
            {"source_mapped_player_by_roster_slot": mapping[:12]},
            {"source_mapped_player_by_roster_slot": mapping[:-1] + (-1,)},
            {"source_enabled_by_player_index": enabled[:14]},
            {"source_club_guard_by_player_index": guards[:-1]},
        )
        for update in invalid:
            with self.subTest(update=update), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_native_candidates_52f690(**(kwargs | update))
        redraw = dict(visible_row=0, native_popup_selection=0,
                      native_redraw_all_mode_byte=0, native_mapped_player_triplet_flag=0)
        for change in ({"visible_row": False}, {"visible_row": -1},
                       {"native_popup_selection": -1},
                       {"native_popup_selection": 0x100000000},
                       {"native_redraw_all_mode_byte": 256},
                       {"native_mapped_player_triplet_flag": True}):
            with self.subTest(change=change), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_redraw_rows_52f690(**(redraw | change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Owner-verified private original EXE not mounted")
    def test_authenticated_original_pe_offsets_for_refresh_and_dual_click_branch(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source = (
            (0x52F69B, "8b 86 90 00 00 00"),
            (0x52F6A1, "8a 9e 45 0b 00 00"),
            (0x52F6C1, "8a 94 31 46 0b 00 00"),
            (0x52F6C8, "8b a8 cc 4b a1 00"),
            (0x52F6E6, "8a 9c c8 0c 4c a1 00"),
            (0x52F723, "8a 84 0e 46 0b 00 00"),
            (0x52F72C, "8a 84 3e 58 0b 00 00"),
            (0x52F75A, "80 bc 82 0c 4c a1 00 00"),
            (0x52F7D2, "89 3a"),
            (0x52F7D4, "89 48 04"),
            (0x52F7D7, "89 18"),
            (0x52F80D, "c7 84 c6 64 48 00 00 00 00 00 00"),
            (0x52F818, "8b 86 68 0a 00 00"),
            (0x52F822, "8a 86 44 0b 00 00"),
            (0x52F833, "8a 84 0a cf 03 00 00"),
            (0x52F83E, "8d be 3c 26 00 00"),
            (0x52F848, "ff 52 3c"),
            (0x52F872, "8b 94 8e 3c 26 00 00"),
            (0x52F880, "ff 52 3c"),
            (0x52EBDC, "e8 cf 2e 12 00"),
            (0x52EC0D, "e8 0e 44 10 00"),
            (0x52EC15, "84 c0"),
            (0x52EC17, "75 7d"),
            (0x52EC23, "e8 48 3b 19 00"),
            (0x651B4E, "8b 4e 24 55 56 8b 01 ff 50 10"),
        )
        for va, hex_bytes in source:
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(hex_bytes))),
                                 bytes.fromhex(hex_bytes))



class NativeFastViewSideSwapSourceTests(unittest.TestCase):
    """Source primitive value tests; does not bypass native validator."""

    def fixture(self):
        words = [0] * 70
        words[5] = 11
        words[8] = 0x11223344
        words[11] = 0xAABBCCDD
        words[26] = 0x76543210
        words[29] = 0xABCDEF00
        data = bytearray(struct.pack("<70I", *words))
        data[0xF0] = 11
        data[0xF1] = 3
        data[0xF2:0xFD] = bytes(range(11))
        data[0x109] = 9
        return OriginalFastViewTacticsSelectionDraft(bytes(data))

    def test_source_swap_and_two_counters_and_word_copies(self):
        original = self.fixture()
        flags = [0] * 20
        flags[2] = 1
        out = source_fastview_6c2770_side_payload_value_only(
            original, source_from_player_index=2,
            source_to_player_index=5, source_club_guard_flags=tuple(flags))
        self.assertEqual(out.original_side_bytes[0xF2:0xFD],
                         bytes((0, 1, 5, 3, 4, 2, 6, 7, 8, 9, 10)))
        self.assertEqual(out.original_side_bytes[0xF0:0xF2], bytes((10, 4)))
        self.assertEqual(out.original_side_bytes[0x109], 0)
        self.assertEqual(struct.unpack_from("<I", out.original_side_bytes, 0x18 + 4 * 5)[0],
                         0x11223344)
        self.assertEqual(struct.unpack_from("<I", out.original_side_bytes, 0x60 + 4 * 5)[0],
                         0x76543210)
        self.assertEqual(original, self.fixture())
        flags[2], flags[5] = 0, 1
        other = source_fastview_6c2770_side_payload_value_only(
            original, source_from_player_index=2,
            source_to_player_index=5, source_club_guard_flags=tuple(flags))
        self.assertEqual(other.original_side_bytes[0xF1], 2)

    def test_invalid_unknown_native_record_fail_closed(self):
        base = dict(draft=self.fixture(), source_from_player_index=2,
                    source_to_player_index=5, source_club_guard_flags=(0,) * 20)
        for modified in ({"source_from_player_index": True},
                         {"source_to_player_index": 20},
                         {"source_club_guard_flags": (0,) * 4},
                         {"source_club_guard_flags": [0] * 20},
                         {"source_from_player_index": 19},
                         {"draft": None}):
            with self.subTest(modified=modified), self.assertRaises(SourceFastViewTacticsSelectionError):
                source_fastview_6c2770_side_payload_value_only(**(base | modified))
        data = bytearray(self.fixture().original_side_bytes)
        struct.pack_into("<I", data, 0x14, 0)
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            source_fastview_6c2770_side_payload_value_only(
                OriginalFastViewTacticsSelectionDraft(bytes(data)),
                source_from_player_index=2, source_to_player_index=5,
                source_club_guard_flags=(0,) * 20)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_authentic_6c2770_instruction_stubs_and_branch_gate(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        probes = (
            (0x6C2770, "8b 44 24 04"),
            (0x6C277A, "8b 68 14"),
            (0x6C2787, "8a 8c 30 f2 00 00 00"),
            (0x6C27A5, "8a 8c 38 f2 00 00 00"),
            (0x6C27BD, "fe c9"),
            (0x6C27C5, "c6 84 10 04 01 00 00 00"),
            (0x6C27DB, "8b 4c 98 18"),
            (0x6C27DF, "89 4c 90 18"),
            (0x6C27E3, "8b 4c 98 60"),
            (0x6C27E7, "89 4c 90 60"),
            (0x6C2800, "8a 9c ce 0c 4c a1 00"),
            (0x6C280B, "fe 80 f1 00 00 00"),
            (0x6C2815, "8a 8c d6 0c 4c a1 00"),
            (0x6C2823, "fe 88 f1 00 00 00"),
            (0x52EC15, "84 c0"),
            (0x52EC17, "75 7d"),
            (0x52EC23, "e8 48 3b 19 00"),
            (0x52EC46, "e8 85 49 10 00"),
        )
        for va, hx in probes:
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(hx))), bytes.fromhex(hx))



class SourceFastViewAuxiliaryNativeSelectionTests(unittest.TestCase):
    """Do not treat native parent callback as proof of an applied edit."""

    def test_pre_base_denial_has_no_result_fields_or_second_callback(self):
        self.assertEqual(
            source_fastview_aux_child_input_outcome_651ac0(
                base_dispatch_result=0, native_selection_index=None,
                child_has_registered_event=True,
                child_input_callback_argument_nonzero=True,
            ),
            SourceFastViewAuxChildInputOutcome(False, None, None, False),
        )

    def test_sentinal_selection_still_allows_second_parent_callback(self):
        self.assertEqual(
            source_fastview_aux_child_input_outcome_651ac0(
                base_dispatch_result=1, native_selection_index=0xFFFF,
                child_has_registered_event=True,
                child_input_callback_argument_nonzero=True,
            ),
            SourceFastViewAuxChildInputOutcome(False, 1, None, True),
        )

    def test_bounded_selected_index_and_callback_matrix(self):
        for ev in (False, True):
            for arg in (False, True):
                with self.subTest(event=ev, arg=arg):
                    actual = source_fastview_aux_child_input_outcome_651ac0(
                        base_dispatch_result=1, native_selection_index=9,
                        child_has_registered_event=ev,
                        child_input_callback_argument_nonzero=arg,
                    )
                    self.assertEqual(actual,
                        SourceFastViewAuxChildInputOutcome(True, 0, 9, ev and arg))
        self.assertEqual(
            source_fastview_aux_child_input_outcome_651ac0(
                base_dispatch_result=1, native_selection_index=0,
                child_has_registered_event=True,
                child_input_callback_argument_nonzero=True),
            SourceFastViewAuxChildInputOutcome(True, 0, 0, True),
        )

    def test_unproven_native_pointer_selection_inputs_fail_closed(self):
        valid = dict(base_dispatch_result=1, native_selection_index=1,
                     child_has_registered_event=True,
                     child_input_callback_argument_nonzero=False)
        for bad in ({"base_dispatch_result": True},
                    {"base_dispatch_result": -1},
                    {"base_dispatch_result": 0x100000000},
                    {"base_dispatch_result": 0, "native_selection_index": 1},
                    {"native_selection_index": None},
                    {"native_selection_index": -1},
                    {"native_selection_index": 0x10000},
                    {"child_has_registered_event": 1},
                    {"child_input_callback_argument_nonzero": 0}):
            with self.subTest(bad=bad), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_aux_child_input_outcome_651ac0(**(valid | bad))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-authorized private original exe not mounted")
    def test_exact_original_651ac0_selected_index_and_callback_source(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source = (
            (0x651ACB, "e8 d0 dc ff ff"),
            (0x651AD0, "85 c0"),
            (0x651AD2, "75 05"),
            (0x651ADF, "ff 90 98 00 00 00"),
            (0x651AEC, "ff 92 9c 00 00 00"),
            (0x651AFA, "ff 50 20"),
            (0x651B0B, "81 fb ff ff 00 00"),
            (0x651B13, "c6 46 40 01"),
            (0x651B1E, "c6 46 40 00"),
            (0x651B24, "89 5e 3c"),
            (0x651B3F, "8b 46 20"),
            (0x651B46, "8b 44 24 18"),
            (0x651B4E, "8b 4e 24 55 56 8b 01 ff 50 10"),
        )
        for va, hx in source:
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(hx))), bytes.fromhex(hx))




class SourceFastViewOriginalValidatorEmptyListTests(unittest.TestCase):
    """Bounded first-call outcome; nonempty edit replay stays unmodeled."""

    def test_native_empty_edit_list_short_circuits_with_zero_al(self):
        self.assertEqual(
            source_fastview_633020_result_when_original_list_empty(
                original_staged_edit_count=0),
            0
        )

    def test_nonempty_source_edit_list_never_implies_accepted_or_rejected(self):
        for count in (1, 2, 11, 100, 0xFFFFFFFF):
            with self.subTest(count=count), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_633020_result_when_original_list_empty(
                    original_staged_edit_count=count
                )

    def test_invalid_source_counts_fail_closed(self):
        for count in (-1, None, False, True, 0.0, 1.0, "0", 0x100000000):
            with self.subTest(count=repr(count)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_633020_result_when_original_list_empty(
                    original_staged_edit_count=count
                )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private EXE not mounted")
    def test_authenticated_633020_count_visitor_and_polymorphic_replay_gates(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        self.assertEqual(SOURCE_FASTVIEW_REPLACEMENT_COUNT_VISITOR_VA, 0x633240)
        self.assertEqual(SOURCE_FASTVIEW_REPLACEMENT_COUNT_VTABLE, 0x7D803C)
        self.assertEqual(SOURCE_FASTVIEW_REPLACEMENT_EDIT_VTABLE, 0x7D7F90)
        self.assertEqual(SOURCE_FASTVIEW_REPLACEMENT_EDIT_FORWARD_METHOD_VA, 0x633600)
        self.assertEqual(SOURCE_FASTVIEW_REPLACEMENT_REPLAY_VISITOR_VA, 0x6331A0)
        probes = (
            (0x52EBFB, "8d 86 a4 48 00 00"),
            (0x52EC0D, "e8 0e 44 10 00"),
            (0x52EC15, "84 c0 75 7d"),
            (0x63303F, "57 e8 fb 01 00 00"),
            (0x63304E, "3b c6"),
            (0x633058, "0f 84 20 01 00 00"),
            (0x63317E, "8a c1"),
            (0x63317F, "c1"),
            (0x633261, "8d 4c 24 10"),
            (0x633265, "89 74 24 0c"),
            (0x633287, "8b 11 ff 52 04"),
            (0x633295, "8b 74 24 08"),
            (0x6332AE, "8b c6"),
            (0x6331FF, "8b 01 ff 50 04"),
            (0x63320D, "8d 4c 24 0c"),
            (0x633211, "e8 da 1b 00 00"),
            (0x634DF0, "8a 41 09 c3"),
            (0x634E40, "8b 41 04 ff 00 c2 04 00"),
            (0x633600, "8b c1"),
            (0x633607, "8b 11 ff 52 04"),
            (0x6335E1, "c7 06 90 7f 7d 00"),
        )
        for va, h in probes:
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(h))), bytes.fromhex(h))
        import struct as _struct
        self.assertEqual(
            _struct.unpack("<I", pe.read(0x7D803C + 4, 4))[0],
            0x634E40
        )
        self.assertEqual(
            _struct.unpack("<I", pe.read(0x7D7F90 + 4, 4))[0],
            0x633600
        )



class OriginalFastViewEightRecordVisitorSourceTests(unittest.TestCase):
    """The original dispatcher is eight distinct classes, not one swap callback."""

    def test_all_native_record_classes_have_distinct_descending_visitor_slots(self):
        self.assertEqual(len(SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH), 8)
        self.assertEqual(
            [x[2] for x in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH],
            list(range(0x20, 0, -4)))
        self.assertEqual(
            [x[0] for x in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH],
            list(range(0x7D7F3C, 0x7D7F91, 12))
        )
        for table, target, slot in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH:
            with self.subTest(vtable=hex(table)):
                self.assertEqual(
                    source_fastview_original_staged_record_visitor_dispatch(
                        native_record_vtable=table
                    ),
                    OriginalFastViewStagedEditVisitorDispatch(table, target, slot),
                )

    def test_unmapped_base_or_nearby_virtual_table_never_becomes_mutable_edit(self):
        valid = {a for a, _, _ in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH}
        for candidate in (None, True, False, -1, 0, 0x7D7F24, 0x7D7F30, 0x7D7F3D,
                          0x7D7F9C, 0x7D8014, 0x7D803C, 0x100000000, "0x7d7f90"):
            if candidate in valid and type(candidate) is int:
                continue
            with self.subTest(candidate=candidate), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_original_staged_record_visitor_dispatch(
                    native_record_vtable=candidate
                )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-authorized original EXE not mounted")
    def test_original_vtables_and_each_visitor_trampoline_source(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for table, target, slot in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH:
            with self.subTest(vtable=hex(table), slot=hex(slot)):
                self.assertEqual(
                    struct.unpack("<I", pe.read(table + 4, 4))[0], target
                )
                self.assertEqual(pe.read(target, 7),
                                 bytes.fromhex("8b c1 8b 4c 24 04 50"))
                self.assertEqual(pe.read(target + 7, 5),
                                 bytes.fromhex("8b 11 ff 52") + bytes((slot,)))
                self.assertEqual(pe.read(target + 12, 3),
                                 bytes.fromhex("c2 04 00"))
        self.assertEqual(
            struct.unpack("<I", pe.read(0x7D8014 + 4, 4))[0],
            0x634B00
        )
        self.assertEqual(
            struct.unpack("<I", pe.read(0x7D803C + 4, 4))[0],
            0x634E40
        )



class SourceFastViewReplacementOnlyCounterCorrectionTests(unittest.TestCase):
    """A nonempty original edit list can have ZERO replacement records."""

    def test_native_count_ignores_seven_other_original_edit_classes(self):
        all_classes = tuple(vtable for vtable, _, _ in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH)
        self.assertEqual(source_fastview_633240_count_replacement_records(
            original_staged_record_vtables=()), 0)
        self.assertEqual(source_fastview_633240_count_replacement_records(
            original_staged_record_vtables=all_classes[:-1]), 0)
        self.assertEqual(source_fastview_633240_count_replacement_records(
            original_staged_record_vtables=all_classes), 1)
        self.assertEqual(source_fastview_633240_count_replacement_records(
            original_staged_record_vtables=(0x7D7F90, 0x7D7F48, 0x7D7F90)), 2)

    def test_native_zero_count_permits_other_class_only_before_independent_gates(self):
        for record_types in ((), (0x7D7F84,), (0x7D7F3C, 0x7D7F48, 0x7D7F78)):
            with self.subTest(records=record_types):
                self.assertEqual(
                    source_fastview_633020_result_without_replacement_records(
                        original_staged_record_vtables=record_types
                    ), 0
                )
        for record_types in ((0x7D7F90,), (0x7D7F3C, 0x7D7F90),
                             (0x7D7F90, 0x7D7F90)):
            with self.subTest(records=record_types), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_633020_result_without_replacement_records(
                    original_staged_record_vtables=record_types
                )

    def test_class_inventory_requires_source_known_exact_type(self):
        for record_types in (None, [], [0x7D7F90], (0x7D7F30,),
                             (0x7D8014,), (True,), ("0x7D7F90",),
                             (-1,), (0x100000000,)):
            with self.subTest(records=record_types):
                with self.assertRaises(SourceFastViewTacticsSelectionError):
                    source_fastview_633240_count_replacement_records(
                        original_staged_record_vtables=record_types
                    )
                with self.assertRaises(SourceFastViewTacticsSelectionError):
                    source_fastview_633020_result_without_replacement_records(
                        original_staged_record_vtables=record_types
                    )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Owner-authorized original PE not mounted")
    def test_original_count_visitor_only_replacement_slot_is_nontrivial(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        original_counter = 0x7D803C
        self.assertEqual(struct.unpack("<I", pe.read(original_counter + 4, 4))[0],
                         0x634E40)
        self.assertEqual(pe.read(0x634E40, 8),
                         bytes.fromhex("8b 41 04 ff 00 c2 04 00"))
        self.assertEqual(pe.read(0x6596D0, 3),
                         bytes.fromhex("c2 04 00"))
        for slot in range(8, 0x21, 4):
            with self.subTest(slot=hex(slot)):
                self.assertEqual(
                    struct.unpack("<I", pe.read(original_counter + slot, 4))[0],
                    0x6596D0
                )
        self.assertEqual(
            struct.unpack("<I", pe.read(0x7D7F90 + 4, 4))[0],
            0x633600
        )



class OriginalFastViewNativeReplayMethodMapTests(unittest.TestCase):
    """Replay visitor may mutate side state; these tests only resolve CALL targets."""

    def test_every_source_record_virtual_four_calls_the_distinct_replay_slot(self):
        expected_by_slot = dict(SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE_METHODS)
        self.assertEqual(len(expected_by_slot), 8)
        self.assertEqual(expected_by_slot[0x04], 0x634B00)
        self.assertEqual(expected_by_slot[0x10], 0x634990)
        self.assertEqual(expected_by_slot[0x14], 0x634920)
        self.assertEqual(
            {slot for slot, call in expected_by_slot.items() if call == 0x634AB0},
            {0x08, 0x0C, 0x18, 0x1C, 0x20}
        )
        for table, wrapper, offset in SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH:
            with self.subTest(vtable=hex(table)):
                self.assertEqual(
                    source_fastview_staged_record_native_replay_method(
                        native_record_vtable=table
                    ),
                    OriginalFastViewReplayMethodResolution(
                        table, wrapper, expected_by_slot[offset], offset
                    )
                )

    def test_unknown_original_types_cannot_reach_replay_methods(self):
        for wrong in (True, 0x7D7F30, 0x7D8014, 0x7D7F9C, -1, None, "0x7d7f90"):
            with self.subTest(wrong=repr(wrong)), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_staged_record_native_replay_method(
                    native_record_vtable=wrong
                )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original owner-authorized PE is not mounted")
    def test_exact_original_replay_visitor_vtable_and_mutation_entrypoints(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for offset, method in SOURCE_FASTVIEW_REPLAY_VISITOR_VTABLE_METHODS:
            with self.subTest(offset=hex(offset)):
                self.assertEqual(
                    struct.unpack("<I", pe.read(0x7D8014 + offset, 4))[0],
                    method
                )
        for addr, source in (
            (0x634AB0, "53 8b 59 14 56 57"),
            (0x634B00, "6a ff 68 b7 4c 7b 00"),
            (0x634990, "64 a1 00 00 00 00"),
            (0x634920, "55 8b 6c 24 08 56"),
            (0x634C1D, "8b 46 1c"),
            (0x634CF4, "c6 46 09 01"),
            (0x634DF0, "8a 41 09 c3"),
        ):
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr, len(bytes.fromhex(source))),
                                 bytes.fromhex(source))



class OriginalFastViewSourceTwoSpecialReplayHandlersTests(unittest.TestCase):
    """Native visitor methods +0x10/+0x14 return distinct list edit choices."""

    def test_omitting_vs_reconstructing_are_different_native_paths(self):
        for cls, expected in (
            (0x7D7F60, "omit_record"),
            (0x7D7F6C, "reconstruct_0x6334f0_record")
        ):
            with self.subTest(cls=hex(cls)):
                self.assertEqual(
                    source_fastview_special_replay_record_branch(
                        native_record_vtable=cls, visitor_status9=1,
                        native_record_dword_four=4, requested_source_dword=4
                    ), expected)
                for flag, old_id, requested in ((0, 4, 4), (1, 4, 5), (255, 0, 4)):
                    self.assertEqual(
                        source_fastview_special_replay_record_branch(
                            native_record_vtable=cls, visitor_status9=flag,
                            native_record_dword_four=old_id,
                            requested_source_dword=requested
                        ), "append_original_record"
                    )

    def test_unsupported_record_and_synthetic_statuses_fail_closed(self):
        base = dict(native_record_vtable=0x7D7F60, visitor_status9=0,
                    native_record_dword_four=3, requested_source_dword=3)
        cases = (
            {"native_record_vtable": 0x7D7F90},
            {"native_record_vtable": 0x7D7F3C},
            {"native_record_vtable": True},
            {"visitor_status9": True},
            {"visitor_status9": 256},
            {"native_record_dword_four": -1},
            {"requested_source_dword": 0x100000000},
            {"requested_source_dword": "3"},
        )
        for change in cases:
            with self.subTest(change=change), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_special_replay_record_branch(**(base | change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original source PE not mounted")
    def test_exact_original_conditional_branch_bytes(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for va, expected in (
            (0x634928, "8a 46 09 84 c0"),
            (0x63492D, "74 0c"),
            (0x634931, "e8 7a ec ff ff"),
            (0x634936, "3b 46 0c"),
            (0x634939, "74 42"),
            (0x634990, "64 a1 00 00 00 00"),
            (0x6349AF, "8a 46 09 84 c0"),
            (0x6349B4, "0f 84 a1 00 00 00"),
            (0x6349BC, "e8 ef eb ff ff"),
            (0x6349C1, "3b 46 0c"),
            (0x6349C4, "0f 85 91 00 00 00"),
            (0x6349F8, "8b cf e8 f1 ea ff ff"),
        ):
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(expected))),
                                 bytes.fromhex(expected))



class OriginalFastViewReplacementReplayFourNativeBranchesTests(unittest.TestCase):
    """0x634B00 branch outcomes preserve original status/skip precedence."""

    def test_status_flags_short_circuit_before_skip_or_matching(self):
        for flag8, flag9 in ((0, 1), (1, 0), (255, 0), (1, 1)):
            with self.subTest(flags=(flag8, flag9)):
                self.assertEqual(
                    source_fastview_replacement_replay_branch_634b00(
                        visitor_status8=flag8, visitor_status9=flag9,
                        native_skip_replacement_count=3,
                        previous_replacement_target_dword=7,
                        requested_source_dword=7,
                    ),
                    "forward_old_record_after_prior_status"
                )

    def test_source_skip_count_decrements_before_old_target_comparison(self):
        for old_target, current_source in ((2, 2), (2, 3)):
            self.assertEqual(
                source_fastview_replacement_replay_branch_634b00(
                    visitor_status8=0, visitor_status9=0,
                    native_skip_replacement_count=1,
                    previous_replacement_target_dword=old_target,
                    requested_source_dword=current_source,
                ),
                "decrement_skip_and_append_empty_link"
            )

    def test_zero_skip_uses_original_previous_destination_match(self):
        for old_to, current_from, expected in (
            (4, 4, "chained_replacement_side_rewrite"),
            (4, 5, "forward_old_record_mark_status8"),
            (0, 0, "chained_replacement_side_rewrite")
        ):
            self.assertEqual(
                source_fastview_replacement_replay_branch_634b00(
                    visitor_status8=0, visitor_status9=0,
                    native_skip_replacement_count=0,
                    previous_replacement_target_dword=old_to,
                    requested_source_dword=current_from
                ), expected
            )

    def test_native_byte_and_dword_contracts_are_strict(self):
        base = dict(visitor_status8=0, visitor_status9=0,
                    native_skip_replacement_count=0,
                    previous_replacement_target_dword=3, requested_source_dword=3)
        for update in ({"visitor_status8": True}, {"visitor_status9": 256},
                       {"native_skip_replacement_count": True},
                       {"native_skip_replacement_count": -1},
                       {"previous_replacement_target_dword": -1},
                       {"requested_source_dword": 0x100000000},
                       {"requested_source_dword": "3"}):
            with self.subTest(update=update), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_replacement_replay_branch_634b00(**(base | update))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original private source PE not mounted")
    def test_exact_original_branch_preconditions_and_chain_constructor(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for va, code in (
            (0x634B1C, "8a 46 09 84 c0"),
            (0x634B21, "0f 85 1e 02 00 00"),
            (0x634B27, "8a 46 08 84 c0"),
            (0x634B2C, "0f 85 13 02 00 00"),
            (0x634B32, "8b 46 04"),
            (0x634B37, "3b c5"),
            (0x634B39, "76 43"),
            (0x634B3B, "48"),
            (0x634B82, "8b cb"),
            (0x634B84, "e8 67 ea ff ff"),
            (0x634B89, "3b 46 0c"),
            (0x634B8C, "0f 85 6b 01 00 00"),
            (0x634BB8, "e8 13 ea ff ff"),
            (0x634CF4, "c6 46 09 01"),
        ):
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va, len(bytes.fromhex(code))),
                                 bytes.fromhex(code))



class OriginalFastViewChainMatchSideWriteOrderTests(unittest.TestCase):
    """Byte-exact in-memory projection; no live edit, owner or mouse event."""

    @staticmethod
    def _payload():
        data = bytearray(280)
        struct.pack_into("<I", data, 0x14, 12)
        data[0xF2:0xFE] = bytes((3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11))
        data[0xF0] = 11
        data[0xF1] = 5
        data[0x104 + 3] = 0
        data[0x104 + 7] = 1
        struct.pack_into("<I", data, 0x18 + 4 * 3, 0x11112222)
        struct.pack_into("<I", data, 0x18 + 4 * 7, 0x33334444)
        struct.pack_into("<I", data, 0x60 + 4 * 3, 0xAAAABBBB)
        struct.pack_into("<I", data, 0x60 + 4 * 7, 0xCCCCDDDD)
        return OriginalFastViewTacticsSelectionDraft(bytes(data))

    def test_native_chain_match_sequential_write_order_not_naive_swap(self):
        draft = self._payload()
        flags = [0] * 12
        flags[3] = 1
        changed = source_fastview_634b00_matched_chain_payload_value_only(
            draft, requested_from_index=3, requested_to_index=7,
            original_club_guard_flags=tuple(flags)
        )
        self.assertEqual(
            changed.original_side_bytes[0xF2:0xFE],
            bytes((7, 0, 1, 3, 4, 5, 6, 2, 8, 9, 10, 11))
        )
        self.assertEqual(changed.original_side_bytes[0x104 + 3], 1)
        self.assertEqual(changed.original_side_bytes[0x104 + 7], 0)
        self.assertEqual(changed.original_side_bytes[0xF0], 11)  # chain does NOT decrement
        self.assertEqual(changed.original_side_bytes[0xF1], 6)
        self.assertEqual(
            struct.unpack_from("<I", changed.original_side_bytes, 0x18 + 4 * 7)[0],
            0x11112222
        )
        self.assertEqual(
            struct.unpack_from("<I", changed.original_side_bytes, 0x60 + 4 * 7)[0],
            0xAAAABBBB
        )
        self.assertEqual(draft, self._payload())  # input is immutable
        self.assertEqual(len(changed.original_side_bytes), 280)

    def test_native_guard_count_decrement_and_wrap(self):
        draft = self._payload()
        flags = [0] * 12
        flags[7] = 1
        changed = source_fastview_634b00_matched_chain_payload_value_only(
            draft, requested_from_index=3, requested_to_index=7,
            original_club_guard_flags=tuple(flags))
        self.assertEqual(changed.original_side_bytes[0xF1], 4)
        same = source_fastview_634b00_matched_chain_payload_value_only(
            draft, requested_from_index=3, requested_to_index=7,
            original_club_guard_flags=tuple([1] * 12))
        self.assertEqual(same.original_side_bytes[0xF1], 5)

    def test_fail_closed_when_prior_source_missing_or_wrong_types(self):
        draft = self._payload()
        common = dict(draft=draft, requested_from_index=3,
                      requested_to_index=7, original_club_guard_flags=(0,) * 12)
        bad = (
            {"requested_from_index": True},
            {"requested_to_index": -1},
            {"requested_to_index": 20},
            {"original_club_guard_flags": [0] * 12},
            {"original_club_guard_flags": (0,) * 7},
            {"original_club_guard_flags": (0,) * 11 + (256,)},
            {"draft": bytearray(draft.original_side_bytes)},
            {"requested_from_index": 12},
        )
        for changed in bad:
            with self.subTest(changed=changed), self.assertRaises(
                SourceFastViewTacticsSelectionError
            ):
                source_fastview_634b00_matched_chain_payload_value_only(
                    **(common | changed)
                )
        absent = bytearray(draft.original_side_bytes)
        absent[0xF2:0xFE] = bytes(range(12))
        with self.assertRaises(SourceFastViewTacticsSelectionError):
            source_fastview_634b00_matched_chain_payload_value_only(
                OriginalFastViewTacticsSelectionDraft(bytes(absent)),
                requested_from_index=15, requested_to_index=7,
                original_club_guard_flags=(0,) * 20
            )

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original PE not mounted")
    def test_authenticated_634c1d_634cf4_actual_native_write_order(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        expected = (
            (0x634C1D, "8b 46 1c"),
            (0x634C23, "c6 84 08 04 01 00 00 01"),
            (0x634C31, "c6 84 02 04 01 00 00 00"),
            (0x634C41, "e8 6a 01 00 00"),
            (0x634C52, "8a 94 11 f2 00 00 00"),
            (0x634C59, "88 94 0f f2 00 00 00"),
            (0x634C68, "88 9c 11 f2 00 00 00"),
            (0x634C75, "88 94 01 f2 00 00 00"),
            (0x634C85, "8b 4c 88 18"),
            (0x634C89, "89 4c 90 18"),
            (0x634C96, "8b 54 90 60"),
            (0x634C9A, "89 54 88 60"),
            (0x634CC3, "fe 80 f1 00 00 00"),
            (0x634CEE, "fe 88 f1 00 00 00"),
            (0x634CF4, "c6 46 09 01"),
        )
        for va, literal in expected:
            with self.subTest(va=hex(va)):
                raw = bytes.fromhex(literal)
                self.assertEqual(pe.read(va, len(raw)), raw)

if __name__ == "__main__":
    unittest.main()
