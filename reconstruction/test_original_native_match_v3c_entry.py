"""Original LeagueMatch virtual+0x3C initial bit0 write, not a match."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack_into,unpack_from
import unittest

from original_leaguematch_native_process_owners import (
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    OriginalLeagueMatchProcessOwnerError,
)
from original_native_match_v3c_entry import (
    source_original_v3c_entry_bit0_write_511370,
    source_original_v38_then_v3c_zero_event_prefix,
)


class SourceV3CInitialEventBitTests(unittest.TestCase):
    def test_all_seven_original_vtables_start_common_v3c_bit0_before_downstream(self):
        for vt, owner in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                before=bytearray(bytes(range(80)))
                pack_into("<I",before,0,vt)
                pack_into("<I",before,0x44,0xA0000020)
                receipt=source_original_v3c_entry_bit0_write_511370(
                    original_native_match_record_at_v3c_entry=bytes(before))
                self.assertEqual(receipt.original_vtable_va,vt)
                self.assertEqual(receipt.native_virtual3c_owner_va,owner[4])
                self.assertTrue(receipt.native_common_511370_called)
                self.assertTrue(receipt.original_events_and_world_callbacks_outstanding)
                after=receipt.match_record_after_first_bit0_store
                self.assertEqual(unpack_from("<I",after,0x44)[0],0xA0000021)
                self.assertEqual(after[:0x44],before[:0x44])
                self.assertEqual(after[0x48:],before[0x48:])
                self.assertEqual(unpack_from("<I",before,0x44)[0],0xA0000020)

    def test_already_set_bit0_stays_set_and_never_clears_other_flags(self):
        for initial in (0,1,0xFFFFFFFF,0x20,0x10,0x80000000):
            before=bytearray(0x48)
            pack_into("<I",before,0,0x7C4CE4)
            pack_into("<I",before,0x44,initial)
            r=source_original_v3c_entry_bit0_write_511370(
                original_native_match_record_at_v3c_entry=bytes(before))
            self.assertEqual(unpack_from("<I",r.match_record_after_first_bit0_store,0x44)[0],
                             initial|1)

    def test_invalid_or_fictional_sources_rejected(self):
        source=bytearray(0x48)
        pack_into("<I",source,0,0x7C4C24)
        for item in (None,bytes(0x47),bytes(0x48),bytearray(source),
                     str(bytes(source)),b"",123,True):
            with self.subTest(item=str(type(item))):
                with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                    source_original_v3c_entry_bit0_write_511370(
                        original_native_match_record_at_v3c_entry=item)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_original_pe_v3c_wrappers_call_common_first_and_write_flag_bit0(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        signatures=(
            (0x5132A9,"ff 52 3c"),
            (0x511370,"55 8b ec 83 e4 f8"),
            (0x511381,"83 4f 44 01"),
            (0x5132EB,"e8 80 e0 ff ff"),
            (0x513703,"e8 68 dc ff ff"),
        )
        for addr,hx in signatures:
            with self.subTest(va=hex(addr)):
                expected=bytes.fromhex(hx)
                self.assertEqual(pe.read(addr,len(expected)),expected)


class SourceNativePostcallbacksZeroEventCompositionTests(unittest.TestCase):
    def context(self, first_event=0, second_event=0):
        buf=bytearray(0xD60)
        pack_into("<II",buf,0xD0C,first_event,second_event)
        # Original 0x5112A0 uses +0xD4C and +0xD50, not adjacent WORDs.
        pack_into("<H",buf,0xD4C,2)
        pack_into("<H",buf,0xD50,3)
        return bytes(buf)

    def test_all_seven_original_v38_classes_reach_exact_score_then_v3c_bit0_when_zero_event(self):
        for vt in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            with self.subTest(vtable=hex(vt)):
                match=bytearray(0x60)
                pack_into("<I",match,0,vt)
                pack_into("<HH",match,0x3C,99,99)
                pack_into("<I",match,0x44,0x20)
                result=source_original_v38_then_v3c_zero_event_prefix(
                    original_native_match_record_before_v38=bytes(match),
                    original_processing_context_after_match=self.context())
                after=result.native_v3c_first_flag.match_record_after_first_bit0_store
                self.assertEqual(unpack_from("<HH",after,0x3C),(2,3))
                self.assertEqual(unpack_from("<I",after,0x44)[0],0x21)
                self.assertTrue(result.native_v3c_first_flag.original_events_and_world_callbacks_outstanding)
                self.assertEqual(bytes(match)[0x48:],after[0x48:])

    def test_wrapped_v38_refuses_any_original_513570_nonzero_event_count(self):
        match=bytearray(0x60)
        pack_into("<I",match,0,0x7C9D9C)
        for first,second in ((1,0),(0,1),(1,1),(0xFFFFFFFF,0)):
            with self.subTest(first=first,second=second):
                with self.assertRaisesRegex(
                    OriginalLeagueMatchProcessOwnerError,"nonzero 513570"):
                    source_original_v38_then_v3c_zero_event_prefix(
                        original_native_match_record_before_v38=bytes(match),
                        original_processing_context_after_match=self.context(first,second))

    def test_direct_v38_has_no_513570_dependency_on_event_counters(self):
        match=bytearray(0x60)
        pack_into("<I",match,0,0x7C4C24)
        result=source_original_v38_then_v3c_zero_event_prefix(
            original_native_match_record_before_v38=bytes(match),
            original_processing_context_after_match=self.context(1,2))
        self.assertFalse(result.native_v38_score_latch.original_wrapped_513570_required)
        self.assertTrue(result.native_v3c_first_flag.original_events_and_world_callbacks_outstanding)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_original_zero_event_513570_fast_exit_opcodes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        signatures=(
            (0x513577,"8b 85 0c 0d 00 00"),
            (0x51357f,"85 c0"),
            (0x513583,"8b 8d 10 0d 00 00"),
            (0x513589,"85 c9"),
            (0x51358b,"0f 84 25 01 00 00"),
            (0x5136b6,"5f 5e 5d c2 04 00"),
        )
        for address,hx in signatures:
            with self.subTest(va=hex(address)):
                v=bytes.fromhex(hx)
                self.assertEqual(pe.read(address,len(v)),v)


if __name__=="__main__":
    unittest.main()
