"""Tests for source-closed FM2001 chant runtime timing."""
from dataclasses import replace
import unittest

from gate14_chant_runtime_timing import (
    ACTIVE_LIST_GLOBAL_VA,
    CHANT_ACTIVE_UPDATE_VA,
    CHANT_PENDING_UPDATE_VA,
    CHANT_READY_GLOBAL_VA,
    CHANT_RUNTIME_UPDATE_VA,
    GATE_DEADLINE_OFFSET,
    PENDING_LIST_GLOBAL_VA,
    PHASE_DEADLINE_OFFSET,
    POLL_GUARD_MS,
    POOL_COOLDOWN_MS,
    POOL_COOLDOWN_WRITE_VA,
    RECYCLE_LIST_GLOBAL_VA,
    SOURCE_BOUNDARY,
    SOURCE_CLOCK_VA,
    STATE_OFFSET,
    STATE_PENDING_RESOURCE,
    STATE_PLAYING_FIRST_PHASE,
    STATE_PLAYING_SECOND_PHASE,
    STATE_READY,
    STATE2_DEADLINE_WRITE_VA,
    STATE3_DEADLINE_WRITE_VA,
    TIMING_FIELD_18_OFFSET,
    TIMING_FIELD_1C_OFFSET,
    TIMING_FIELD_20_OFFSET,
    Gate14ChantRuntimeTimingError,
    first_phase_deadline,
    pending_poll_deadline,
    pool_cooldown_deadline,
    second_phase_deadline,
)


class Gate14ChantRuntimeTimingTests(unittest.TestCase):
    def test_exact_runtime_addresses_offsets_and_states(self):
        self.assertEqual(CHANT_RUNTIME_UPDATE_VA, 0x7235E0)
        self.assertEqual(CHANT_PENDING_UPDATE_VA, 0x723600)
        self.assertEqual(CHANT_ACTIVE_UPDATE_VA, 0x7236E0)
        self.assertEqual(SOURCE_CLOCK_VA, 0x6AAE40)
        self.assertEqual(CHANT_READY_GLOBAL_VA, 0xA878D0)
        self.assertEqual(PENDING_LIST_GLOBAL_VA, 0xA87910)
        self.assertEqual(ACTIVE_LIST_GLOBAL_VA, 0xA8792C)
        self.assertEqual(RECYCLE_LIST_GLOBAL_VA, 0xA878F4)

        self.assertEqual(STATE_OFFSET, 0x08)
        self.assertEqual(GATE_DEADLINE_OFFSET, 0x10)
        self.assertEqual(PHASE_DEADLINE_OFFSET, 0x14)
        self.assertEqual(TIMING_FIELD_18_OFFSET, 0x18)
        self.assertEqual(TIMING_FIELD_1C_OFFSET, 0x1C)
        self.assertEqual(TIMING_FIELD_20_OFFSET, 0x20)
        self.assertEqual(
            (
                STATE_PENDING_RESOURCE,
                STATE_READY,
                STATE_PLAYING_FIRST_PHASE,
                STATE_PLAYING_SECOND_PHASE,
            ),
            (0, 1, 2, 3),
        )

    def test_exact_deadline_arithmetic(self):
        self.assertEqual(POLL_GUARD_MS, 200)
        self.assertEqual(POOL_COOLDOWN_MS, 6000)
        self.assertEqual(STATE2_DEADLINE_WRITE_VA, 0x723850)
        self.assertEqual(STATE3_DEADLINE_WRITE_VA, 0x7237B1)
        self.assertEqual(POOL_COOLDOWN_WRITE_VA, 0x723869)

        self.assertEqual(first_phase_deadline(1000, 250, 500), 1750)
        self.assertEqual(second_phase_deadline(1000, 300), 1500)
        self.assertEqual(pending_poll_deadline(1000), 1200)
        self.assertEqual(pool_cooldown_deadline(1000), 7000)

    def test_invalid_timing_inputs_fail_closed(self):
        for call in (
            lambda: first_phase_deadline(-1, 0, 0),
            lambda: first_phase_deadline(0, -1, 0),
            lambda: second_phase_deadline(0, -1),
            lambda: pending_poll_deadline(-1),
            lambda: pool_cooldown_deadline(-1),
        ):
            with self.assertRaises(Gate14ChantRuntimeTimingError):
                call()

    def test_timing_boundary_does_not_promote_record_or_event_semantics(self):
        self.assertTrue(SOURCE_BOUNDARY.source_clock_recovered)
        self.assertTrue(SOURCE_BOUNDARY.four_state_lifecycle_recovered)
        self.assertFalse(SOURCE_BOUNDARY.timing_field_semantics_recovered)
        self.assertFalse(SOURCE_BOUNDARY.event_binding_recovered)
        self.assertFalse(SOURCE_BOUNDARY.chant_meaning_recovered)
        for field in (
            "timing_field_semantics_recovered",
            "event_binding_recovered",
            "chant_meaning_recovered",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantRuntimeTimingError,
                    "cannot promote",
                ):
                    replace(SOURCE_BOUNDARY, **{field: True})


if __name__ == "__main__":
    unittest.main()
