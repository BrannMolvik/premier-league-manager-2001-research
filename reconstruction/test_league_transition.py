import unittest
from dataclasses import dataclass

from league_transition import (
    apply_league_allocation_exchanges,
    ordered_english_league_allocations,
)


@dataclass(frozen=True)
class Allocation:
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


class LeagueTransitionTests(unittest.TestCase):
    def test_playoff_endpoint_swaps_current_parent_league_membership(self):
        allocation = Allocation(1, 0, 17, 17, 11, 0, 0)
        premier = tuple(range(100, 120))
        playoff_winner = 250
        memberships = {club_id: 0 for club_id in premier}
        memberships[playoff_winner] = 2

        result = apply_league_allocation_exchanges(
            (allocation,),
            {
                0: premier,
                11: (playoff_winner,),
            },
            memberships,
        )

        relegated = premier[17]
        self.assertEqual(result.memberships[relegated], 2)
        self.assertEqual(result.memberships[playoff_winner], 0)
        self.assertEqual(
            (
                result.exchanges[0].membership_a_before,
                result.exchanges[0].membership_b_before,
            ),
            (0, 2),
        )

    def test_english_allocation_order_is_instruction_closed(self):
        rows = (
            Allocation(25, 7, 19, 21, 89, 0, 2),
            Allocation(6, 4, 23, 23, 7, 0, 0),
            Allocation(5, 3, 20, 20, 13, 0, 0),
            Allocation(4, 3, 21, 23, 4, 0, 2),
            Allocation(3, 2, 21, 21, 12, 0, 0),
            Allocation(2, 2, 22, 23, 3, 0, 1),
            Allocation(1, 0, 17, 17, 11, 0, 0),
            Allocation(0, 0, 18, 19, 2, 0, 1),
        )
        self.assertEqual(
            tuple(row.id for row in ordered_english_league_allocations(rows)),
            (0, 1, 2, 3, 4, 5, 6, 25),
        )

    def test_english_chain_exchanges_exact_number_of_clubs(self):
        rows = ordered_english_league_allocations((
            Allocation(0, 0, 18, 19, 2, 0, 1),
            Allocation(1, 0, 17, 17, 11, 0, 0),
            Allocation(2, 2, 22, 23, 3, 0, 1),
            Allocation(3, 2, 21, 21, 12, 0, 0),
            Allocation(4, 3, 21, 23, 4, 0, 2),
            Allocation(5, 3, 20, 20, 13, 0, 0),
            Allocation(6, 4, 23, 23, 7, 0, 0),
            Allocation(25, 7, 19, 21, 89, 0, 2),
        ))
        rankings = {
            0: tuple(range(100, 120)),
            2: tuple(range(200, 224)),
            3: tuple(range(300, 324)),
            4: tuple(range(400, 424)),
            7: tuple(range(700, 722)),
            11: (205,),
            12: (305,),
            13: (405,),
            89: tuple(range(890, 905)),
        }
        memberships = {}
        for competition_id in (0, 2, 3, 4, 7, 89):
            for club_id in rankings[competition_id]:
                memberships[club_id] = competition_id

        result = apply_league_allocation_exchanges(
            rows,
            rankings,
            memberships,
        )

        self.assertEqual(len(result.exchanges), 14)
        self.assertEqual(result.memberships[118], 2)
        self.assertEqual(result.memberships[119], 2)
        self.assertEqual(result.memberships[117], 2)
        self.assertEqual(result.memberships[200], 0)
        self.assertEqual(result.memberships[201], 0)
        self.assertEqual(result.memberships[205], 0)
        self.assertEqual(result.memberships[423], 7)
        self.assertEqual(result.memberships[700], 4)
        self.assertEqual(result.memberships[719], 89)
        self.assertEqual(result.memberships[720], 89)
        self.assertEqual(result.memberships[721], 89)
        self.assertEqual(result.memberships[890], 7)
        self.assertEqual(result.memberships[891], 7)
        self.assertEqual(result.memberships[892], 7)


if __name__ == "__main__":
    unittest.main()
