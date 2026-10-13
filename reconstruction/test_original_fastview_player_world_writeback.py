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


if __name__=="__main__":
    unittest.main()
