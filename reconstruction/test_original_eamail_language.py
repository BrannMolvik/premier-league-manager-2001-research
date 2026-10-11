"""Original EAMail language source bytes and unguessed index selection."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from original_eamail_language import (
    OriginalEAMailLanguageError,
    ORIGINAL_EAMAIL_STR_SHA256,
    ORIGINAL_EAMAIL_IDX_SHA256,
    ORIGINAL_EAMAIL_STRING_COUNT,
    ORIGINAL_EAMAIL_INDEX_COUNT,
    load_verified_original_eamail_language,
)


ORIGINAL_ROOT = Path(__file__).resolve().parent.parent / "original_assets" / "source"


class OriginalEAMLanguageSourceTests(TestCase):
    def test_exact_original_pair_parses_with_original_language_index(self):
        resources = load_verified_original_eamail_language(ORIGINAL_ROOT)
        self.assertEqual(len(resources.strings.strings), ORIGINAL_EAMAIL_STRING_COUNT)
        self.assertEqual(len(resources.index.string_ids), ORIGINAL_EAMAIL_INDEX_COUNT)
        self.assertEqual(resources.strings.payload_size, 292303)
        self.assertEqual(len(resources.index.string_ids), 2877)
        self.assertTrue(any("transfer" in row.lower() for row in resources.strings.strings))
        # Test exact original native index mechanics only, NOT an unproven
        # EAMPlayerAskTransferList message template choice.
        self.assertEqual(resources.source_selected_template(
            0, original_selector_proven=True),
            resources.strings.strings[resources.index.string_ids[0]])
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "not proven"):
            resources.source_selected_template(0, original_selector_proven=False)
        for invalid in (-1, 2877, True):
            with self.assertRaises(OriginalEAMailLanguageError):
                resources.source_selected_template(invalid, original_selector_proven=True)

    def test_verified_resource_absence_and_altered_language_file_fail_closed(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            with self.assertRaisesRegex(OriginalEAMailLanguageError, "missing"):
                load_verified_original_eamail_language(tmp)
            idx = ORIGINAL_ROOT / "EnglishEAM.idx"
            str_file = ORIGINAL_ROOT / "EnglishEAM.str"
            self.assertEqual(idx.stat().st_size, 5754)
            self.assertEqual(str_file.stat().st_size, 298747)
            (tmp / "EnglishEAM.idx").write_bytes(idx.read_bytes())
            (tmp / "EnglishEAM.str").write_bytes(str_file.read_bytes()[:-1] + b"X")
            with self.assertRaisesRegex(OriginalEAMailLanguageError, "differ"):
                load_verified_original_eamail_language(tmp)

    def test_original_source_sha_receipts_are_pinned_not_guessed(self):
        from hashlib import sha256
        self.assertEqual(
            sha256((ORIGINAL_ROOT / "EnglishEAM.str").read_bytes()).hexdigest(),
            ORIGINAL_EAMAIL_STR_SHA256,
        )
        self.assertEqual(
            sha256((ORIGINAL_ROOT / "EnglishEAM.idx").read_bytes()).hexdigest(),
            ORIGINAL_EAMAIL_IDX_SHA256,
        )


if __name__ == "__main__":
    main()
