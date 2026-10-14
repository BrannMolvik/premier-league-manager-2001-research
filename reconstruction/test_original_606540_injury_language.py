"""Original 606540 notice title source: all 15 native vtables and IDX slots.

The original source receipts do NOT establish a live queue append, a native
user+6B4 delivery, an interpolated player name, or a visible Inbox row.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack

from unittest import TestCase, main

from original_eamail_language import (
    ORIGINAL_606540_TITLE_ROUTES,
    ORIGINAL_606540_TITLE_SOURCE_TEXTS,
    OriginalEAMailLanguageError,
    VerifiedOriginalEAMailLanguage,
    load_verified_original_eamail_language,
)
from original_native_606540_human_mail_route import Original606540HumanDueReceipt


ORIGINAL_ROOT = Path(__file__).resolve().parent.parent / "original_assets" / "source"


def _due_receipt(constructor: int) -> Original606540HumanDueReceipt:
    vtable, tag, _, _, _ = ORIGINAL_606540_TITLE_ROUTES[constructor]
    return Original606540HumanDueReceipt(
        original_player_id=11,
        original_constructor=constructor,
        original_concrete_notice_vtable=vtable,
        original_native_virtual0c_tag=tag,
        original_native_type_descriptor=31,
        original_type_case_address=0x413218,
        original_source_due_date_signed32=200,
        original_source_current_date_signed32=200,
        original_source_due_wrapper_after_5cfa20=b"\\0" * 12,
        original_source_notice_after_5cfa20=b"\\0" * 0x44,
        original_413020_reached_manager_links=(),
        original_413020_qualified_recipient_user_pointer=None,
        original_413020_candidate_user_queue_pointer=None,
        original_413020_deferred_lookup_gated_out=False,
    )


class SourceQualified606540NoticeTitlesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load_verified_original_eamail_language(ORIGINAL_ROOT)

    def test_all_fifteen_independent_constructor_title_slots(self):
        self.assertEqual(len(ORIGINAL_606540_TITLE_ROUTES), 15)
        self.assertEqual({v[4] for v in ORIGINAL_606540_TITLE_ROUTES.values()},
                         {1153, 1158})
        self.assertEqual(len({v[0] for v in ORIGINAL_606540_TITLE_ROUTES.values()}), 15)
        self.assertEqual(len({v[2] for v in ORIGINAL_606540_TITLE_ROUTES.values()}), 15)
        for constructor, (vtable, tag, callback, ordinal, string_id) in ORIGINAL_606540_TITLE_ROUTES.items():
            with self.subTest(constructor=hex(constructor)):
                self.assertTrue(0x401000 <= callback < 0x7B86BD)
                self.assertEqual(self.original.index.string_ids[ordinal], string_id)
                self.assertEqual(
                    self.original.original_606540_notice_subject_template(
                        _due_receipt(constructor)),
                    ORIGINAL_606540_TITLE_SOURCE_TEXTS[string_id],
                )
                # The receipt is source-only, not a claimed native execution.
                self.assertFalse(_due_receipt(constructor).original_inbox_row_rendered)
                self.assertFalse(_due_receipt(constructor).live_game_state_updated)

    def test_template_selection_never_fabricates_visible_player_name(self):
        with_player = next(c for c, x in ORIGINAL_606540_TITLE_ROUTES.items() if x[4] == 1153)
        without_player = next(c for c, x in ORIGINAL_606540_TITLE_ROUTES.items() if x[4] == 1158)
        self.assertEqual(
            self.original.original_606540_notice_subject_template(_due_receipt(with_player)),
            "Ankle injury to {PLAYERNAME:1}",
        )
        self.assertEqual(
            self.original.original_606540_notice_subject_template(_due_receipt(without_player)),
            "Ankle injury",
        )

    def test_wrong_source_owner_vtable_or_tag_fails_closed(self):
        base = _due_receipt(next(iter(ORIGINAL_606540_TITLE_ROUTES)))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "receipt"):
            self.original.original_606540_notice_subject_template(None)
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "constructor"):
            self.original.original_606540_notice_subject_template(
                replace(base, original_constructor=0x41B580))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "selector"):
            self.original.original_606540_notice_subject_template(
                replace(base, original_concrete_notice_vtable=0x7D1D34))
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "selector"):
            self.original.original_606540_notice_subject_template(
                replace(base, original_native_virtual0c_tag=364))

    def test_modified_original_index_and_text_fail_closed(self):
        base = _due_receipt(next(iter(ORIGINAL_606540_TITLE_ROUTES)))
        ordinal = ORIGINAL_606540_TITLE_ROUTES[base.original_constructor][3]
        altered_idx = list(self.original.index.string_ids)
        altered_idx[ordinal] = 942  # Original transfer request, not injury.
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "selector"):
            replace(self.original, index=replace(
                self.original.index, string_ids=tuple(altered_idx)
            )).original_606540_notice_subject_template(base)
        altered_str = list(self.original.strings.strings)
        altered_str[1153] = "Unverified message"
        with self.assertRaisesRegex(OriginalEAMailLanguageError, "selector"):
            replace(self.original, strings=replace(
                self.original.strings, strings=tuple(altered_str)
            )).original_606540_notice_subject_template(base)

    def test_all_native_vtable_title_callbacks_against_private_source_if_available(self):
        """Optional independent native PE opcode/owner assertion; never ship PE."""
        import os
        from hashlib import sha256
        from struct import unpack_from

        name = os.environ.get("FM2001_ORIGINAL_EXECUTABLE")
        if not name:
            self.skipTest("Private original executable not installed in CI")
        source = Path(name).read_bytes()
        self.assertEqual(len(source), 4714541)
        self.assertEqual(sha256(source).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        for constructor, (vtable, _, function, ordinal, _) in ORIGINAL_606540_TITLE_ROUTES.items():
            with self.subTest(constructor=hex(constructor)):
                self.assertEqual(unpack_from("<I", source, vtable - 0x400000 + 0x18)[0],
                                 function)
                slot = 0x87AC28 - ordinal * 4
                self.assertIn(pack("<I", slot),
                              source[function - 0x400000:function - 0x400000 + 128])


if __name__ == "__main__":
    main()
