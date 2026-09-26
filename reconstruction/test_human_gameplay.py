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


def players_for_club(club_id: int, start: int):
    roles = [slot.role for slot in AI_FORMATIONS[0]]
    roles += [12, 19, 4, 1, 10, 11, 18, 9, 2]
    return [
        Player(
            index=start + offset,
            club_id=club_id,
            positions=(int(role), 0, 0),
            shirt_number=offset + 1,
        )
        for offset, role in enumerate(roles)
    ]


class Database:
    players = players_for_club(1, 100) + players_for_club(2, 200)
    clubs = (Club(1, 10), Club(2, 20))
    managers = (Manager(10), Manager(20))
    competitions = (Competition(),)
    countries = ()
    real_fixtures = (
        Fixture(0, 0, 1, 2),
        Fixture(1, 1, 2, 1),
        Fixture(2, 2, 1, 2),
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
        state.install_premier_league_scheduler_order(
            (
                (0, (0,)),
                (1, (1,)),
                (2, (2,)),
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

        outcome = controller.play_user_fixture()

        self.assertEqual(outcome.fixture_id, 0)
        self.assertIn(0, controller.state.premier_league.results)
        self.assertEqual([fixture_id for fixture_id, _ in outcome.matchday_results], [0])
        self.assertEqual(sum(row.played for row in outcome.table), 2)
        self.assertIsNone(controller.pending_fixture_id)

    def test_three_week_human_loop_reuses_same_backend(self):
        controller = self.build_controller()
        controller.select_club(1)

        completed = []
        for expected_fixture_id in (0, 1, 2):
            self.set_available_lineup(controller)
            fixture = controller.advance_to_next_user_fixture()
            self.assertEqual(fixture.id, expected_fixture_id)
            outcome = controller.play_user_fixture()
            completed.append(outcome.fixture_id)

        self.assertEqual(completed, [0, 1, 2])
        self.assertEqual(
            set(controller.state.premier_league.results),
            {0, 1, 2},
        )
        self.assertEqual(
            sum(row.played for row in controller.state.premier_league_table()),
            6,
        )
        self.assertTrue(
            all(
                0 <= player.condition <= 100
                for player in controller.squad()
            )
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
