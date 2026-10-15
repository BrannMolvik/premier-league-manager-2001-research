"""Source-only PResults PBg 432505 -> 4325DF guarded original StartMenu."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase
from original_postresults_432505_single_user_return import (
    OriginalPostResultsReturnSourceError,
    source_original_432505_single_user_startmenu_plan as plan,
)


def inputs():
    return dict(original_reached_post_presults_432505=True,
                original_global_date_9847fc=0x2000123,
                original_reached_user_pointer_4139d0=0x1000,
                original_875680_settings_owner_pointer=0,
                original_4290f0_eax_at_43254c=1,
                original_516010_al_at_432559=1,
                original_registered_manager_count_8755e4=1,
                original_413ac0_update_completed=True)


class OriginalPostResultsSingleUserTests(TestCase):
    def test_original_one_user_4325df_starts_real_pstartmenu_not_generic_management(self):
        r=plan(**inputs())
        self.assertEqual((r.original_branch_destination,r.original_start_menu_constructor_va),
                         (0x4325df,0x4c3280))
        self.assertEqual(r.original_875614_zero_store_va,0x4325df)
        self.assertFalse(r.live_game_state_modified)
        self.assertFalse(r.native_original_process_executed)
        self.assertFalse(r.windows11_gui_accepted)

    def test_sibling_native_return_paths_must_not_be_promoted_to_startmenu(self):
        base=inputs()
        cases=[
            {'original_reached_post_presults_432505':False},
            {'original_reached_post_presults_432505':0},
            {'original_413ac0_update_completed':False},
            {'original_reached_user_pointer_4139d0':0},
            {'original_875680_settings_owner_pointer':0x7000},
            {'original_4290f0_eax_at_43254c':0},
            {'original_516010_al_at_432559':0},
            {'original_registered_manager_count_8755e4':2},
            {'original_registered_manager_count_8755e4':0},
            {'original_global_date_9847fc':-1},
            {'original_4290f0_eax_at_43254c':True},
            {'original_4290f0_eax_at_43254c':0x100000000},
            {'original_516010_al_at_432559':256},
            {'original_registered_manager_count_8755e4':True},
        ]
        for change in cases:
            with self.subTest(change=change),self.assertRaises(OriginalPostResultsReturnSourceError):
                plan(**(base|change))

    def test_original_4290f0_returns_full_eax_not_al(self):
        self.assertEqual(plan(**(inputs() | {'original_4290f0_eax_at_43254c':0x100})).original_branch_destination,0x4325df)

    def test_original_pe_native_return_pbg_432505_guards_and_startmenu_call(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE not available in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x432505:'a1 fc 47 98 00',
            0x432522:'b9 10 4c 87 00',
            0x432527:'e8 94 15 fe ff',
            0x43252c:'a1 80 56 87 00',
            0x432535:'0f 85 bc 00 00 00',
            0x432540:'e8 8b 14 fe ff',
            0x432547:'e8 a4 6b ff ff',
            0x432554:'e8 b7 3a 0e 00',
            0x432561:'83 3d e4 55 87 00 01',
            0x432568:'7e 75',
            0x4325df:'89 35 14 56 87 00 e8 96 0c 09 00',
            0x516010:'a0 6e 85 82 00 c3',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bytes.fromhex(h))],
                                 bytes.fromhex(h))
        for site,target in ((0x432527,0x413ac0),(0x432540,0x4139d0),
                            (0x432547,0x4290f0),(0x432554,0x516010),
                            (0x4325e5,0x4c3280)):
            i=site-0x400000
            self.assertEqual(raw[i],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,i+1)[0],target)
