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


if __name__=="__main__":
    unittest.main()
