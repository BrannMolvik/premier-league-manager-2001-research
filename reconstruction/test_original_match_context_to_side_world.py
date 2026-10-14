"""Original 5DB6FA native context joined to existing first-side source owner."""
from struct import pack_into,unpack_from
from unittest import TestCase,main
from original_match_context_to_side_world import source_original_5db6fa_context_then_first_side
from test_original_match_first_side_human_owner import source_fixture
from test_original_match_first_side_world_write import native_bytes as fixture
from original_native_5db6fa_context_tail import OriginalContextTailSourceError

def joined(skip=False,keys=(777,)):
    owner=source_fixture(manager_keys=keys)
    before=fixture()
    club=bytearray(before['original_first_side_before_tail'])
    pack_into('<I',club,4,777)
    return dict(
        original_processing_object_pointer_at_entry=0xC0000,
        original_reached_processing_pointer_at_5db70c=0xC0000,
        original_processing_context_before_5db6fa=before['original_processing_context_at_tail'],
        original_ebx_component_at_5db6fc=45,
        original_ecx_component_at_5db704=55,
        original_source_owner_call=owner,
        original_first_side_pointer_at_5db7d0=0x90000,
        original_first_side_before_5db7d0=bytes(club),
        original_5da5f4_final_virtual18_nonzero=skip,
        original_stack_cap_div10_input_if_reached=None if skip else 4000,
    )

class OriginalContextToSideWorldTests(TestCase):
    def test_same_reached_native_context_in_the_first_side_world(self):
        data=joined()
        result=source_original_5db6fa_context_then_first_side(**data)
        context=result.source_native_context.native_context_after_reached_stores
        club=result.source_first_side.source_tail.original_first_side_after_bounded_tail
        self.assertEqual([unpack_from('<I',context,o)[0]
                          for o in (0xd84,0xd8c,0xd90,0xd94,0xd98,0xd9c)],
                         [100,45,55,2,2,4])
        self.assertEqual(unpack_from('<I',club,0x148)[0],45)
        self.assertEqual(unpack_from('<I',club,0x160)[0],100)
        self.assertFalse(result.original_world_state_committed)

    def test_original_callback_skip_still_updates_context_but_not_club(self):
        data=joined(skip=True)
        result=source_original_5db6fa_context_then_first_side(**data)
        self.assertEqual(result.source_first_side.source_tail.original_first_side_after_bounded_tail,
                         data['original_first_side_before_5db7d0'])
        self.assertEqual(result.source_native_context.source_context_d84,100)

    def test_wrong_processor_identity_and_zero_division_component_fail(self):
        data=joined()
        for fake in (
            {'original_reached_processing_pointer_at_5db70c':0xdeadbeef},
            {'original_ecx_component_at_5db704':0},
        ):
            with self.subTest(fake=fake):
                with self.assertRaises(OriginalContextTailSourceError):
                    source_original_5db6fa_context_then_first_side(**(data|fake))
if __name__=='__main__':main()
