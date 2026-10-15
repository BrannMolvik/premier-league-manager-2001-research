"""Original 41B970/41E1D0 and 409C90 final team+34 source tests."""
import os,unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from struct import pack_into,unpack_from
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_409c90_initial_availability import (
    source_original_409c90_initial_roster_mask_all_team_classes)
from original_native_409c90_first_pass_xi import (
    SourceOriginal409C90FirstPassCandidate as C1,
    SourceOriginal409C90FirstPassRole as R1,
    source_original_409c90_first_pass_eleven_strict_role_slots)
from original_native_409c90_second_pass_xi import (
    SourceOriginal409C90SecondPassRole as R2,
    source_original_409c90_second_pass_fill_unmatched_eleven_slots)
from original_native_409c90_postselection_scoring import (
    Original409C90ScoreSourceError,
    source_original_41b970_player_morale_factor as source_factor,
    source_original_41e1d0_max_status_role_score as source_max,
    source_original_409c90_selected_slot_score_contribution as source_contribution,
    source_original_409c90_exact_eleven_score_to_team_plus34 as source_team_score,
)


def pbytes(pid=51,kind=2):
    p=bytearray(0x24c)
    pack_into("<H",p,4,pid)
    pack_into("<h",p,0x10,7)
    pack_into("<I",p,0x248,0x90000000+pid)
    p[0x192]=kind
    return bytes(p)


def team(ids=tuple(range(51,62)),cls=2):
    t=bytearray(0x298)
    pack_into("<I",t,4,7)
    t[0x74]=cls
    pack_into("<i",t,0x294,len(ids))
    for i,pid in enumerate(ids):pack_into("<H",t,0x244+i*2,pid)
    return bytes(t)


class Original409C90PostselectionScoreTests(unittest.TestCase):
    def test_original_41b970_five_factor_double_sources_and_unknown_default(self):
        for kind,expected,address in (
            (0,0.9,0x822268),(1,0.95,0x822270),(2,1.0,0x822278),
            (3,1.05,0x822280),(4,1.1,0x822288),(5,1.0,0x822278),
            (255,1.0,0x822278)):
            with self.subTest(kind=kind):
                receipt=source_factor(original_native_player_at_41b970=pbytes(kind=kind))
                self.assertEqual(receipt.original_native_player_kind_byte192,kind)
                self.assertEqual(receipt.original_source_factor_double,expected)
                self.assertEqual(receipt.original_source_constant_va,address)
                self.assertFalse(receipt.original_41b970_executed)
        with self.assertRaises(Original409C90ScoreSourceError):
            source_factor(original_native_player_at_41b970=bytes(20))

    def test_source_41e1d0_max_status_role_three_source_4ea300_visits(self):
        p=pbytes()
        x=source_max(original_player_record_at_41e1d0=p,
                original_status_record_at_41e1d0=b"\x00\x03\x05",
                original_reached_41c7e0_signed_eax_per_nonzero_role=(None,-2,40))
        self.assertEqual(x.source_reached_41c7e0_arguments,(3,5))
        self.assertEqual(x.original_return_eax,40)
        self.assertFalse(x.native_41e1d0_or_41c7e0_executed)
        y=source_max(original_player_record_at_41e1d0=p,
                original_status_record_at_41e1d0=b"\x02\x02\x00",
                original_reached_41c7e0_signed_eax_per_nonzero_role=(-2,-1,None))
        self.assertEqual(y.original_return_eax,0)
        for scores in ((0,-2,40),(None,-2,None),(None,-2,40,3)):
            with self.subTest(scores=scores),self.assertRaises(Original409C90ScoreSourceError):
                source_max(original_player_record_at_41e1d0=p,
                    original_status_record_at_41e1d0=b"\x00\x03\x05",
                    original_reached_41c7e0_signed_eax_per_nonzero_role=scores)

    def test_original_mode1_uses_reached_41e1d0_41b970_and_668350(self):
        p=pbytes(kind=3)
        best=source_max(original_player_record_at_41e1d0=p,
            original_status_record_at_41e1d0=b"\x01\x02\x00",
            original_reached_41c7e0_signed_eax_per_nonzero_role=(10,13,None))
        factor=source_factor(original_native_player_at_41b970=p)
        x=source_contribution(original_slot_index=0,
            original_native_player_pointer_at_scoring=0x40000000+51*0x250,
            original_409c90_plus90_mode_dword=1,
            original_native_player_at_post_assignment_scoring=p,
            original_role_dword_from_original_876cb8=1,
            original_team_score_accumulator_before=0,
            original_reached_41e1d0_receipt_if_mode1=best,
            original_reached_41b970_receipt_if_mode1=factor,
            original_reached_668350_eax_if_mode1=13,
            original_reached_41c7e0_eax_if_other_mode=None)
        self.assertEqual(x.original_native_score_subcall_return_signed_eax,13)
        self.assertEqual(x.original_team_score_accumulator_after_source_add_signed,13)
        self.assertFalse(x.live_game_state_modified)
        for wrong in (
            dict(original_reached_41b970_receipt_if_mode1=replace(
                factor,original_native_player_at_call=pbytes(52))),
            dict(original_reached_41e1d0_receipt_if_mode1=None),
            dict(original_reached_41c7e0_eax_if_other_mode=15),
            dict(original_reached_668350_eax_if_mode1=None),
        ):
            with self.subTest(wrong=str(wrong)[:72]),self.assertRaises(Original409C90ScoreSourceError):
                source_contribution(**(dict(original_slot_index=0,
                    original_native_player_pointer_at_scoring=0x40000000+51*0x250,
                    original_409c90_plus90_mode_dword=1,
                    original_native_player_at_post_assignment_scoring=p,
                    original_role_dword_from_original_876cb8=1,
                    original_team_score_accumulator_before=0,
                    original_reached_41e1d0_receipt_if_mode1=best,
                    original_reached_41b970_receipt_if_mode1=factor,
                    original_reached_668350_eax_if_mode1=13,
                    original_reached_41c7e0_eax_if_other_mode=None)|wrong))

    def test_original_other_mode_single_41c7e0_and_signed_accumulator_wrap(self):
        p=pbytes()
        opts=dict(original_slot_index=0,original_native_player_pointer_at_scoring=0x40000000+51*0x250,
            original_409c90_plus90_mode_dword=0,
            original_native_player_at_post_assignment_scoring=p,
            original_role_dword_from_original_876cb8=8,
            original_team_score_accumulator_before=0x7fffffff,
            original_reached_41e1d0_receipt_if_mode1=None,
            original_reached_41b970_receipt_if_mode1=None,
            original_reached_668350_eax_if_mode1=None,
            original_reached_41c7e0_eax_if_other_mode=4)
        x=source_contribution(**opts)
        self.assertEqual(x.original_team_score_accumulator_after_source_add_signed,-0x7ffffffd)
        self.assertEqual(x.original_role_dword_from_876cb8,8)
        for bad in (
            dict(original_native_player_at_post_assignment_scoring=bytes(5)),
            dict(original_team_score_accumulator_before=True),
            dict(original_reached_41e1d0_receipt_if_mode1=object()),
            dict(original_reached_668350_eax_if_mode1=3),
        ):
            with self.subTest(bad=str(bad)[:70]),self.assertRaises(Original409C90ScoreSourceError):
                source_contribution(**(opts|bad))

    def full_xi_fixture(self):
        ids=tuple(range(51,62))
        records=tuple(SourceOriginal406BE0Player(pid,0x40000000+pid*0x250,pbytes(pid),None)
                      for pid in ids)
        t=team(ids)
        mask=source_original_409c90_initial_roster_mask_all_team_classes(
            original_team_record_at_409c90=t,
            original_reached_409b50_roster_count_argument=11,
            original_global_875640_native_player_base=0x40000000,
            original_ordered_at_call_player_records=records)
        source_roles=[]
        for i in range(11):
            facts=[]
            for j in range(11):
                if j<i:facts.append(C1(j))
                else:
                    extra=(dict(original_reached_41c7e0_eax_if_scored=5,
                                original_reached_668350_eax_if_scored=5)
                           if i==j else {})
                    facts.append(C1(j,
                        original_reached_status_bytes_if_4ea300_called=
                            bytes((j+1,0,0)),**extra))
            source_roles.append(R1((i+1).to_bytes(4,"little")+bytes(4),tuple(facts)))
        first=source_original_409c90_first_pass_eleven_strict_role_slots(
            original_team_record_at_first_pass=t,
            original_global_875640_native_player_base=0x40000000,
            original_mask_receipt_after_409d5e=mask,
            original_ordered_player_records_at_first_pass=records,
            original_first_pass_esp14_special_count=0,
            original_first_pass_esp94_mode_flag=0,
            original_eleven_role_source_inputs=tuple(source_roles))
        second=source_original_409c90_second_pass_fill_unmatched_eleven_slots(
            original_first_pass=first,
            original_team_record_at_second_pass=t,
            original_global_875640_player_base=0x40000000,
            original_ordered_players_at_second_pass=records,
            original_eleven_second_pass_roles=tuple(R2((i+1).to_bytes(4,"little")+bytes(4))
                                                   for i in range(11)))
        self.assertTrue(second.source_409c90_has_eleven_selected_slots)
        return t,second

    def test_original_40a2a4_team34_from_all_selected_eleven_scores(self):
        t,second=self.full_xi_fixture()
        accum=0
        receipts=[]
        for i,pid in enumerate(range(51,62)):
            r=source_contribution(original_slot_index=i,
                original_native_player_pointer_at_scoring=0x40000000+pid*0x250,
                original_409c90_plus90_mode_dword=0,
                original_native_player_at_post_assignment_scoring=pbytes(pid),
                original_role_dword_from_original_876cb8=i+1,
                original_team_score_accumulator_before=accum,
                original_reached_41e1d0_receipt_if_mode1=None,
                original_reached_41b970_receipt_if_mode1=None,
                original_reached_668350_eax_if_mode1=None,
                original_reached_41c7e0_eax_if_other_mode=5)
            receipts.append(r)
            accum=r.original_team_score_accumulator_after_source_add_signed
        args=dict(original_complete_source_second_pass=second,
                  original_native_team_at_40a2a4=t,
                  original_global_875640_player_array_base_at_scoring=0x40000000,
                  original_40a1f8_mode_dword=0,
                  original_eleven_reached_scores=tuple(receipts))
        result=source_team_score(**args)
        self.assertEqual(result.original_accumulator_final_signed32,55)
        self.assertEqual(unpack_from("<i",result.original_team_source_after_40a2a4_literal_store,0x34)[0],55)
        self.assertEqual(unpack_from("<i",result.original_team_source_before_40a2a4,0x34)[0],0)
        self.assertEqual(result.original_selected_original_word_ids_in_slot_order,tuple(range(51,62)))
        self.assertFalse(result.native_40a2a4_executed)
        self.assertFalse(result.live_game_state_modified)
        for changed in (
            dict(original_eleven_reached_scores=tuple(receipts[:-1])),
            dict(original_40a1f8_mode_dword=1),
            dict(original_global_875640_player_array_base_at_scoring=0),
            dict(original_eleven_reached_scores=(replace(receipts[0],
                original_role_dword_from_876cb8=99),)+tuple(receipts[1:])),
            dict(original_eleven_reached_scores=(replace(receipts[0],
                original_native_player_pointer_at_scoring=0x4abcde),)+tuple(receipts[1:])),
            dict(original_eleven_reached_scores=(replace(receipts[0],
                original_native_slot_index=1),)+tuple(receipts[1:])),
            dict(original_eleven_reached_scores=(replace(receipts[0],
                original_previous_team_score_accumulator_signed=1),)+tuple(receipts[1:])),
            dict(original_eleven_reached_scores=(replace(receipts[0],
                original_player_after_source_assignment_at_call=pbytes(999)),)+tuple(receipts[1:])),
        ):
            with self.subTest(changed=str(changed)[:80]),self.assertRaises(Original409C90ScoreSourceError):
                source_team_score(**(args|changed))

    def test_original_private_41b970_factor_table_and_40a2a4_source_opcodes(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("original licensed PE not present in CI")
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        import struct
        factors=((0x822268,0.9),(0x822270,0.95),(0x822278,1.0),
                 (0x822280,1.05),(0x822288,1.1))
        for va,num in factors:
            with self.subTest(factor=hex(va)):
                self.assertEqual(struct.unpack_from("<d",raw,va-0x400000)[0],num)
        addresses={
            0x41b970:"33 c0",0x41b972:"8a 81 92 01 00 00",
            0x41b978:"83 f8 04",0x41b97d:"ff 24 85 a8 b9 41 00",
            0x41b984:"dd 05 68 22 82 00",0x41b98b:"dd 05 70 22 82 00",
            0x41b992:"dd 05 80 22 82 00",0x41b999:"dd 05 88 22 82 00",
            0x41b9a0:"dd 05 78 22 82 00",
            0x41e1d0:"53",0x41e1d9:"8b 8e 48 02 00 00",
            0x41e1e0:"e8 1b c1 0c 00",
            0x41e1ec:"e8 ef e5 ff ff",0x41e1f1:"3b c3",
            0x41e1f8:"83 ff 03",0x41e1fe:"8b c3",
            0x40a1f8:"83 f8 01",0x40a242:"e8 89 3f 01 00",
            0x40a250:"db 84 24 84 00 00 00",
            0x40a25b:"e8 10 17 01 00",
            0x40a260:"dc 4c 24 44",0x40a264:"e8 e7 e0 25 00",
            0x40a269:"01 44 24 2c",
            0x40a282:"e8 59 25 01 00",
            0x40a287:"01 44 24 2c",
            0x40a2a0:"8b 44 24 2c",
            0x40a2a4:"89 46 34",
            0x66835f:"80 cc 0c",
            0x668369:"df 7d f4",
        }
        for va,text in addresses.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(text)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)


if __name__=="__main__":
    unittest.main()
