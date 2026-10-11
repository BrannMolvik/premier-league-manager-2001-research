"""Source original EAMPlayer ID2 P/C raw typed descriptor resolution."""

from unittest import TestCase, main

from original_eamail_tagged_link_target import (
    OriginalEAMLinkSourceError, original_eam_typed_link_index,
    NATIVE_EAM_LINK_RESOLVER_VA, NATIVE_EAM_ROW_LINK_DISPATCH_VA,
    NATIVE_EAM_PLAYER_DETAILS_VA, NATIVE_EAM_CLUB_DETAILS_VA,
    NATIVE_EAM_ASSOC_TABLE_GLOBAL_VA, NATIVE_EAM_ASSOC_TABLE_STRIDE,
    NATIVE_EAM_ASSOC_TABLE_CLUB_WORD_OFFSET,
)


def resolve(selector, descriptor_type=0, word4=12, word8=31, club_lookup=None):
    return original_eam_typed_link_index(
        selector, verified_descriptor_type=descriptor_type,
        verified_descriptor_word4=word4,
        verified_descriptor_word8=word8,
        qualified_original_assoc_table_club_at_index=club_lookup,
    )


class NativeEAMTaggedTargetTests(TestCase):
    def test_source_addresses_and_player_P_uses_descriptor_word4(self):
        self.assertEqual((NATIVE_EAM_LINK_RESOLVER_VA, NATIVE_EAM_ROW_LINK_DISPATCH_VA,
                          NATIVE_EAM_PLAYER_DETAILS_VA, NATIVE_EAM_CLUB_DETAILS_VA),
                         (0x5CF7B0, 0x471C60, 0x605DC0, 0x604900))
        for kind in (0, 1, 2, 17, 33):
            with self.subTest(kind=kind):
                target=resolve(ord("P"), descriptor_type=kind)
                self.assertEqual(target.source_kind, "player")
                self.assertEqual(target.original_signed_index, 12)
                self.assertFalse(target.native_detail_gui_verified)
        self.assertIsNone(resolve(ord("P"), word4=-1))
        self.assertIsNone(resolve(0, descriptor_type=1))
        self.assertIsNone(resolve(ord("Q"), descriptor_type=1))

    def test_source_C_club_descriptor_kind_direct_second_and_table_branches(self):
        for kind, expected in ((0,12),(2,31),(17,31),(4,12),(33,12)):
            with self.subTest(kind=kind):
                target=resolve(ord("C"), descriptor_type=kind)
                self.assertEqual((target.source_kind,target.original_signed_index),
                                 ("club",expected))
        self.assertEqual((NATIVE_EAM_ASSOC_TABLE_GLOBAL_VA,
                          NATIVE_EAM_ASSOC_TABLE_STRIDE,
                          NATIVE_EAM_ASSOC_TABLE_CLUB_WORD_OFFSET),
                         (0x875628,64,0x24))
        table={12:44}
        target=resolve(ord("C"), descriptor_type=1,
                       club_lookup=lambda index:table[index])
        self.assertEqual(target.original_signed_index,44)
        self.assertIsNone(resolve(ord("C"),descriptor_type=2,word8=-1))
        self.assertIsNone(resolve(ord("C"),descriptor_type=1,
                                  club_lookup=lambda index:-1))

    def test_native_unqualified_assoc_and_invalid_index_fail_closed(self):
        with self.assertRaisesRegex(OriginalEAMLinkSourceError,"association"):
            resolve(ord("C"),descriptor_type=1)
        with self.assertRaisesRegex(OriginalEAMLinkSourceError,"association"):
            resolve(ord("C"),descriptor_type=1,word4=-3,club_lookup=lambda i:4)
        with self.assertRaisesRegex(OriginalEAMLinkSourceError,"callable"):
            resolve(ord("C"),descriptor_type=1,club_lookup=23)
        with self.assertRaisesRegex(OriginalEAMLinkSourceError,"signed DWORD"):
            resolve(ord("C"),descriptor_type=1,club_lookup=lambda i:"Arsenal")
        for selector in (True, -1, 256, "P", None):
            with self.subTest(selector=repr(selector)), self.assertRaises(
                OriginalEAMLinkSourceError
            ):
                resolve(selector)
        for kind in (True, 1 << 32, -(1 << 32), "1"):
            with self.assertRaises(OriginalEAMLinkSourceError):
                resolve(ord("P"),descriptor_type=kind)
        # Original parent treats -1 as no action; other signed negatives
        # still select original fallback club path, which this helper
        # retains only as unexpanded source index.
        result=resolve(ord("C"),descriptor_type=0,word4=-2)
        self.assertEqual(result.original_signed_index,-2)
        self.assertFalse(result.native_detail_gui_verified)


if __name__ == "__main__":
    main()
