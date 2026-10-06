import unittest

from match_detail_mode import (
    MATCH_DETAIL_LABELS,
    NATIVE_MATCH_DETAIL_GLOBAL_VA,
    NATIVE_UNRESOLVED_SENTINEL,
    MatchDetailMode,
    coerce_match_detail_mode,
    match_detail_label,
    source_selects_fastview,
)


class MatchDetailModeTests(unittest.TestCase):
    def test_source_values_and_labels_are_exact(self):
        self.assertEqual(NATIVE_MATCH_DETAIL_GLOBAL_VA, 0x877530)
        self.assertEqual(NATIVE_UNRESOLVED_SENTINEL, 5)
        self.assertEqual(
            tuple((int(mode), MATCH_DETAIL_LABELS[mode]) for mode in MatchDetailMode),
            (
                (0, "3D Match"),
                (1, "3D Highlights"),
                (2, "FastView"),
                (3, "Quick Match"),
            ),
        )

    def test_only_mode_two_selects_fastview(self):
        self.assertFalse(source_selects_fastview(None))
        for mode in MatchDetailMode:
            self.assertEqual(
                source_selects_fastview(mode),
                mode is MatchDetailMode.FASTVIEW,
            )

    def test_selectable_values_are_strictly_bounded(self):
        for value in range(4):
            self.assertEqual(int(coerce_match_detail_mode(value)), value)
            self.assertEqual(match_detail_label(value), MATCH_DETAIL_LABELS[MatchDetailMode(value)])
        for value in (-1, 4, NATIVE_UNRESOLVED_SENTINEL, True, False, "bad"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    coerce_match_detail_mode(value)


if __name__ == "__main__":
    unittest.main()
