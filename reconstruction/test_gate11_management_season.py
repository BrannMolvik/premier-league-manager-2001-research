import unittest
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from game_state import GameState
from human_gameplay import HumanGameplayController
from match_lineup import AI_FORMATIONS
from match_schedule import MsvcCrtRng


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    positions: tuple[int, int, int]
    first_name: str = "Season"
    surname: str = "Player"
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 1
    height_cm: int = 180
    weight_kg: int = 75
    current_raw: tuple[int, ...] = (160,) * 17
    target_raw: tuple[int, ...] = (180,) * 17
    eu_status_code: int = 2


@dataclass(frozen=True)
class Club:
    index: int
    manager_id: int
    country_id: int = 0
    competition_id: int = 0


@dataclass(frozen=True)
class Country:
    id: int = 0
    name: str = "Testland"
    nationality_id: int = 0
    european_index: int = 1
    eu_status_flag: int = 1
    continent_id: int = 0
    financial_multiplier_percent: int = 100


@dataclass(frozen=True)
class Manager:
    index: int
    formation_default: int = 0
    formation_class3: int = 2
    formation_class1: int = 1


@dataclass(frozen=True)
class Competition:
    id: int = 0
    substitute_quota: int = 5
    max_non_eu_players: int = 10


@dataclass(frozen=True)
class Fixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass(frozen=True)
class Round:
    round_number: int
    scheduled_week: int
    scheduled_weekday: int


def coefficient_matrix(value=1.0):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


def players_for_club(club_id: int):
    base_roles = [int(slot.role) for slot in AI_FORMATIONS[0]]
    reserve_roles = [12, 19, 4, 1, 10, 11, 18, 9, 2, 6, 14, 16, 7, 15, 3]
    roles = base_roles + reserve_roles
    return tuple(
        Player(
            index=club_id * 1000 + offset,
            club_id=club_id,
            positions=(int(role), 0, 0),
            shirt_number=offset + 1,
        )
        for offset, role in enumerate(roles)
    )


def round_robin_fixtures():
    teams = list(range(1, 21))
    first_half = []
    for round_index in range(19):
        pairs = []
        for pair_index in range(10):
            left = teams[pair_index]
            right = teams[-1 - pair_index]
            if (round_index + pair_index) % 2:
                home, away = right, left
            else:
                home, away = left, right
            pairs.append((home, away))
        first_half.append(tuple(pairs))
        teams = [teams[0], teams[-1], *teams[1:-1]]

    fixtures = []
    for round_index, pairs in enumerate(first_half):
        for pair_index, (home, away) in enumerate(pairs):
            fixtures.append(
                Fixture(round_index * 10 + pair_index, round_index, home, away)
            )
    for offset, pairs in enumerate(first_half, start=19):
        for pair_index, (home, away) in enumerate(pairs):
            fixtures.append(
                Fixture(offset * 10 + pair_index, offset, away, home)
            )
    return tuple(fixtures)


class FullSeasonDatabase:
    players = tuple(
        player
        for club_id in range(1, 21)
        for player in players_for_club(club_id)
    )
    clubs = tuple(Club(club_id, club_id) for club_id in range(1, 21))
    managers = tuple(Manager(club_id) for club_id in range(1, 21))
    competitions = (Competition(),)
    countries = (Country(),)
    real_fixtures = round_robin_fixtures()
    premier_league_rounds = tuple(
        Round(round_index + 1, 7 + round_index, 6)
        for round_index in range(38)
    )


class Gate11HumanSeasonTests(unittest.TestCase):
    def test_human_manager_completes_38_round_management_season(self):
        state = GameState.from_database(
            FullSeasonDatabase(),
            date(2000, 8, 18),
            seed=1,
            season_year=2000,
        )
        state.positions.update(
            {role: SimpleNamespace(lineup_group=0) for role in range(20)}
        )

        scheduler_order = []
        for round_index in range(38):
            ids = [
                int(fixture.id)
                for fixture in state.premier_league.fixtures_for_round(round_index)
            ]
            human_id = next(
                fixture_id
                for fixture_id in ids
                if 1
                in (
                    int(state.premier_league.fixtures[fixture_id].home_club_id),
                    int(state.premier_league.fixtures[fixture_id].away_club_id),
                )
            )
            ids.remove(human_id)
            ids.insert(5, human_id)
            scheduler_order.append((round_index, tuple(ids)))
        state.install_premier_league_scheduler_order(scheduler_order)

        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )
        controller.select_club(1)
        state.configure_user_training_calendar(
            recovery_threshold=50,
            quality_multiplier=1.30,
        )
        controller.set_player_training_method(controller.squad()[0].index, 1)

        completed = []
        for round_index in range(38):
            selection = controller.autofill_lineup(0)
            self.assertEqual(len(selection.lineup.starters), 11)
            self.assertEqual(len(selection.lineup.substitutes), 5)

            fixture = controller.advance_to_next_user_fixture()
            self.assertIsNotNone(fixture)
            self.assertEqual(int(fixture.round_index), round_index)
            outcome = controller.play_user_fixture()
            completed.append(int(outcome.fixture_id))

            self.assertEqual(len(outcome.matchday_results), 10)
            self.assertTrue(
                all(0 <= int(player.condition) <= 100 for player in controller.squad())
            )
            self.assertTrue(
                all(0 <= int(player.form_state) <= 4 for player in controller.squad())
            )

        self.assertEqual(len(completed), 38)
        self.assertEqual(len(set(completed)), 38)
        self.assertEqual(len(state.premier_league.results), 380)
        self.assertEqual(
            sum(row.played for row in state.premier_league_table()),
            760,
        )
        human_row = next(
            row for row in state.premier_league_table()
            if int(row.club_id) == 1
        )
        self.assertEqual(int(human_row.played), 38)
        self.assertIsNone(controller.next_user_fixture())


if __name__ == "__main__":
    unittest.main()
