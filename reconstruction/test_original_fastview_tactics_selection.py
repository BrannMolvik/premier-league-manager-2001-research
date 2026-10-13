"""Tests only a source-verified subset of native human FastView tactics input."""
import struct
import unittest

from original_fastview_tactics_selection import (
    OriginalFastViewTacticsSelectionDraft,
    SOURCE_SELECTOR_RULES,
    SOURCE_SIDE_BUFFER_SIZE,
    SourceFastViewTacticsSelectionError,
    SOURCE_PLAYER_CONTROL_EVENT_FAMILIES,
    SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT,
    source_classify_fastview_player_control_event,
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


    def test_exact_five_native_high_event_families_decode_all_fifty_five_controls(self):
        self.assertEqual(SOURCE_PLAYER_CONTROL_EVENT_ROW_COUNT, 11)
        self.assertEqual(len(SOURCE_PLAYER_CONTROL_EVENT_FAMILIES), 5)
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
        self.assertEqual(len(all_seen), 55)


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


if __name__ == "__main__":
    unittest.main()
