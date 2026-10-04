"""Tests for source-closed chant pool shuffle/routing."""
from dataclasses import replace
import unittest

from gate14_chant_bank_selection import (
    AWAY_POOL_TYPE,
    GENERIC_POOL_TYPE,
    HOME_POOL_TYPE,
)
from gate14_chant_pool_order import (
    AWAY_POOL_GLOBAL_VA,
    GENERIC_POOL_COUNT_GLOBAL_VA,
    GENERIC_POOL_GLOBAL_VA,
    HOME_POOL_GLOBAL_VA,
    POOL_APPEND_VA,
    POOL_ROUTE_SWITCH_VA,
    REMOVE_BY_INDEX_VA,
    RNG_DRAW_VA,
    SOURCE_LIST_COUNT_VA,
    ChantMatchedRecord,
    Gate14ChantPoolOrderError,
    route_chant_records_by_source_shuffle,
)


class Gate14ChantPoolOrderTests(unittest.TestCase):
    def test_exact_shuffle_and_pool_addresses(self):
        self.assertEqual(SOURCE_LIST_COUNT_VA, 0x723142)
        self.assertEqual(RNG_DRAW_VA, 0x723157)
        self.assertEqual(REMOVE_BY_INDEX_VA, 0x6B2810)
        self.assertEqual(POOL_ROUTE_SWITCH_VA, 0x723171)
        self.assertEqual(POOL_APPEND_VA, 0x6B1F90)
        self.assertEqual(HOME_POOL_GLOBAL_VA, 0xA87984)
        self.assertEqual(AWAY_POOL_GLOBAL_VA, 0xA879A0)
        self.assertEqual(GENERIC_POOL_GLOBAL_VA, 0xA87968)
        self.assertEqual(GENERIC_POOL_COUNT_GLOBAL_VA, 0xA878DC)

    def test_removes_random_index_then_appends_to_type_pool(self):
        records = (
            ChantMatchedRecord("cgener01", GENERIC_POOL_TYPE),
            ChantMatchedRecord("c0000401", HOME_POOL_TYPE),
            ChantMatchedRecord("c0001701", AWAY_POOL_TYPE),
            ChantMatchedRecord("cgener02", GENERIC_POOL_TYPE),
        )
        # remaining:
        # [g1,h,a,g2] -> pick 2=a
        # [g1,h,g2]   -> pick 1=h
        # [g1,g2]     -> pick 1=g2
        # [g1]        -> pick 0=g1
        order = route_chant_records_by_source_shuffle(records, (2, 1, 1, 0))

        self.assertEqual([x.basename for x in order.away], ["c0001701"])
        self.assertEqual([x.basename for x in order.home], ["c0000401"])
        self.assertEqual(
            [x.basename for x in order.generic],
            ["cgener02", "cgener01"],
        )
        self.assertEqual(order.source_record_count, 4)
        self.assertTrue(order.random_without_replacement_recovered)
        self.assertFalse(order.event_binding_recovered)
        self.assertFalse(order.playback_timing_recovered)

    def test_invalid_reduced_rng_sequence_fails_closed(self):
        records = (
            ChantMatchedRecord("cgener01", GENERIC_POOL_TYPE),
            ChantMatchedRecord("c0000401", HOME_POOL_TYPE),
        )
        with self.assertRaisesRegex(
            Gate14ChantPoolOrderError,
            "exactly one selection index",
        ):
            route_chant_records_by_source_shuffle(records, (0,))
        with self.assertRaisesRegex(
            Gate14ChantPoolOrderError,
            "current remaining record list",
        ):
            route_chant_records_by_source_shuffle(records, (2, 0))

    def test_pool_order_cannot_promote_event_or_timing_semantics(self):
        order = route_chant_records_by_source_shuffle(
            (ChantMatchedRecord("cgener01", GENERIC_POOL_TYPE),),
            (0,),
        )
        for field in ("event_binding_recovered", "playback_timing_recovered"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantPoolOrderError,
                    "cannot promote",
                ):
                    replace(order, **{field: True})


if __name__ == "__main__":
    unittest.main()
