import unittest
from types import SimpleNamespace

from gate14_prematch_rating_widths import (
    PREMATCH_RATING_GROUPS,
    PrematchRatingWidthError,
    prematch_rating_width_contract,
    source_prematch_team_rating_widths,
)


class FakePlayer:
    def __init__(self, role, rating):
        self.current_position = role
        self._rating = rating

    def current_role_rating(self):
        return self._rating


class PrematchRatingWidthTests(unittest.TestCase):
    def setUp(self):
        # GameState keys Position records by zero-based source-table index.
        self.positions = {
            1: SimpleNamespace(lineup_group=3),   # GK
            2: SimpleNamespace(lineup_group=0),   # defence
            9: SimpleNamespace(lineup_group=1),   # midfield
            16: SimpleNamespace(lineup_group=255), # RF native unclassified
            18: SimpleNamespace(lineup_group=2),  # CF
        }

    def test_exact_native_group_scales_and_semantics(self):
        self.assertEqual(
            PREMATCH_RATING_GROUPS,
            (
                (0x49A3D0, 3, 1.71, "goalkeeper"),
                (0x49A460, 0, 0.342, "defence"),
                (0x49A4F0, 1, 0.342, "midfield"),
                (0x49A580, 2, 0.57, "attack"),
            ),
        )

    def test_widths_use_current_role_rating_and_position_lineup_group(self):
        starters = (
            FakePlayer(1, 80),
            FakePlayer(2, 60), FakePlayer(2, 70), FakePlayer(2, 50),
            FakePlayer(9, 75), FakePlayer(9, 65), FakePlayer(9, 55),
            FakePlayer(18, 90), FakePlayer(18, 85), FakePlayer(18, 80),
            FakePlayer(16, 99),
        )
        widths = source_prematch_team_rating_widths(starters, self.positions)
        self.assertEqual(widths.goalkeeper, int(80 * 1.71))
        self.assertEqual(widths.defence, int((60 + 70 + 50) * 0.342))
        self.assertEqual(widths.midfield, int((75 + 65 + 55) * 0.342))
        self.assertEqual(widths.attack, int((90 + 85 + 80) * 0.57))

    def test_unclassified_rf_lf_style_group_255_is_excluded_exactly(self):
        starters = (
            FakePlayer(1, 0),
            FakePlayer(2, 0), FakePlayer(2, 0), FakePlayer(2, 0),
            FakePlayer(9, 0), FakePlayer(9, 0), FakePlayer(9, 0),
            FakePlayer(18, 0), FakePlayer(18, 0), FakePlayer(18, 0),
            FakePlayer(16, 99),
        )
        widths = source_prematch_team_rating_widths(starters, self.positions)
        self.assertEqual(
            (widths.goalkeeper, widths.defence, widths.midfield, widths.attack),
            (0, 0, 0, 0),
        )

    def test_native_99_rating_ceiling_leaves_two_pixel_source_border(self):
        starters = (
            FakePlayer(1, 99),
            *(FakePlayer(2, 99) for _ in range(5)),
            *(FakePlayer(9, 99) for _ in range(2)),
            *(FakePlayer(18, 99) for _ in range(3)),
        )
        widths = source_prematch_team_rating_widths(starters, self.positions)
        self.assertEqual(widths.goalkeeper, 169)
        self.assertEqual(widths.defence, 169)
        self.assertEqual(widths.attack, 169)
        self.assertLessEqual(widths.midfield, 171)

    def test_exactly_eleven_starters_required(self):
        with self.assertRaises(PrematchRatingWidthError):
            source_prematch_team_rating_widths(
                (FakePlayer(1, 50),),
                self.positions,
            )

    def test_contract_remains_source_specific(self):
        contract = prematch_rating_width_contract()
        self.assertEqual(contract["starter_count"], 11)
        self.assertEqual(contract["bar_width"], 171)
        self.assertEqual(contract["rating_source"], "RuntimePlayer.current_role_rating")
        self.assertEqual(contract["position_group_source"], "Position.lineup_group")
        self.assertTrue(contract["unclassified_group_255_excluded"])


if __name__ == "__main__":
    unittest.main()
