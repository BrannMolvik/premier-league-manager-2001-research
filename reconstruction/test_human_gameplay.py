import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from human_gameplay import HumanGameplayController
from match_lineup import AI_FORMATIONS
from match_schedule import MsvcCrtRng
from match_team_setup import TeamTacticalState


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    positions: tuple[int, int, int]
    first_name: str = "Test"
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


def players_for_club(club_id: int):
    roles = [slot.role for slot in AI_FORMATIONS[0]]
    roles += [12, 19, 4, 1, 10, 11, 18, 9, 2]
    return [
        Player(
            index=club_id * 1000 + offset,
            club_id=club_id,
            positions=(int(role), 0, 0),
            shirt_number=offset + 1,
        )
        for offset, role in enumerate(roles)
    ]


def round_fixtures(round_index: int, start_id: int):
    fixtures = []
    for pair in range(10):
        left = pair * 2 + 1
        right = left + 1
        if round_index % 2:
            home, away = right, left
        else:
            home, away = left, right
        fixtures.append(
            Fixture(start_id + pair, round_index, home, away)
        )
    return fixtures


class Database:
    players = [
        player
        for club_id in range(1, 21)
        for player in players_for_club(club_id)
    ]
    clubs = tuple(Club(club_id, club_id) for club_id in range(1, 21))
    managers = tuple(Manager(club_id) for club_id in range(1, 21))
    competitions = (Competition(),)
    countries = ()
    real_fixtures = tuple(
        round_fixtures(0, 0)
        + round_fixtures(1, 10)
        + round_fixtures(2, 20)
    )
    premier_league_rounds = (
        Round(1, 0, 6),
        Round(2, 1, 6),
        Round(3, 2, 6),
    )


def coefficient_matrix(value=1.0):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


class HumanGameplayControllerTests(unittest.TestCase):
    def build_controller(self):
        state = GameState.from_database(
            Database(),
            date(2000, 6, 30),
            seed=1,
            season_year=2000,
        )
        # Put the human club-1 fixture in the middle of each same-day list so
        # the controller must execute AI matches both before and after it.
        state.install_premier_league_scheduler_order(
            (
                (0, (5, 6, 7, 8, 9, 0, 1, 2, 3, 4)),
                (1, (15, 16, 17, 18, 19, 10, 11, 12, 13, 14)),
                (2, (25, 26, 27, 28, 29, 20, 21, 22, 23, 24)),
            )
        )
        return HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )

    def set_available_lineup(self, controller):
        available = [
            player.index
            for player in controller.squad()
            if not player.base_match_unavailable
        ]
        self.assertGreaterEqual(len(available), 16)
        controller.set_lineup(
            0,
            available[:11],
            available[11:16],
        )

    def test_club_squad_lineup_and_tactics_persist(self):
        controller = self.build_controller()
        human = controller.select_club(1)
        self.assertEqual(human.club_id, 1)
        self.assertEqual(len(controller.squad()), 20)

        tactics = TeamTacticalState(
            play_style=2,
            without_ball_style=1,
            with_ball_style=3,
            aggression=7,
        )
        controller.set_tactics(tactics)
        self.assertEqual(controller.state.team_tactics[1], tactics)

        self.set_available_lineup(controller)
        roster = controller.squad()
        self.assertEqual(sum(player.match_active for player in roster), 11)
        self.assertEqual(
            sum(player.match_substitute_available for player in roster),
            5,
        )
        self.assertEqual(controller.human.formation_id, 0)

    def test_advance_stops_before_human_fixture_then_shared_backend_finishes_day(self):
        controller = self.build_controller()
        controller.select_club(1)
        self.set_available_lineup(controller)

        fixture = controller.advance_to_next_user_fixture()
        self.assertEqual(fixture.id, 0)
        self.assertEqual(controller.state.calendar.current_date, date(2000, 7, 1))
        self.assertNotIn(0, controller.state.premier_league.results)
        self.assertEqual(controller.pending_fixture_id, 0)
        self.assertEqual(
            tuple(sorted(controller.state.premier_league.results)),
            (5, 6, 7, 8, 9),
        )

        outcome = controller.play_user_fixture()

        self.assertEqual(outcome.fixture_id, 0)
        self.assertEqual(
            [fixture_id for fixture_id, _ in outcome.matchday_results],
            [5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
        )
        self.assertEqual(len(controller.state.premier_league.results), 10)
        self.assertEqual(sum(row.played for row in outcome.table), 20)
        self.assertIsNone(controller.pending_fixture_id)

    def test_three_week_human_loop_reuses_same_backend(self):
        controller = self.build_controller()
        controller.select_club(1)

        completed = []
        for expected_fixture_id in (0, 10, 20):
            self.set_available_lineup(controller)
            fixture = controller.advance_to_next_user_fixture()
            self.assertEqual(fixture.id, expected_fixture_id)
            outcome = controller.play_user_fixture()
            completed.append(outcome.fixture_id)

        self.assertEqual(completed, [0, 10, 20])
        self.assertEqual(len(controller.state.premier_league.results), 30)
        self.assertEqual(
            sum(row.played for row in controller.state.premier_league_table()),
            60,
        )
        self.assertTrue(
            all(
                0 <= player.condition <= 100
                for player in controller.squad()
            )
        )

    def test_autofill_produces_persistent_legal_11_plus_5(self):
        controller = self.build_controller()
        controller.select_club(1)

        selection = controller.autofill_lineup(0)

        self.assertEqual(len(selection.lineup.starters), 11)
        self.assertEqual(len(selection.lineup.substitutes), 5)
        self.assertEqual(
            tuple(
                int(assignment.player_index)
                for assignment in selection.lineup.starters
            ),
            controller.human.starter_ids,
        )
        self.assertEqual(
            tuple(int(value) for value in selection.lineup.substitutes),
            controller.human.substitute_ids,
        )

    def test_unavailable_human_player_is_rejected(self):
        controller = self.build_controller()
        controller.select_club(1)
        player = controller.squad()[0]
        player.injured = True
        ids = [entry.index for entry in controller.squad()]

        with self.assertRaisesRegex(ValueError, "unavailable"):
            controller.set_lineup(
                0,
                ids[:11],
                ids[11:16],
            )


if __name__ == "__main__":
    unittest.main()
