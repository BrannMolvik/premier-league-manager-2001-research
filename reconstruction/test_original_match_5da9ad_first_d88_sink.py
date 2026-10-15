"""Original 5DA9AD first scored-stage match context+D88 writeback."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack,pack_into,unpack_from,unpack
from unittest import TestCase
from original_match_40cbc0_5e48d0_b_join import OriginalScoredStageFreshCallbackSource as Stage
from original_match_5da2f0_team_inputs import OriginalMatch4037B0TeamOwner as Membership
from original_match_5da9ad_first_d88_sink import (
    OriginalFirstStageD88SourceError,
    source_original_5da9ad_first_stage_d88 as source,
)


def inputs(*,human=False,coefficient=30.,existing=105):
    context=bytes(0xd8c)
    stage=Stage(
        1,'40cbc0-ebp8-first',0x5da987,0x5da995,
        pack('<d',coefficient),pack('<d',0.),pack('<d',1.),
        pack('<d',coefficient),0x5da9ad,human)
    userptr=0x3000 if human else None
    membership=Membership(0x1000,17,(0x3000,) if human else (),
                          userptr,int(human))
    kw=dict(original_stage1_5e48d0=stage,
            original_4037b0_registered_club=membership,
            original_context_pointer_from_ebp0c=0x9000,
            original_context_record_before_d88=context,
            original_actual_registered_user_pointer_if_human=None,
            original_reached_user_694_owner_pointer_if_human=None,
            original_reached_user_694_owner_record_if_human=None,
            original_reached_user_record_if_human=None)
    if human:
        user=bytearray(0x698)
        pack_into('<I',user,0x694,0x4000)
        owner=bytearray(0x10)
        pack_into('<i',owner,0xc,existing)
        kw.update(original_actual_registered_user_pointer_if_human=userptr,
                  original_reached_user_694_owner_pointer_if_human=0x4000,
                  original_reached_user_694_owner_record_if_human=bytes(owner),
                  original_reached_user_record_if_human=bytes(user))
    return kw


class OriginalFirstScoredStageD88Tests(TestCase):
    def test_original_nonhuman_qword_factor_truncates_into_context_d88(self):
        for score,want in ((30.,30),(20.75,20),(-1.9,-1),(0.0,0)):
            got=source(**inputs(coefficient=score))
            self.assertEqual(got.original_context_d88_signed_int,want)
            self.assertEqual(got.original_d88_store_va,0x5daa05)
            self.assertIsNone(got.original_human_difference_stack30_qword)
            self.assertFalse(got.original_store_executed)
            self.assertFalse(got.game_state_modified)

    def test_human_score_uses_reached_user_694_plus0c_unmodified(self):
        for before,factor,expected in ((100,30.,70.),(-15,10.,-25.),(0,0.,0.)):
            with self.subTest(before=before):
                x=source(**inputs(human=True,existing=before,coefficient=factor))
                self.assertEqual(x.original_context_d88_signed_int,before)
                self.assertEqual(unpack('<d',x.original_human_difference_stack30_qword)[0],expected)
                self.assertEqual(x.original_d88_store_va,0x5da9e4)
                self.assertFalse(x.original_store_executed)

    def test_source_rejects_unreached_registered_owner_alias_or_bad_inputs(self):
        good=inputs(human=True)
        cases=[
            {'original_actual_registered_user_pointer_if_human':0x3001},
            {'original_reached_user_694_owner_pointer_if_human':0x4001},
            {'original_reached_user_694_owner_record_if_human':bytes(10)},
            {'original_reached_user_record_if_human':bytes(0x698)},
            {'original_reached_user_record_if_human':bytes(100)},
            {'original_stage1_5e48d0':None},
            {'original_4037b0_registered_club':None},
            {'original_context_record_before_d88':bytes(0xd88)},
            {'original_context_pointer_from_ebp0c':True},
        ]
        for changed in cases:
            with self.subTest(changed=changed),self.assertRaises(OriginalFirstStageD88SourceError):
                source(**(good|changed))
        with self.assertRaises(OriginalFirstStageD88SourceError):
            source(**(inputs()|{'original_actual_registered_user_pointer_if_human':0x3000}))

    def test_source_callback_qword_must_be_safe_native_int32_for_both_paths(self):
        for score in (float('inf'),float('nan'),2147483648.,-2147483648.):
            for human in (False,True):
                with self.subTest(score=score,human=human),self.assertRaises(OriginalFirstStageD88SourceError):
                    source(**inputs(human=human,coefficient=score))

    def test_canonical_original_pe_source_qword_and_managed_unmanaged_context_write_sites(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('owner-private shipped original PE unavailable')
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
          0x5da9a1:'e8 0a 9a 00 00',
          0x5da9a8:'e8 23 9f 00 00',
          0x5da9ad:'dd 5c 24 38',
          0x5da9b3:'e8 f8 8d e2 ff',
          0x5da9bc:'8b ce e8 8d 8e e2 ff',
          0x5da9c3:'8b 80 94 06 00 00',
          0x5da9cb:'db 40 0c',
          0x5da9ce:'dc 64 24 38',
          0x5da9e1:'8b 50 0c',
          0x5da9e4:'89 97 88 0d 00 00',
          0x5da9ec:'dd 44 24 38',
          0x5daa00:'e8 4b d9 08 00',
          0x5daa05:'89 87 88 0d 00 00',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                x=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(x)],x)
