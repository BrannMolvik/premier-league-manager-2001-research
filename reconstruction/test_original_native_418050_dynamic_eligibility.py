"""Original 418050 & 409C90 non-class2/3 per-player availability source tests."""
import os
import unittest
from hashlib import sha256
from pathlib import Path
from struct import pack_into
from original_native_418050_dynamic_eligibility import (
    Original418050SourceError,
    source_original_418050_reached_availability as eligibility,
)


def native_player(*, pid=51,club=7,flags14=0,flags174=0):
    raw=bytearray(0x24c)
    pack_into("<H",raw,4,pid)
    pack_into("<h",raw,0x10,club)
    pack_into("<I",raw,0x14,flags14)
    pack_into("<I",raw,0x174,flags174)
    return bytes(raw)


def original_owner(type34):
    raw=bytearray(0x38)
    pack_into("<I",raw,0x34,type34)
    return bytes(raw)


class Original418050EligibilitySourceTests(unittest.TestCase):
    def project(self,p=None,**kw):
        if p is None:
            p=native_player()
        d=dict(
            original_player_record_at_418050=p,
            original_club_key_dword_arg1=7,
            original_dynamic_owner_ptr_arg2=0,
            original_player_record_at_reached_41b490=p,
        )
        d.update(kw)
        return eligibility(**d)

    def test_baseline_original_low_three_flags_and_full_signed_club_key(self):
        for club,flags,expect in ((7,0,False),(7,1,True),(7,7,True),
                                  (8,0,True),(-1,0,False)):
            with self.subTest(club=club,flags=flags):
                expected=expect if club!=-1 else True
                p=native_player(club=club,flags14=flags)
                d={"original_club_key_dword_arg1":0xffffffff} if club==-1 else {}
                r=self.project(p,**d)
                self.assertEqual(r.original_source_return_al_nonzero,
                                 bool(flags&7 or (club&0xffffffff)!=d.get("original_club_key_dword_arg1",7)))
                self.assertEqual(r.original_reached_call_sites,(0x41B490,))
                self.assertFalse(r.native_418050_executed)

    def test_nonzero_owner_calls_41b360_even_when_bit8_zero(self):
        p=native_player(flags174=0)
        x=self.project(p,original_dynamic_owner_ptr_arg2=0x80000)
        self.assertEqual(x.original_reached_call_sites,(0x41B360,0x41B490))
        self.assertFalse(x.original_source_return_al_nonzero)

    def test_type1_owner_initial_4f8e40_and_negative_first_419350(self):
        p=native_player(flags174=0x100)
        x=self.project(p,original_dynamic_owner_ptr_arg2=0x80000,
            original_dynamic_owner_record_if_reached=original_owner(1),
            original_4f8e40_al_if_reached=True,
            original_first_419350_signed_dword_if_reached=-1)
        self.assertEqual(x.original_reached_call_sites,
                         (0x41B360,0x4F8E40,0x419350,0x41B490))
        self.assertTrue(x.original_source_return_al_nonzero)
        y=self.project(p,original_dynamic_owner_ptr_arg2=0x80000,
            original_dynamic_owner_record_if_reached=original_owner(1),
            original_4f8e40_al_if_reached=False,
            original_first_419350_signed_dword_if_reached=-1)
        self.assertFalse(y.original_source_return_al_nonzero)

    def test_type1_signed_threshold_mode1_mode2_and_other_case(self):
        p=native_player(flags174=0x100)
        base=dict(original_dynamic_owner_ptr_arg2=0x80000,
            original_dynamic_owner_record_if_reached=original_owner(1),
            original_4f8e40_al_if_reached=False,
            original_first_419350_signed_dword_if_reached=0)
        for mode,second,threshold,expected in (
            (1,-7,-8,True),(2,-8,-8,False),(2,9,8,True),
            (1,-9,-8,False)):
            with self.subTest(mode=mode,second=second,threshold=threshold):
                r=self.project(p,**base,
                    original_global_8755e8_mode_if_reached=mode,
                    original_global_threshold_8755ec_or_f0_if_reached=threshold,
                    original_second_419350_signed_dword_if_reached=second)
                self.assertEqual(r.original_source_return_al_nonzero,expected)
                self.assertEqual(r.original_reached_call_sites,
                    (0x41B360,0x4F8E40,0x419350,0x419350,0x41B490))
        r=self.project(p,**base,original_global_8755e8_mode_if_reached=3)
        self.assertEqual(r.original_reached_call_sites,
                         (0x41B360,0x4F8E40,0x419350,0x41B490))
        self.assertFalse(r.original_source_return_al_nonzero)

    def test_owner_non_type1_uses_virtual30_then_conditional_4f8e40(self):
        p=native_player(flags174=0x100)
        base=dict(original_dynamic_owner_ptr_arg2=0x80000,
                  original_dynamic_owner_record_if_reached=original_owner(0))
        true=self.project(p,**base,original_dynamic_owner_vtable30_al_if_reached=True)
        self.assertFalse(true.original_source_return_al_nonzero)
        self.assertEqual(true.original_reached_call_sites,(0x41B360,0x4180E4,0x41B490))
        negative=self.project(p,**base,original_dynamic_owner_vtable30_al_if_reached=False,
                    original_4f8e40_al_if_reached=True)
        self.assertEqual(negative.original_reached_call_sites,
            (0x41B360,0x4180E4,0x4F8E40,0x41B490))
        self.assertTrue(negative.original_source_return_al_nonzero)

    def test_final_bit11_41b4d0_4e9be0_overrides_bl_when_expired(self):
        p=native_player(flags14=0x800)
        optional=dict(original_41b4d0_returned_pointer_if_reached=0x90000)
        owner=bytearray(0x18);pack_into("<i",owner,0x14,100)
        for day,expected in ((90,False),(100,False),(101,True)):
            with self.subTest(day=day):
                x=self.project(p,**optional,
                     original_41b4d0_returned_record_if_reached=bytes(owner),
                     original_global_9847fc_current_day_if_reached=day)
                self.assertEqual(x.original_source_return_al_nonzero,expected)
                self.assertEqual(x.original_reached_call_sites,
                    (0x41B490,0x41B4D0,0x4E9BE0))
        # In BL-true cases a nonexpired 4E9BE0 still returns BL true.
        y=self.project(native_player(flags14=0x801),**optional,
            original_41b4d0_returned_record_if_reached=bytes(owner),
            original_global_9847fc_current_day_if_reached=90)
        self.assertTrue(y.original_source_return_al_nonzero)

    def test_fail_closed_unreached_callback_and_forged_source_fields(self):
        p=native_player(flags174=0x100)
        default=dict(original_dynamic_owner_ptr_arg2=0x80000,
                     original_dynamic_owner_record_if_reached=original_owner(1),
                     original_4f8e40_al_if_reached=False,
                     original_first_419350_signed_dword_if_reached=-1)
        failures=(
            dict(original_global_8755e8_mode_if_reached=1),
            dict(original_second_419350_signed_dword_if_reached=1),
            dict(original_4f8e40_al_if_reached=1),
            dict(original_first_419350_signed_dword_if_reached=None),
            dict(original_dynamic_owner_vtable30_al_if_reached=False),
        )
        for changed in failures:
            with self.subTest(fields=changed),self.assertRaises(Original418050SourceError):
                self.project(p,**(default|changed))
        for changed in (
            dict(original_club_key_dword_arg1=True),
            dict(original_dynamic_owner_ptr_arg2=0x100000000),
            dict(original_4f8e40_al_if_reached=False),
            dict(original_player_record_at_reached_41b490=native_player(flags14=0x800)),
        ):
            with self.subTest(fields=str(changed)[:70]),self.assertRaises(Original418050SourceError):
                self.project(**changed)
        non_type=dict(original_dynamic_owner_ptr_arg2=0x80000,
            original_dynamic_owner_record_if_reached=original_owner(2),
            original_dynamic_owner_vtable30_al_if_reached=True)
        for changed in (dict(original_4f8e40_al_if_reached=False),
                        dict(original_first_419350_signed_dword_if_reached=10)):
            with self.assertRaises(Original418050SourceError):
                self.project(p,**(non_type|changed))
        with self.assertRaises(Original418050SourceError):
            self.project(native_player(flags14=0x800))

    def test_private_pe_418050_branches_and_direct_leaf_bytes(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:
            self.skipTest("private original PE omitted from public CI")
        raw=Path(original).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
          (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x418050:"53 55 8b 6c 24 0c",
            0x418059:"8a 56 14",
            0x41805C:"0f bf 46 10",
            0x418060:"f6 c2 07",
            0x418063:"0f 95 c3",
            0x418066:"3b c5",
            0x418071:"85 ff",
            0x41807B:"e8 e0 32 00 00",
            0x418084:"83 7f 34 01",
            0x418094:"e8 a7 0d 0e 00",
            0x4180A6:"e8 a5 12 00 00",
            0x4180AB:"83 38 00",
            0x4180B0:"a1 e8 55 87 00",
            0x4180BB:"8b 3d f0 55 87 00",
            0x4180C8:"8b 3d ec 55 87 00",
            0x4180D5:"e8 76 12 00 00",
            0x4180DA:"39 38",
            0x4180E4:"ff 52 30",
            0x4180F5:"e8 46 0d 0e 00",
            0x418102:"e8 89 33 00 00",
            0x418107:"3c 01",
            0x41810E:"e8 bd 33 00 00",
            0x418115:"e8 c6 1a 0d 00",
            0x41811C:"b0 01",
            0x418120:"8a c3",
            0x41B360:"8b 81 74 01 00 00",
            0x41B366:"c1 e8 08",
            0x41B490:"8b 41 14",
            0x41B493:"c1 e8 0b",
            0x41B4D3:"e8 b8 ff ff ff",
            0x4E9BE0:"a1 fc 47 98 00",
            0x4E9BE8:"3b c2",
            0x4E9BEA:"0f 9e c0",
        }
        for va,text in sites.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(text)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bs)],bs)


if __name__=="__main__":
    unittest.main()
