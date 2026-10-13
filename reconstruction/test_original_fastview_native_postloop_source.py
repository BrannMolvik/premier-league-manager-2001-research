"""Original native FastView 533270/631270/631290/6CC890 value tests."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into, unpack_from
import unittest

from original_fastview_native_postloop_source import (
    SourceFastViewOriginalPostLoopError,
    SourceFastViewOriginalThreeGlobalValues,
    source_fastview_original_postloop_global_values_533270,
)


def source_sample(mode_value=18):
    match=bytearray(b"\x9E"*0x1120)
    pack_into("<I",match,0xFF8,mode_value)
    for off,values in (
        (0x1058,(100,400)),
        (0x10B8,(0xFFFFFFFF,3)),
        (0x1118,(1,0xFFFFFFFF)),
    ):
        pack_into("<II",match,off,*values)
    return dict(
        original_live_match_object=bytes(match),
        original_three_global_buffers_before=(
            b"\xAA"*16,b"\xBB"*16,b"\xCC"*16),
        original_uninitialized_stack_values_when_mode_four=None,
    )


class SourceFastViewOriginalPostLoopTests(unittest.TestCase):
    def test_case2_shipped_original_3_two_dword_averages_preserve_other_globals(self):
        args=source_sample()
        actual=source_fastview_original_postloop_global_values_533270(**args)
        self.assertIsInstance(actual,SourceFastViewOriginalThreeGlobalValues)
        self.assertTrue(actual.native_631290_wrote_outputs)
        self.assertEqual(actual.source_631270_iteration_count,2)
        self.assertEqual(actual.native_three_dword_parameters,(250,1,0))
        for arr,expected,preserve in (
            (actual.original_globals_a25940_bytes,250,b"\xAA"*8),
            (actual.original_globals_a25950_bytes,1,b"\xBB"*8),
            (actual.original_globals_a25930_bytes,0,b"\xCC"*8),
        ):
            self.assertEqual(len(arr),16)
            self.assertEqual(unpack_from("<2I",arr,0),(expected,expected))
            self.assertEqual(arr[8:],preserve)
        self.assertEqual(args["original_three_global_buffers_before"],
                         (b"\xAA"*16,b"\xBB"*16,b"\xCC"*16))

    def test_source_not_18_jumps_case4_and_retains_existing_original_stack(self):
        for value in (0,17,19,0xFFFFFFFF):
            args=source_sample(value)
            args["original_live_match_object"]=args["original_live_match_object"][:0xFFC]
            args["original_uninitialized_stack_values_when_mode_four"]=(0x12345678,0,0xFFFFFFFF)
            result=source_fastview_original_postloop_global_values_533270(**args)
            self.assertFalse(result.native_631290_wrote_outputs)
            self.assertEqual(result.source_631270_iteration_count,4)
            self.assertEqual(tuple(unpack_from("<4I",result.original_globals_a25940_bytes)),(0x12345678,)*4)
            self.assertEqual(tuple(unpack_from("<4I",result.original_globals_a25950_bytes)),(0,)*4)
            self.assertEqual(tuple(unpack_from("<4I",result.original_globals_a25930_bytes)),(0xFFFFFFFF,)*4)

    def test_original_unsigned_overflow_and_floor_average_not_64bit_average(self):
        args=source_sample(18)
        m=bytearray(args["original_live_match_object"])
        pack_into("<II",m,0x1058,0xFFFFFFFF,0xFFFFFFFF)
        pack_into("<II",m,0x10B8,0xFFFFFFFE,2)
        pack_into("<II",m,0x1118,1,2)
        out=source_fastview_original_postloop_global_values_533270(
            **(args|{"original_live_match_object":bytes(m)}))
        self.assertEqual(out.native_three_dword_parameters,(0x7FFFFFFF,0,1))

    def test_unavailable_original_stack_or_buffer_width_fails_closed(self):
        args=source_sample()
        invalid=(
            {"original_live_match_object":args["original_live_match_object"][:0xFFB]},
            {"original_live_match_object":bytearray(args["original_live_match_object"])},
            {"original_live_match_object":args["original_live_match_object"][:0x111F]},
            {"original_three_global_buffers_before":(b"\x00"*16,b"\x00"*15,b"\x00"*16)},
            {"original_three_global_buffers_before":[b"\x00"*16]*3},
            {"original_three_global_buffers_before":(b"\x00"*16,b"\x00"*16,bytearray(16))},
            {"original_uninitialized_stack_values_when_mode_four":(1,2,3)},
        )
        for change in invalid:
            with self.subTest(change=repr(change)[:100]), self.assertRaises(SourceFastViewOriginalPostLoopError):
                source_fastview_original_postloop_global_values_533270(**(args|change))
        alternate=source_sample(2)
        for bad in (None,(1,2),(1,2,True),(1,2,-1),(1,2,0x100000000),
                    [1,2,3],(1,2,3.0)):
            with self.subTest(mode_four=repr(bad)),self.assertRaises(SourceFastViewOriginalPostLoopError):
                source_fastview_original_postloop_global_values_533270(
                    **(alternate|{"original_uninitialized_stack_values_when_mode_four":bad}))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original source executable not mounted")
    def test_original_631270_mode_selector_and_631290_case2_and_global_writes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x5332c1:"e8 aa df 0f 00",
            0x5332e0:"e8 ab df 0f 00",
            0x5332f5:"e8 96 95 19 00",
            0x631270:"8b 81 f8 0f 00 00",
            0x631276:"83 e8 12",
            0x631279:"f7 d8",
            0x63127b:"1b c0",
            0x63127d:"83 e0 02",
            0x631280:"83 c0 02",
            0x631296:"83 f8 03",
            0x6312a2:"ff 24 85 d0 14 63 00",
            0x6313c9:"8d 8e 60 10 00 00",
            0x6313cf:"8d be 58 10 00 00",
            0x6313dd:"8b 1a",
            0x6313e2:"03 c3",
            0x6313ef:"f7 f1",
            0x6313f5:"8d be b8 10 00 00",
            0x6313ff:"8d 8e c0 10 00 00",
            0x631418:"33 d2",
            0x63141d:"f7 f1",
            0x631423:"8d 8e 20 11 00 00",
            0x631429:"81 c6 18 11 00 00",
            0x63144b:"f7 f1",
            0x6314c8:"5f",
            0x6cc890:"8b 44 24 04",
            0x6cc89c:"89 0c 85 40 59 a2 00",
            0x6cc8a7:"89 14 85 50 59 a2 00",
            0x6cc8ae:"89 0c 85 30 59 a2 00",
        }
        for va,hx in samples.items():
            with self.subTest(address=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),
                                 bytes.fromhex(hx))



class SourceFastViewOriginal24SlotsAndResetTests(unittest.TestCase):
    def test_source_24_match_bytes_to_global_dwords_and_pointer_scalar_and_grid(self):
        from original_fastview_native_postloop_source import source_fastview_original_postloop_slot_and_reset_533270
        match=bytearray(b"\xCD"*0x1145)
        for i in range(24):
            match[0x112D+i]=(i*11+3)&0xFF
        pack_into("<I",match,0xB68,0xDEADBEEF)
        args=dict(original_match_object=bytes(match),
                  original_global_slots_a257b8_before=b"\xFA"*96,
                  original_grid_a14828_before=b"\xE3"*108,
                  original_877534_pointer_is_nonzero=False)
        got=source_fastview_original_postloop_slot_and_reset_533270(**args)
        self.assertEqual(len(got.original_24_dword_global_a257b8),96)
        self.assertEqual(tuple(unpack_from("<24I",got.original_24_dword_global_a257b8)),
                         tuple((i*11+3)&0xFF for i in range(24)))
        self.assertEqual(got.original_match_b60_pointer_offset_intent,0xB60)
        self.assertEqual(got.original_match_b68_dword_to_a25874,0xDEADBEEF)
        self.assertEqual(got.original_877534_null_mode_to_a2578c,1)
        self.assertEqual(got.source_grid_a14828_108_after_reset,b"\x00"*108)
        self.assertEqual(args["original_global_slots_a257b8_before"],b"\xFA"*96)
        self.assertEqual(args["original_grid_a14828_before"],b"\xE3"*108)
        other=source_fastview_original_postloop_slot_and_reset_533270(
            **(args|{"original_877534_pointer_is_nonzero":True}))
        self.assertEqual(other.original_877534_null_mode_to_a2578c,0)
        self.assertEqual(other.original_24_dword_global_a257b8,got.original_24_dword_global_a257b8)

    def test_unqualified_original_pointer_or_insufficient_both_side_slots_fails(self):
        from original_fastview_native_postloop_source import source_fastview_original_postloop_slot_and_reset_533270
        args=dict(original_match_object=bytes(0x1145),
                  original_global_slots_a257b8_before=b"\x10"*96,
                  original_grid_a14828_before=b"\x30"*108,
                  original_877534_pointer_is_nonzero=True)
        changes=(
            {"original_match_object":bytes(0x1144)},
            {"original_match_object":bytearray(0x1145)},
            {"original_global_slots_a257b8_before":bytes(95)},
            {"original_global_slots_a257b8_before":bytearray(96)},
            {"original_grid_a14828_before":bytes(107)},
            {"original_grid_a14828_before":bytearray(108)},
            {"original_877534_pointer_is_nonzero":1},
            {"original_877534_pointer_is_nonzero":None},
        )
        for change in changes:
            with self.subTest(change=repr(change)[:70]),self.assertRaises(SourceFastViewOriginalPostLoopError):
                source_fastview_original_postloop_slot_and_reset_533270(**(args|change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original source executable not mounted")
    def test_native_533270_24_slots_and_last_reset_private_opcode_signatures(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        examples={
            0x533305:"8d 4c 24 0c",
            0x53330b:"8b cf",
            0x53330d:"e8 9e 83 0f 00",
            0x533318:"e8 e3 75 19 00",
            0x533320:"46",
            0x533321:"83 fe 18",
            0x533326:"8d 87 60 0b 00 00",
            0x53332d:"e8 4e 8a 19 00",
            0x533332:"8b 8f 68 0b 00 00",
            0x533339:"e8 b2 75 19 00",
            0x53333e:"8b 35 34 75 87 00",
            0x533346:"85 f6",
            0x533348:"0f 94 c2",
            0x53334c:"e8 bf 75 19 00",
            0x533354:"e8 37 f5 18 00",
            0x62b6b0:"8b 54 24 04",
            0x62b6b6:"8a 84 0a 2d 11 00 00",
            0x62b6c1:"89 01",
            0x6ca900:"8b 4c 24 04",
            0x6ca908:"89 04 8d b8 57 a2 00",
            0x6cbd80:"8b 44 24 04",
            0x6cbd84:"a3 c0 58 a2 00",
            0x6ca8f0:"8b 44 24 04",
            0x6ca8f4:"a3 74 58 a2 00",
            0x6ca910:"8b 44 24 04",
            0x6ca914:"a3 8c 57 a2 00",
            0x6c2890:"b8 2a 48 a1 00",
            0x6c2897:"b9 12 00 00 00",
            0x6c289c:"88 50 fe",
            0x6c289f:"88 50 ff",
            0x6c28a2:"88 10",
            0x6c28a4:"83 c0 03",
            0x6c28aa:"3d 60 48 a1 00",
            0x6c28b1:"c3",
        }
        for va,hx in examples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class SourceFastViewOriginalCompleteSetupValueStageTests(unittest.TestCase):
    def test_source_533270_full_two_club_tactical_statistics_and_24_slots(self):
        from original_fastview_native_postloop_source import source_fastview_original_complete_value_stage_533270
        from test_original_fastview_native_full_side_setup import original_source_test_inputs
        base=original_source_test_inputs()
        match=bytearray(base["original_match_object"])
        match.extend(b"\0"*(0x1145-len(match)))
        pack_into("<I",match,0xFF8,18)
        for addr,values in ((0x1058,(3,5)),(0x10B8,(7,9)),(0x1118,(100,300))):
            pack_into("<II",match,addr,*values)
        for i in range(24):
            match[0x112D+i]=i+5
        pack_into("<I",match,0xB68,0xABCD1234)
        args=dict(original_live_match_object=bytes(match),
                  original_side0=base["source_side0"],
                  original_side1=base["source_side1"],
                  original_human_registry_club_ids_in_link_order=(44,),
                  original_country_name_indexes_germany_france_england=(7,11,15),
                  original_three_global_buffers_before=(b"\xDD"*16,b"\xEE"*16,b"\xFF"*16),
                  original_uninitialized_stack_values_when_mode_four=None,
                  original_global_slots_a257b8_before=b"\x55"*96,
                  original_grid_a14828_before=b"\x99"*108,
                  original_877534_pointer_is_nonzero=False)
        stage=source_fastview_original_complete_value_stage_533270(**args)
        first=stage.two_sided_roster_and_tactics
        self.assertEqual(len(first.original_full_side_global_memory),3112)
        self.assertEqual(tuple(unpack_from("<I",first.original_full_side_global_memory,i)[0]
                               for i in (0xFC,1556+0xFC)),(12,11))
        self.assertEqual(stage.native_three_statistics_globals.native_three_dword_parameters,(4,8,200))
        self.assertEqual(stage.native_three_statistics_globals.source_631270_iteration_count,2)
        self.assertEqual(stage.native_three_statistics_globals.original_globals_a25930_bytes[8:],b"\xFF"*8)
        slots=stage.native_match_slots_and_reset
        self.assertEqual(tuple(unpack_from("<24I",slots.original_24_dword_global_a257b8)),tuple(range(5,29)))
        self.assertEqual(slots.original_877534_null_mode_to_a2578c,1)
        self.assertEqual(slots.original_match_b68_dword_to_a25874,0xABCD1234)
        self.assertEqual(slots.source_grid_a14828_108_after_reset,bytes(108))
        self.assertEqual(args["original_grid_a14828_before"],b"\x99"*108)

    def test_source_unknown_postloop_is_rejected_without_publishing_sides(self):
        from original_fastview_native_postloop_source import source_fastview_original_complete_value_stage_533270
        from test_original_fastview_native_full_side_setup import original_source_test_inputs
        base=original_source_test_inputs()
        match=bytearray(base["original_match_object"])
        match.extend(b"\0"*(0x1145-len(match)))
        pack_into("<I",match,0xFF8,18)
        args=dict(original_live_match_object=bytes(match),
                  original_side0=base["source_side0"],
                  original_side1=base["source_side1"],
                  original_human_registry_club_ids_in_link_order=(44,),
                  original_country_name_indexes_germany_france_england=(7,11,15),
                  original_three_global_buffers_before=(bytes(16),)*3,
                  original_uninitialized_stack_values_when_mode_four=None,
                  original_global_slots_a257b8_before=bytes(96),
                  original_grid_a14828_before=bytes(108),
                  original_877534_pointer_is_nonzero=True)
        expected=source_fastview_original_complete_value_stage_533270(**args)
        for change in (
            {"original_live_match_object":bytes(match[:0x1120])},
            {"original_side0":None},
            {"original_grid_a14828_before":bytes(107)},
            {"original_877534_pointer_is_nonzero":None},
            {"original_country_name_indexes_germany_france_england":(7,True,15)},
        ):
            with self.subTest(change=repr(change)[:90]),self.assertRaises(
                (SourceFastViewOriginalPostLoopError,ValueError)):
                source_fastview_original_complete_value_stage_533270(**(args|change))
        self.assertEqual(source_fastview_original_complete_value_stage_533270(**args),expected)

    def test_source_mode_four_retains_unknown_original_stack_not_guess_zero(self):
        from original_fastview_native_postloop_source import source_fastview_original_complete_value_stage_533270
        from test_original_fastview_native_full_side_setup import original_source_test_inputs
        base=original_source_test_inputs()
        match=bytearray(base["original_match_object"])
        match.extend(b"\0"*(0x1145-len(match)))
        pack_into("<I",match,0xFF8,19)
        args=dict(original_live_match_object=bytes(match),
                  original_side0=base["source_side0"],original_side1=base["source_side1"],
                  original_human_registry_club_ids_in_link_order=(44,),
                  original_country_name_indexes_germany_france_england=(7,11,15),
                  original_three_global_buffers_before=(b"\x44"*16,)*3,
                  original_uninitialized_stack_values_when_mode_four=(81,83,89),
                  original_global_slots_a257b8_before=bytes(96),
                  original_grid_a14828_before=bytes(108),
                  original_877534_pointer_is_nonzero=True)
        got=source_fastview_original_complete_value_stage_533270(**args)
        self.assertFalse(got.native_three_statistics_globals.native_631290_wrote_outputs)
        self.assertEqual(got.native_three_statistics_globals.native_three_dword_parameters,(81,83,89))
        self.assertEqual(got.native_match_slots_and_reset.original_877534_null_mode_to_a2578c,0)
        with self.assertRaises(SourceFastViewOriginalPostLoopError):
            source_fastview_original_complete_value_stage_533270(**(args|{"original_uninitialized_stack_values_when_mode_four":None}))

if __name__=="__main__":
    unittest.main()
