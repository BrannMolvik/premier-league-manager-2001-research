"""Original 4325F7/43261F PMenu return and registered-user rotation."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase
from original_postresults_4325f7_pmenu_return import (
    OriginalPBgReturnSourceError,source_original_4325f7_pmenu_return as route,
)


def base():
    return dict(original_4325f7_source_reached=True,original_local_byte_esp12=0,
                original_local_dword_esp14=None,
                original_875680_settings_owner_pointer=0,
                original_8755d4_current_registered_ordinal=None,
                original_8755e4_registered_user_count=None)


class OriginalPostResultsPMenuTests(TestCase):
    def test_zero_branch_resets_manager_ordinal_and_builds_real_pmenu(self):
        r=route(**base())
        self.assertEqual((r.original_return_branch,r.original_native_selected_manager_8755d4_after,
                          r.original_source_pmenu_args),(0x4325f7,0,(1,0,1)))
        self.assertTrue(r.original_4a9e20_cleanup_reached)
        self.assertFalse(r.game_state_mutated)
        b=route(**(base()|{'original_875680_settings_owner_pointer':0x12345}))
        self.assertFalse(b.original_4a9e20_cleanup_reached)
        self.assertEqual(b.original_native_selected_manager_8755d4_after,0)

    def test_source_byte_nonzero_unqualified_mode_returns_without_creating_menu(self):
        for k in (0,1,3,0xffffffff):
            r=route(**(base()|{'original_local_byte_esp12':1,
                                'original_local_dword_esp14':k}))
            self.assertEqual((r.original_return_branch,r.original_source_pmenu_args,
                              r.original_native_selected_manager_8755d4_after),
                             (0x43261f,None,None))
            self.assertFalse(r.original_active_876760_disposal_may_be_reached)

    def test_native_two_to_six_registered_user_selection_wraps_exactly(self):
        for n in range(2,7):
            for old in range(n):
                r=route(**(base()|{
                    'original_local_byte_esp12':255,
                    'original_local_dword_esp14':2,
                    'original_8755d4_current_registered_ordinal':old,
                    'original_8755e4_registered_user_count':n,
                }))
                self.assertEqual(r.original_native_selected_manager_8755d4_after,(old+1)%n)
                self.assertEqual(r.original_source_pmenu_args,(1,1,1))
                self.assertTrue(r.original_active_876760_disposal_may_be_reached)
                self.assertFalse(r.game_state_mutated)

    def test_source_fails_closed_out_of_bounds_negative_and_bypassed_fields(self):
        good=base()
        for bad in (
             {'original_4325f7_source_reached':False},
             {'original_4325f7_source_reached':1},
             {'original_local_byte_esp12':True},
             {'original_local_byte_esp12':256},
             {'original_local_dword_esp14':2},
             {'original_8755d4_current_registered_ordinal':0},
             {'original_875680_settings_owner_pointer':-1},
        ):
            with self.subTest(case=bad),self.assertRaises(OriginalPBgReturnSourceError):
                route(**(good|bad))
        reached=(good|{'original_local_byte_esp12':1,
                       'original_local_dword_esp14':2,
                       'original_8755d4_current_registered_ordinal':1,
                       'original_8755e4_registered_user_count':2})
        for bad in ({'original_8755d4_current_registered_ordinal':2},
                    {'original_8755d4_current_registered_ordinal':-1},
                    {'original_8755d4_current_registered_ordinal':0x7fffffff},
                    {'original_8755e4_registered_user_count':0},
                    {'original_8755e4_registered_user_count':False},
                    {'original_8755e4_registered_user_count':-1}):
            with self.subTest(case=bad),self.assertRaises(OriginalPBgReturnSourceError):
                route(**(reached|bad))

    def test_private_original_pbg_post_return_mode_flag_rotation_and_pmenu_calls(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE required')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        source={
            0x4325f7:'8a 44 24 12 84 c0 75 20',
            0x4325ff:'39 35 80 56 87 00',
            0x432607:'8b 44 24 20 50 e8 0f 78 07 00',
            0x432614:'6a 01 89 35 d4 55 87 00 56 eb 54',
            0x43261f:'83 7c 24 14 02 75 57',
            0x432626:'a1 d4 55 87 00 40 99',
            0x43262d:'f7 3d e4 55 87 00',
            0x432639:'89 15 d4 55 87 00',
            0x43266f:'6a 01 6a 01',
            0x432673:'6a 01 e8 36 09 09 00',
        }
        for va,h in source.items():
            with self.subTest(va=hex(va)):
                data=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(data)],data)
        for site,target in ((0x43260c,0x4a9e20),(0x432675,0x4c2fb0)):
            loc=site-0x400000
            self.assertEqual(raw[loc],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,loc+1)[0],target)


    def test_native_432333_rotation_prebranch_rejects_last_registered_manager(self):
        from original_postresults_4325f7_pmenu_return import (
            source_original_432333_native_rotation_prebranch as before)
        for n in range(2,7):
            for old in range(n-1):
                r=before(original_8755d4_before_43231a=old,
                         original_8755e4_count_before_43231f=n)
                self.assertEqual((r.original_local_esp12_byte_at_43232e,
                                  r.original_local_esp14_dword_at_432333,
                                  r.original_next_432505),(1,2,0x432505))
                self.assertFalse(r.native_413ac0_mutations_after_source_test_ruled_out)
            with self.assertRaises(OriginalPBgReturnSourceError):
                before(original_8755d4_before_43231a=n-1,
                       original_8755e4_count_before_43231f=n)
        for old,n in ((0,1),(1,1),(0,0),(-1,5),(0x7fffffff,5),
                      (True,2),(0,False)):
            with self.subTest(old=old,count=n),self.assertRaises(OriginalPBgReturnSourceError):
                before(original_8755d4_before_43231a=old,
                       original_8755e4_count_before_43231f=n)

    def test_original_source_43231a_selection_and_state2_local_writes(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE required')
        raw=Path(p).read_bytes()
        sites={
           0x43231a:'a1 d4 55 87 00 8b 0d e4 55 87 00 40',
           0x432326:'3b c1',
           0x432328:'0f 8d d0 01 00 00',
           0x43232e:'c6 44 24 12 01',
           0x432333:'c7 44 24 14 02 00 00 00',
           0x43233b:'e9 c5 01 00 00',
           0x4324fe:'8b cd e8 6b fa ff ff',
        }
        for site,hexbytes in sites.items():
            with self.subTest(va=hex(site)):
                data=bytes.fromhex(hexbytes)
                self.assertEqual(raw[site-0x400000:site-0x400000+len(data)],data)
