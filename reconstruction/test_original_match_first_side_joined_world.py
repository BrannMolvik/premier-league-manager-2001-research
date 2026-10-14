"""Source first-side owner→world-tail joined journey, not a live match."""
from __future__ import annotations

from struct import pack_into
from unittest import TestCase, main
from test_original_match_first_side_human_owner import source_fixture
from test_original_match_first_side_world_write import native_bytes, dw
from original_match_first_side_joined_world import (
    OriginalFirstSideJoinedWorldError,
    source_original_5da2f0_first_side_joined_world,
)


def joined(users=(777,),final_nonzero=False):
    owner=source_fixture(manager_keys=users)
    tail=native_bytes()
    club=bytearray(tail["original_first_side_before_tail"])
    pack_into("<I",club,4,777)
    return dict(
        original_source_owner_call=owner,
        original_first_side_pointer_at_5db7d0=owner["original_513244_first_side_club_pointer"],
        original_first_side_before_5db7d0=bytes(club),
        original_processing_context_at_5db7d0=tail["original_processing_context_at_tail"],
        original_5da5f4_final_virtual18_nonzero=final_nonzero,
        original_stack_cap_div10_input_if_reached=None if final_nonzero else 4000,
    )


class SourceOriginalFirstSideJoinedWorldTests(TestCase):
    def test_reached_human_first_manager_identity_into_complete_native_tail(self):
        before=joined(users=(111,777))
        out=source_original_5da2f0_first_side_joined_world(**before)
        self.assertTrue(out.source_human_selector.original_4037b0_full_key_human)
        self.assertEqual(out.source_human_selector.original_403850_selected_masked_user_pointer,0x42000)
        self.assertEqual(dw(out.source_tail.original_first_side_after_bounded_tail,0x144),585)
        self.assertFalse(out.actual_original_callbacks_executed)
        self.assertFalse(out.live_match_state_committed)

    def test_nonhuman_owner_uses_nonhuman_source_branch_not_fake_human(self):
        out=source_original_5da2f0_first_side_joined_world(**joined(users=(111,)))
        self.assertFalse(out.source_human_selector.original_4037b0_full_key_human)
        self.assertIsNone(out.source_human_selector.original_403850_selected_masked_user_pointer)
        self.assertEqual(dw(out.source_tail.original_first_side_after_bounded_tail,0x160),50)

    def test_last_virtual18_nonzero_skips_every_first_side_write(self):
        before=joined(final_nonzero=True)
        out=source_original_5da2f0_first_side_joined_world(**before)
        self.assertTrue(out.source_tail.source_first_side_writes_skipped)
        self.assertEqual(out.source_tail.original_first_side_after_bounded_tail,
                         before["original_first_side_before_5db7d0"])

    def test_native_pointer_club_key_and_callback_type_mismatch_fail_closed(self):
        before=joined()
        for corrupt in (
            {"original_first_side_pointer_at_5db7d0":0x99999},
            {"original_5da5f4_final_virtual18_nonzero":1},
            {"original_5da5f4_final_virtual18_nonzero":None},
        ):
            with self.subTest(corrupt=corrupt):
                with self.assertRaises(OriginalFirstSideJoinedWorldError):
                    source_original_5da2f0_first_side_joined_world(**(before|corrupt))
        club=bytearray(before["original_first_side_before_5db7d0"])
        pack_into("<I",club,4,999)
        with self.assertRaisesRegex(OriginalFirstSideJoinedWorldError,"identity changed"):
            source_original_5da2f0_first_side_joined_world(**(before|{
                "original_first_side_before_5db7d0":bytes(club)}))

    def test_513238_skip_or_unreached_cap_cannot_publish_world(self):
        before=joined(final_nonzero=True)
        with self.assertRaisesRegex(ValueError,"unreachable"):
            source_original_5da2f0_first_side_joined_world(**(before|{
                "original_stack_cap_div10_input_if_reached":4000}))
        before=joined()
        owner=before["original_source_owner_call"]|{"original_513238_flags44_at_entry":0x20}
        with self.assertRaisesRegex(ValueError,"skips side"):
            source_original_5da2f0_first_side_joined_world(**(before|{
                "original_source_owner_call":owner}))


if __name__=="__main__":
    main()
