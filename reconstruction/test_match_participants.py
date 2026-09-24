import unittest
from dataclasses import dataclass

from match_participants import collect_match_participants


@dataclass
class Player:
    player_index: int
    club_id: int
    match_active: bool = False
    match_substitute_available: bool = False


class MatchParticipantCollectorTests(unittest.TestCase):
    def test_collects_active_and_substitute_players_in_roster_order(self):
        roster = [
            Player(5, 7, match_substitute_available=True),
            Player(2, 7),
            Player(9, 7, match_active=True),
            Player(1, 7, match_substitute_available=True),
        ]

        participants = collect_match_participants(7, roster)

        self.assertEqual(
            [player.player_index for player in participants],
            [5, 9, 1],
        )

    def test_team_mismatch_fails_same_club_guard(self):
        roster = [
            Player(1, 8, match_active=True),
            Player(2, 7, match_active=True),
        ]

        participants = collect_match_participants(7, roster)

        self.assertEqual(
            [player.player_index for player in participants],
            [2],
        )

    def test_unselected_player_is_omitted(self):
        roster = [Player(1, 7)]
        self.assertEqual(collect_match_participants(7, roster), ())


if __name__ == "__main__":
    unittest.main()
