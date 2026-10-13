"""Native original 0x616100 serialized event family versus final class vtable."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack
import unittest

from original_native_serialized_event_loader import (
    OriginalSerializedEventLoaderSourceError,
    SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH,
    SOURCE_ORIGINAL_LOADER_JUMP_TABLE_ENTRIES_2_TO_5,
    source_original_serialized_event_class_616100,
)
from original_leaguematch_native_process_owners import (
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
)


class OriginalNativeSerializedEventLoaderTests(unittest.TestCase):
    def test_source_0_to_6_class_dispatch_and_original_vtable_family(self):
        self.assertEqual(tuple(SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH),tuple(range(7)))
        for type_code,(size,ctor,vt,site) in SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH.items():
            with self.subTest(native_type=type_code):
                got=source_original_serialized_event_class_616100(
                    original_native_serialized_type_code=type_code)
                self.assertEqual((got.source_allocated_size_bytes,got.source_constructor_va,
                    got.source_final_vtable_va,got.source_call_site_va),(size,ctor,vt,site))
                self.assertEqual(got.source_is_league_match_vtable,type_code!=0)
                self.assertEqual(vt in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,type_code!=0)
        self.assertEqual(SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH[0],
                         (0x1C,0x510380,0x7C9FE8,0x6161A0))
        self.assertEqual(SOURCE_ORIGINAL_SERIALIZED_EVENT_CLASS_DISPATCH[6],
                         (0x50,0x5105D0,0x7C9E14,0x616265))

    def test_native_type_is_not_a_fixture_kind_and_unknown_loader_path_fails_closed(self):
        for val in (True,False,None,-1,7,99,0xFFFFFFFF,0x100000000,"2",2.0):
            with self.subTest(value=val),self.assertRaises(
                OriginalSerializedEventLoaderSourceError):
                source_original_serialized_event_class_616100(
                    original_native_serialized_type_code=val)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner original source not mounted for hosted CI")
    def test_private_original_loader_dispatch_native_sites_and_table(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x616145:"85 c0",
            0x6161F7:"83 f8 01",
            0x616235:"83 f8 06",
            0x6162A7:"8d 42 fe",
            0x6162AA:"83 f8 03",
            0x6162B3:"ff 24 85 d0 63 61 00",
            0x6161A0:"e8 db a1 ef ff",
            0x61622B:"e8 c0 a2 ef ff",
            0x6162F5:"e8 26 a2 ef ff",
            0x616332:"e8 c9 a2 ef ff",
            0x616369:"e8 d2 a2 ef ff",
            0x6163A1:"e8 da a2 ef ff",
            0x616265:"e8 66 a3 ef ff",
            0x6161AB:"c7 06 e8 9f 7c 00",
            0x51050E:"c7 06 24 4c 7c 00",
            0x51054D:"c7 06 9c 9d 7c 00",
            0x5105ED:"c7 06 14 9e 7c 00",
            0x510630:"c7 06 80 9e 7c 00",
            0x51066B:"c7 06 f8 9e 7c 00",
            0x5106B3:"c7 06 70 9f 7c 00",
        }
        for addr,hx in sites.items():
            with self.subTest(va=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))
        for n,va in enumerate(SOURCE_ORIGINAL_LOADER_JUMP_TABLE_ENTRIES_2_TO_5):
            self.assertEqual(pe.read(0x6163D0+4*n,4),pack("<I",va))


if __name__=="__main__":
    unittest.main()
