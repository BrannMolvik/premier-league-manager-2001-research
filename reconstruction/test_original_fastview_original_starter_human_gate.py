"""Original native starter 0x417340 source human gate and 0x41EDF0 counter."""
import os
import unittest
from pathlib import Path
from struct import pack_into
from original_fastview_native_player_registry import SourceFastViewOriginalPlayerRegistryReference
from original_fastview_original_starter_human_gate import (
    SourceFastViewOriginalClubRegistry,
    SourceFastViewOriginalStarterWorldError,
    source_fastview_original_starter_human_external_4182f0,
)
from original_fastview_player_world_writeback import source_fastview_original_starter_external_count_41edf0


def _setup(*,club10=0,club72=1,flag14=0x1000,flag174=0,club_ids=(101,202,303),
           club_count_values=(10,0x80000000,6),human_ids=(101,),fallback_id=404,
           fallback_count=5):
    record=bytearray(0x250)
    pack_into("<I",record,0x14,flag14)
    pack_into("<I",record,0x174,flag174)
    pack_into("<h",record,0x10,club10)
    pack_into("<h",record,0x72,club72)
    clubs=bytearray(0x2A8*len(club_ids))
    for idx,(cid,count) in enumerate(zip(club_ids,club_count_values)):
        pack_into("<I",clubs,idx*0x2A8+4,cid)
        pack_into("<I",clubs,idx*0x2A8+0x1A8,count)
    fallback=bytearray(0x2A8)
    pack_into("<I",fallback,4,fallback_id)
    pack_into("<I",fallback,0x1A8,fallback_count)
    return dict(original_player=SourceFastViewOriginalPlayerRegistryReference(
        side_index=0,ordinal=0,original_player_id_word=3,
        source_player_record_592=bytes(record),
        source_native_subobject_pointer_dword=0xAABBCC00),
        original_clubs=SourceFastViewOriginalClubRegistry(
            original_live_club_array_bytes=bytes(clubs),
            original_fallback_club_record_680=bytes(fallback)),
        original_human_registry_club_ids_in_link_order=human_ids)


class OriginalStarterHumanSourceTests(unittest.TestCase):
    def test_original_417340_human_club_uses_player_word10_not_word72(self):
        args=_setup(club10=0,club72=2,human_ids=(101,),flag14=0x1000,flag174=3)
        result=source_fastview_original_starter_human_external_4182f0(**args)
        self.assertTrue(result.original_417340_human_owned)
        self.assertEqual(result.original_resolved_human_registry_ordinal,0)
        self.assertEqual(result.original_player_club_index10_signed,0)
        self.assertIsNone(result.original_player_count_index72_signed)
        self.assertFalse(result.source_external_result.invoked_41edf0)
        self.assertEqual(result.source_external_result.native_flag14_after,0x1010)
        self.assertTrue(result.original_player_direct_status.requires_original_attribute_cache_swap_418220)
        self.assertEqual(result.original_player_direct_status.direct_flag174_dword,0)
        self.assertIsNone(result.original_count_source_before)

    def test_original_417340_not_human_and_distinct_index72_selects_count(self):
        args=_setup(club10=1,club72=0,human_ids=(101,),flag14=0x1000)
        result=source_fastview_original_starter_human_external_4182f0(**args)
        self.assertFalse(result.original_417340_human_owned)
        self.assertEqual(result.original_player_club_index10_signed,1)
        self.assertEqual(result.original_player_count_index72_signed,0)
        self.assertTrue(result.source_external_result.invoked_41edf0)
        self.assertTrue(result.source_external_result.clears_0x1000_flag)
        self.assertEqual(result.source_external_result.native_count_after,9)
        self.assertEqual(result.source_external_result.native_flag14_after,0x10)
        self.assertEqual(result.original_count_source_before,10)

    def test_highbit_signed_count_not_decremented_but_flag_cleared(self):
        args=_setup(club10=2,club72=1,human_ids=(),flag14=0x1000)
        result=source_fastview_original_starter_human_external_4182f0(**args)
        self.assertEqual(result.original_count_source_before,0x80000000)
        self.assertEqual(result.source_external_result.native_count_after,0x80000000)
        self.assertEqual(result.source_external_result.native_flag14_after,0x10)
        for count in (0xFFFFFFFF,0,0x7FFFFFFF):
            r=source_fastview_original_starter_external_count_41edf0(
                native_flag14_after_direct=0x1010,original_417340_result_byte=0,
                original_signed_club_index_word=-1,native_selected_owner_count_dword=count)
            self.assertEqual(r.native_count_after,
                             count-1 if count==0x7FFFFFFF else count)

    def test_original_negative_club10_and_negative_count72_are_independent_fallbacks(self):
        args=_setup(club10=-1,club72=-2,human_ids=(404,),flag14=0x1000)
        got=source_fastview_original_starter_human_external_4182f0(**args)
        self.assertTrue(got.original_417340_human_owned)
        self.assertFalse(got.source_external_result.invoked_41edf0)
        args=_setup(club10=-1,club72=-2,human_ids=(),flag14=0x1000,fallback_count=5)
        got=source_fastview_original_starter_human_external_4182f0(**args)
        self.assertFalse(got.original_417340_human_owned)
        self.assertEqual(got.original_player_count_index72_signed,-2)
        self.assertTrue(got.source_external_result.uses_fallback_count_owner)
        self.assertEqual(got.source_external_result.native_count_after,4)

    def test_skip_via_status_2000_and_count_1000_absent_does_not_read_word72(self):
        for flag14,invoked in ((0x3000,False),(0,True)):
            args=_setup(club10=2,club72=32000,human_ids=(),flag14=flag14)
            got=source_fastview_original_starter_human_external_4182f0(**args)
            self.assertEqual(got.source_external_result.invoked_41edf0,invoked)
            self.assertIsNone(got.original_player_count_index72_signed)
            self.assertIsNone(got.original_count_source_before)

    def test_missing_original_club_and_invalid_types_fail_without_mutating(self):
        args=_setup(club10=2,club72=0,human_ids=())
        expected=source_fastview_original_starter_human_external_4182f0(**args)
        from dataclasses import replace
        for change in (
            {"original_clubs":None},
            {"original_player":None},
            {"original_human_registry_club_ids_in_link_order":[303]},
            {"original_clubs":SourceFastViewOriginalClubRegistry(
                original_live_club_array_bytes=bytes(0x2A8),
                original_fallback_club_record_680=bytes(0x2A8))},
            {"original_player":replace(args["original_player"],source_player_record_592=bytes(591))},
            {"original_player":replace(args["original_player"],source_player_record_592=bytearray(592))},
        ):
            with self.subTest(change=repr(change)[:75]),self.assertRaises((ValueError,TypeError)):
                source_fastview_original_starter_human_external_4182f0(**(args|change))
        self.assertEqual(source_fastview_original_starter_human_external_4182f0(**args),expected)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),"owner original private PE absent")
    def test_original_417270_417340_and_41edf0_signed_branch_opcode_proof(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x417270:"0f bf 49 10",0x417274:"85 c9",0x417276:"7d 06",
            0x417278:"a1 94 4b 87 00",0x41727e:"8b c1",
            0x417280:"c1 e0 04",0x417283:"03 c1",
            0x417285:"8b 0d 90 4b 87 00",0x41728b:"8d 04 80",
            0x41728e:"8d 04 c1",
            0x417340:"e8 2b ff ff ff",0x417345:"8b c8",
            0x417347:"e9 64 c4 fe ff",0x4037b0:"51",
            0x4037b1:"b9 10 4c 87 00",0x4037b6:"e8 25 02 01 00",
            0x41edf0:"8b 41 14",0x41edf4:"c1 e8 0c",
            0x41edf7:"a8 01",0x41edfb:"8b 51 14",
            0x41ee04:"8b 15 90 4b 87 00",
            0x41ee0a:"0f bf 41 72",0x41ee0e:"8b 35 94 4b 87 00",
            0x41ee2a:"8b b9 a8 01 00 00",0x41ee30:"85 ff",
            0x41ee33:"7e 29",0x41ee3c:"ff 88 a8 01 00 00",
            0x41ee54:"49",0x41ee58:"89 88 a8 01 00 00",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
