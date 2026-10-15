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


class Original4290F0PredicateSourceTests(TestCase):
    def _user_record(self, value):
        from struct import pack_into
        b=bytearray(0x10dc)
        pack_into('<I',b,0x10d8,value)
        return bytes(b)

    def test_source_5160a0_flag_causes_original_4290f0_early_exit_without_user_read(self):
        from original_postresults_432505_single_user_return import source_original_4290f0_return_from_reached
        r=source_original_4290f0_return_from_reached(
            original_global_87755a_byte_at_5160a0=1,
            original_current_user_record_at_429126=None,
            original_current_user_record_at_429424=None)
        self.assertEqual((r.original_4290f0_eax_result,r.original_4290f0_exit_va),(0,0x429125))
        self.assertFalse(r.native_intervening_callbacks_executed)
        with self.assertRaises(OriginalPostResultsReturnSourceError):
            source_original_4290f0_return_from_reached(
                original_global_87755a_byte_at_5160a0=1,
                original_current_user_record_at_429126=self._user_record(1),
                original_current_user_record_at_429424=None)

    def test_post_callback_native_user_state_controls_full_final_4290f0_eax(self):
        from original_postresults_432505_single_user_return import source_original_4290f0_return_from_reached
        for before,after,wanted in ((0,0,0),(0,1,1),(1,0,0),(1,5,1),(6,4,1)):
            with self.subTest(before=before,after=after):
                r=source_original_4290f0_return_from_reached(
                    original_global_87755a_byte_at_5160a0=0,
                    original_current_user_record_at_429126=self._user_record(before),
                    original_current_user_record_at_429424=self._user_record(after))
                self.assertEqual((r.original_4290f0_eax_result,r.original_4290f0_exit_va),
                                 (wanted,0x429441))
                self.assertFalse(r.original_gui_side_effects_proven)

    def test_actual_4290f0_join_wont_allow_independent_predicate_override(self):
        from original_postresults_432505_single_user_return import (
            source_original_4290f0_return_from_reached,
            source_original_432505_single_user_startmenu_from_4290f0,
        )
        before=self._user_record(1)
        real=source_original_4290f0_return_from_reached(
            original_global_87755a_byte_at_5160a0=0,
            original_current_user_record_at_429126=before,
            original_current_user_record_at_429424=before)
        data=inputs()
        data.pop('original_4290f0_eax_at_43254c')
        self.assertEqual(source_original_432505_single_user_startmenu_from_4290f0(
            source_4290f0=real,**data).original_branch_destination,0x4325df)
        with self.assertRaises(OriginalPostResultsReturnSourceError):
            source_original_432505_single_user_startmenu_from_4290f0(
                source_4290f0=real,**inputs())
        for wrong in (None,True,dict()):
            with self.assertRaises(OriginalPostResultsReturnSourceError):
                source_original_432505_single_user_startmenu_from_4290f0(
                    source_4290f0=wrong,**data)
        zero=source_original_4290f0_return_from_reached(
            original_global_87755a_byte_at_5160a0=1,
            original_current_user_record_at_429126=None,
            original_current_user_record_at_429424=None)
        with self.assertRaises(OriginalPostResultsReturnSourceError):
            source_original_432505_single_user_startmenu_from_4290f0(
                source_4290f0=zero,**data)

    def test_native_4290f0_function_source_sites(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical original private EXE not available')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5160a0:'a0 5a 75 87 00 c3',
            0x42910b:'e8 90 cf 0e 00 84 c0 74 12',
            0x429114:'33 c0 5e',
            0x429126:'8b 86 d8 10 00 00 57 85 c0',
            0x42918d:'8b 86 d8 10 00 00 48 83 f8 04',
            0x429424:'8b 8e d8 10 00 00 33 c0 85 c9',
            0x429433:'0f 95 c0',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        call=0x42910b
        self.assertEqual(call+5+unpack_from('<i',raw,call-0x400000+1)[0],0x5160a0)
