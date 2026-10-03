"""Tests for source-closed FastView PossessionDiagram primitives."""
import unittest

from gate14_possession_diagram import (
    INITIAL_OVERLAY_STATE,
    OFFSCREEN_X,
    OVERLAY_PATHS,
    PITCH_NORMAL_PATH,
    PITCH_RECT,
    PROCESS_INITIAL_PRESENTATION_RNG_STATE,
    SOURCE_GLOBAL_PENALTIES_RECEIVER_VA,
    SOURCE_GOAL_RECEIVER_VA,
    SOURCE_PENALTIES_LATCH_OFFSET,
    SOURCE_MATCH_ITERATOR_TICK_VA,
    SOURCE_MATCH_ITERATOR_VFTABLE,
    SOURCE_EVENT_POSSESSION_CONSTRUCTOR_VA,
    SOURCE_EVENT_POSSESSION_CONSTRUCT_CALL_VA,
    SOURCE_EVENT_POSSESSION_SENDER_OFFSET,
    SOURCE_GLOBAL_TICK_DIVISOR,
    active_overlay_rect,
    advance_possession_diagram,
    apply_global_penalties_event,
    apply_goal_event,
    apply_possession_event,
    possession_roll,
    presentation_rand_step,
    should_emit_possession_on_global_tick,
)


class PossessionDiagramTests(unittest.TestCase):
    def test_source_geometry(self):
        self.assertEqual(PITCH_RECT, (253, 139, 547, 217))
        self.assertEqual(INITIAL_OVERLAY_STATE, 1)
        self.assertEqual(OFFSCREEN_X, 4000)
        self.assertEqual(
            [active_overlay_rect(i) for i in range(3)],
            [
                (253, 139, 378, 217),
                (351, 139, 449, 217),
                (422, 139, 547, 217),
            ],
        )
        self.assertTrue(
            PITCH_NORMAL_PATH.endswith("FastView/pitch_normal.444")
        )
        self.assertEqual(len(OVERLAY_PATHS), 3)

    def test_private_rng_matches_source_constants(self):
        state, value = presentation_rand_step(
            PROCESS_INITIAL_PRESENTATION_RNG_STATE
        )
        self.assertEqual(state, 2531011)
        self.assertEqual(value, (2531011 >> 16) & 0x7FFF)
        state2, value2 = presentation_rand_step(state)
        self.assertEqual(
            state2, (214013 * state + 2531011) & 0xFFFFFFFF
        )
        self.assertEqual(value2, (state2 >> 16) & 0x7FFF)

    def test_source_roll_is_floor_division_by_327(self):
        self.assertEqual(possession_roll(0), 0)
        self.assertEqual(possession_roll(326), 0)
        self.assertEqual(possession_roll(327), 1)
        self.assertEqual(possession_roll(32700), 100)
        self.assertEqual(possession_roll(32767), 100)

    def test_success_moves_right_unless_already_at_right_edge(self):
        self.assertEqual(
            advance_possession_diagram(0, 100, 0).next_state, 1
        )
        self.assertEqual(
            advance_possession_diagram(1, 100, 0).next_state, 2
        )
        self.assertEqual(
            advance_possession_diagram(2, 100, 0).next_state, 1
        )

    def test_failed_roll_moves_left_with_zero_clamp(self):
        seed = 1
        while True:
            next_seed, rand15 = presentation_rand_step(seed)
            if possession_roll(rand15) > 0:
                break
            seed = next_seed
        self.assertEqual(
            advance_possession_diagram(2, 0, seed).next_state, 1
        )
        self.assertEqual(
            advance_possession_diagram(1, 0, seed).next_state, 0
        )
        self.assertEqual(
            advance_possession_diagram(0, 0, seed).next_state, 0
        )

    def test_receiver_addresses_and_latch_offset_are_source_bound(self):
        self.assertEqual(SOURCE_GOAL_RECEIVER_VA, 0x522C30)
        self.assertEqual(SOURCE_GLOBAL_PENALTIES_RECEIVER_VA, 0x522C60)
        self.assertEqual(SOURCE_PENALTIES_LATCH_OFFSET, 0x20)

    def test_possession_event_uses_rng_until_penalties_latches(self):
        normal = apply_possession_event(
            1, 100, 0, penalties_latched=False
        )
        self.assertEqual(normal.next_state, 2)
        self.assertNotEqual(normal.rng_state_after, normal.rng_state_before)
        self.assertIsNotNone(normal.transition)

        latched = apply_possession_event(
            2, 0, normal.rng_state_after, penalties_latched=True
        )
        self.assertEqual(latched.next_state, 1)
        self.assertEqual(latched.rng_state_after, normal.rng_state_after)
        self.assertIsNone(latched.transition)

    def test_goal_event_snaps_source_field_zero_and_one_to_edges(self):
        self.assertEqual(
            apply_goal_event(
                1, 0, 123, penalties_latched=False
            ).next_state,
            2,
        )
        self.assertEqual(
            apply_goal_event(
                1, 1, 123, penalties_latched=False
            ).next_state,
            0,
        )
        other = apply_goal_event(
            2, 7, 123, penalties_latched=True
        )
        self.assertEqual(other.next_state, 2)
        self.assertTrue(other.penalties_latched)
        self.assertEqual(other.rng_state_after, 123)

    def test_global_penalties_only_latches_until_next_possession_event(self):
        latched = apply_global_penalties_event(
            2, 77, penalties_latched=False
        )
        self.assertEqual(latched.next_state, 2)
        self.assertTrue(latched.penalties_latched)
        self.assertEqual(latched.rng_state_after, 77)
        followup = apply_possession_event(
            latched.next_state,
            100,
            latched.rng_state_after,
            penalties_latched=latched.penalties_latched,
        )
        self.assertEqual(followup.next_state, 1)
        self.assertEqual(followup.rng_state_after, 77)

    def test_event_possession_emits_every_fifth_global_tick_under_source_gates(self):
        self.assertEqual(SOURCE_MATCH_ITERATOR_TICK_VA, 0x519630)
        self.assertEqual(SOURCE_MATCH_ITERATOR_VFTABLE, 0x7CA1DC)
        self.assertEqual(SOURCE_EVENT_POSSESSION_CONSTRUCTOR_VA, 0x51A6B0)
        self.assertEqual(SOURCE_EVENT_POSSESSION_CONSTRUCT_CALL_VA, 0x5197B8)
        self.assertEqual(SOURCE_EVENT_POSSESSION_SENDER_OFFSET, 0x20)
        self.assertEqual(SOURCE_GLOBAL_TICK_DIVISOR, 5)
        self.assertFalse(
            should_emit_possession_on_global_tick(
                4, field_a5=0, field_98_present=True, field_a0_present=True
            )
        )
        self.assertTrue(
            should_emit_possession_on_global_tick(
                5, field_a5=0, field_98_present=True, field_a0_present=True
            )
        )
        self.assertTrue(
            should_emit_possession_on_global_tick(
                10, field_a5=0, field_98_present=True, field_a0_present=True
            )
        )

    def test_event_possession_global_tick_gates_fail_closed(self):
        for kwargs in (
            dict(field_a5=1, field_98_present=True, field_a0_present=True),
            dict(field_a5=0, field_98_present=False, field_a0_present=True),
            dict(field_a5=0, field_98_present=True, field_a0_present=False),
        ):
            self.assertFalse(
                should_emit_possession_on_global_tick(10, **kwargs)
            )
        for call in (
            lambda: should_emit_possession_on_global_tick(
                -1, field_a5=0, field_98_present=True, field_a0_present=True
            ),
            lambda: should_emit_possession_on_global_tick(
                5, field_a5=256, field_98_present=True, field_a0_present=True
            ),
            lambda: should_emit_possession_on_global_tick(
                5, field_a5=0, field_98_present=1, field_a0_present=True
            ),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            active_overlay_rect(3)
        with self.assertRaises(ValueError):
            advance_possession_diagram(1, 101, 0)
        with self.assertRaises(ValueError):
            presentation_rand_step(-1)
        with self.assertRaises(ValueError):
            apply_possession_event(1, 50, 0, penalties_latched=1)
        with self.assertRaises(ValueError):
            apply_goal_event(1, "0", 0, penalties_latched=False)
        with self.assertRaises(ValueError):
            apply_global_penalties_event(3, 0, penalties_latched=False)


if __name__ == "__main__":
    unittest.main()
