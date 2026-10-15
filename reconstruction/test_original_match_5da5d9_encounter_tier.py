"""Original 5DA5D9 encounter pointer and native tier constants."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_match_5da5d9_encounter_tier import (
    OriginalMatchEncounterSourceError,
    source_original_5da5d9_encounter_and_tier as resolve,
)


def evidence(*,alternate=0,first=1,second=1,encounter=12,shift=10):
    ctx=bytearray(0x50)
    pack_into('<I',ctx,0x4c,0x2000)
    primary=bytearray(0x40)
    pack_into('<I',primary,4,alternate)
    pack_into('<I',primary,0x3c,encounter)
    selectedptr=alternate if first==0 and alternate else 0x2000
    selected=bytearray(0x40)
    pack_into('<I',selected,4,alternate if selectedptr==0x2000 else 0)
    pack_into('<I',selected,0x3c,encounter)
    return dict(original_match_context_record=bytes(ctx),
        original_initial_encounter_pointer=0x2000,
        original_initial_encounter_record=bytes(primary),
        original_initial_encounter_v18_return_eax=first,
        original_selected_encounter_pointer=selectedptr,
        original_selected_encounter_record=bytes(selected),
        original_second_selected_v18_return_eax=second,
        original_match_context_v60_return_eax=shift if second else None)


class Original5DA5D9EncounterSourceTests(TestCase):
    def test_live_initial_encounter_chooses_differential_native_tier_constants(self):
        for diff,tier in ((2,30),(3,20),(4,15),(1,14),(0,14),(6,14)):
            r=resolve(**evidence(encounter=diff+10,shift=10))
            self.assertEqual((r.source_level_difference,r.original_source_tier_constant),(diff,tier))
            self.assertEqual(r.source_next_branch_va,0x5da5ff)
            self.assertFalse(r.source_fallback_plus4_selected)
            self.assertFalse(r.source_fpu_ratios_executed)
            self.assertFalse(r.game_state_updated)

    def test_dead_initial_encounter_with_alternate_selects_after_v18_other(self):
        r=resolve(**evidence(alternate=0x3000,first=0,second=1,encounter=24,shift=20))
        self.assertEqual(r.selected_encounter_pointer,0x3000)
        self.assertTrue(r.source_fallback_plus4_selected)
        self.assertEqual(r.original_source_tier_constant,15)
        r=resolve(**evidence(alternate=0x3000,first=0,second=0))
        self.assertEqual((r.source_next_branch_va,r.original_source_tier_constant),(0x5da746,None))
        self.assertFalse(r.original_selected_v18_alive)

    def test_missing_alternate_or_second_false_uses_actual_native_fallback(self):
        x=resolve(**evidence(alternate=0,first=0,second=0))
        self.assertEqual((x.selected_encounter_pointer,x.source_next_branch_va),(0x2000,0x5da746))
        with self.assertRaises(OriginalMatchEncounterSourceError):
            resolve(**(evidence(first=1,second=0)|{'original_match_context_v60_return_eax':1}))

    def test_original_unsigned_sub_wrap_stays_outside_known_tier_and_not_python_negative(self):
        r=resolve(**evidence(encounter=1,shift=2))
        self.assertEqual(r.source_level_difference,0xffffffff)
        self.assertEqual(r.original_source_tier_constant,14)

    def test_broken_original_pointer_and_unreached_context_v60_fail_closed(self):
        baseline=evidence()
        for change in (
            {'original_match_context_record':bytes(0x50)},
            {'original_match_context_record':b''},
            {'original_initial_encounter_pointer':0},
            {'original_selected_encounter_pointer':0},
            {'original_selected_encounter_pointer':0x3000},
            {'original_initial_encounter_record':bytes(2)},
            {'original_selected_encounter_record':b''},
            {'original_initial_encounter_v18_return_eax':False},
            {'original_second_selected_v18_return_eax':-1},
            {'original_match_context_v60_return_eax':None},
            {'original_match_context_v60_return_eax':True},
        ):
            with self.subTest(changed=change),self.assertRaises(OriginalMatchEncounterSourceError):
                resolve(**(baseline|change))

    def test_canonical_private_pe_stores_source_encounter_selection_and_tier_global(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable')
        b=Path(p).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        source={
            0x5da5d9:'8b 59 4c 8b cb 8b 13 ff 52 18',
            0x5da5e7:'8b 43 04 85 c0 74 02',
            0x5da5f0:'8b 03 8b cb ff 50 18 85 c0',
            0x5da5ff:'8b 4b 3c',
            0x5da60b:'ff 52 60',
            0x5da612:'2b c8 49 74 2f',
            0x5da617:'49 74 21',
            0x5da61a:'49 74 13',
            0x5da61d:'a1 90 10 82 00',
            0x5da630:'db 05 90 10 82 00',
            0x5da63b:'db 05 8c 10 82 00',
            0x5da646:'db 05 88 10 82 00',
            0x5da746:'8b 5d 08',
        }
        for va,h in source.items():
            with self.subTest(site=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)
        self.assertEqual(tuple(unpack_from('<I',b,va-0x400000)[0]
                               for va in (0x821088,0x82108c,0x821090,0x821094)),
                         (30,20,15,10))
