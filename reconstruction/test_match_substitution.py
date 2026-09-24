import unittest
from dataclasses import dataclass

from match_substitution import (
    ai_substitution_threshold_minute,
    apply_ai_substitution,
    best_available_replacement,
    substitution_availability_value,
    substitution_timing_value,
)


@dataclass
class Player:
    side: int
    player_index: int
    active: bool
    substitution_available: bool
    form_state: int
    current_position: int
    position_aux_code: int
    preferred_positions: tuple[int, int, int]
    skills: tuple[int, ...]


def skills(value: int) -> tuple[int, ...]:
    return (value,) * 17


def player(
    idx: int,
    role: int,
    value: int,
    *,
    active: bool,
    bench: bool = False,
    form: int = 2,
    preferred: tuple[int, int, int] | None = None,
    aux: int = 0,
) -> Player:
    return Player(
        side=0,
        player_index=idx,
        active=active,
        substitution_available=bench,
        form_state=form,
        current_position=role,
        position_aux_code=aux,
        preferred_positions=preferred or (role, 0, 0),
        skills=skills(value),
    )


class SubstitutionStateTests(unittest.TestCase):
    def test_timing_value_counts_inactive_original_starters(self):
        players = [
            player(0, 4, 100, active=True),
            player(1, 12, 100, active=True),
            player(2, 18, 100, active=True),
        ]
        starters = (0, 1, 2)

        self.assertEqual(substitution_timing_value(players, starters), 3)
        self.assertEqual(ai_substitution_threshold_minute(players, starters), 60)

        players[2].active = False
        self.assertEqual(substitution_timing_value(players, starters), 2)
        self.assertEqual(ai_substitution_threshold_minute(players, starters), 70)

        players[1].active = False
        self.assertEqual(ai_substitution_threshold_minute(players, starters), 80)

    def test_availability_value_counts_neither_active_nor_bench_state(self):
        players = [
            player(0, 12, 100, active=True),
            player(1, 12, 100, active=False, bench=True),
            player(2, 12, 100, active=False),
        ]
        self.assertEqual(substitution_availability_value(players), 2)

    def test_best_replacement_preserves_first_player_on_equal_rating(self):
        players = [
            player(0, 12, 80, active=True),
            player(1, 12, 180, active=False, bench=True),
            player(2, 12, 180, active=False, bench=True),
        ]
        replacement = best_available_replacement(players, 12)
        self.assertIsNotNone(replacement)
        self.assertEqual(replacement.player_index, 1)


class AiSubstitutionTests(unittest.TestCase):
    def test_tied_ai_side_substitutes_from_minute_60(self):
        outgoing = player(
            0,
            12,
            60,
            active=True,
            preferred=(10, 12, 0),
            aux=7,
        )
        bench = player(
            1,
            10,
            220,
            active=False,
            bench=True,
            preferred=(10, 12, 0),
            aux=2,
        )
        players = [outgoing, bench]

        event = apply_ai_substitution(
            0,
            60,
            (0, 0),
            players,
            (0,),
            user_controlled=False,
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.player_side, 0)
        self.assertEqual(event.outgoing_player_index, 0)
        self.assertEqual(event.incoming_player_index, 1)
        self.assertFalse(outgoing.active)
        self.assertTrue(bench.active)
        self.assertFalse(bench.substitution_available)
        self.assertEqual(bench.current_position, 12)
        self.assertEqual(bench.position_aux_code, 7)
        self.assertEqual(outgoing.current_position, 10)
        self.assertEqual(outgoing.position_aux_code, 0)

    def test_routine_does_not_substitute_while_leading(self):
        players = [
            player(0, 12, 60, active=True),
            player(1, 12, 220, active=False, bench=True),
        ]
        event = apply_ai_substitution(
            0,
            60,
            (2, 1),
            players,
            (0,),
            user_controlled=False,
        )
        self.assertIsNone(event)

    def test_user_controlled_side_is_excluded(self):
        players = [
            player(0, 12, 60, active=True),
            player(1, 12, 220, active=False, bench=True),
        ]
        event = apply_ai_substitution(
            0,
            60,
            (0, 0),
            players,
            (0,),
            user_controlled=True,
        )
        self.assertIsNone(event)

    def test_best_candidate_with_low_pre_sub_role_causes_pair_rejection(self):
        outgoing = player(0, 12, 60, active=True)
        # This player wins 0x409950's queried-role rating, but its own current
        # role is below 8, so 0x62E2F0 rejects the pair without asking 0x409950
        # for the next-best bench option.
        rejected_best = player(
            1,
            4,
            255,
            active=False,
            bench=True,
            preferred=(12, 4, 0),
        )
        acceptable_second = player(
            2,
            12,
            120,
            active=False,
            bench=True,
        )
        event = apply_ai_substitution(
            0,
            60,
            (0, 0),
            [outgoing, rejected_best, acceptable_second],
            (0,),
            user_controlled=False,
        )
        self.assertIsNone(event)

    def test_no_automatic_outgoing_defender_substitution(self):
        players = [
            player(0, 4, 60, active=True),
            player(1, 12, 220, active=False, bench=True),
        ]
        event = apply_ai_substitution(
            0,
            60,
            (0, 0),
            players,
            (0,),
            user_controlled=False,
        )
        self.assertIsNone(event)


if __name__ == "__main__":
    unittest.main()
