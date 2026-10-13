"""Owner-original FastView postmodal player value/branch source regressions.

These are pure data contracts, NOT game object commits or GUI tests.
"""
import os
import struct
import unittest
from pathlib import Path

from original_fastview_two_sided_live_writeback import SourceFastViewTwoSideBlockState
from original_fastview_player_world_writeback import (
    SourceFastViewPlayerWorldWritebackError,
    source_fastview_native_postmodal_player_write_intents_533ca0,
    source_fastview_original_player_low5_low4_getters_4ea3c0,
    source_fastview_original_player_low5_low4_setters_4ea330,
    source_fastview_original_player_field_pre_modal_capture_533bf0,
    SourceFastViewPlayerPreModalGlobals,
    source_fastview_original_player_direct_status_stage_4182f0,
    source_fastview_original_player_attribute_cache_swap_418220,
    source_fastview_original_substitute_pre_restore_reset_4ea370,
    SourceFastViewPlayerDirectStatusStage,
    SourceFastViewPlayerAttributeCacheSwap,
)


def sample_native_postmodal_world():
    left=bytearray(b"L"*0x300)
    right=bytearray(b"R"*0x300)
    for i in range(18):
        struct.pack_into("<H",left,0x244+2*i,100+i)
        struct.pack_into("<H",right,0x244+2*i,200+i)
    values=bytearray(b"\x00"*0x140)
    flags=bytearray(b"\x00"*0x140)
    for side in range(2):
        for i in range(18):
            offset=0xA0*side+4*i
            struct.pack_into("<I",values,offset,0x10000+100*side+i)
            flags[offset]=0xA0+side*16+i
    return (SourceFastViewTwoSideBlockState(bytes(left),bytes(right)),
            bytes(values),bytes(flags))


class OriginalFastViewNativePerPlayerWriteIntentTests(unittest.TestCase):
    def test_original_both_sides_and_first_eleven_have_different_status_methods(self):
        sides,values,flags=sample_native_postmodal_world()
        intent=source_fastview_native_postmodal_player_write_intents_533ca0(
            live_sides_after_modal=sides,native_player_counts=(12,18),
            global_player_low5_dwords=values,global_player_low4_dwords=flags)
        self.assertEqual(len(intent),30)
        self.assertEqual([p.side_index for p in intent[:12]],[0]*12)
        self.assertEqual([p.side_index for p in intent[12:]],[1]*18)
        for side,expected_count,base in ((0,12,100),(1,18,200)):
            rows=[row for row in intent if row.side_index==side]
            self.assertEqual(len(rows),expected_count)
            for i,item in enumerate(rows):
                self.assertEqual(item.player_ordinal,i)
                self.assertEqual(item.source_player_id_word,base+i)
                self.assertEqual(item.native_player_branch_va,
                                 0x4182F0 if i<11 else 0x4182C0)
                self.assertEqual(item.native_object_status_or_bit,
                                 0x10 if i<11 else 0x20)
                self.assertEqual(item.original_low5_parameter_dword,0x10000+100*side+i)
                self.assertEqual(item.original_low4_parameter_byte,
                                 (0xA0+side*16+i)&0xFF)
        self.assertEqual(struct.unpack_from("<H",sides.first_side_bytes,0x244)[0],100)

    def test_source_original_player_setters_preserve_upper_bits_and_all_other_bytes(self):
        original=bytes((0x11,0x22,0x33,0xE5,0xA9,0x66,0x77))
        self.assertEqual(source_fastview_original_player_low5_low4_getters_4ea3c0(
            original_player_attribute_bytes=original),(5,9))
        changed=source_fastview_original_player_low5_low4_setters_4ea330(
            original_player_attribute_bytes=original,
            native_low5_parameter_dword=0x1234567F,
            native_low4_parameter_byte=0xF2)
        self.assertEqual(changed,bytes((0x11,0x22,0x33,0xFF,0xA2,0x66,0x77)))
        self.assertEqual(source_fastview_original_player_low5_low4_getters_4ea3c0(
            original_player_attribute_bytes=changed),(31,2))
        self.assertEqual(original[3:5],b"\xE5\xA9")

    def test_source_original_world_setter_masks_even_large_legal_dword(self):
        got=source_fastview_original_player_low5_low4_setters_4ea330(
            original_player_attribute_bytes=b"\0\0\0\xC0\xF0",
            native_low5_parameter_dword=0xFFFFFFFF,native_low4_parameter_byte=255)
        self.assertEqual(got,b"\0\0\0\xDF\xFF")

    def test_first_eleven_last_player_and_first_reserve_branches_never_overlap(self):
        sides,low5,low4=sample_native_postmodal_world()
        rows=source_fastview_native_postmodal_player_write_intents_533ca0(
            live_sides_after_modal=sides,native_player_counts=(11,11),
            global_player_low5_dwords=low5,global_player_low4_dwords=low4)
        self.assertEqual(len(rows),22)
        self.assertTrue(all(p.native_player_branch_va==0x4182F0 for p in rows))
        rows2=source_fastview_native_postmodal_player_write_intents_533ca0(
            live_sides_after_modal=sides,native_player_counts=(12,11),
            global_player_low5_dwords=low5,global_player_low4_dwords=low4)
        self.assertEqual(rows2[10].native_player_branch_va,0x4182F0)
        self.assertEqual(rows2[11].native_player_branch_va,0x4182C0)
        self.assertEqual(rows2[12].native_player_branch_va,0x4182F0)

    def test_original_source_array_types_and_owner_counts_fail_closed(self):
        sides,low5,low4=sample_native_postmodal_world()
        valid=dict(live_sides_after_modal=sides,native_player_counts=(12,18),
                   global_player_low5_dwords=low5,global_player_low4_dwords=low4)
        for change in (
            {"live_sides_after_modal":None},
            {"native_player_counts":(12,)},
            {"native_player_counts":[12,18]},
            {"native_player_counts":(True,18)},
            {"native_player_counts":(10,18)},
            {"native_player_counts":(12,19)},
            {"global_player_low5_dwords":low5[:-1]},
            {"global_player_low4_dwords":bytearray(low4)},
        ):
            with self.subTest(change=repr(change)),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_native_postmodal_player_write_intents_533ca0(
                    **(valid|change))

    def test_original_subobject_inputs_reject_invalid_lengths_or_parameters(self):
        for bad in (None,b"",b"\x00"*4,bytearray(b"\x00"*5)):
            with self.subTest(value=repr(bad)),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_low5_low4_getters_4ea3c0(
                    original_player_attribute_bytes=bad)
        original=b"\x00"*5
        for bad in (-1,True,1.0,None,0x100000000):
            with self.subTest(value=bad),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_low5_low4_setters_4ea330(
                    original_player_attribute_bytes=original,
                    native_low5_parameter_dword=bad,native_low4_parameter_byte=0)
        for bad in (-1,True,256,None,"0"):
            with self.subTest(value=repr(bad)),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_low5_low4_setters_4ea330(
                    original_player_attribute_bytes=original,
                    native_low5_parameter_dword=0,native_low4_parameter_byte=bad)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original private owner executable not mounted")
    def test_source_native_player_capture_writeback_status_methods_and_bit_masks(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x533C1D:"b9 14 00 00 00",
            0x533C2A:"f3 a5",
            0x533C2C:"8b ad 94 02 00 00",
            0x533C40:"66 8b 33",
            0x533C48:"8b 88 48 02 00 00",
            0x533C4E:"e8 6d 67 fb ff",
            0x533C59:"89 87 b4 7b 87 00",
            0x533C64:"8b 88 48 02 00 00",
            0x533C6A:"e8 61 67 fb ff",
            0x533C77:"89 87 74 7a 87 00",
            0x533C7D:"83 c7 04",
            0x533D06:"66 8b 75 00",
            0x533D0A:"83 fb 0b",
            0x533D16:"e8 d5 45 ee ff",
            0x533D24:"e8 97 45 ee ff",
            0x533D34:"8b b0 48 02 00 00",
            0x533D3A:"8b 87 b4 7b 87 00",
            0x533D43:"e8 e8 65 fb ff",
            0x533D48:"8a 8f 74 7a 87 00",
            0x533D51:"e8 fa 65 fb ff",
            0x533D5B:"83 c5 02",
            0x533D5E:"83 c7 04",
            0x533D69:"42",
            0x533D6A:"83 fa 01",
            0x4182C0:"56",
            0x4182CD:"0c 20",
            0x4182F3:"83 4e 14 10",
            0x4EA330:"8a 41 03",
            0x4EA33D:"80 e2 1f",
            0x4EA342:"88 51 03",
            0x4EA350:"8a 41 04",
            0x4EA35D:"80 e2 0f",
            0x4EA362:"88 51 04",
            0x4EA3C0:"8a 41 03 83 e0 1f",
            0x4EA3D0:"8a 41 04 24 0f",
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),
                                 bytes.fromhex(hx))




class OriginalFastViewOriginalPlayerPreModalRoundTripTests(unittest.TestCase):
    def test_capture_native_players_two_sides_and_preserve_other_global_bytes(self):
        first=(b"\x00\x00\x00\xE1\xF2",b"\x00\x00\x00\xFA\xC5")
        second=(b"\x00\x00\x00\x97\xAB",)
        before5=b"\x88"*320
        before4=b"\x77"*320
        result=source_fastview_original_player_field_pre_modal_capture_533bf0(
            original_player_subobjects_by_side=(first,second),
            original_low5_globals_before=before5,
            original_low4_globals_before=before4)
        self.assertEqual(tuple(struct.unpack_from("<2I",result.original_low5_globals_320,0)),(1,26))
        self.assertEqual(tuple(struct.unpack_from("<2I",result.original_low4_globals_320,0)),(2,5))
        self.assertEqual(struct.unpack_from("<I",result.original_low5_globals_320,0xA0)[0],23)
        self.assertEqual(struct.unpack_from("<I",result.original_low4_globals_320,0xA0)[0],11)
        self.assertEqual(result.original_low5_globals_320[0x20:0x30],b"\x88"*16)
        self.assertEqual(result.original_low4_globals_320[0x20:0x30],b"\x77"*16)
        self.assertEqual(before5,b"\x88"*320)
        self.assertEqual(before4,b"\x77"*320)

    def test_pre_modal_getters_restore_exact_packed_lower_fields_after_intent(self):
        sides,_,_=sample_native_postmodal_world()
        left=(b"\x11\x22\x33\xE7\xB4",)*12
        right=(b"\x11\x22\x33\xC1\xFB",)*11
        captured=source_fastview_original_player_field_pre_modal_capture_533bf0(
            original_player_subobjects_by_side=(left,right),
            original_low5_globals_before=b"\xCC"*320,
            original_low4_globals_before=b"\xDD"*320)
        rows=source_fastview_native_postmodal_player_write_intents_533ca0(
            live_sides_after_modal=sides,native_player_counts=(12,11),
            global_player_low5_dwords=captured.original_low5_globals_320,
            global_player_low4_dwords=captured.original_low4_globals_320)
        self.assertEqual(len(rows),23)
        for intent in rows:
            old=(left if intent.side_index==0 else right)[intent.player_ordinal]
            updated=source_fastview_original_player_low5_low4_setters_4ea330(
                original_player_attribute_bytes=old,
                native_low5_parameter_dword=intent.original_low5_parameter_dword,
                native_low4_parameter_byte=intent.original_low4_parameter_byte)
            self.assertEqual(updated,old)

    def test_source_pre_capture_unknown_owner_count_types_and_bytes_are_rejected(self):
        base=dict(original_player_subobjects_by_side=((b"\0"*5,),()),
                  original_low5_globals_before=b"\x00"*320,
                  original_low4_globals_before=b"\x00"*320)
        for bad in (
            {"original_player_subobjects_by_side":None},
            {"original_player_subobjects_by_side":([],())},
            {"original_player_subobjects_by_side":((bytearray(b"\0"*5),),())},
            {"original_player_subobjects_by_side":((b"\0"*5,)*21,())},
            {"original_low5_globals_before":b"\x00"*319},
            {"original_low4_globals_before":bytearray(b"\x00"*320)},
        ):
            with self.subTest(bad=repr(bad)),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_field_pre_modal_capture_533bf0(
                    **(base|bad))



class SourceFastViewPlayerOriginalXIReserveLifecycleTests(unittest.TestCase):
    def test_starter_vs_reserve_status_flag14_and_flag174_direct_effects(self):
        for is_starter,flag14,flag174,expected in (
            (True,0x30,3,SourceFastViewPlayerDirectStatusStage(0x10,0,True,True)),
            (False,0x30,3,SourceFastViewPlayerDirectStatusStage(0x20,0,True,False)),
            (True,0x20,2,SourceFastViewPlayerDirectStatusStage(0x10,0,False,True)),
            (False,0x10,0,SourceFastViewPlayerDirectStatusStage(0x20,0,False,False)),
            (True,0xABCD0030,0xDEADBEEF,
             SourceFastViewPlayerDirectStatusStage(0xABCD0010,0xDEADBEEC,True,True)),
        ):
            with self.subTest(starter=is_starter,flag14=hex(flag14)):
                self.assertEqual(source_fastview_original_player_direct_status_stage_4182f0(
                    source_flag14_dword=flag14,source_flag174_dword=flag174,
                    starting_eleven=is_starter),expected)

    def test_actual_native_418220_swap_is_a_two_way_value_exchange_only(self):
        record=bytearray(b"R"*0x260)
        record[0x152]=0xAA
        record[0x153]=0xBB
        subobj=bytes((0x17,0x01,0x02,0xE5,0xA9,0xFC))
        result=source_fastview_original_player_attribute_cache_swap_418220(
            original_player_record_bytes=bytes(record),
            original_player_subobject_bytes=subobj)
        self.assertEqual((result.updated_player_record[0x152],
                          result.updated_player_record[0x153]),(5,9))
        self.assertEqual(result.updated_player_subobject,
                         bytes((0x17,0x01,0x02,0xEA,0xAB,0xFC)))
        self.assertEqual(record[0x152:0x154],b"\xAA\xBB")
        self.assertEqual(subobj[3:5],b"\xE5\xA9")

    def test_substitute_reset_then_source_modal_restoration_preserves_upper_bits(self):
        before=bytes((0x17,0x10,0x20,0xE5,0xA9,0x30))
        reset=source_fastview_original_substitute_pre_restore_reset_4ea370(
            original_player_subobject_bytes=before)
        self.assertEqual(reset,bytes((0x17,0x10,0x20,0xF7,0xA0,0x30)))
        restored=source_fastview_original_player_low5_low4_setters_4ea330(
            original_player_attribute_bytes=reset,
            native_low5_parameter_dword=5,
            native_low4_parameter_byte=9)
        self.assertEqual(restored,before)

    def test_unqualified_flag_record_and_subobject_inputs_fail_closed(self):
        for change in (
            {"source_flag14_dword":True},
            {"source_flag14_dword":-1},
            {"source_flag174_dword":0x100000000},
            {"starting_eleven":1},
            {"starting_eleven":None},
        ):
            inputs=dict(source_flag14_dword=0,source_flag174_dword=0,
                        starting_eleven=True)
            with self.subTest(change=change),self.assertRaises(
                SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_direct_status_stage_4182f0(
                    **(inputs|change))
        for record,subobject in (
            (b"X"*0x153,b"\x00"*5),
            (bytearray(b"X"*0x260),b"\x00"*5),
            (b"X"*0x260,b"\x00"*4),
            (b"X"*0x260,bytearray(b"\x00"*5)),
        ):
            with self.assertRaises(SourceFastViewPlayerWorldWritebackError):
                source_fastview_original_player_attribute_cache_swap_418220(
                    original_player_record_bytes=record,
                    original_player_subobject_bytes=subobject)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original owner EXE not mounted")
    def test_exact_original_native_status_cached_field_and_restore_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x418150:"8b 41 14",
            0x418153:"24 ef",
            0x418160:"8b 41 14",
            0x418163:"24 df",
            0x418170:"8b 81 74 01 00 00",
            0x418176:"24 fd",
            0x418183:"f6 86 74 01 00 00 01",
            0x41818C:"e8 8f 00 00 00",
            0x418197:"24 fe",
            0x418220:"51 53 56",
            0x418225:"8b 8e 48 02 00 00",
            0x41822B:"e8 90 21 0d 00",
            0x418238:"e8 93 21 0d 00",
            0x418249:"8a 86 52 01 00 00",
            0x418250:"e8 db 20 0d 00",
            0x418255:"8a 8e 53 01 00 00",
            0x418262:"e8 e9 20 0d 00",
            0x41826B:"88 9e 52 01 00 00",
            0x418271:"88 96 53 01 00 00",
            0x4182C3:"e8 88 fe ff ff",
            0x4182CD:"0c 20",
            0x4182D2:"e8 a9 fe ff ff",
            0x4182D9:"e8 92 fe ff ff",
            0x4182E4:"e8 87 20 0d 00",
            0x4182F3:"83 4e 14 10",
            0x4182F7:"e8 64 fe ff ff",
            0x4182FE:"e8 7d fe ff ff",
            0x418305:"e8 66 fe ff ff",
            0x41830C:"e8 2f f0 ff ff",
            0x418321:"e8 ca 6a 00 00",
            0x4EA370:"8a 41 03",
            0x4EA383:"24 f0",
            0x4EA385:"88 51 03",
            0x4EA388:"88 41 04",
        }
        for va,hx in sites.items():
            with self.subTest(source_va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),
                                 bytes.fromhex(hx))

if __name__=="__main__":
    unittest.main()
