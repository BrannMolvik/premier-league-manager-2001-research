"""Tests for source-closed FM2001 chant-bank selection."""
from dataclasses import replace
import unittest

from gate14_chant_bank_selection import (
    AWAY_POOL_TYPE,
    BANK_PREFIX_CLASSIFIER_VA,
    BANK_RECORD_LOWERCASE_VA,
    CHANT_DYNAMIC_LOAD_VA,
    CHANT_PAIR_SELECTION_VA,
    CL_FAMILY_BANK_COUNT,
    CLUB_BANK_COUNT,
    CLUB_SOURCE_ID_COUNTS,
    GENERIC_BANK_COUNT,
    GENERIC_POOL_TYPE,
    HOME_POOL_TYPE,
    Gate14ChantSelectionError,
    chant_selection_patterns,
    classify_chant_bank_basename,
)


class Gate14ChantBankSelectionTests(unittest.TestCase):
    def test_exact_source_addresses_and_inventory_shape(self):
        self.assertEqual(CHANT_PAIR_SELECTION_VA, 0x722F00)
        self.assertEqual(CHANT_DYNAMIC_LOAD_VA, 0x723010)
        self.assertEqual(BANK_PREFIX_CLASSIFIER_VA, 0x7230D6)
        self.assertEqual(BANK_RECORD_LOWERCASE_VA, 0x7231D0)
        self.assertEqual(GENERIC_BANK_COUNT, 21)
        self.assertEqual(CLUB_BANK_COUNT, 35)
        self.assertEqual(CL_FAMILY_BANK_COUNT, 0)
        self.assertEqual(sum(count for _source_id, count in CLUB_SOURCE_ID_COUNTS), 35)
        self.assertEqual(len(CLUB_SOURCE_ID_COUNTS), 22)

    def test_distinct_club_ids_map_directly_to_home_and_away_prefixes(self):
        patterns = chant_selection_patterns(4, 17, cl_rng_bit=1)
        self.assertEqual(patterns.cl_rng_bit, 1)
        self.assertIsNone(patterns.club_same_id_rng_bit)
        self.assertEqual(patterns.cl_home_pattern, "cl000001")
        self.assertEqual(patterns.cl_away_pattern, "cl000000")
        self.assertEqual(patterns.club_home_pattern, "c00004")
        self.assertEqual(patterns.club_away_pattern, "c00017")

        self.assertEqual(classify_chant_bank_basename("C0000401", patterns), HOME_POOL_TYPE)
        self.assertEqual(classify_chant_bank_basename("C0001703", patterns), AWAY_POOL_TYPE)
        self.assertEqual(classify_chant_bank_basename("CGENER12", patterns), GENERIC_POOL_TYPE)
        self.assertIsNone(classify_chant_bank_basename("C0000901", patterns))

    def test_equal_club_ids_use_separate_second_rng_draw(self):
        home_specific = chant_selection_patterns(
            9,
            9,
            cl_rng_bit=0,
            club_same_id_rng_bit=1,
        )
        self.assertEqual(home_specific.cl_home_pattern, "cl000000")
        self.assertEqual(home_specific.cl_away_pattern, "cl000001")
        self.assertEqual(home_specific.club_home_pattern, "c00009")
        self.assertEqual(home_specific.club_away_pattern, "c0000000")
        self.assertEqual(
            classify_chant_bank_basename("C0000902", home_specific),
            HOME_POOL_TYPE,
        )

        away_specific = chant_selection_patterns(
            9,
            9,
            cl_rng_bit=1,
            club_same_id_rng_bit=0,
        )
        self.assertEqual(away_specific.club_home_pattern, "c0000000")
        self.assertEqual(away_specific.club_away_pattern, "c00009")
        self.assertEqual(
            classify_chant_bank_basename("C0000903", away_specific),
            AWAY_POOL_TYPE,
        )

    def test_rng_contract_fails_closed(self):
        with self.assertRaisesRegex(Gate14ChantSelectionError, "CL RNG bit"):
            chant_selection_patterns(4, 17, cl_rng_bit=2)
        with self.assertRaisesRegex(
            Gate14ChantSelectionError,
            "require the separate club RNG",
        ):
            chant_selection_patterns(4, 4, cl_rng_bit=0)
        with self.assertRaisesRegex(
            Gate14ChantSelectionError,
            "do not consume a club RNG",
        ):
            chant_selection_patterns(4, 17, cl_rng_bit=0, club_same_id_rng_bit=1)

    def test_bank_selection_does_not_promote_event_or_timing_semantics(self):
        patterns = chant_selection_patterns(4, 17, cl_rng_bit=0)
        self.assertTrue(patterns.bank_to_club_mapping_recovered)
        self.assertFalse(patterns.event_binding_recovered)
        self.assertFalse(patterns.playback_timing_recovered)
        for field in ("event_binding_recovered", "playback_timing_recovered"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantSelectionError,
                    "cannot promote",
                ):
                    replace(patterns, **{field: True})


if __name__ == "__main__":
    unittest.main()
