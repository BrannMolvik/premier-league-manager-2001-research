"""Original 409F74 second XI fallback source tests, not original execution."""
import os,unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from struct import pack_into

from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_418050_dynamic_eligibility import source_original_418050_reached_availability
from original_native_409c90_initial_availability import (
    source_original_409c90_initial_roster_mask_all_team_classes)
from original_native_409c90_first_pass_xi import (
    SourceOriginal409C90FirstPassCandidate as C1,
    SourceOriginal409C90FirstPassRole as R1,
    source_original_409c90_first_pass_eleven_strict_role_slots as first_source,
)
from original_native_409c90_second_pass_xi import (
    SourceOriginal409C90SecondPassCandidate as C2,
    SourceOriginal409C90SecondPassRole as R2,
    Original409C90SecondPassSourceError,
    source_original_409c90_second_pass_fill_unmatched_eleven_slots as second_source,
)


def player(pid,flags14=0):
    raw=bytearray(0x24c)
    pack_into("<H",raw,4,pid)
    pack_into("<h",raw,0x10,7)
    pack_into("<I",raw,0x14,flags14)
    pack_into("<I",raw,0x248,0x90000000+pid)
    return SourceOriginal406BE0Player(
        pid,0x40000000+pid*0x250,bytes(raw),None)


def team(ids,team_cls=2):
    raw=bytearray(0x298)
    pack_into("<I",raw,4,7)
    raw[0x74]=team_cls
    pack_into("<i",raw,0x294,len(ids))
    for i,pid in enumerate(ids):pack_into("<H",raw,0x244+i*2,pid)
    return bytes(raw)


def entry(role):
    return role.to_bytes(4,"little")+bytes(4)


class Original409C90SecondPassTests(unittest.TestCase):
    def sample(self,rows,cls=2,mode=0):
        ids=tuple(x.original_roster_word_id for x in rows)
        t=team(ids,cls)
        extra={}
        if cls not in (2,3):
            recs=tuple(source_original_418050_reached_availability(
                original_player_record_at_418050=r.original_player_record_bytes,
                original_club_key_dword_arg1=7,
                original_dynamic_owner_ptr_arg2=0,
                original_player_record_at_reached_41b490=r.original_player_record_bytes)
                for r in rows)
            extra=dict(original_reached_409c90_dynamic_owner_ptr=0,
                original_418050_receipts_if_reached=recs)
        m=source_original_409c90_initial_roster_mask_all_team_classes(
            original_team_record_at_409c90=t,
            original_reached_409b50_roster_count_argument=len(rows),
            original_global_875640_native_player_base=0x40000000,
            original_ordered_at_call_player_records=rows,**extra)
        base=dict(original_team_record_at_first_pass=t,
             original_global_875640_native_player_base=0x40000000,
             original_mask_receipt_after_409d5e=m,
             original_ordered_player_records_at_first_pass=rows,
             original_first_pass_esp14_special_count=0,
             original_first_pass_esp94_mode_flag=mode)
        return t,m,base

    def second(self,t,rows,first,roles,human=None):
        return second_source(original_first_pass=first,
            original_team_record_at_second_pass=t,
            original_global_875640_player_base=0x40000000,
            original_ordered_players_at_second_pass=rows,
            original_eleven_second_pass_roles=roles,
            original_4037b0_human_al_if_any_slot_unfilled=human)

    def test_source_fallback_fills_only_empty_slot_without_status_role_getters(self):
        rows=(player(51,0),player(52,0),player(53,1))
        t,m,base=self.sample(rows)
        a=R1(entry(1),(
            C1(0,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
               original_reached_41c7e0_eax_if_scored=10,
               original_reached_668350_eax_if_scored=10),
            C1(1,original_reached_status_bytes_if_4ea300_called=bytes(3)),
            C1(2)))
        b=R1(entry(99),(
            C1(0),C1(1,original_reached_status_bytes_if_4ea300_called=bytes(3)),C1(2)))
        first=first_source(**base,original_eleven_role_source_inputs=(a,)+(b,)*10)
        self.assertEqual(first.source_original_selection_indices11,(0,)+(-1,)*10)
        retry_role=R2(entry(99),(
            C2(0),C2(1,original_reached_41c7e0_eax_if_scored=8,
                         original_reached_668350_eax_if_scored=8),C2(2)))
        noone=R2(entry(99),tuple(C2(i) for i in range(3)))
        after=self.second(t,rows,first,
            (R2(entry(1)),retry_role)+(noone,)*9,human=True)
        self.assertEqual(after.source_original_selected_roster_indices11,
            (0,1)+(-1,)*9)
        self.assertEqual(after.source_second_pass_newly_selected_roster_indices11,
            (-1,1)+(-1,)*9)
        self.assertEqual(after.source_used_mask_after_both_passes,b"\x01\x01\x00")
        self.assertFalse(after.source_409c90_should_retry_at_409ca5_with_mode0)
        self.assertFalse(after.source_409c90_has_eleven_selected_slots)
        self.assertFalse(after.original_live_game_state_modified)

    def test_exact_eleven_role_match_completes_and_never_reaches_4037b0(self):
        ids=tuple(range(51,62))
        rows=tuple(player(pid) for pid in ids)
        t,m,base=self.sample(rows)
        roles=[]
        for i in range(11):
            candidates=[]
            for j in range(11):
                if j<i:candidates.append(C1(j))
                else:
                    score=dict(original_reached_41c7e0_eax_if_scored=10,
                               original_reached_668350_eax_if_scored=10) if j==i else {}
                    candidates.append(C1(j,
                        original_reached_status_bytes_if_4ea300_called=
                        bytes((j+1,0,0)),**score))
            roles.append(R1(entry(i+1),tuple(candidates)))
        first=first_source(**base,original_eleven_role_source_inputs=tuple(roles))
        self.assertEqual(first.source_original_selection_indices11,tuple(range(11)))
        second_roles=tuple(R2(entry(i+1)) for i in range(11))
        final=self.second(t,rows,first,second_roles)
        self.assertTrue(final.source_409c90_has_eleven_selected_slots)
        self.assertEqual(final.source_original_selected_roster_indices11,tuple(range(11)))
        self.assertEqual(final.source_second_pass_newly_selected_roster_indices11,(-1,)*11)
        self.assertEqual(final.source_used_mask_after_both_passes,bytes([1]*11))
        self.assertIsNone(final.original_unfilled_40a105_reached_4037b0_human_al)
        self.assertTrue(final.original_40a1bb_assignment_not_executed)

    def test_source_incomplete_nonhuman_mode1_retries_from_409ca5_not_fake_completion(self):
        rows=tuple(player(pid,1) for pid in (51,52,53))
        t,m,base=self.sample(rows,cls=0,mode=1)
        self.assertEqual(m.source_mask_bytes,b"\x01\x01\x01")
        emptyfirst=R1(entry(1),tuple(C1(i) for i in range(3)))
        first=first_source(**base,original_eleven_role_source_inputs=(emptyfirst,)*11)
        emptysecond=R2(entry(1),tuple(C2(i) for i in range(3)))
        for human,retry in ((False,True),(True,False)):
            with self.subTest(human=human):
                r=self.second(t,rows,first,(emptysecond,)*11,human=human)
                self.assertEqual(r.source_original_selected_roster_indices11,(-1,)*11)
                self.assertEqual(r.source_used_mask_after_both_passes,bytes(3))
                self.assertEqual(r.source_409c90_should_retry_at_409ca5_with_mode0,retry)
                self.assertFalse(r.source_409c90_has_eleven_selected_slots)

    def test_guard_unvisited_second_pass_callbacks_role_and_first_mask_integrity(self):
        rows=(player(51),player(52),player(53,1))
        t,m,base=self.sample(rows)
        a=R1(entry(1),(
            C1(0,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=10,
                original_reached_668350_eax_if_scored=10),
            C1(1,original_reached_status_bytes_if_4ea300_called=bytes(3)),C1(2)))
        b=R1(entry(99),(
            C1(0),C1(1,original_reached_status_bytes_if_4ea300_called=bytes(3)),C1(2)))
        first=first_source(**base,original_eleven_role_source_inputs=(a,)+(b,)*10)
        missing=R2(entry(99),(
            C2(0),C2(1,original_reached_41c7e0_eax_if_scored=1,
                         original_reached_668350_eax_if_scored=1),C2(2)))
        all_missing=(R2(entry(1)),)+(missing,)*10
        for changed in (
            {"original_eleven_second_pass_roles":(R2(entry(1),
                (C2(0),C2(1),C2(2))),)+all_missing[1:]},
            {"original_eleven_second_pass_roles":(R2(entry(7)),)+all_missing[1:]},
            {"original_first_pass":replace(first,source_used_mask_after_first_pass=b"\x00\x00\x00")},
            {"original_global_875640_player_base":0},
            {"original_4037b0_human_al_if_any_slot_unfilled":None},
        ):
            with self.subTest(changed=str(changed)[:80]),self.assertRaises(
                    Original409C90SecondPassSourceError):
                second_source(**(dict(original_first_pass=first,
                    original_team_record_at_second_pass=t,
                    original_global_875640_player_base=0x40000000,
                    original_ordered_players_at_second_pass=rows,
                    original_eleven_second_pass_roles=all_missing,
                    original_4037b0_human_al_if_any_slot_unfilled=True)|changed))

    def test_private_pe_409f74_40a158_second_scan_cutoff_and_retry_opcode_sites(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("source original PE omitted from CI")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x409F74:"83 7c 24 28 0b",
            0x409F93:"83 3a ff",
            0x409F9C:"33 ff",
            0x409FD8:"80 3c 03 00",
            0x409FDE:"80 38 00",
            0x409FE5:"e8 a6 14 01 00",
            0x409FF2:"e8 f9 dd ff ff",
            0x409FF7:"39 44 24 14",
            0x409FFD:"8b 84 24 84 00 00 00",
            0x40A01A:"e8 c1 27 01 00",
            0x40A02D:"e8 3e 19 01 00",
            0x40A036:"e8 15 e3 25 00",
            0x40A03B:"85 c0",
            0x40A03F:"b8 01 00 00 00",
            0x40A044:"3b 44 24 10",
            0x40A048:"7e 10",
            0x40A088:"89 08",
            0x40A08C:"c6 04 11 01",
            0x40A0A9:"e8 e2 13 01 00",
            0x40A0B2:"83 bc 24 94 00 00 00 01",
            0x40A0C5:"a1 e0 4b 87 00",
            0x40A0DB:"8b 4c 24 14",
            0x40A105:"8b 4c 24 18",
            0x40A120:"e8 8b 96 ff ff",
            0x40A125:"84 c0",
            0x40A129:"83 bc 24 94 00 00 00 01",
            0x40A13A:"c7 84 24 94 00 00 00 00 00 00 00",
            0x40A147:"e9 59 fb ff ff",
            0x40A14F:"33 c0",
            0x40A158:"8b 44 24 1c",
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                x=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(x)],x)


if __name__=="__main__":
    unittest.main()
