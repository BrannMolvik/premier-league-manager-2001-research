"""Original 409C90 source class2/3 and non-class dynamic initial-mask joins."""
import unittest,os
from hashlib import sha256
from pathlib import Path
from struct import pack_into
from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_418050_dynamic_eligibility import (
    source_original_418050_reached_availability as dynamic_source,
)
from original_native_409c90_initial_availability import (
    Original409C90InitialMaskSourceError,
    source_original_409c90_initial_roster_mask_all_team_classes as source,
)


def team(cls,ids=(51,52,53),key=7):
    b=bytearray(0x298)
    b[0x74]=cls
    pack_into("<I",b,4,key)
    pack_into("<i",b,0x294,len(ids))
    for i,pid in enumerate(ids):
        pack_into("<H",b,0x244+2*i,pid)
    return bytes(b)


def player(pid,flags14,club=7,flags174=0):
    p=bytearray(0x24c)
    pack_into("<H",p,4,pid)
    pack_into("<h",p,0x10,club)
    pack_into("<I",p,0x14,flags14)
    pack_into("<I",p,0x174,flags174)
    return SourceOriginal406BE0Player(pid,0x40000000+pid*0x250,bytes(p),None)


class Original409C90InitialAvailabilitySourceTests(unittest.TestCase):
    def args(self,cls=0,rows=None):
        rows=rows or (player(51,0),player(52,1),player(53,0,club=8))
        return dict(original_team_record_at_409c90=team(cls),
             original_reached_409b50_roster_count_argument=3,
             original_global_875640_native_player_base=0x40000000,
             original_ordered_at_call_player_records=rows)

    def returns(self,rows,owner=0):
        receipts=[]
        for r in rows:
            p=r.original_player_record_bytes
            receipts.append(dynamic_source(
                original_player_record_at_418050=p,
                original_club_key_dword_arg1=7,
                original_dynamic_owner_ptr_arg2=owner,
                original_player_record_at_reached_41b490=p))
        return tuple(receipts)

    def test_class0_1_418050_null_owner_original_mask_uses_each_source(self):
        for cls in (0,1,4):
            a=self.args(cls)
            receipt=self.returns(a["original_ordered_at_call_player_records"])
            x=source(**a,original_reached_409c90_dynamic_owner_ptr=0,
                     original_418050_receipts_if_reached=receipt)
            self.assertEqual(x.original_team_class_byte74,cls)
            self.assertEqual(x.original_roster_word_ids_in_order,(51,52,53))
            self.assertEqual(x.source_mask_bytes,b"\x00\x01\x01")
            self.assertEqual(x.original_418050_receipts_if_reached,receipt)
            self.assertFalse(x.native_original_callbacks_executed)
            self.assertFalse(x.live_game_state_modified)

    def test_class2_3_418130_pure_mask_does_not_accept_unreached_dynamic(self):
        for cls in (2,3):
            a=self.args(cls)
            r=source(**a)
            self.assertEqual(r.source_mask_bytes,b"\x00\x01\x00")
            self.assertEqual(r.original_418050_receipts_if_reached,())
            self.assertEqual(r.original_source_409c90_dynamic_owner_ptr,0)
            with self.assertRaises(Original409C90InitialMaskSourceError):
                source(**a,original_reached_409c90_dynamic_owner_ptr=0,
                       original_418050_receipts_if_reached=())

    def test_dynamic_nonnull_owner_requires_same_actual_owner_for_each_418050(self):
        a=self.args(0,rows=(player(51,0),player(52,0,flags174=0x100),player(53,0)))
        owner=0x990000
        data=bytearray(0x38)
        pack_into("<I",data,0x34,4)
        receipts=[]
        for row in a["original_ordered_at_call_player_records"]:
            p=row.original_player_record_bytes
            extra=(dict(original_dynamic_owner_record_if_reached=bytes(data),
                original_dynamic_owner_vtable30_al_if_reached=False,
                original_4f8e40_al_if_reached=True)
                if row.original_roster_word_id==52 else {})
            receipts.append(dynamic_source(
                original_player_record_at_418050=p,
                original_club_key_dword_arg1=7,
                original_dynamic_owner_ptr_arg2=owner,
                original_player_record_at_reached_41b490=p,**extra))
        x=source(**a,original_reached_409c90_dynamic_owner_ptr=owner,
                 original_418050_receipts_if_reached=tuple(receipts))
        self.assertEqual(x.source_mask_bytes,b"\x00\x01\x00")
        with self.assertRaises(Original409C90InitialMaskSourceError):
            source(**a,original_reached_409c90_dynamic_owner_ptr=0,
                   original_418050_receipts_if_reached=tuple(receipts))

    def test_source_invalid_roster_pointer_order_and_bad_receipt_fail(self):
        a=self.args()
        valid=self.returns(a["original_ordered_at_call_player_records"])
        for changed in (
            dict(original_reached_409b50_roster_count_argument=4),
            dict(original_reached_409b50_roster_count_argument=True),
            dict(original_global_875640_native_player_base=0),
            dict(original_ordered_at_call_player_records=tuple(reversed(a[
                 "original_ordered_at_call_player_records"]))),
            dict(original_ordered_at_call_player_records=a[
                 "original_ordered_at_call_player_records"][:2]),
            dict(original_418050_receipts_if_reached=valid[:2]),
            dict(original_418050_receipts_if_reached=tuple(reversed(valid))),
            dict(original_418050_receipts_if_reached=None),
            dict(original_reached_409c90_dynamic_owner_ptr=None),
        ):
            with self.subTest(change=str(changed)[:90]),self.assertRaises(
                 Original409C90InitialMaskSourceError):
                source(**(a|dict(original_reached_409c90_dynamic_owner_ptr=0,
                   original_418050_receipts_if_reached=valid)|changed))

    def test_private_original_409c90_branch_dispatch_opcode_sites(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("original private PE intentionally absent from GitHub")
        b=Path(original).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),
         (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x409D0E:"8b 4c 24 1c",
            0x409D12:"e8 29 99 ff ff",
            0x409D17:"3c 01",
            0x409D19:"74 29",
            0x409D1F:"8b 54 24 7c",
            0x409D24:"8b 41 04",
            0x409D3D:"e8 0e e3 00 00",
            0x409D44:"33 c0",
            0x409D59:"e8 d2 e3 00 00",
            0x409D5E:"88 04 2e",
            0x409D61:"46",
            0x409D65:"3b f3",
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)


if __name__=="__main__":
    unittest.main()
