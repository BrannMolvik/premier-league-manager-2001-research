import unittest

from transfer_decision import (
    SellingClubBidInputs,
    SellingClubDecision,
    evaluate_selling_club_bid,
    protected_young_first_team_player,
)


class SellingClubDecisionTests(unittest.TestCase):
    def inputs(self, **changes):
        values = dict(
            proposal_total_value=600_000,
            player_value=1_000_000,
            target_age=25,
            higher_rated_squadmates=5,
            eligible_squad_count=20,
        )
        values.update(changes)
        return SellingClubBidInputs(**values)

    def test_4212f0_exact_age_and_higher_rated_boundaries(self):
        self.assertTrue(
            protected_young_first_team_player(
                target_age=29,
                higher_rated_squadmates=10,
            )
        )
        self.assertFalse(
            protected_young_first_team_player(
                target_age=30,
                higher_rated_squadmates=10,
            )
        )
        self.assertFalse(
            protected_young_first_team_player(
                target_age=29,
                higher_rated_squadmates=11,
            )
        )

    def test_protected_player_offer_below_sixty_percent_is_too_cheap(self):
        result = evaluate_selling_club_bid(
            self.inputs(proposal_total_value=599_999)
        )
        self.assertEqual(result, SellingClubDecision.TOO_CHEAP)

    def test_exactly_sixty_percent_passes_price_check(self):
        result = evaluate_selling_club_bid(self.inputs())
        self.assertEqual(result, SellingClubDecision.ACCEPTED)

    def test_unprotected_player_skips_too_cheap_branch(self):
        result = evaluate_selling_club_bid(
            self.inputs(
                proposal_total_value=1,
                target_age=30,
            )
        )
        self.assertEqual(result, SellingClubDecision.ACCEPTED)

    def test_fewer_than_seventeen_eligible_players_is_squad_too_small(self):
        result = evaluate_selling_club_bid(
            self.inputs(eligible_squad_count=16)
        )
        self.assertEqual(result, SellingClubDecision.SQUAD_TOO_SMALL)

    def test_seventeen_eligible_players_passes_squad_check(self):
        result = evaluate_selling_club_bid(
            self.inputs(eligible_squad_count=17)
        )
        self.assertEqual(result, SellingClubDecision.ACCEPTED)

    def test_too_cheap_reason_precedes_small_squad_reason(self):
        result = evaluate_selling_club_bid(
            self.inputs(
                proposal_total_value=100_000,
                eligible_squad_count=10,
            )
        )
        self.assertEqual(result, SellingClubDecision.TOO_CHEAP)


if __name__ == "__main__":
    unittest.main()
