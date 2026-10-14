"""Original match first-side native linked user key projection, never runtime execution."""
from dataclasses import replace
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into
from unittest import TestCase, main

from original_native_417340_registered_user_gate import Original417340ReachedUser
from original_match_first_side_human_owner import (
    OriginalFirstSideHumanOwnerSourceError,
    source_original_5da2f0_first_side_human_owner,
)


def source_fixture(club_key=777, manager_keys=(777,)):
    club=bytearray(8)
    pack_into("<I",club,4,club_key)
    root=bytearray(0x9d0)
    links=[]
    if manager_keys:
        pack_into("<I",root,0x9cc,0x10000)
    for i,key in enumerate(manager_keys):
        nodeptr=0x10000+i*0x100
        nxt=nodeptr+0x100 if i+1<len(manager_keys) else 0
        uptr=0x40000+i*0x2000
        ctxptr=0x80000+i*0x200
        node=bytearray(8)
        user=bytearray(0x6b4)
        ctx=bytearray(8)
        pack_into("<II",node,0,uptr,nxt)
        pack_into("<I",user,0x5b4,ctxptr)
        pack_into("<I",user,0x694,0xA0000+i*0x100)
        pack_into("<I",user,0x6b0,0xB0000+i*0x100)
        pack_into("<I",ctx,4,key)
        links.append(Original417340ReachedUser(nodeptr,bytes(node),uptr,bytes(user),ctxptr,bytes(ctx)))
    return dict(
        original_513238_flags44_at_entry=0x10,
        original_513244_first_side_club_pointer=0x90000,
        original_513244_first_side_club_record=bytes(club),
        original_global_874c10_record_at_5da31a=bytes(root),
        original_4139f0_manager_links_at_5da31a=tuple(links),
    )


class OriginalMatchFirstSideHumanOwnerSourceTests(TestCase):
    def test_qualified_owner_reads_source_first_registered_user(self):
        source=source_fixture(manager_keys=(999,777,777))
        receipt=source_original_5da2f0_first_side_human_owner(**source)
        self.assertTrue(receipt.original_4037b0_full_key_human)
        self.assertEqual(receipt.original_first_full_key_user_pointer,0x42000)
        self.assertEqual(receipt.original_403850_selected_masked_user_pointer,0x42000)
        self.assertEqual(receipt.original_selected_user_694_pointer,0xA0100)
        self.assertEqual(receipt.original_selected_user_6b0_pointer,0xB0100)
        self.assertFalse(receipt.original_5da2f0_calculation_executed)
        self.assertFalse(receipt.live_game_state_updated)

    def test_full_dword_owner_and_low16_user_selection_are_not_equivalent(self):
        # Actual source 4139F0 compares full DWORD, 413B40 masks first.
        source=source_fixture(club_key=0x10042,manager_keys=(0x42,0x10042))
        receipt=source_original_5da2f0_first_side_human_owner(**source)
        self.assertEqual(receipt.original_first_full_key_user_pointer,0x42000)
        self.assertEqual(receipt.original_403850_selected_masked_user_pointer,0x40000)
        self.assertEqual(receipt.original_selected_user_694_pointer,0xA0000)

    def test_low16_alias_alone_never_enters_human_branch(self):
        source=source_fixture(club_key=0x10042,manager_keys=(0x42,))
        receipt=source_original_5da2f0_first_side_human_owner(**source)
        self.assertFalse(receipt.original_4037b0_full_key_human)
        self.assertIsNone(receipt.original_403850_selected_masked_user_pointer)
        self.assertIsNone(receipt.original_selected_user_694_pointer)

    def test_nonhuman_and_empty_user_chain_avoid_unreached_human_dereferences(self):
        for keys in ((100,200),()):
            with self.subTest(keys=keys):
                data=source_fixture(manager_keys=keys)
                out=source_original_5da2f0_first_side_human_owner(**data)
                self.assertFalse(out.original_4037b0_full_key_human)
                self.assertIsNone(out.original_selected_user_6b0_pointer)

    def test_4037b0_full_match_without_413b40_low16_match_fails_closed(self):
        data=source_fixture(club_key=0x10042,manager_keys=(0x10042,))
        with self.assertRaisesRegex(OriginalFirstSideHumanOwnerSourceError,"null masked"):
            source_original_5da2f0_first_side_human_owner(**data)

    def test_skipped_513238_bit20_never_reaches_source_side(self):
        data=source_fixture()
        data["original_513238_flags44_at_entry"]=0x20
        with self.assertRaisesRegex(OriginalFirstSideHumanOwnerSourceError,"skips side"):
            source_original_5da2f0_first_side_human_owner(**data)

    def test_corrupt_chain_pointer_owner_or_selected_user_stats_fail_closed(self):
        data=source_fixture(manager_keys=(999,777))
        a,b=data["original_4139f0_manager_links_at_5da31a"]
        for changed in (
            (replace(a,original_manager_link_pointer=123),b),
            (a,replace(b,original_manager_link_pointer=a.original_manager_link_pointer)),
            (a,replace(b,original_user_context_record=b"")),
            (a,),
            (a,replace(b,original_user_record=b.original_user_record[:0x600])),
            (a,replace(b,original_user_pointer=0)),
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(OriginalFirstSideHumanOwnerSourceError):
                    source_original_5da2f0_first_side_human_owner(**{
                        **data,"original_4139f0_manager_links_at_5da31a":changed})

    def test_noninteger_or_forged_zero_selected_stat_pointer_fail_closed(self):
        data=source_fixture()
        for bad in (True,-1,0x100000000):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalFirstSideHumanOwnerSourceError):
                    source_original_5da2f0_first_side_human_owner(**{
                        **data,"original_513244_first_side_club_pointer":bad})
        link=data["original_4139f0_manager_links_at_5da31a"][0]
        user=bytearray(link.original_user_record)
        pack_into("<I",user,0x694,0)
        with self.assertRaisesRegex(OriginalFirstSideHumanOwnerSourceError,r"\+694"):
            source_original_5da2f0_first_side_human_owner(**{
                **data,"original_4139f0_manager_links_at_5da31a":(
                    replace(link,original_user_record=bytes(user)),)})

    def test_optional_original_pe_source_opcodes(self):
        p=environ.get("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("original proprietary executable intentionally absent from CI")
        exe=Path(p).read_bytes()
        self.assertEqual(len(exe),4714541)
        self.assertEqual(sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        sig={
            0x513238:"8b 4e 44",0x51323c:"c1 e9 05",0x513242:"75 50",
            0x513244:"8b 17",0x513252:"e8 99 70 0c 00",
            0x5da301:"8b f1",0x5da31a:"e8 91 94 e2 ff",0x5da321:"0f 84 11 02 00 00",
            0x5da32c:"e8 1f 95 e2 ff",0x5da331:"8b 88 94 06 00 00",
            0x5da34a:"e8 01 95 e2 ff",0x5da34f:"8b 88 b0 06 00 00",
            0x4037b0:"51 b9 10 4c 87 00",0x403850:"56 8b f1",
            0x403858:"3c 01",0x403865:"e8 d6 02 01 00",
            0x4139e0:"8b 44 24 04",0x4139e4:"8b 40 04",
            0x413a06:"39 4a 04",0x413b4e:"81 e1 ff ff 00 00",
            0x413b5c:"39 4a 04",0x413b6d:"8b 00",
            0x5db7d0:"84 c0",0x5db7f8:"89 9e 48 01 00 00",
            0x5da5f0:"8b 03",0x5da5f4:"ff 50 18",
            0x5da5f7:"85 c0",0x5da5f9:"0f 84 47 01 00 00",
            0x5da705:"c6 44 24 0f 01",0x5da74d:"ff 52 28",
            0x5da750:"83 f8 06",0x5da757:"e8 74 15 00 00",
            0x5da76b:"e8 f0 12 00 00",0x5db7d2:"0f 85 1a 02 00 00",
            0x5dbc1b:"8b 86 94 02 00 00",0x5dbc25:"81 c6 44 02 00 00",
            0x5dbcf8:"8d b0 44 02 00 00",0x5dba6f:"8b 70 4c",
        }
        for va,hexdump in sig.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(hexdump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    main()
