"""Tests for the source-backed FM2001 chant catalog boundary."""
from dataclasses import replace
import unittest

from gate14_chant_resource_catalog import (
    ACTIVE_AWAY_CLUB_GLOBAL_VA,
    ACTIVE_HOME_CLUB_GLOBAL_VA,
    BANK_CATALOG_SHA256,
    BANK_COUNT,
    BANK_TOTAL_BYTES,
    C0_FORMAT,
    C0_FORMAT_VA,
    CHANT_CONTROL_HANDLE_VA,
    CHANT_CONTROL_PATH_VA,
    CHANT_DIRECTORY_SUFFIX_VA,
    CHANT_DYNAMIC_LOAD_VA,
    CHANT_INIT_VA,
    CHANT_INTERNAL_NAME_VA,
    CHANT_PAIR_SELECTION_VA,
    CHANT_PATH_BUFFER_VA,
    CHANT_READY_GLOBAL_VA,
    CL_FORMAT,
    CL_FORMAT_VA,
    CLUB_SOURCE_ID_OFFSET,
    CONTROL_MAGIC,
    CONTROL_PATH,
    CONTROL_SHA256,
    CONTROL_SIZE_BYTES,
    SOURCE_BOUNDARY,
    Gate14ChantCatalogError,
    dynamic_chant_inputs,
)


class Gate14ChantResourceCatalogTests(unittest.TestCase):
    def test_exact_control_file_and_bank_catalog_receipt(self):
        self.assertEqual(CHANT_INIT_VA, 0x722D80)
        self.assertEqual(CHANT_CONTROL_PATH_VA, 0x866314)
        self.assertEqual(CHANT_DIRECTORY_SUFFIX_VA, 0x866300)
        self.assertEqual(CHANT_INTERNAL_NAME_VA, 0x866338)
        self.assertEqual(CHANT_PATH_BUFFER_VA, 0xA879BC)
        self.assertEqual(CHANT_CONTROL_HANDLE_VA, 0xA878EC)
        self.assertEqual(CHANT_READY_GLOBAL_VA, 0xA878D0)

        self.assertEqual(CONTROL_PATH, "Data/Audio/Chants/CHANT.eam")
        self.assertEqual(CONTROL_SIZE_BYTES, 704)
        self.assertEqual(CONTROL_MAGIC, b"MIDx")
        self.assertEqual(
            CONTROL_SHA256,
            "b2b26a6a8a7c2d904df4868ee8454169ef49dbd69b07fa22d926ec11aafafbee",
        )
        self.assertEqual(BANK_COUNT, 56)
        self.assertEqual(BANK_TOTAL_BYTES, 2_523_996)
        self.assertEqual(
            BANK_CATALOG_SHA256,
            "b81f2f45c033d8da53f5a27696f07a70662f90fd277f51f5a3f3b1920c98c264",
        )

    def test_dynamic_naming_inputs_are_recorded_without_mapping_claim(self):
        self.assertEqual(ACTIVE_HOME_CLUB_GLOBAL_VA, 0xAD6060)
        self.assertEqual(ACTIVE_AWAY_CLUB_GLOBAL_VA, 0xAD6174)
        self.assertEqual(CLUB_SOURCE_ID_OFFSET, 0x32)
        self.assertEqual(CHANT_PAIR_SELECTION_VA, 0x722F00)
        self.assertEqual(CHANT_DYNAMIC_LOAD_VA, 0x723010)
        self.assertEqual(CL_FORMAT_VA, 0x866360)
        self.assertEqual(C0_FORMAT_VA, 0x86634C)
        self.assertEqual(CL_FORMAT, "cl%06.6d")
        self.assertEqual(C0_FORMAT, "c0%4.4d")

        inputs = dynamic_chant_inputs()
        self.assertEqual(inputs["club_source_id_offset"], 0x32)
        self.assertEqual(inputs["cl_format"], "cl%06.6d")
        self.assertEqual(inputs["c0_format"], "c0%4.4d")
        self.assertFalse(inputs["bank_to_club_mapping_recovered"])

    def test_catalog_cannot_promote_mid_sequence_or_event_semantics(self):
        for field in (
            "control_sequence_decoded",
            "bank_to_club_mapping_recovered",
            "event_binding_recovered",
            "playback_timing_recovered",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14ChantCatalogError,
                    "cannot promote",
                ):
                    replace(SOURCE_BOUNDARY, **{field: True})

    def test_integrity_guard_rejects_catalog_drift(self):
        with self.assertRaisesRegex(
            Gate14ChantCatalogError,
            "inventory summary drift",
        ):
            replace(SOURCE_BOUNDARY, bank_count=55)
        with self.assertRaisesRegex(
            Gate14ChantCatalogError,
            "CHANT.eam magic",
        ):
            replace(SOURCE_BOUNDARY, control_magic=b"BAD!")


if __name__ == "__main__":
    unittest.main()
