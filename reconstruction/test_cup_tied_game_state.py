import unittest
from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace

from game_state import GameState
from transfer_state import PlayerMovement


@dataclass
class Player:
    index: int
    club_id: int


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    parent_competition_id: int | None = None
    cup_restriction_mode: int = 0


def side(side_id: int, starter_count: int):
    return SimpleNamespace(
        side=side_id,
        starting_player_indices=tuple(range(starter_count)),
    )


class GameStateCupTiedIntegrationTests(unittest.TestCase):
    def test_appeared_players_record_against_root_cup_context_in_roster_order(self):
        home = (Player(11, 10), Player(12, 10), Player(13, 10))
        away = (Player(21, 20), Player(22, 20))
        state = GameState.from_players((*home, *away), date(2000, 8, 1))
        state.competitions = {
            100: Competition(100, 2),
            101: Competition(101, 1, 100),
        }
        result = SimpleNamespace(events=())

        inserted = state._record_cup_tied_appearances(
            competition_id=101,
            home_club_id=10,
            away_club_id=20,
            home_side=side(0, 2),
            away_side=side(1, 1),
            home_participants=home,
            away_participants=away,
            result=result,
        )

        self.assertEqual(inserted, (11, 12, 21))
        self.assertEqual(
            tuple(
                (record.player_id, record.club_id)
                for record in state.cup_tied_collections[100].records
            ),
            ((11, 10), (12, 10), (21, 20)),
        )

    def test_first_appearance_club_survives_later_transfer_and_drives_lookup(self):
        player = Player(11, 10)
        state = GameState.from_players((player,), date(2000, 8, 1))
        state.competitions = {100: Competition(100, 2)}
        result = SimpleNamespace(events=())

        state._record_cup_tied_appearances(
            competition_id=100,
            home_club_id=10,
            away_club_id=20,
            home_side=side(0, 1),
            away_side=side(1, 0),
            home_participants=(player,),
            away_participants=(),
            result=result,
        )
        self.assertFalse(state.is_player_cup_tied(100, 11, 10))

        # Transfer after the qualifying appearance. The original collection is
        # not rewritten; 0x4E9710 now sees the differing current club.
        player.club_id = 20
        state.club_roster_order = {20: [11]}

        self.assertTrue(state.is_player_cup_tied(100, 11, 20))
        self.assertEqual(state.cup_tied_collections[100].recorded_club_id(11), 10)

    def test_mode1_collection_miss_uses_latest_persisted_transfer_date(self):
        player = Player(11, 10)
        state = GameState.from_players((player,), date(2000, 7, 1))
        state.competitions = {100: Competition(100, 2, cup_restriction_mode=1)}
        state.cup_tied_transfer_window.advance_day(date(2000, 8, 30))
        movement_date = state.cup_tied_transfer_window.cutoff_1 + timedelta(days=1)
        state.transfers.record_movement(
            PlayerMovement(11, 10, 20, 100, movement_date)
        )
        player.club_id = 20
        state.club_roster_order = {20: [11]}

        self.assertTrue(state.is_player_cup_tied_for_status(100, 11, 20))

    def test_mode1_transfer_date_equality_is_not_tied(self):
        player = Player(11, 20)
        state = GameState.from_players((player,), date(2000, 7, 1))
        state.competitions = {100: Competition(100, 2, cup_restriction_mode=1)}
        state.cup_tied_transfer_window.advance_day(date(2000, 8, 30))
        state.transfers.record_movement(
            PlayerMovement(
                11, 10, 20, 100, state.cup_tied_transfer_window.cutoff_1
            )
        )
        self.assertFalse(state.is_player_cup_tied_for_status(100, 11, 20))

    def test_non_mode1_collection_miss_does_not_use_transfer_date_fallback(self):
        player = Player(11, 20)
        state = GameState.from_players((player,), date(2000, 7, 1))
        state.competitions = {100: Competition(100, 2, cup_restriction_mode=2)}
        state.cup_tied_transfer_window.advance_day(date(2000, 8, 30))
        state.transfers.record_movement(
            PlayerMovement(
                11,
                10,
                20,
                100,
                state.cup_tied_transfer_window.cutoff_1 + timedelta(days=10),
            )
        )
        self.assertFalse(state.is_player_cup_tied_for_status(100, 11, 20))

    def test_stale_latest_movement_fails_closed(self):
        player = Player(11, 20)
        state = GameState.from_players((player,), date(2000, 7, 1))
        state.competitions = {100: Competition(100, 2, cup_restriction_mode=1)}
        state.cup_tied_transfer_window.advance_day(date(2000, 8, 30))
        state.transfers.record_movement(
            PlayerMovement(
                11,
                9,
                19,
                100,
                state.cup_tied_transfer_window.cutoff_1 + timedelta(days=10),
            )
        )
        self.assertFalse(state.is_player_cup_tied_for_status(100, 11, 20))

    def test_daily_hook_moves_selector_on_source_boundaries(self):
        state = GameState.from_players((), date(2000, 8, 29))
        self.assertEqual(state.cup_tied_transfer_window.selector, 0)
        state.calendar.advance_one_day()
        self.assertEqual(state.cup_tied_transfer_window.selector, 1)
        days = (
            date(2001, 1, 30).toordinal()
            - date(2000, 8, 30).toordinal()
        )
        state.calendar.advance(days)
        self.assertEqual(state.cup_tied_transfer_window.selector, 2)

    def test_missing_runtime_kind_metadata_does_not_mutate_state(self):
        player = Player(11, 10)
        state = GameState.from_players((player,), date(2000, 8, 1))
        state.competitions = {100: SimpleNamespace(id=100, parent_competition_id=None)}
        result = SimpleNamespace(events=())

        inserted = state._record_cup_tied_appearances(
            competition_id=100,
            home_club_id=10,
            away_club_id=20,
            home_side=side(0, 1),
            away_side=side(1, 0),
            home_participants=(player,),
            away_participants=(),
            result=result,
        )

        self.assertEqual(inserted, ())
        self.assertEqual(state.cup_tied_collections, {})

    def test_root_league_context_never_creates_cup_tied_state(self):
        player = Player(11, 10)
        state = GameState.from_players((player,), date(2000, 8, 1))
        state.competitions = {0: Competition(0, 1)}
        result = SimpleNamespace(events=())

        inserted = state._record_cup_tied_appearances(
            competition_id=0,
            home_club_id=10,
            away_club_id=20,
            home_side=side(0, 1),
            away_side=side(1, 0),
            home_participants=(player,),
            away_participants=(),
            result=result,
        )

        self.assertEqual(inserted, ())
        self.assertEqual(state.cup_tied_collections, {})
        self.assertFalse(state.is_player_cup_tied(0, 11, 20))


if __name__ == "__main__":
    unittest.main()
