import unittest
from dataclasses import dataclass

from match_schedule import MsvcCrtRng
from startup_rng import StartupUserRngConfig
from startup_sequence import replay_startup_rng_to_primary_shuffle


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    first_name: str
    surname: str
    nationality_id: int
    initial_flags: int = 0


@dataclass(frozen=True)
class Country:
    id: int
    nationality_id: int
    eu_status_flag: int


@dataclass(frozen=True)
class Club:
    index: int
    name: str
    country_id: int
    team_category_code: int
    runtime_value_1c_source: int


class StartupSequenceTests(unittest.TestCase):
    def test_shared_rng_reaches_exact_primary_shuffle_checkpoint(self):
        players = tuple(
            [
                Player(i, 332, "Alan", f"Smith{i}", 26)
                for i in range(12)
            ]
            + [
                Player(12 + i, 332, "Eric", f"Brown{i}", 31)
                for i in range(13)
            ]
        )
        countries = (
            Country(26, 26, 1),
            Country(31, 31, 1),
            Country(33, 33, 1),
            Country(24, 24, 1),
            Country(40, 40, 1),
            Country(66, 66, 1),
            Country(73, 73, 1),
        )
        clubs = (
            # Name-generation / youth source fixtures.
            Club(0, "Arsenal", 26, 1, 0),
            Club(332, "!Spare", 26, 1, 0),
            Club(2, "England", 26, 2, 0),
            Club(3, "Chelsea", 31, 1, 0),
            # Canonical seven Europe-root selector candidates.
            Club(1118, "England Select", 26, 2, 90000),
            Club(1135, "France Select", 31, 2, 90000),
            Club(1137, "Germany Select", 33, 2, 75000),
            Club(1139, "Holland Select", 24, 2, 60000),
            Club(1143, "Italy Select", 40, 2, 60000),
            Club(1159, "Scotland Select", 66, 2, 55000),
            Club(1162, "Spain Select", 73, 2, 100000),
        )
        users = (
            StartupUserRngConfig(country_id=26, option_mode=0),
            StartupUserRngConfig(country_id=31, option_mode=2),
        )
        rng = MsvcCrtRng(0x12345678)

        replay = replay_startup_rng_to_primary_shuffle(
            rng,
            clubs,
            countries,
            players,
            selected_user_country_id=31,
            users=users,
        )

        # Adding the seven category-2 competition selector clubs does not add
        # 0x414330 name calls, so the precompetition checkpoints are identical
        # to test_startup_rng's synthetic full replay.
        self.assertEqual(
            replay.precompetition.after_loader444_state,
            0xC526B5BC,
        )
        self.assertEqual(
            replay.precompetition.after_players_state,
            0x7B7B62DB,
        )
        self.assertEqual(
            replay.precompetition.after_team_names_state,
            0x0C18030B,
        )
        self.assertEqual(
            replay.precompetition.after_youth_state,
            0x2797444C,
        )

        self.assertEqual(
            replay.primary_competition.candidate_ids,
            (1118, 1135, 1137, 1139, 1143, 1159, 1162),
        )
        self.assertEqual(
            replay.primary_competition.champions_league_club_id,
            1118,
        )
        self.assertEqual(
            replay.primary_competition.uefa_cup_club_id,
            1143,
        )
        self.assertEqual(
            replay.state_entering_primary_shuffle,
            0x5D07D526,
        )
        self.assertEqual(rng.state, 0x5D07D526)


if __name__ == "__main__":
    unittest.main()
