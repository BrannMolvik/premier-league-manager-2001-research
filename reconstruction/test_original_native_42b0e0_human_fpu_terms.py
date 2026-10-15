"""Native original 42B0E0 owner and three independently present FPU terms."""
from hashlib import sha256
from itertools import product
from os import environ
from pathlib import Path
from struct import pack_into, pack
from unittest import TestCase
from original_native_42b0e0_human_fpu_terms import (
    Original42B0E0HumanModifierError,source_original_42b0e0_human_modifier_terms,
)

def fixture(mask=(True,True,True),values=(0,9,0xffffffff)):
    user=bytearray(0x660)
    pack_into('<I',user,0x65c,0x20000)
    return dict(original_selected_user_pointer=0x10000,
                original_selected_user_record_at_entry=bytes(user),
                original_5ee9a0_presence_for_options_1_4_6=mask,
                original_5eeb10_eax_for_present_options_1_4_6=tuple(v if b else None for b,v in zip(mask,values)))

class SourceOriginal42B0E0HumanTermsTests(TestCase):
    def test_all_eight_option_presence_masks_have_exact_independent_terms(self):
        for mask in product((False,True),repeat=3):
            with self.subTest(mask=mask):
                out=source_original_42b0e0_human_modifier_terms(**fixture(mask))
                self.assertEqual(out.original_source_option_owner_65c_pointer,0x20000)
                self.assertEqual(tuple(t.original_source_option_id for t in out.original_terms),(1,4,6))
                self.assertEqual(tuple(t.original_5ee9a0_present for t in out.original_terms),mask)
                self.assertEqual(tuple(t.native_signed_increment_if_present for t in out.original_terms),tuple(x if p else None for x,p in zip((1,10,0),mask)))
                self.assertEqual(tuple(t.original_source_qword_coefficient for t in out.original_terms),tuple(pack('<d',x) for x in (0.08,0.04,0.05)))
                self.assertEqual(out.original_literal_base_0p9_qword,pack('<d',0.9))
                self.assertFalse(out.original_x87_result_computed)

    def test_missing_owner_wrong_predicate_and_unreached_value_fail_closed(self):
        original=fixture()
        bad_user=bytearray(original['original_selected_user_record_at_entry']);pack_into('<I',bad_user,0x65c,0)
        for change in (
            {'original_selected_user_pointer':0},
            {'original_selected_user_pointer':True},
            {'original_selected_user_record_at_entry':bytes(bad_user)},
            {'original_selected_user_record_at_entry':b''},
            {'original_5ee9a0_presence_for_options_1_4_6':(1,True,False)},
            {'original_5eeb10_eax_for_present_options_1_4_6':(-1,9,1)},
            {'original_5ee9a0_presence_for_options_1_4_6':(False,True,True)},
        ):
            with self.subTest(change=change):
                with self.assertRaises(Original42B0E0HumanModifierError):
                    source_original_42b0e0_human_modifier_terms(**(original|change))

    def test_private_original_four_stage_modifier_call_chain(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical proprietary executable not available in CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
                         (4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        # Each source sequence:
        # call 4037B0; test human gate; skip-if-not-human +0x14;
        # mov ecx,esi; call 403850; mov ecx,eax;
        # call 42B0E0; fmul stage stack QWORD; skip; fld same QWORD.
        # Source continuity only, NOT proof of a live GameState match.
        prefixes=(
            (0x5dab30,'e8 7b 8c e2 ff 84 c0 74 14 8b ce e8 10 8d e2 ff 8b c8 e8 99 05 e5 ff dc 4c 24 60 eb 04 dd 44 24 60'),
            (0x5dadb0,'e8 fb 89 e2 ff 84 c0 74 14 8b ce e8 90 8a e2 ff 8b c8 e8 19 03 e5 ff dc 4c 24 58 eb 04 dd 44 24 58'),
            (0x5db02c,'e8 7f 87 e2 ff 84 c0 74 14 8b ce e8 14 88 e2 ff 8b c8 e8 9d 00 e5 ff dc 4c 24 68 eb 04 dd 44 24 68'),
            (0x5db2ac,'e8 ff 84 e2 ff 84 c0 74 14 8b ce e8 94 85 e2 ff 8b c8 e8 1d fe e4 ff dc 4c 24 50 eb 04 dd 44 24 50'),
        )
        for va,sequence in prefixes:
            with self.subTest(stage=hex(va)):
                want=bytes.fromhex(sequence)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(want)],want)

    def test_private_original_pe_three_options_and_weights(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical proprietary executable not available in CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        for addr,coeff in ((0x822520,0.08),(0x822528,0.04),(0x822530,0.05),(0x7bdd98,0.9)):
            self.assertEqual(raw[addr-0x400000:addr-0x400000+8],pack('<d',coeff))
        sig={0x42b0f0:'8b 8e 5c 06 00 00',0x42b0fe:'e8 9d 38 1c 00',0x42b10f:'e8 fc 39 1c 00',0x42b11d:'dc 0d 20 25 82 00',0x42b123:'dc 05 98 dd 7b 00',0x42b133:'6a 04',0x42b146:'e8 c5 39 1c 00',0x42b154:'dc 0d 28 25 82 00',0x42b168:'6a 06',0x42b17b:'e8 90 39 1c 00',0x42b18a:'dc 0d 30 25 82 00'}
        for a,seq in sig.items():
            with self.subTest(va=hex(a)):
                want=bytes.fromhex(seq)
                self.assertEqual(raw[a-0x400000:a-0x400000+len(want)],want)
