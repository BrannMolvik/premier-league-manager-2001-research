"""Original 409D79–409F5E strict first eleven-slot source selection tests."""
import os,unittest
from hashlib import sha256
from pathlib import Path
from struct import pack_into
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_409c90_initial_availability import (
    source_original_409c90_initial_roster_mask_all_team_classes as first_mask)
from original_native_409c90_first_pass_xi import (
    SourceOriginal409C90FirstPassCandidate as Candidate,
    SourceOriginal409C90FirstPassRole as Role,
    Original409C90FirstPassSourceError,
    source_original_409c90_first_pass_eleven_strict_role_slots as project,
)


def player(pid, flags, club=7):
    b=bytearray(0x24c)
    pack_into("<H",b,4,pid)
    pack_into("<h",b,0x10,club)
    pack_into("<I",b,0x14,flags)
    pack_into("<I",b,0x248,0x90000000+pid)
    return SourceOriginal406BE0Player(pid,0x40000000+pid*0x250,bytes(b),None)


def team(ids=(51,52,53),cls=2,key=7):
    b=bytearray(0x298)
    b[0x74]=cls
    pack_into("<I",b,4,key)
    pack_into("<i",b,0x294,len(ids))
    for i,pid in enumerate(ids):
        pack_into("<H",b,0x244+i*2,pid)
    return bytes(b)


def slot(role, facts,word=None):
    return Role(role.to_bytes(4,"little")+bytes(4),tuple(facts),word)


class Original409C90StrictFirstPassTests(unittest.TestCase):
    def defaults(self,rows=None):
        rows=rows or (player(51,0),player(52,0),player(53,1))
        original_team=team()
        m=first_mask(original_team_record_at_409c90=original_team,
             original_reached_409b50_roster_count_argument=3,
             original_global_875640_native_player_base=0x40000000,
             original_ordered_at_call_player_records=rows)
        return dict(original_team_record_at_first_pass=original_team,
             original_global_875640_native_player_base=0x40000000,
             original_mask_receipt_after_409d5e=m,
             original_ordered_player_records_at_first_pass=rows,
             original_first_pass_esp14_special_count=0,
             original_first_pass_esp94_mode_flag=0)

    def empty_candidate(self,i):
        return Candidate(i)

    def test_source_exclusion_mask_nonzero_skips_and_stable_ties_keep_first(self):
        args=self.defaults()
        # Source 409DDA skips 53 because the *nonzero* original mask is an
        # EXCLUSION, not a player-can-be-selected flag.
        self.assertEqual(args["original_mask_receipt_after_409d5e"].source_mask_bytes,
                         b"\x00\x00\x01")
        a=slot(1,(
            Candidate(0,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=12,
                original_reached_668350_eax_if_scored=10),
            Candidate(1,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=13,
                original_reached_668350_eax_if_scored=10),
            Candidate(2),
        ))
        b=slot(1,(
            Candidate(0), # already selected in role0, no callbacks reached
            Candidate(1,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=13,
                original_reached_668350_eax_if_scored=9),
            Candidate(2),
        ))
        c=slot(99,tuple(Candidate(i) for i in range(3)))
        result=project(**args,original_eleven_role_source_inputs=(a,b)+tuple(c for _ in range(9)))
        self.assertEqual(result.source_original_selection_indices11,(0,1)+(-1,)*9)
        self.assertEqual(result.source_used_mask_after_first_pass,b"\x01\x01\x00")
        self.assertEqual(result.source_best_scores11,(10,9)+(0,)*9)
        self.assertEqual(result.original_reached_first_mask,b"\x00\x00\x01")
        self.assertFalse(result.original_41c7e0_41b970_668350_callbacks_executed)
        self.assertFalse(result.live_game_state_modified)

    def test_source_no_role_match_skips_scorer_and_zero_score_clamps_to_one(self):
        args=self.defaults()
        a=slot(2,(
            Candidate(0,original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x03"),
            Candidate(1,original_reached_status_bytes_if_4ea300_called=b"\x01\x02\x03",
                original_reached_41c7e0_eax_if_scored=1,
                original_reached_668350_eax_if_scored=0),
            Candidate(2),
        ))
        b=slot(2,(Candidate(0,original_reached_status_bytes_if_4ea300_called=b"\x02\x00\x00",
                       original_reached_41c7e0_eax_if_scored=4,
                       original_reached_668350_eax_if_scored=-3),
                  Candidate(1),Candidate(2)))
        c=slot(100,(Candidate(0,original_reached_status_bytes_if_4ea300_called=bytes(3)),
                    Candidate(1),Candidate(2)))
        x=project(**args,original_eleven_role_source_inputs=(a,b)+(c,)*9)
        self.assertEqual(x.source_original_selection_indices11,(1,-1)+(-1,)*9)
        self.assertEqual(x.source_best_scores11,(1,0)+(0,)*9)

    def test_409ca6_counter_zero_and_class23_409cf7_mode_zero(self):
        args=self.defaults()
        c=slot(100,tuple(Candidate(i) for i in range(3)))
        for change in (
            dict(original_first_pass_esp14_special_count=1),
            dict(original_first_pass_esp94_mode_flag=1),
        ):
            with self.subTest(change=change),self.assertRaises(
                    Original409C90FirstPassSourceError):
                project(**(args|change),
                        original_eleven_role_source_inputs=(c,)*11)

    def test_class0_selected_bit11_874be0_counter_then_407df0_unsigned_cutoff(self):
        from original_native_418050_dynamic_eligibility import (
            source_original_418050_reached_availability as dynamic)
        rows=(player(51,0x800),player(52,0x800),player(53,1))
        t=team(cls=0)
        rec=bytearray(0x18)
        pack_into("<i",rec,0x14,100)
        dyn=[]
        for row in rows:
            p=row.original_player_record_bytes
            extra=(dict(original_41b4d0_returned_pointer_if_reached=0x800000,
                        original_41b4d0_returned_record_if_reached=bytes(rec),
                        original_global_9847fc_current_day_if_reached=90)
                   if row.original_roster_word_id!=53 else {})
            dyn.append(dynamic(original_player_record_at_418050=p,
                original_club_key_dword_arg1=7,
                original_dynamic_owner_ptr_arg2=0,
                original_player_record_at_reached_41b490=p,**extra))
        m=first_mask(original_team_record_at_409c90=t,
             original_reached_409b50_roster_count_argument=3,
             original_global_875640_native_player_base=0x40000000,
             original_ordered_at_call_player_records=rows,
             original_reached_409c90_dynamic_owner_ptr=0,
             original_418050_receipts_if_reached=tuple(dyn))
        self.assertEqual(m.source_mask_bytes,b"\x00\x00\x01")
        args=dict(original_team_record_at_first_pass=t,
             original_global_875640_native_player_base=0x40000000,
             original_mask_receipt_after_409d5e=m,
             original_ordered_player_records_at_first_pass=rows,
             original_first_pass_esp14_special_count=0,
             original_first_pass_esp94_mode_flag=1)
        first=slot(1,(
            Candidate(0,original_reached_407df0_eax_if_bit11=2,
                original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=11,
                original_reached_668350_eax_if_scored=10),
            Candidate(1,original_reached_407df0_eax_if_bit11=2,
                original_reached_status_bytes_if_4ea300_called=b"\x01\x00\x00",
                original_reached_41c7e0_eax_if_scored=9,
                original_reached_668350_eax_if_scored=8),
            Candidate(2)),word=1)
        later=slot(1,(
            Candidate(0), # already selected in previous slot
            Candidate(1,original_reached_407df0_eax_if_bit11=1),
            Candidate(2)))
        x=project(**args,original_eleven_role_source_inputs=(first,)+(later,)*10)
        self.assertEqual(x.source_original_selection_indices11,(0,)+(-1,)*10)
        self.assertEqual(x.source_used_mask_after_first_pass,b"\x01\x00\x00")
        self.assertEqual(x.source_special_count_after_first_pass,1)

    def test_original_unreached_callbacks_malformed_source_and_roster_fail_closed(self):
        args=self.defaults()
        c=slot(100,tuple(Candidate(i) for i in range(3)))
        default=(c,)*11
        for changed in (
            dict(original_first_pass_esp14_special_count=True),
            dict(original_first_pass_esp94_mode_flag=-1),
            dict(original_eleven_role_source_inputs=default[:10]),
            dict(original_global_875640_native_player_base=0),
            dict(original_ordered_player_records_at_first_pass=tuple(reversed(args[
                "original_ordered_player_records_at_first_pass"]))),
        ):
            with self.subTest(changed=str(changed)[:90]),self.assertRaises(
                    Original409C90FirstPassSourceError):
                project(**(args|dict(original_eleven_role_source_inputs=default)|changed))
        bad_cases=(
            slot(100,(Candidate(0,original_reached_668350_eax_if_scored=8),
                      Candidate(1),Candidate(2))),
            slot(100,(Candidate(0,original_reached_status_bytes_if_4ea300_called=b"\x00\x00\x00",
                          original_reached_668350_eax_if_scored=5),
                      Candidate(1),Candidate(2))),
            slot(100,(Candidate(0,original_reached_status_bytes_if_4ea300_called=bytes(2)),
                      Candidate(1),Candidate(2))),
            slot(100,(Candidate(1),Candidate(0),Candidate(2))),
            slot(100,(Candidate(0),Candidate(1),Candidate(2,
                      original_reached_status_bytes_if_4ea300_called=bytes(3)))),
        )
        for invalid in bad_cases:
            with self.subTest(invalid=str(invalid)[:70]),self.assertRaises(
                    Original409C90FirstPassSourceError):
                project(**args,original_eleven_role_source_inputs=(invalid,)+default[1:])

    def test_private_original_409d79_409f5e_exclusion_greedy_and_tie_opcodes(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("canonical licensed original omitted from CI")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x409CA6:"89 74 24 18",
            0x409CF7:"89 b4 24 94 00 00 00",
            0x409D79:"8b 54 24 38",
            0x409D85:"c7 44 24 34 ff ff ff ff",
            0x409DD5:"8a 0c 02",
            0x409DDA:"84 c9",
            0x409DDC:"0f 85 db 00 00 00",
            0x409DE2:"80 38 00",
            0x409DE5:"0f 85 d2 00 00 00",
            0x409DF3:"e8 98 16 01 00",
            0x409E00:"e8 eb df ff ff",
            0x409E05:"39 44 24 14",
            0x409E09:"0f 83 a3 00 00 00",
            0x409E26:"8b 3c dd b8 6c 87 00",
            0x409E2D:"e8 ce 04 0e 00",
            0x409E41:"e8 ba 04 0e 00",
            0x409E55:"e8 a6 04 0e 00",
            0x409E61:"e8 7a 29 01 00",
            0x409E74:"e8 f7 1a 01 00",
            0x409E7D:"e8 ce e4 25 00",
            0x409E82:"85 c0",
            0x409E86:"b8 01 00 00 00",
            0x409E8B:"3b 44 24 10",
            0x409E8F:"7e 21",
            0x409EF0:"c6 04 01 01",
            0x409EFE:"89 0a",
            0x409F11:"e8 7a 15 01 00",
            0x409F1A:"83 bc 24 94 00 00 00 01",
            0x409F2D:"a1 e0 4b 87 00",
            0x409F32:"66 83 7c 90 18 00",
            0x409F43:"01 44 24 14",
            0x409F53:"83 f8 0b",
        }
        for va,hexbytes in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(hexbytes)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)


if __name__=="__main__":
    unittest.main()
