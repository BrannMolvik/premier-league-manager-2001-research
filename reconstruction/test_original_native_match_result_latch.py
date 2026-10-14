"""Native FM2001 LeagueMatch v38 score latch: source-only and fail-closed."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack_into, unpack_from
import unittest

from original_leaguematch_native_process_owners import (
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    OriginalLeagueMatchProcessOwnerError,
)
from original_native_match_result_latch import (
    source_original_native_match_v38_two_score_words_5112a0 as source_latch,
    SOURCE_ORIGINAL_MATCH_V38_WORD_COPY_VA,
    SOURCE_ORIGINAL_MATCH_V38_WRAPPED_VA,
)


class OriginalNativeMatchV38ScoreLatchTests(unittest.TestCase):
    def valid_input(self, vt=0x7C4C24, length=0x70, size=0xD60):
        match=bytearray((i*3+7)&0xFF for i in range(length))
        context=bytearray((i*7+5)&0xFF for i in range(size))
        pack_into("<I",match,0,vt)
        pack_into("<HH",match,0x3C,44,45)
        pack_into("<H",context,0xD4C,3)
        pack_into("<H",context,0xD50,1)
        return bytes(match),bytes(context)

    def test_every_native_vtable_routes_exact_first_second_score_words(self):
        for vt, owners in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                match,ctx=self.valid_input(vt)
                result=source_latch(
                    original_native_match_record_before_v38=match,
                    original_processing_context_after_match=ctx)
                self.assertEqual((result.first_score_word,result.second_score_word),(3,1))
                self.assertEqual(unpack_from("<HH",result.updated_match_record_after_two_word_stores,0x3C),(3,1))
                self.assertEqual(result.updated_match_record_after_two_word_stores[:0x3C],match[:0x3C])
                self.assertEqual(result.updated_match_record_after_two_word_stores[0x40:],match[0x40:])
                self.assertTrue(result.original_later_v3c_callback_required)
                self.assertEqual(result.original_wrapped_513570_required,owners[3]==SOURCE_ORIGINAL_MATCH_V38_WRAPPED_VA)
                self.assertEqual(result.original_v38_function,owners[3])

    def test_score_zero_and_65535_are_raw_source_words_not_ints_or_clamped(self):
        match,ctx=self.valid_input()
        ctx=bytearray(ctx)
        pack_into("<H",ctx,0xD4C,0)
        pack_into("<H",ctx,0xD50,65535)
        result=source_latch(
            original_native_match_record_before_v38=match,
            original_processing_context_after_match=bytes(ctx))
        self.assertEqual((result.first_score_word,result.second_score_word),(0,65535))

    def test_incomplete_or_invented_original_input_is_rejected(self):
        match,ctx=self.valid_input()
        for m,c in (
            (bytearray(match),ctx),
            (match,bytearray(ctx)),
            (match[:0x3F],ctx),
            (match,ctx[:0xD51]),
            (bytes(0x40),ctx),
            (None,ctx),
            (match,None),
        ):
            with self.subTest(match=m,ctxlen=len(c) if c is not None else None):
                with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                    source_latch(
                        original_native_match_record_before_v38=m,
                        original_processing_context_after_match=c)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original owner-private executable not mounted")
    def test_original_pe_byte_proof_v38_common_and_wrapped_score_copy(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        evidence=(
            (0x51329D,"ff 52 38"),
            (0x5132A9,"ff 52 3c"),
            (0x5112a0,"8b 44 24 04"),
            (0x5112a4,"66 8b 90 4c 0d 00 00"),
            (0x5112ab,"66 89 51 3c"),
            (0x5112af,"66 8b 80 50 0d 00 00"),
            (0x5112b6,"66 89 41 3e"),
            (0x5136c8,"57"),
            (0x5136c9,"e8 d2 db ff ff"),
            (0x5136cf,"8b ce"),
            (0x5136d1,"e8 9a fe ff ff"),
        )
        for address,hx in evidence:
            with self.subTest(va=hex(address)):
                expected=bytes.fromhex(hx)
                self.assertEqual(pe.read(address,len(expected)),expected)

if __name__=="__main__":
    unittest.main()
