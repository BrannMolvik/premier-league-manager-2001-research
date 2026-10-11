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
    ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_SLOT_VA,
    ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_VIRTUAL_VA,
    ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_IDX_ORDINAL,
    ORIGINAL_TRANSFER_LIST_SUBJECT_STRING_ID,
    ORIGINAL_TRANSFER_LIST_BODY_NATIVE_SLOT_VA,
    ORIGINAL_TRANSFER_LIST_BODY_NATIVE_VIRTUAL_VA,
    ORIGINAL_TRANSFER_LIST_BODY_NATIVE_IDX_ORDINAL,
    ORIGINAL_TRANSFER_LIST_BODY_STRING_ID,
    ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE,
    ORIGINAL_TRANSFER_REASON_DISPATCH_VA,
    ORIGINAL_TRANSFER_REASON_TOKEN_LITERAL_VA,
    ORIGINAL_TRANSFER_REASON_FIRST_SLOT_VA,
    ORIGINAL_TRANSFER_REASON_FIRST_IDX_ORDINAL,
    ORIGINAL_TRANSFER_REASON_STRING_IDS,
    native_transfer_reason_from_crt_draw,
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
        # Generic unproven selectors remain fail-closed; only this exact
        # argument-zero native body slot and title have separate proof.
        self.assertEqual(resources.source_selected_template(
            0, original_selector_proven=True),
            resources.strings.strings[resources.index.string_ids[0]])
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "not proven"):
            resources.source_selected_template(0, original_selector_proven=False)
        for invalid in (-1, 2877, True):
            with self.assertRaises(OriginalEAMailLanguageError):
                resources.source_selected_template(invalid, original_selector_proven=True)

    def test_original_transfer_subject_exact_native_slot_and_language_bytes(self):
        resource = load_verified_original_eamail_language(ORIGINAL_ROOT)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_SLOT_VA, 0x8797A4)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_VIRTUAL_VA, 0x56FB70)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_IDX_ORDINAL, 1313)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_SUBJECT_STRING_ID, 942)
        self.assertEqual(resource.index.string_ids[1313], 942)
        self.assertEqual(resource.original_player_asks_transfer_list_subject(), "Transfer List")
        # Neighbouring genuine original entries are NOT identical and must
        # never be chosen as the initial row caption by substring matching.
        self.assertEqual(resource.strings[resource.index.string_ids[1312]],
                         "Player Ask To Be Transfer Listed")
        self.assertIn("{MANAGERNAME:1}", resource.strings[
            resource.index.string_ids[1314]])
        with self.assertRaises(OriginalEAMailLanguageError):
            resource.source_selected_template(1314, original_selector_proven=False)

    def test_original_transfer_preview_template_exact_arg_zero_source_only(self):
        resource = load_verified_original_eamail_language(ORIGINAL_ROOT)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_BODY_NATIVE_SLOT_VA, 0x8797A0)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_BODY_NATIVE_VIRTUAL_VA, 0x56FBA0)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_BODY_NATIVE_IDX_ORDINAL, 1314)
        self.assertEqual(ORIGINAL_TRANSFER_LIST_BODY_STRING_ID, 943)
        self.assertEqual((0x87AC28 - ORIGINAL_TRANSFER_LIST_BODY_NATIVE_SLOT_VA) // 4, 1314)
        self.assertEqual(resource.index.string_ids[1314], 943)
        self.assertEqual(resource.index.string_ids[1315], 943)
        source_template = resource.original_player_asks_transfer_list_body_template()
        self.assertEqual(source_template, ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE)
        self.assertEqual(source_template, (
            "Dear {MANAGERNAME:1}<P><P>{PHRASE:PLAYERASKTRANSFERLISTREASON}"
            "<P><P><P>Yours Sincerely,<P><P>{PLAYERNAME:1}"
        ))
        self.assertNotEqual(source_template, resource.original_player_asks_transfer_list_subject())
        # Runtime substitutions are NOT an independently validated message body.
        self.assertIn("{PHRASE:PLAYERASKTRANSFERLISTREASON}", source_template)
        self.assertIn("{PLAYERNAME:1}", source_template)
        self.assertIn("{MANAGERNAME:1}", source_template)
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "not proven"):
            resource.source_selected_template(1314, original_selector_proven=False)
        # A forged IDX→different original message or altered STR body fails closed.
        from dataclasses import replace
        changed_idx = replace(resource.index, string_ids=(
            resource.index.string_ids[:1314] + (942,) + resource.index.string_ids[1315:]
        ))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "body template"):
            replace(resource, index=changed_idx).original_player_asks_transfer_list_body_template()
        changed_strings = replace(resource.strings, strings=(
            resource.strings.strings[:943] + ("Forged original body",)
            + resource.strings.strings[944:]
        ))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "body template"):
            replace(resource, strings=changed_strings).original_player_asks_transfer_list_body_template()

    def test_native_seven_transfer_reason_slots_are_actual_original_strings(self):
        from dataclasses import replace
        res = load_verified_original_eamail_language(ORIGINAL_ROOT)
        self.assertEqual(ORIGINAL_TRANSFER_REASON_DISPATCH_VA, 0x60FE40)
        self.assertEqual(ORIGINAL_TRANSFER_REASON_TOKEN_LITERAL_VA, 0x8327FC)
        self.assertEqual(ORIGINAL_TRANSFER_REASON_FIRST_SLOT_VA, 0x87A70C)
        self.assertEqual(ORIGINAL_TRANSFER_REASON_FIRST_IDX_ORDINAL, 327)
        self.assertEqual(ORIGINAL_TRANSFER_REASON_STRING_IDS, tuple(range(326, 333)))
        phrases = tuple(res.original_player_asks_transfer_list_reason_phrase(k)
                        for k in range(1, 8))
        self.assertEqual(len(set(phrases)), 7)
        self.assertTrue(phrases[0].startswith("I've enjoyed my time"))
        self.assertTrue(phrases[-1].startswith("The atmosphere about the place"))
        for i, phrase in enumerate(phrases):
            self.assertEqual(
                res.index.string_ids[327 + i], ORIGINAL_TRANSFER_REASON_STRING_IDS[i]
            )
            self.assertEqual(phrase, res.strings[326 + i])
        for bad in (-1, 0, 8, 10, True, "2", None):
            with self.assertRaises(OriginalEAMailLanguageError):
                res.original_player_asks_transfer_list_reason_phrase(bad)
        damaged_index = replace(res.index, string_ids=(
            res.index.string_ids[:329] + (942,) + res.index.string_ids[330:]
        ))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "slot mismatch"):
            replace(res, index=damaged_index).original_player_asks_transfer_list_reason_phrase(3)

    def test_native_crt_draw_to_reason_matches_signed_magic_for_all_32768_values(self):
        # Independently reproduce original 0x80010003 signed multiply-high,
        # signed >>14, negative correction and zero-to-one: do not derive
        # expected from the implementation's simplified integer division.
        def signed32(v):
            return (v & 0xFFFFFFFF) - (0x100000000 if v & 0x80000000 else 0)

        counts = {v: 0 for v in range(1, 8)}
        for raw in range(32768):
            product = signed32(raw * 7)
            hi = signed32((signed32(0x80010003) * product) >> 32)
            quotient = signed32(hi + product) >> 14
            quotient += (quotient & 0xFFFFFFFF) >> 31
            expected = quotient if quotient else 1
            self.assertEqual(native_transfer_reason_from_crt_draw(raw), expected)
            counts[expected] += 1
        self.assertEqual(counts, {1: 9362, 2: 4681, 3: 4681,
                                  4: 4681, 5: 4681, 6: 4681, 7: 1})
        for invalid in (-1, 32768, True, None, 0.5, "7"):
            with self.assertRaisesRegex(OriginalEAMailLanguageError, "15-bit"):
                native_transfer_reason_from_crt_draw(invalid)

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
