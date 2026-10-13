"""Auth original 0x875644 global player registry record mapping tests, not GUI."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into,unpack_from
import unittest

from original_fastview_native_player_registry import (
    SourceFastViewOriginalPlayerRegistry,
    SourceFastViewOriginalPlayerRegistryError,
    source_fastview_original_player_registry_get_416f90,
    source_fastview_original_pre_modal_registry_refs_533bf0,
    source_fastview_original_pre_modal_registry_capture_533bf0,
    source_fastview_original_post_modal_registry_intents_533ca0,
)
from original_fastview_two_sided_live_writeback import SourceFastViewTwoSideBlockState


def authentic_shape_fixture():
    # Synthetic data ONLY; original byte layout is independently PE-proven.
    pool=bytearray(0x250*32)
    pointer_targets={}
    for i in range(32):
        at=0x250*i
        pack_into("<I",pool,at+0x04,0xABC000+i)
        pack_into("<I",pool,at+0x248,0x10000000+i*0x20)
        pointer_targets[0x10000000+i*0x20]=bytes(
            (i,0,0,0xE0|(i&0x1F),0xF0|(i&0x0F)))
    registry=SourceFastViewOriginalPlayerRegistry(
        original_native_registered_count_dword=32,
        original_record_array_bytes=bytes(pool))
    left=bytearray(b"L"*0x300)
    right=bytearray(b"R"*0x300)
    left_ids=tuple(range(2,14))
    right_ids=tuple(range(13,24))
    for club,ids in ((left,left_ids),(right,right_ids)):
        pack_into("<I",club,0x294,len(ids))
        for k,pid in enumerate(ids):
            pack_into("<H",club,0x244+2*k,pid)
    return registry,SourceFastViewTwoSideBlockState(bytes(left),bytes(right)),pointer_targets,left_ids,right_ids


class OriginalPlayerRegistrySourceIdentityTests(unittest.TestCase):
    def test_original_vtable0_id_mul_592_maps_exact_raw_record_not_other_ordinal(self):
        r,sides,pointers,li,ri=authentic_shape_fixture()
        self.assertEqual(len(r.original_record_array_bytes),32*592)
        for pid in (0,1,2,13,31):
            got=source_fastview_original_player_registry_get_416f90(
                source_registry=r,original_player_id_word=pid)
            self.assertEqual(got.original_player_id_word,pid)
            self.assertEqual(len(got.source_player_record_592),0x250)
            self.assertEqual(unpack_from("<I",got.source_player_record_592,4)[0],0xABC000+pid)
            self.assertEqual(got.source_native_subobject_pointer_dword,
                             0x10000000+pid*0x20)
        self.assertEqual(source_fastview_original_player_registry_get_416f90(
            source_registry=r,original_player_id_word=13
        ).source_player_record_592, r.original_record_array_bytes[13*0x250:14*0x250])

    def test_pre_533bf0_club_count_and_16bit_ids_to_source_world_records(self):
        r,sides,pointers,left_ids,right_ids=authentic_shape_fixture()
        refs=source_fastview_original_pre_modal_registry_refs_533bf0(
            original_club_sides_before_modal=sides,source_registry=r)
        self.assertEqual(len(refs),(2))
        self.assertEqual(tuple(x.original_player_id_word for x in refs[0]),left_ids)
        self.assertEqual(tuple(x.original_player_id_word for x in refs[1]),right_ids)
        self.assertEqual(refs[0][0].ordinal,0)
        self.assertEqual(refs[1][-1].ordinal,10)
        self.assertEqual(refs[1][-1].source_native_subobject_pointer_dword,
                         0x10000000+23*0x20)
        self.assertEqual(refs[0][-1].source_player_record_592,refs[1][0].source_player_record_592)

    def test_pointer_qualified_pre_modal_low5_low4_glob_capture_keeps_other_bytes(self):
        r,sides,pointers,left_ids,right_ids=authentic_shape_fixture()
        before5=b"\xAA"*320
        before4=b"\xBB"*320
        cap=source_fastview_original_pre_modal_registry_capture_533bf0(
            original_club_sides_before_modal=sides,source_registry=r,
            original_subobject_bytes_by_native_pointer=pointers,
            original_low5_globals_before=before5,original_low4_globals_before=before4)
        for side,ids in enumerate((left_ids,right_ids)):
            for k,pid in enumerate(ids):
                off=side*0xA0+4*k
                self.assertEqual(unpack_from("<I",cap.original_low5_globals_320,off)[0],pid&31)
                self.assertEqual(unpack_from("<I",cap.original_low4_globals_320,off)[0],pid&15)
        self.assertEqual(cap.original_low5_globals_320[12*4:12*4+8],b"\xAA"*8)
        self.assertEqual(cap.original_low4_globals_320[0xA0+11*4:0xA0+11*4+8],b"\xBB"*8)
        self.assertEqual(before5,b"\xAA"*320)
        self.assertEqual(before4,b"\xBB"*320)

    def test_post_533ca0_resolves_modified_club_id_blocks_with_real_source_592_record(self):
        r,sides,pointers,left_ids,right_ids=authentic_shape_fixture()
        match=bytearray(0xB58)
        pack_into("<I",match,0x5A4,12)
        pack_into("<I",match,0xB54,11)
        # Actual modal can change club+0x244 BEFORE native 533CA0 ID resolution.
        changed=bytearray(sides.first_side_bytes)
        pack_into("<H",changed,0x244,25)
        after=SourceFastViewTwoSideBlockState(bytes(changed),sides.second_side_bytes)
        gl5=bytearray(bytes(320));gl4=bytearray(bytes(320))
        for side,count in ((0,12),(1,11)):
            for k in range(count):
                off=side*0xA0+4*k
                pack_into("<I",gl5,off,0x10000+side*100+k)
                gl4[off]=0xA0+side*16+k
        records=source_fastview_original_post_modal_registry_intents_533ca0(
            original_club_sides_after_modal=after,
            original_match_object=bytes(match),source_registry=r,
            global_player_low5_dwords=bytes(gl5),global_player_low4_dwords=bytes(gl4))
        self.assertEqual(len(records),23)
        self.assertEqual(records[0].source_native_player_intent.source_player_id_word,25)
        self.assertEqual(records[0].source_native_subobject_pointer_dword,
                         0x10000000+25*0x20)
        self.assertEqual(records[11].source_native_player_intent.native_player_branch_va,0x4182C0)
        self.assertEqual(records[12].source_native_player_intent.native_player_branch_va,0x4182F0)
        self.assertEqual(records[0].source_native_player_intent.original_low5_parameter_dword,0x10000)
        self.assertEqual(records[12].source_native_player_intent.original_low4_parameter_byte,0xB0)
        self.assertEqual(records[12].source_player_record_592_before_write,
                         r.original_record_array_bytes[13*0x250:14*0x250])
        self.assertEqual(after.first_side_bytes[0x244:0x246],bytes((25,0)))

    def test_invalid_native_registry_source_and_nonexistent_or_null_pointer_fails_closed(self):
        r,sides,pointers,li,ri=authentic_shape_fixture()
        for kwargs in (
            dict(original_native_registered_count_dword=-1,original_record_array_bytes=bytes()),
            dict(original_native_registered_count_dword=2,original_record_array_bytes=bytes(591*2)),
            dict(original_native_registered_count_dword=True,original_record_array_bytes=bytes(592)),
            dict(original_native_registered_count_dword=1,original_record_array_bytes=bytearray(592)),
        ):
            with self.subTest(args=repr(kwargs)[:80]),self.assertRaises(SourceFastViewOriginalPlayerRegistryError):
                SourceFastViewOriginalPlayerRegistry(**kwargs)
        for value in (True,-1,32,65536,None):
            with self.subTest(native_id=value),self.assertRaises(SourceFastViewOriginalPlayerRegistryError):
                source_fastview_original_player_registry_get_416f90(source_registry=r,original_player_id_word=value)
        for change in ({'original_subobject_bytes_by_native_pointer':{}},
                       {'original_subobject_bytes_by_native_pointer':{0:bytes(5)}},
                       {'original_subobject_bytes_by_native_pointer':pointers|{1:bytearray(5)}},
                       {'original_subobject_bytes_by_native_pointer':pointers|{True:bytes(5)}},
                       {'original_subobject_bytes_by_native_pointer':pointers|{1:bytes(4)}}):
            with self.subTest(change=str(change)[:45]),self.assertRaises(SourceFastViewOriginalPlayerRegistryError):
                source_fastview_original_pre_modal_registry_capture_533bf0(
                    **(dict(original_club_sides_before_modal=sides,source_registry=r,
                            original_subobject_bytes_by_native_pointer=pointers,
                            original_low5_globals_before=bytes(320),
                            original_low4_globals_before=bytes(320))|change))
        bad=bytearray(r.original_record_array_bytes)
        pack_into("<I",bad,2*0x250+0x248,0)
        with self.assertRaises(SourceFastViewOriginalPlayerRegistryError):
            source_fastview_original_pre_modal_registry_refs_533bf0(
                original_club_sides_before_modal=sides,
                source_registry=SourceFastViewOriginalPlayerRegistry(
                    32,bytes(bad)))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private owner original executable not mounted")
    def test_original_registry_ctor_vtable_stride_and_fv_getter_pe_opcode_proof(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x416f60:"33 c0",
            0x416f62:"c7 05 38 56 87 00 78 da 7b 00",
            0x416f6c:"a3 3c 56 87 00",
            0x416f71:"a3 40 56 87 00",
            0x416f76:"c7 05 44 56 87 00 38 56 87 00",
            0x416f90:"8b 44 24 04",
            0x416f94:"8d 14 c0",
            0x416f97:"8d 04 90",
            0x416f9a:"8b 51 08",
            0x416f9d:"c1 e0 04",
            0x416fa0:"03 c2",
            0x416fb0:"b8 50 02 00 00",
            0x416fd8:"8b f9",
            0x416fda:"8b 77 04",
            0x416fe0:"8d 0c 86",
            0x416fe3:"c1 e1 04",
            0x417011:"68 50 02 00 00",
            0x417017:"89 30",
            0x41701e:"89 5f 08",
            0x533c38:"8b 0d 44 56 87 00",
            0x533c46:"ff 12",
            0x533c48:"8b 88 48 02 00 00",
            0x533d00:"8b 0d 44 56 87 00",
            0x533d12:"ff 12",
            0x533d34:"8b b0 48 02 00 00",
            0x7bda78:"90 6f 41 00",
        }
        for va,hx in samples.items():
            with self.subTest(address=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
