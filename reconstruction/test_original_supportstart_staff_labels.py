"""Source original role labels, independently grounded in original .idx/.str."""
from pathlib import Path
import unittest

from ea_language_strings import EAStringTable, EAStringIndex
from support_staff import SupportStaffState, INITIAL_SUPPORT_STAFF_TYPES
from original_supportstart_staff_labels import (
    SOURCE_NATIVE_STAFF_LABEL_INDEX,
    SOURCE_NATIVE_STAFF_SPECIAL_CASE_13_GLOBAL,
    original_supportstart_native_staff_label,
    original_supportstart_staff_type_label,
)


class OriginalSupportStaffSourceLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        cls.strings = EAStringTable.from_bytes((root / "English.str").read_bytes())
        cls.indices = EAStringIndex.from_bytes((root / "English.idx").read_bytes(), cls.strings)

    def test_source_exact_original_english_label_switch_nonexception_cases(self):
        expected = {
            1: "ASSISTANT MANAGER",
            2: "STADIUM MANAGER",
            3: "YOUTH TEAM MANAGER",
            4: "BUSINESS CONSULTANT",
            5: "CHIEF SCOUT",
            6: "GROUNDSMAN",
            7: "GK COACH",
            8: "FITNESS COACH",
            9: "TECHNIQUE COACH",
            10: "DEFENSIVE COACH",
            11: "MIDFIELD COACH",
            12: "ATTACKING COACH",
            13: "Physiotherapist",
            14: "DOCTOR",
            15: "TALENT SCOUT",
            16: "SCOUT",
        }
        self.assertEqual(tuple(sorted(SOURCE_NATIVE_STAFF_LABEL_INDEX)),
                         tuple(sorted(expected)))
        for ordinal, label in expected.items():
            with self.subTest(ordinal=ordinal):
                self.assertEqual(
                    original_supportstart_native_staff_label(
                        ordinal, self.strings, self.indices),
                    label,
                )

    def test_native_special_label_13_uses_distinct_original_resource_and_unknown_cases_fail_closed(self):
        self.assertEqual(SOURCE_NATIVE_STAFF_SPECIAL_CASE_13_GLOBAL, 0x9821E4)
        self.assertEqual(SOURCE_NATIVE_STAFF_LABEL_INDEX[13], 2437)
        self.assertEqual(original_supportstart_native_staff_label(
            13, self.strings, self.indices), "Physiotherapist")
        for ordinal in (-10, 0, 17, 99):
            with self.subTest(ordinal=ordinal):
                self.assertIsNone(original_supportstart_native_staff_label(
                    ordinal, self.strings, self.indices))


    def test_concrete_staff_type_getter_matches_all_six_fresh_user_labels(self):
        # Original 0x4CA2F0 field+4, 0x42CB40 vft+0x14,
        # 0x4D0725 -> 0x4CDCD0 proves ordinal equals staff.staff_type.
        self.assertEqual(INITIAL_SUPPORT_STAFF_TYPES, (1, 2, 3, 4, 5, 13))
        self.assertEqual(
            tuple(original_supportstart_staff_type_label(
                SupportStaffState(type_id, 30, 3), self.strings, self.indices
            ) for type_id in INITIAL_SUPPORT_STAFF_TYPES),
            ("ASSISTANT MANAGER", "STADIUM MANAGER",
             "YOUTH TEAM MANAGER", "BUSINESS CONSULTANT",
             "CHIEF SCOUT", "Physiotherapist"),
        )
        with self.assertRaises(TypeError):
            original_supportstart_staff_type_label(None, self.strings, self.indices)
        self.assertIsNone(original_supportstart_staff_type_label(
            SupportStaffState(17, 30, 2), self.strings, self.indices
        ))

    def test_type_and_incomplete_index_tables_fail_closed(self):
        with self.assertRaises(TypeError):
            original_supportstart_native_staff_label(True, self.strings, self.indices)
        with self.assertRaises(TypeError):
            original_supportstart_native_staff_label(1, None, self.indices)
        with self.assertRaises(TypeError):
            original_supportstart_native_staff_label(1, self.strings, None)
        with self.assertRaises(ValueError):
            original_supportstart_native_staff_label(
                16, self.strings, EAStringIndex((0,)*20))


if __name__ == "__main__":
    unittest.main()
