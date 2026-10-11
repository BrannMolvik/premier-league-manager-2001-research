"""Original EAM player labels from native CP1252 and type2 descriptor branch."""
from __future__ import annotations

from unittest import TestCase, main

from original_eamail_player_name import (
    ORIGINAL_EAM_PLAYER_ASSOCIATION_RECORD_OFFSET,
    ORIGINAL_EAM_PLAYER_NAME_INITIAL_SURNAME_FORMAT_VA,
    ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT_VA,
    OriginalEAMPlayerNameSourceError,
    original_eam_player_initial_surname,
    original_eam_player_no_association_label,
)


class OriginalEAMNativePlayerLabelTests(TestCase):
    def test_source_initial_surname_exact_native_byte_pattern(self):
        self.assertEqual(ORIGINAL_EAM_PLAYER_NAME_INITIAL_SURNAME_FORMAT_VA, 0x818EB0)
        self.assertEqual(original_eam_player_initial_surname("John", "Smith"), "J. Smith")
        self.assertEqual(original_eam_player_initial_surname("Édouard", "Mendy"), "É. Mendy")
        self.assertEqual(original_eam_player_initial_surname("Daniel", "van der Berg"),
                         "D. van der Berg")
        self.assertEqual(original_eam_player_initial_surname("-", "Ronaldo"), "Ronaldo")
        self.assertEqual(original_eam_player_initial_surname("-Special", "Pelé"), "Pelé")
        self.assertEqual(original_eam_player_initial_surname("Anne Marie", "O'Neil"),
                         "A. O'Neil")
        # Source name fields are not normalized; original game preserves
        # capitalization and leading whitespace in source surname.
        self.assertEqual(original_eam_player_initial_surname("jo", "sMiTh"), "j. sMiTh")

    def test_only_source_verified_signed_negative_association_original_markup(self):
        self.assertEqual(ORIGINAL_EAM_PLAYER_ASSOCIATION_RECORD_OFFSET, 0x72)
        self.assertEqual(ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT_VA, 0x83330C)
        for source_native_word in (-1, -32768, -42):
            self.assertEqual(
                original_eam_player_no_association_label(
                    first_name="John", surname="Smith",
                    verified_native_association_word=source_native_word,
                ),
                "<T+P>J. Smith<T->",
            )
        self.assertEqual(
            original_eam_player_no_association_label(
                first_name="-", surname="Ronaldo",
                verified_native_association_word=-1,
            ),
            "<T+P>Ronaldo<T->",
        )
        # Original has a separate distinct formatter that uses native
        # associated club refs; never treat port club_id as that word.
        for word in (0, 1, 32767):
            with self.assertRaisesRegex(
                OriginalEAMPlayerNameSourceError, "original 0x40DA70"
            ):
                original_eam_player_no_association_label(
                    first_name="John", surname="Smith",
                    verified_native_association_word=word,
                )

    def test_unqualified_names_native_words_and_unicode_fail_closed(self):
        for first, last in (("", "Smith"), ("John", ""), ("🙂", "Smith"),
                            ("J\x00unk", "Smith"), ("John", "🙂")):
            with self.assertRaises(OriginalEAMPlayerNameSourceError):
                original_eam_player_initial_surname(first, last)
        for word in (-32769, 32768, None, True, "3", 2.5):
            with self.assertRaises(OriginalEAMPlayerNameSourceError):
                original_eam_player_no_association_label(
                    first_name="John", surname="Smith",
                    verified_native_association_word=word,
                )


if __name__ == "__main__":
    main()
