import unittest
from dataclasses import dataclass

from match_schedule import MsvcCrtRng
from startup_rng import (
    LOADER444_FIRST_DECODE_RAW_DRAWS,
    StartupUserRngConfig,
    consume_dbtplayers_startup_rng,
    consume_loader444_first_decode_rng,
    consume_rng_bounds,
    consume_startup_team_name_rng,
    generated_name_rng_bound,
    generated_name_source_eligible,
    generated_name_source_ids,
    replay_precompetition_startup_rng,
    replay_startup_youth_generation,
    replay_startup_youth_generation_for_country,
    select_startup_youth_candidate,
    startup_spare_club_id,
    startup_youth_candidate_ids,
    startup_youth_target_count,
    startup_youth_selection_bounds,
    startup_team_name_country_ids,
    startup_team_name_rng_bounds,
)


class RecordingRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError((value, bound))
        return value


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    initial_flags: int = 0


class Loader444StartupRngTests(unittest.TestCase):
    def test_first_decode_consumes_exactly_260_raw_crt_draws(self):
        class RecordingRawRng:
            def __init__(self):
                self.calls = 0

            def rand15(self):
                self.calls += 1
                return 0

        rng = RecordingRawRng()
        consumed = consume_loader444_first_decode_rng(rng)

        self.assertEqual(LOADER444_FIRST_DECODE_RAW_DRAWS, 260)
        self.assertEqual(consumed, 260)
        self.assertEqual(rng.calls, 260)

    def test_first_decode_advances_real_msvc_state_exactly_like_260_rand_calls(self):
        replay_rng = MsvcCrtRng(0x12345678)
        manual_rng = MsvcCrtRng(0x12345678)

        consume_loader444_first_decode_rng(replay_rng)
        for _ in range(260):
            manual_rng.rand15()

        self.assertEqual(replay_rng.state, manual_rng.state)
        self.assertEqual(replay_rng.rand15(), manual_rng.rand15())


class DbtPlayersStartupRngTests(unittest.TestCase):
    def test_exact_two_phase_bounds_for_two_players(self):
        rng = RecordingRng([0] * 12)

        consumed = consume_dbtplayers_startup_rng(rng, 2)

        self.assertEqual(consumed, 12)
        self.assertEqual(
            rng.calls,
            [15, 15, 1, 1, 2, 2, 5, 1, 1, 2, 2, 5],
        )

    def test_shipped_player_count_reaches_fixed_seed_checkpoint(self):
        rng = MsvcCrtRng(0x12345678)
        consume_loader444_first_decode_rng(rng)
        self.assertEqual(rng.state, 0xC526B5BC)

        consumed = consume_dbtplayers_startup_rng(rng, 30064)

        self.assertEqual(consumed, 180384)
        self.assertEqual(rng.state, 0xA9C5115C)


class StartupYouthRngTests(unittest.TestCase):
    def test_option_target_count_preserves_exact_bounds_and_offsets(self):
        rng = RecordingRng([1, 0, 2])
        self.assertEqual(startup_youth_target_count(0, rng), 5)
        self.assertEqual(startup_youth_target_count(1, rng), 5)
        self.assertEqual(startup_youth_target_count(2, rng), 8)
        self.assertEqual(rng.calls, [2, 2, 3])

    def test_missing_or_unknown_option_consumes_no_rng(self):
        class NoRng:
            def randbelow(self, bound):
                raise AssertionError(f"unexpected RNG({bound})")
        rng = NoRng()
        self.assertEqual(startup_youth_target_count(None, rng), 4)
        self.assertEqual(startup_youth_target_count(99, rng), 4)

    def test_candidate_scan_uses_club_and_bit_three_in_source_order(self):
        players = (
            Player(7, 50, 0),
            Player(8, 50, 0x08),
            Player(9, 49, 0),
            Player(10, 50, 0x10),
        )
        self.assertEqual(startup_youth_candidate_ids(players, 50), (7, 10))


    def test_spare_lookup_returns_first_exact_name_or_zero(self):
        @dataclass(frozen=True)
        class Team:
            index: int
            name: str

        clubs = (
            Team(1, "!Spare Youth"),
            Team(332, "!Spare"),
            Team(900, "!Spare"),
        )
        self.assertEqual(startup_spare_club_id(clubs), 332)
        self.assertEqual(startup_spare_club_id((Team(1, "Spare"),)), 0)

    def test_candidate_scan_stops_at_original_512_entry_buffer(self):
        players = tuple(Player(i, 332, 0) for i in range(700))
        result = startup_youth_candidate_ids(players, 332)
        self.assertEqual(len(result), 512)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[-1], 511)

    def test_candidate_cap_counts_only_eligible_source_players(self):
        players = tuple(
            Player(i, 332 if i % 2 == 0 else 99, 0x08 if i % 4 == 0 else 0)
            for i in range(3000)
        )
        expected = tuple(
            p.index for p in players
            if p.club_id == 332 and not (p.initial_flags & 0x08)
        )[:512]
        self.assertEqual(startup_youth_candidate_ids(players, 332), expected)

    def test_selection_bounds_descend_from_actual_candidate_count(self):
        self.assertEqual(
            startup_youth_selection_bounds(512, 5),
            (512, 511, 510, 509, 508),
        )
        self.assertEqual(startup_youth_selection_bounds(3, 8), (3, 2, 1))
        self.assertEqual(
            startup_youth_selection_bounds(512, 8, destination_count=18),
            (512, 511),
        )

    def test_selection_uses_current_count_then_swap_deletes(self):
        candidates = [10, 20, 30, 40]
        rng = RecordingRng([1, 1])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 20)
        self.assertEqual(candidates, [10, 40, 30])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 40)
        self.assertEqual(candidates, [10, 30])
        self.assertEqual(rng.calls, [4, 3])


@dataclass(frozen=True)
class NamePlayer:
    index: int
    first_name: str
    surname: str
    nationality_id: int


@dataclass(frozen=True)
class Country:
    id: int
    nationality_id: int


@dataclass(frozen=True)
class Club:
    index: int
    name: str
    country_id: int
    team_category_code: int


class GeneratedNameRngTests(unittest.TestCase):
    def test_name_source_filter_preserves_original_literal_character_quirks(self):
        self.assertTrue(generated_name_source_eligible("Alan", "Smith"))
        self.assertFalse(generated_name_source_eligible("A.", "Smith"))
        self.assertFalse(generated_name_source_eligible("Alan", "Nash"))
        self.assertFalse(generated_name_source_eligible("Alan", "Bob"))
        self.assertFalse(generated_name_source_eligible("Alan", "Ab."))

    def test_nationality_source_vector_preserves_player_table_order(self):
        players = (
            NamePlayer(3, "Alan", "Smith", 7),
            NamePlayer(4, "A.", "Smith", 7),
            NamePlayer(5, "John", "Jones", 8),
            NamePlayer(6, "Eric", "Brown", 7),
        )
        self.assertEqual(generated_name_source_ids(players, 7), (3, 6))

    def test_name_rng_uses_nationality_count_only_when_above_ten(self):
        players = tuple(
            NamePlayer(i, "Alan", f"Smith{i}", 7 if i < 11 else 8)
            for i in range(15)
        )
        countries = (Country(26, 7), Country(31, 8))
        self.assertEqual(generated_name_rng_bound(26, countries, players), 11)
        self.assertEqual(generated_name_rng_bound(31, countries, players), 15)

    def test_country_minus_one_nationality_falls_back_to_index_26(self):
        players = tuple(
            NamePlayer(i, "Alan", f"Smith{i}", 26)
            for i in range(12)
        )
        countries = (Country(199, 0xFFFFFFFF),)
        self.assertEqual(generated_name_rng_bound(199, countries, players), 12)

    def test_team_name_loop_filter_and_two_draws_per_team(self):
        clubs = (
            Club(0, "Arsenal", 26, 1),
            Club(1, "!Spare", 26, 1),
            Club(2, "England", 26, 2),
            Club(3, "Chelsea", 31, 1),
        )
        players = tuple(
            [NamePlayer(i, "Alan", f"Smith{i}", 26) for i in range(12)]
            + [NamePlayer(100+i, "Eric", f"Brown{i}", 31) for i in range(13)]
        )
        countries = (Country(26, 26), Country(31, 31))
        self.assertEqual(startup_team_name_country_ids(clubs), (26, 31))
        self.assertEqual(
            startup_team_name_rng_bounds(clubs, countries, players),
            (12, 12, 13, 13),
        )


@dataclass(frozen=True)
class FullStartupPlayer:
    index: int
    club_id: int
    first_name: str
    surname: str
    nationality_id: int
    initial_flags: int = 0


class StartupReplayTests(unittest.TestCase):
    def test_full_precompetition_replay_has_exact_phase_states(self):
        players = tuple(
            [
                FullStartupPlayer(i, 332, "Alan", f"Smith{i}", 26)
                for i in range(12)
            ]
            + [
                FullStartupPlayer(12 + i, 332, "Eric", f"Brown{i}", 31)
                for i in range(13)
            ]
        )
        countries = (Country(26, 26), Country(31, 31))
        clubs = (
            Club(0, "Arsenal", 26, 1),
            Club(332, "!Spare", 26, 1),
            Club(2, "England", 26, 2),
            Club(3, "Chelsea", 31, 1),
        )
        users = (
            StartupUserRngConfig(country_id=26, option_mode=0),
            StartupUserRngConfig(country_id=31, option_mode=2),
        )
        rng = MsvcCrtRng(0x12345678)

        replay = replay_precompetition_startup_rng(
            rng,
            clubs,
            countries,
            players,
            selected_user_country_id=31,
            users=users,
        )

        self.assertEqual(replay.after_loader444_state, 0xC526B5BC)
        self.assertEqual(replay.after_players_state, 0xC6A1E94A)
        self.assertEqual(replay.after_team_names_state, 0x9936CABA)
        self.assertEqual(replay.after_youth_state, 0x4B68DE28)
        self.assertEqual(rng.state, replay.after_youth_state)

        self.assertEqual(replay.loader444_draw_count, 260)
        self.assertEqual(replay.player_draw_count, 150)
        self.assertEqual(replay.team_name_draw_count, 112)
        self.assertEqual(replay.youth_targets, (4, 8))
        self.assertEqual(
            replay.youth_source_ids,
            (
                (5, 1, 11, 0),
                (6, 2, 23, 21, 0, 1, 20, 8),
            ),
        )

    def test_consume_rng_bounds_preserves_order(self):
        rng = RecordingRng([1, 0, 2])
        self.assertEqual(consume_rng_bounds(rng, (3, 4, 5)), (1, 0, 2))
        self.assertEqual(rng.calls, [3, 4, 5])

    def test_team_name_replay_adds_108_selected_user_country_draws(self):
        clubs = (
            Club(0, "Arsenal", 26, 1),
            Club(1, "!Spare", 26, 1),
            Club(2, "England", 26, 2),
            Club(3, "Chelsea", 31, 1),
        )
        players = tuple(
            [NamePlayer(i, "Alan", f"Smith{i}", 26) for i in range(12)]
            + [NamePlayer(100+i, "Eric", f"Brown{i}", 31) for i in range(13)]
        )
        countries = (Country(26, 26), Country(31, 31))
        rng = RecordingRng([0] * 112)

        consumed = consume_startup_team_name_rng(
            rng,
            clubs,
            countries,
            players,
            selected_user_country_id=31,
        )

        self.assertEqual(consumed, 112)
        self.assertEqual(rng.calls[:4], [12, 12, 13, 13])
        self.assertEqual(rng.calls[4:], [13] * 108)

    def test_youth_replay_interleaves_selection_and_two_name_draws(self):
        # option mode 0 first draws RNG(2)=1, requesting five players. Only
        # four candidates exist, so all four are consumed.
        rng = RecordingRng([1] + [0] * 12)
        target, selected = replay_startup_youth_generation(
            rng,
            (10, 20, 30, 40),
            option_mode=0,
            name_bound=13,
        )

        self.assertEqual(target, 5)
        self.assertEqual(selected, (10, 40, 30, 20))
        self.assertEqual(
            rng.calls,
            [2, 4, 13, 13, 3, 13, 13, 2, 13, 13, 1, 13, 13],
        )

    def test_country_wrapper_uses_exact_generated_name_bound(self):
        players = tuple(
            [NamePlayer(i, "Alan", f"Smith{i}", 26) for i in range(12)]
            + [NamePlayer(100+i, "Eric", f"Brown{i}", 31) for i in range(13)]
        )
        countries = (Country(26, 26), Country(31, 31))
        # Unknown option value gives deterministic target 4, so the only
        # calls are candidate/name/name repeated four times.
        rng = RecordingRng([0] * 12)
        target, selected = replay_startup_youth_generation_for_country(
            rng,
            (10, 20, 30, 40),
            99,
            31,
            countries,
            players,
        )

        self.assertEqual(target, 4)
        self.assertEqual(selected, (10, 40, 30, 20))
        self.assertEqual(
            rng.calls,
            [4, 13, 13, 3, 13, 13, 2, 13, 13, 1, 13, 13],
        )


if __name__ == "__main__":
    unittest.main()
