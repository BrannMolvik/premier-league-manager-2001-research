"""Tests for source-closed FastView PossessionDiagram primitives."""
import unittest

from gate14_possession_diagram import (
    INITIAL_OVERLAY_STATE,
    OFFSCREEN_X,
    OVERLAY_PATHS,
    PITCH_NORMAL_PATH,
    PITCH_RECT,
    PROCESS_INITIAL_PRESENTATION_RNG_STATE,
    active_overlay_rect,
    advance_possession_diagram,
    possession_roll,
    presentation_rand_step,
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

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            active_overlay_rect(3)
        with self.assertRaises(ValueError):
            advance_possession_diagram(1, 101, 0)
        with self.assertRaises(ValueError):
            presentation_rand_step(-1)


if __name__ == "__main__":
    unittest.main()
