"""Tests for source-closed chant runtime pool selection."""
from dataclasses import replace
import unittest

from gate14_chant_runtime_pool_selection import (
    AWAY_POOL_GLOBAL_VA,
    AWAY_POOL_INDEX,
    AWAY_SELECTOR,
    ENQUEUE_VA,
    GENERIC_CURSOR_GLOBAL_VA,
    GENERIC_PICK_VA,
    GENERIC_POOL_GLOBAL_VA,
    GENERIC_POOL_INDEX,
    GENERIC_SELECTOR,
    HOME_POOL_GLOBAL_VA,
    HOME_POOL_INDEX,
    HOME_SELECTOR,
    RECORD_GATE_DEADLINE_OFFSET,
    RECORD_USE_FIELD_OFFSET,
    SELECTOR_TABLE_VA,
    SELECT_POOL_VA,
    SOURCE_BOUNDARY,
    SPECIALIZED_PICK_VA,
    SPECIALIZED_PREDICATE_VA,
    Gate14ChantPoolSelectionError,
    RuntimeChantCandidate,
    select_generic_candidate,
    select_specialized_candidate,
    selector_pool,
    specialized_candidate_is_eligible,
)


class Gate14ChantRuntimePoolSelectionTests(unittest.TestCase):
    def test_exact_source_selector_and_pool_addresses(self):
        self.assertEqual(ENQUEUE_VA, 0x723360)
        self.assertEqual(SELECT_POOL_VA, 0x723440)
        self.assertEqual(GENERIC_PICK_VA, 0x723470)
        self.assertEqual(SPECIALIZED_PICK_VA, 0x7234D0)
        self.assertEqual(SPECIALIZED_PREDICATE_VA, 0x723510)
        self.assertEqual(SELECTOR_TABLE_VA, 0x7DE270)

        self.assertEqual((HOME_SELECTOR, AWAY_SELECTOR, GENERIC_SELECTOR), (0, 1, 2))
        self.assertEqual((HOME_POOL_INDEX, AWAY_POOL_INDEX, GENERIC_POOL_INDEX), (2, 3, 1))
        self.assertEqual(HOME_POOL_GLOBAL_VA, 0xA87984)
        self.assertEqual(AWAY_POOL_GLOBAL_VA, 0xA879A0)
        self.assertEqual(GENERIC_POOL_GLOBAL_VA, 0xA87968)
        self.assertEqual(GENERIC_CURSOR_GLOBAL_VA, 0xA878DC)
        self.assertEqual(RECORD_USE_FIELD_OFFSET, 0x04)
        self.assertEqual(RECORD_GATE_DEADLINE_OFFSET, 0x0C)

        self.assertEqual(selector_pool(0), "home")
        self.assertEqual(selector_pool(1), "away")
        self.assertEqual(selector_pool(2), "generic")

    def test_specialized_gate_and_one_in_pool_count_acceptance(self):
        blocked = RuntimeChantCandidate("blocked", 2, 2000)
        fresh_use = RuntimeChantCandidate("fresh-use", 1, 2000)
        expired = RuntimeChantCandidate("expired", 4, 900)

        self.assertFalse(specialized_candidate_is_eligible(blocked, now_ms=1000))
        self.assertTrue(specialized_candidate_is_eligible(fresh_use, now_ms=1000))
        self.assertTrue(specialized_candidate_is_eligible(expired, now_ms=1000))

        # pool count is 3. blocked consumes no RNG. fresh-use gets remainder 2
        # and fails; expired gets remainder 0 and is the first accepted record.
        selected = select_specialized_candidate(
            (blocked, fresh_use, expired),
            now_ms=1000,
            rng_remainders=(2, 0),
        )
        self.assertIs(selected, expired)

        self.assertIsNone(
            select_specialized_candidate(
                (blocked, fresh_use, expired),
                now_ms=1000,
                rng_remainders=(1, 2),
            )
        )

    def test_specialized_search_stops_consuming_rng_after_acceptance(self):
        candidates = (
            RuntimeChantCandidate("a", 0, 9999),
            RuntimeChantCandidate("b", 0, 9999),
        )
        self.assertIs(
            select_specialized_candidate(
                candidates,
                now_ms=0,
                rng_remainders=(0,),
            ),
            candidates[0],
        )
        with self.assertRaisesRegex(
            Gate14ChantPoolSelectionError,
            "stops consuming RNG",
        ):
            select_specialized_candidate(
                candidates,
                now_ms=0,
                rng_remainders=(0, 1),
            )

    def test_generic_pool_cycles_backwards_and_reloads_at_zero(self):
        records = (
            RuntimeChantCandidate("g0", 0, 0),
            RuntimeChantCandidate("g1", 0, 0),
            RuntimeChantCandidate("g2", 0, 0),
        )

        item, cursor = select_generic_candidate(records, cursor=0)
        self.assertIs(item, records[2])
        self.assertEqual(cursor, 2)

        item, cursor = select_generic_candidate(records, cursor=cursor)
        self.assertIs(item, records[1])
        self.assertEqual(cursor, 1)

        item, cursor = select_generic_candidate(records, cursor=cursor)
        self.assertIs(item, records[0])
        self.assertEqual(cursor, 0)

        item, cursor = select_generic_candidate(records, cursor=cursor)
        self.assertIs(item, records[2])
        self.assertEqual(cursor, 2)

    def test_selection_boundary_does_not_promote_rng_or_event_semantics(self):
        self.assertTrue(SOURCE_BOUNDARY.specialized_fallback_to_generic_recovered)
        self.assertTrue(SOURCE_BOUNDARY.specialized_list_order_recovered)
        self.assertTrue(SOURCE_BOUNDARY.generic_reverse_cursor_recovered)
        for field in (
            "rng_generator_state_recovered",
            "event_binding_recovered",
            "chant_meaning_recovered",
        ):
            self.assertFalse(getattr(SOURCE_BOUNDARY, field))
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantPoolSelectionError,
                    "cannot promote",
                ):
                    replace(SOURCE_BOUNDARY, **{field: True})

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaisesRegex(Gate14ChantPoolSelectionError, "0, 1, or 2"):
            selector_pool(3)
        with self.assertRaisesRegex(
            Gate14ChantPoolSelectionError,
            "missing RNG remainder",
        ):
            select_specialized_candidate(
                (RuntimeChantCandidate("a", 0, 0),),
                now_ms=0,
                rng_remainders=(),
            )
        with self.assertRaisesRegex(
            Gate14ChantPoolSelectionError,
            "cannot exceed",
        ):
            select_generic_candidate(
                (RuntimeChantCandidate("g", 0, 0),),
                cursor=2,
            )


if __name__ == "__main__":
    unittest.main()
