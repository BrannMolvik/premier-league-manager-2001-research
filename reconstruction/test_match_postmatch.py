import unittest
from dataclasses import dataclass

from match_events import IncidentKind, IncidentRecord, SubstitutionRecord
from match_postmatch import (
    FormTransitionSettings,
    appeared_player_indices,
    persist_post_match_side,
    update_post_match_form,
)
from match_simulation import (
    NormalMatchResult,
    PreparedMatchPlayer,
    PreparedMatchSide,
    TimedMatchEvent,
)
from match_strength import TeamStrengthContext


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError(f"{value} outside RNG({bound})")
        return value


@dataclass
class RuntimePlayer:
    condition: int = 80
    form_state: int = 2
    injured: bool = False


def prepared_player(index, *, active=True, bench=False, condition=80):
    return PreparedMatchPlayer(
        side=0,
        player_index=index,
        condition=condition,
        form_state=2,
        current_position=12,
        balance_position_code=10,
        preferred_positions=(12, 0, 0),
        skills=(100,) * 17,
        active=active,
        substitution_available=bench,
    )


def prepared_side():
    context = TeamStrengthContext(
        tactic_style=0,
        match_bias=2,
        user_controlled=False,
        aggression=5,
    )
    return PreparedMatchSide(
        players=(
            prepared_player(0, condition=74),
            prepared_player(1, condition=73),
            prepared_player(2, active=False, bench=True, condition=79),
            prepared_player(3, active=False, bench=True, condition=80),
        ),
        attack_context=context,
        defence_context=context,
        penalty_taker_priority=(),
        corner_taker_priority=(),
        free_kick_taker_priority=(),
        starting_player_indices=(0, 1),
    )


class FormTransitionTests(unittest.TestCase):
    def test_failed_trigger_consumes_only_one_rng_draw(self):
        rng = ScriptedRng([5])
        self.assertEqual(update_post_match_form(2, rng), 2)
        self.assertEqual(rng.calls, [100])

    def test_neutral_form_can_increase_or_decrease(self):
        self.assertEqual(
            update_post_match_form(2, ScriptedRng([0, 49])),
            3,
        )
        self.assertEqual(
            update_post_match_form(2, ScriptedRng([0, 50])),
            1,
        )

    def test_out_of_form_and_in_form_use_their_exact_trigger_probabilities(self):
        settings = FormTransitionSettings(
            form_change_prob=5,
            in_form_change_prob=20,
            out_of_form_change_prob=20,
            form_increase_prob=50,
        )
        self.assertEqual(
            update_post_match_form(1, ScriptedRng([19, 0]), settings),
            2,
        )
        self.assertEqual(
            update_post_match_form(1, ScriptedRng([20]), settings),
            1,
        )
        self.assertEqual(
            update_post_match_form(3, ScriptedRng([19, 99]), settings),
            2,
        )
        self.assertEqual(
            update_post_match_form(3, ScriptedRng([20]), settings),
            3,
        )

    def test_boundary_states_clamp_exactly(self):
        self.assertEqual(update_post_match_form(0, ScriptedRng([0, 99])), 0)
        self.assertEqual(update_post_match_form(4, ScriptedRng([0, 0])), 4)
        self.assertEqual(update_post_match_form(0, ScriptedRng([0, 0])), 1)
        self.assertEqual(update_post_match_form(4, ScriptedRng([0, 99])), 3)


class PostMatchPersistenceTests(unittest.TestCase):
    def test_appeared_set_is_starters_plus_incoming_substitutes(self):
        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(60, SubstitutionRecord(0, 1, 2)),
        ))
        self.assertEqual(
            appeared_player_indices(side, result),
            frozenset((0, 1, 2)),
        )

    def test_condition_injury_and_form_persist_in_participant_order(self):
        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(55, IncidentRecord(IncidentKind.INJURED, 0, 1)),
            TimedMatchEvent(55, SubstitutionRecord(0, 1, 2)),
        ))
        runtime = [
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=4),
        ]
        # Three appeared players. Every trigger succeeds and every transition
        # chooses the increase branch: two RNG(100) draws per appeared player.
        rng = ScriptedRng([0, 0, 0, 0, 0, 0])
        settings = FormTransitionSettings(
            form_change_prob=100,
            in_form_change_prob=100,
            out_of_form_change_prob=100,
            form_increase_prob=100,
        )

        summary = persist_post_match_side(
            side,
            runtime,
            result,
            rng,
            form_settings=settings,
        )

        self.assertEqual([p.condition for p in runtime], [74, 73, 79, 80])
        self.assertEqual([p.form_state for p in runtime], [3, 3, 3, 4])
        self.assertFalse(runtime[0].injured)
        self.assertTrue(runtime[1].injured)
        self.assertFalse(runtime[2].injured)
        self.assertEqual(summary.appeared_player_indices, frozenset((0, 1, 2)))
        self.assertEqual(summary.injured_player_indices, frozenset((1,)))
        self.assertEqual(rng.calls, [100] * 6)

    def test_wrong_participant_count_is_rejected(self):
        with self.assertRaises(ValueError):
            persist_post_match_side(
                prepared_side(),
                [RuntimePlayer()],
                NormalMatchResult(events=()),
                ScriptedRng([]),
            )


if __name__ == "__main__":
    unittest.main()
