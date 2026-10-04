"""Tests for source-closed numeric chant event-code routing."""
from dataclasses import replace
import unittest

from gate14_chant_event_code_routing import (
    AUDIO_EVENT_DISPATCH_VA,
    AUDIO_EVENT_JUMP_TABLE_VA,
    AUDIO_EVENT_RECORD_SIZE,
    AUDIO_EVENT_TYPE_OFFSET,
    AWAY_SELECTOR,
    CHANT_CALLBACK_SLOT_VA,
    CHANT_ENQUEUE_VA,
    HOME_SELECTOR,
    NUMERIC_EVENT_ROUTES,
    ROUTES,
    SOURCE_BOUNDARY,
    Gate14ChantEventRoutingError,
    chant_route_for_numeric_event,
    chant_selector_for_numeric_event,
)


class Gate14ChantEventCodeRoutingTests(unittest.TestCase):
    def test_exact_dispatch_and_callback_addresses(self):
        self.assertEqual(CHANT_ENQUEUE_VA, 0x723360)
        self.assertEqual(CHANT_CALLBACK_SLOT_VA, 0x86644C)
        self.assertEqual(AUDIO_EVENT_DISPATCH_VA, 0x70C97D)
        self.assertEqual(AUDIO_EVENT_JUMP_TABLE_VA, 0x70D18C)
        self.assertEqual(AUDIO_EVENT_RECORD_SIZE, 0x10)
        self.assertEqual(AUDIO_EVENT_TYPE_OFFSET, 0)

    def test_exact_numeric_routes_preserve_unnamed_event_boundary(self):
        self.assertEqual(
            NUMERIC_EVENT_ROUTES,
            (
                (9, 0x727710, HOME_SELECTOR),
                (10, 0x7277C0, HOME_SELECTOR),
                (11, 0x727860, HOME_SELECTOR),
                (12, 0x727900, HOME_SELECTOR),
                (13, 0x7279A0, HOME_SELECTOR),
                (14, 0x727A40, AWAY_SELECTOR),
                (15, 0x727A40, AWAY_SELECTOR),
                (16, 0x727A40, AWAY_SELECTOR),
            ),
        )
        self.assertEqual([route.event_code for route in ROUTES], list(range(9, 17)))
        for code in range(9, 14):
            self.assertEqual(chant_selector_for_numeric_event(code), HOME_SELECTOR)
        for code in range(14, 17):
            self.assertEqual(chant_selector_for_numeric_event(code), AWAY_SELECTOR)

        for route in ROUTES:
            self.assertFalse(route.event_semantics_recovered)
            self.assertFalse(route.matchcalculator_type_equivalence_recovered)
            self.assertFalse(route.fastview_event_equivalence_recovered)

    def test_other_valid_dispatch_codes_remain_unmapped(self):
        for code in tuple(range(1, 9)) + tuple(range(17, 31)):
            with self.subTest(code=code):
                self.assertIsNone(chant_route_for_numeric_event(code))
                self.assertIsNone(chant_selector_for_numeric_event(code))

    def test_does_not_equate_numeric_codes_with_other_event_models(self):
        route = chant_route_for_numeric_event(10)
        self.assertIsNotNone(route)
        for field in (
            "event_semantics_recovered",
            "matchcalculator_type_equivalence_recovered",
            "fastview_event_equivalence_recovered",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantEventRoutingError,
                    "cannot promote",
                ):
                    replace(route, **{field: True})

        for field in (
            "named_event_semantics_recovered",
            "matchcalculator_record_equivalence_recovered",
            "fastview_sender_equivalence_recovered",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantEventRoutingError,
                    "cannot promote",
                ):
                    replace(SOURCE_BOUNDARY, **{field: True})

    def test_out_of_range_codes_fail_closed(self):
        for code in (0, 31, -1):
            with self.subTest(code=code):
                with self.assertRaisesRegex(
                    Gate14ChantEventRoutingError,
                    "within dispatcher range",
                ):
                    chant_route_for_numeric_event(code)


if __name__ == "__main__":
    unittest.main()
