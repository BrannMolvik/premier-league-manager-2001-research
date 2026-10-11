"""Native English 0x5CE73C club suffix / 0x471F3E row-date regression."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from original_eamail_main_language import (
    ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL,
    ORIGINAL_EAM_CLUB_SUFFIX_STR_ID,
    ORIGINAL_EAM_DATE_FORMAT,
    ORIGINAL_EAM_DATE_IDX_ORDINAL,
    ORIGINAL_EAM_DATE_STR_ID,
    ORIGINAL_EAM_JANUARY_IDX_ORDINAL,
    ORIGINAL_EAM_JANUARY_STR_ID,
    ORIGINAL_MAIN_IDX_COUNT,
    ORIGINAL_MAIN_STR_COUNT,
    OriginalEAMMainLanguageError,
    load_verified_original_main_eam_language,
)


SOURCE = Path(__file__).resolve().parent.parent / "original_assets" / "source"


class NativeEnglishEAMRowLanguageTests(TestCase):
    def test_native_club_suffix_main_index_and_calendar_format(self):
        original = load_verified_original_main_eam_language(SOURCE)
        self.assertEqual(len(original.strings.strings), ORIGINAL_MAIN_STR_COUNT)
        self.assertEqual(len(original.index.string_ids), ORIGINAL_MAIN_IDX_COUNT)
        self.assertEqual(original.index.string_ids[ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL],
                         ORIGINAL_EAM_CLUB_SUFFIX_STR_ID)
        self.assertEqual(original.original_club_suffix(), "Football Club")
        self.assertEqual(original.index.string_ids[ORIGINAL_EAM_DATE_IDX_ORDINAL],
                         ORIGINAL_EAM_DATE_STR_ID)
        self.assertEqual(original.index.resolve(
            original.strings, ORIGINAL_EAM_DATE_IDX_ORDINAL),
            ORIGINAL_EAM_DATE_FORMAT)
        self.assertEqual(original.index.string_ids[ORIGINAL_EAM_JANUARY_IDX_ORDINAL],
                         ORIGINAL_EAM_JANUARY_STR_ID)
        self.assertEqual(original.original_mail_row_date(date(2000, 1, 1)),
                         "1/Jan/2000")
        self.assertEqual(original.original_mail_row_date(date(2000, 8, 9)),
                         "9/Aug/2000")
        self.assertEqual(original.original_mail_row_date(date(2000, 12, 31)),
                         "31/Dec/2000")
        self.assertEqual(original.original_mail_row_date(date(2001, 2, 10)),
                         "10/Feb/2001")
        for month in range(1, 13):
            with self.subTest(month=month):
                label = original.original_mail_row_date(date(2000, month, 5))
                self.assertEqual(label,
                    "5/" + original.index.resolve(
                        original.strings,
                        ORIGINAL_EAM_JANUARY_IDX_ORDINAL + month - 1)[:3]
                    + "/2000")
        for invalid in (None, "1/Jan/2000", 20000101, True):
            with self.assertRaises(OriginalEAMMainLanguageError):
                original.original_mail_row_date(invalid)

    def test_source_file_absence_and_mutation_fail_closed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(OriginalEAMMainLanguageError, "Missing"):
                load_verified_original_main_eam_language(root)
            for name in ("English.str", "English.idx"):
                (root/name).write_bytes((SOURCE/name).read_bytes())
            self.assertEqual(load_verified_original_main_eam_language(root).
                             original_club_suffix(), "Football Club")
            (root/"English.idx").write_bytes((SOURCE/"English.idx").read_bytes()[:-2])
            with self.assertRaisesRegex(OriginalEAMMainLanguageError, "checksum"):
                load_verified_original_main_eam_language(root)
            (root/"English.idx").write_bytes((SOURCE/"English.idx").read_bytes())
            (root/"English.str").write_bytes((SOURCE/"English.str").read_bytes()[:-1] + b"X")
            with self.assertRaisesRegex(OriginalEAMMainLanguageError, "checksum"):
                load_verified_original_main_eam_language(root)


if __name__ == "__main__":
    main()
