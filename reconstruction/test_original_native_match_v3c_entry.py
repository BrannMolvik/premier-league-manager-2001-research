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

if __name__=="__main__":
    unittest.main()
