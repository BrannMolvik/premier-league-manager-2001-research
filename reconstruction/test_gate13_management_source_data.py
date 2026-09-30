from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)


@dataclass
class FakeClub:
    name: str
    short_name: str


@dataclass
class FakePlayer:
    index: int
    first_name: str
    surname: str
    shirt_number: int
    positions: tuple[int, int, int]
    condition: int
    form_state: int
    morale: int
    injured: bool = False
    suspended: bool = False
    out_of_contract: bool = False
    transfer_listed: bool = False
    loan_listed: bool = False
    wanted: bool = False


@dataclass
class FakeFixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass
class FakeTableRow:
    club_id: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against


class FakeLeague:
    def __init__(self):
        # Deliberately not numeric or chronological order: the bridge must
        # preserve recovered source insertion order, not invent a UI sort.
        self.fixture_source_order = (17, 3)
        self.fixtures = {
            3: FakeFixture(3, 1, 11, 10),
            17: FakeFixture(17, 0, 10, 11),
        }
        self.results = {
            17: SimpleNamespace(home_goals=2, away_goals=1),
        }
        self._dates = {
            0: date(2000, 8, 19),
            1: date(2000, 8, 26),
        }

    def round_date(self, round_index):
        return self._dates.get(round_index)


class FakeState:
    def __init__(self):
        self.clubs = {
            10: FakeClub("Alpha FC", "Alpha"),
            11: FakeClub("Beta City", "Beta"),
        }
        self.calendar = SimpleNamespace(current_date=date(2000, 8, 20))
        self.premier_league = FakeLeague()
        # Deliberately Beta first: represents the backend's already recovered
        # native-comparator order, which the bridge must not second-guess.
        self._table = (
            FakeTableRow(11, 2, 2, 0, 0, 4, 1, 6),
            FakeTableRow(10, 2, 1, 0, 1, 3, 2, 3),
        )

    def premier_league_table(self):
        return self._table


class FakeController:
    def __init__(self):
        self.state = FakeState()
        self.human = SimpleNamespace(club_id=10)
        self.squad_calls = 0
        self._squad = (
            FakePlayer(
                202, "Second", "Source", 9, (4, 0, 0),
                91, 3, 88, transfer_listed=True,
            ),
            FakePlayer(
                101, "First", "Source", 1, (0, 1, 0),
                77, 2, 92, injured=True, suspended=True,
                out_of_contract=True, loan_listed=True, wanted=True,
            ),
        )

    def squad(self):
        self.squad_calls += 1
        return self._squad


class ManagementSourceDataBridgeTests(unittest.TestCase):
    def test_snapshot_preserves_backend_source_order_and_exact_table_order(self):
        controller = FakeController()
        bridge = ManagementSourceDataBridge(controller)

        snapshot = bridge.snapshot()

        self.assertEqual(
            (snapshot.club.club_id, snapshot.club.name,
             snapshot.club.short_name, snapshot.club.current_date),
            (10, "Alpha FC", "Alpha", date(2000, 8, 20)),
        )
        self.assertEqual(
            [row.player_id for row in snapshot.squad],
            [202, 101],
        )
        self.assertEqual(
            [row.source_roster_index for row in snapshot.squad],
            [0, 1],
        )
        self.assertEqual(
            [row.fixture_id for row in snapshot.fixtures_in_source_order],
            [17, 3],
        )
        self.assertEqual(
            [row.source_fixture_index for row in snapshot.fixtures_in_source_order],
            [0, 1],
        )
        self.assertEqual(
            [row.club_id for row in snapshot.league_table],
            [11, 10],
        )
        self.assertEqual(
            [row.position for row in snapshot.league_table],
            [1, 2],
        )
        self.assertEqual(controller.squad_calls, 1)

    def test_fixture_projection_uses_recovered_dates_names_and_result_only(self):
        bridge = ManagementSourceDataBridge(FakeController())

        first, second = bridge.fixture_rows()

        self.assertEqual(
            (
                first.fixture_id, first.round_index, first.scheduled_date,
                first.home_club_name, first.away_club_name,
                first.played, first.home_goals, first.away_goals,
            ),
            (17, 0, date(2000, 8, 19),
             "Alpha FC", "Beta City", True, 2, 1),
        )
        self.assertEqual(
            (
                second.fixture_id, second.round_index, second.scheduled_date,
                second.home_club_name, second.away_club_name,
                second.played, second.home_goals, second.away_goals,
            ),
            (3, 1, date(2000, 8, 26),
             "Beta City", "Alpha FC", False, None, None),
        )

    def test_squad_projection_retains_recovered_neutral_runtime_fields(self):
        bridge = ManagementSourceDataBridge(FakeController())

        second, first = bridge.squad_rows()

        self.assertEqual(
            (second.full_name, second.shirt_number, second.positions,
             second.condition, second.form_state, second.morale),
            ("Second Source", 9, (4, 0, 0), 91, 3, 88),
        )
        self.assertTrue(second.transfer_listed)
        self.assertFalse(second.injured)
        self.assertEqual(
            (first.full_name, first.condition, first.form_state, first.morale),
            ("First Source", 77, 2, 92),
        )
        self.assertTrue(first.injured)
        self.assertTrue(first.suspended)
        self.assertTrue(first.out_of_contract)
        self.assertTrue(first.loan_listed)
        self.assertTrue(first.wanted)

    def test_table_projection_does_not_resort_native_comparator_output(self):
        controller = FakeController()
        controller.state._table = (
            FakeTableRow(10, 3, 1, 2, 0, 3, 1, 5),
            FakeTableRow(11, 3, 1, 2, 0, 3, 1, 5),
        )
        rows = ManagementSourceDataBridge(controller).league_table_rows()

        # Even a numerically identical synthetic pair remains in the backend's
        # returned order. The bridge never substitutes ID/name sorting.
        self.assertEqual([row.club_id for row in rows], [10, 11])
        self.assertEqual([row.short_name for row in rows], ["Alpha", "Beta"])

    def test_missing_human_or_source_identity_fails_closed(self):
        controller = FakeController()
        controller.human = None
        bridge = ManagementSourceDataBridge(controller)
        with self.assertRaisesRegex(ManagementPresentationError, "Select"):
            bridge.club_header()
        with self.assertRaisesRegex(ManagementPresentationError, "Select"):
            bridge.squad_rows()

        controller = FakeController()
        controller.state.clubs[11] = SimpleNamespace(name="Beta City")
        bridge = ManagementSourceDataBridge(controller)
        with self.assertRaisesRegex(ManagementPresentationError, "short name"):
            bridge.fixture_rows()
        with self.assertRaisesRegex(ManagementPresentationError, "short name"):
            bridge.league_table_rows()

    def test_incomplete_fixture_source_contract_is_rejected_not_guessed(self):
        controller = FakeController()
        controller.state.premier_league.fixture_source_order = [17, 3]
        with self.assertRaisesRegex(ManagementPresentationError, "source ordering"):
            ManagementSourceDataBridge(controller).fixture_rows()

        controller = FakeController()
        controller.state.premier_league.fixture_source_order = (17, 999)
        with self.assertRaisesRegex(ManagementPresentationError, "missing"):
            ManagementSourceDataBridge(controller).fixture_rows()


if __name__ == "__main__":
    unittest.main()
