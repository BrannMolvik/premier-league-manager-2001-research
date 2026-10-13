"""Tests only a source-verified subset of native human FastView tactics input."""
import struct
import unittest

from original_fastview_tactics_selection import (
    OriginalFastViewTacticsSelectionDraft,
    SOURCE_SELECTOR_RULES,
    SOURCE_SIDE_BUFFER_SIZE,
    SourceFastViewTacticsSelectionError,
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


if __name__ == "__main__":
    unittest.main()
