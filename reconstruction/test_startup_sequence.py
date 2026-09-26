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
    short_name: str = ""
    competition_id: int = 0
    historical_competition_id: int = 0
    historical_slot_index: int = 0


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 0
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 0
    enumerated_club_reference_0: int = -1
    enumerated_club_reference_1: int = -1


@dataclass(frozen=True)
class Round:
    competition_id: int
    team_count: int
    id: int = 0
    type_code: int = 1
    scheduled_week: int = 0
    scheduled_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF
    new_entrants: int = 0
    replay_week: int = 0
    replay_weekday: int = 1


@dataclass(frozen=True)
class Allocation:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int = 0


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
            Country(123, 123, 1),
        )
        clubs = (
            # Name-generation / youth source fixtures. These four also form a
            # deterministic type-3 source for the synthetic Cup below;
            # competition membership does not change the precompetition path.
            Club(0, "Arsenal", 26, 1, 0, "Arsenal", 20, 20, 0),
            Club(332, "!Spare", 26, 1, 0, "!Spare", 20, 20, 1),
            Club(2, "England", 26, 2, 0, "England", 20, 20, 2),
            Club(3, "Chelsea", 31, 1, 0, "Chelsea", 20, 20, 3),
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
        competitions = (
            Competition(20, 3, 1, None, -1, 26),
            Competition(9, 2, 1, None, 0, 123),
            Competition(10, 2, 1, None, 1, 123),
            Competition(170, 2, 2, None, 0, 116),
            Competition(0, 1, 1, None, 9, 26),
        )
        rounds = (
            Round(9, 4, 198, 2, 2, 3, new_entrants=4, replay_week=3),
            Round(9, 2, 205, 1, 47, 3, new_entrants=0),
            Round(170, 16, 1000, 1, 10, 1),
            Round(0, 20, 0, 4, 7, 6),
        )
        rng = MsvcCrtRng(0x12345678)

        replay = replay_startup_rng_to_primary_shuffle(
            rng,
            clubs,
            countries,
            players,
            selected_user_country_id=31,
            users=users,
            competitions=competitions,
            rounds=rounds,
            allocation_instructions=(
                Allocation(1, 9, 1, 3, 20, 4),
            ),
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
            0xC6A1E94A,
        )
        self.assertEqual(
            replay.precompetition.after_team_names_state,
            0x9936CABA,
        )
        self.assertEqual(
            replay.precompetition.after_youth_state,
            0x4B68DE28,
        )

        self.assertEqual(
            replay.primary_competition_state.rng_plan_total_draw_count,
            6,
        )
        self.assertEqual(
            sum(
                len(event.bounds)
                for event in replay.primary_competition_state.rng_events
                if event.kind == "cup_round_shuffle"
            ),
            4,
        )
        self.assertEqual(
            sum(
                len(event.bounds)
                for event in replay.primary_competition_state.rng_events
                if event.kind == "europe_selector"
            ),
            2,
        )
        self.assertEqual(
            tuple(
                (event.kind, event.competition_id, event.round_id)
                for event in replay.primary_competition_state.rng_events
                if event.kind != "fixed_league"
            ),
            (
                ("europe_selector", 9, None),
                ("cup_round_shuffle", 9, 198),
                ("cup_round_shuffle", 9, 205),
                ("europe_selector", 10, None),
            ),
        )
        self.assertEqual(
            tuple(
                event.participant_count
                for event in replay.primary_competition_state.rng_events
                if event.kind == "cup_round_shuffle"
            ),
            (4, 2),
        )
        self.assertEqual(
            replay.state_entering_primary_shuffle,
            0x44D2B546,
        )
        self.assertEqual(rng.state, 0x44D2B546)


if __name__ == "__main__":
    unittest.main()
