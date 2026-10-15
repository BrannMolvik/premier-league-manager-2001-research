"""Original 40CBC0 native type1A first and second output lookups."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_40cbc0_type1a_pair import (
    OriginalMatch40CBC0SourceError,
    SOURCE_NATIVE_40CBC0_SUBSELECTOR_JUMP,
    source_original_40cbc0_team_type1a_output_pair as pair,
)


def case(category=0x1a,key=0x123456,selector=0):
    team=bytearray(0x18)
    pack_into('<I',team,0x10,key)
    pack_into('<I',team,0x14,category)
    return dict(original_team_pointer=0x4000,original_team_record=bytes(team),
                original_reached_4056d0_source_key_pointer=key,
                original_reached_4fa520_selector_dword=selector)


class OriginalMatch40CBC0Type1AOutputTests(TestCase):
    def test_all_five_source_enum_values_to_actual_two_qwords(self):
        for index,base in enumerate((30.,20.,16.,12.,9.)):
            got=pair(**case(selector=index))
            self.assertEqual(got.original_native_case_callsite,
                             SOURCE_NATIVE_40CBC0_SUBSELECTOR_JUMP[index])
            self.assertEqual(got.first_original_qword_output,base)
            self.assertEqual(got.second_original_qword_output,base*.75)
            self.assertFalse(got.original_4056d0_4fa520_callbacks_executed)
            self.assertFalse(got.original_native_40cbc0_executed)
            self.assertFalse(got.original_match_state_written)

    def test_reject_other_original_club_category_or_unreached_enum(self):
        for kind in (0x18,0x1f,0x21,0x28,0x42,0x49,0x50,0):
            with self.subTest(category=hex(kind)),self.assertRaises(OriginalMatch40CBC0SourceError):
                pair(**case(category=kind))
        for val in (-1,5,0xffffffff,None,True):
            with self.subTest(selector=val),self.assertRaises(OriginalMatch40CBC0SourceError):
                pair(**case(selector=val))

    def test_pointer_identity_and_corrupt_native_team_bytes_cannot_guess_scores(self):
        source=case()
        for changes in (
            {'original_team_pointer':0},
            {'original_team_pointer':False},
            {'original_reached_4056d0_source_key_pointer':0x123457},
            {'original_reached_4056d0_source_key_pointer':False},
            {'original_team_record':b''},
            {'original_team_record':bytearray(0x18)},
            {'original_team_record':bytes(0x18)},
        ):
            with self.subTest(changes=changes),self.assertRaises(OriginalMatch40CBC0SourceError):
                pair(**(source|changes))

    def test_original_pe_jumptable_and_two_outputs_are_genuine(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('owner-authorized original exe unavailable')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x40cbd4:'8b 47 14 83 c0 e8 83 f8 31',
            0x40cbe5:'8a 88 c0 cf 40 00',
            0x40cbeb:'ff 24 8d a0 cf 40 00',
            0x40cbf2:'8b 47 10',
            0x40cc0d:'e8 0e d9 0e 00',
            0x40cc14:'83 f8 04',
            0x40cc1d:'ff 24 85 f4 cf 40 00',
            0x40cc24:'dd 05 40 20 82 00',
            0x40cc34:'dc 0d 58 d5 7b 00',
            0x40cc45:'dd 05 50 20 82 00',
            0x40cc66:'dd 05 60 20 82 00',
            0x40cc87:'dd 05 70 20 82 00',
            0x40cca8:'dd 05 80 20 82 00',
        }
        for va,h in sites.items():
            with self.subTest(site=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
        self.assertEqual(tuple(unpack_from('<I',raw,0x40cff4-0x400000+4*i)[0]
                               for i in range(5)),SOURCE_NATIVE_40CBC0_SUBSELECTOR_JUMP)
        self.assertEqual(tuple(unpack_from('<d',raw,va-0x400000)[0] for va in
            (0x822040,0x822050,0x822060,0x822070,0x822080)),(30.,20.,16.,12.,9.))
        self.assertEqual(unpack_from('<d',raw,0x7bd558-0x400000)[0],.75)
        self.assertEqual(raw[0x40cfc0-0x400000+(0x1a-0x18)],1)
        call=0x40cc0d
        self.assertEqual(call+5+unpack_from('<i',raw,call-0x400000+1)[0],0x4fa520)
