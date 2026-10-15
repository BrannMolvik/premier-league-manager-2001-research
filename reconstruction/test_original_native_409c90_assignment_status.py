"""Original 409C90 one-player actual status-byte mutation source prefix."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_409c90_assignment_status import (
    Original409C90SourceError,
    source_original_4ea330_then_4ea350_status_writes as status_write,
    source_original_4182f0_initial_player_flag14_bit4_store as bit4_write,
    source_original_409c90_one_selected_player_source_prefix as compose,
)


def original_player(status_pointer=0x550000,flags14=0x2208):
    b=bytearray(0x24c)
    pack_into("<I",b,0x248,status_pointer)
    pack_into("<I",b,0x14,flags14)
    return bytes(b)


class Original409C90AssignmentStatusSourceTests(TestCase):
    def test_original_4ea330_4ea350_preserve_high_bits_and_replace_low_fields(self):
        p=status_write(original_source_status_pointer=0x550000,
            original_source_status_record_before=b"\x10\x20\x30\xe5\xb7",
            original_4ea330_reached_role_argument_byte=0x04,
            original_4ea350_reached_position_argument_byte=0x09)
        self.assertEqual(p.source_status_after_two_stores,b"\x10\x20\x30\xe4\xb9")
        self.assertEqual(p.original_status_before,b"\x10\x20\x30\xe5\xb7")
        self.assertFalse(p.native_4ea330_executed)
        self.assertFalse(p.native_4ea350_executed)
        self.assertFalse(p.original_live_game_state_modified)
        q=status_write(original_source_status_pointer=0x550000,
            original_source_status_record_before=b"\x10\x20\x30\xe5\xb7",
            original_4ea330_reached_role_argument_byte=0xff,
            original_4ea350_reached_position_argument_byte=0xff)
        self.assertEqual(q.source_status_after_two_stores[3:],b"\xff\xbf")

    def test_source_player_flag_bit4_first_write_is_not_full_4182f0_world(self):
        before=original_player(flags14=0x2208)
        x=bit4_write(original_native_player_pointer=0x500000,
            original_native_player_record_before=before)
        self.assertEqual(unpack_from("<I",x.source_player_after_first_flag14_bit4_store,0x14)[0],0x2218)
        self.assertEqual(unpack_from("<I",x.source_player_before,0x14)[0],0x2208)
        self.assertFalse(x.native_4182f0_executed)
        self.assertFalse(x.original_other_4182f0_callbacks_executed)

    def test_original_409c90_true_mode_selected_player_source_byte_join(self):
        x=compose(original_40a1f8_reached_stack_eax=1,
             original_native_player_pointer=0x500000,
             original_native_player_record_at_40a211=original_player(),
             original_native_player_status_record_at_40a21d=b"\x10\x20\x30\x00\xf0",
             original_876cb8_reached_role_dword=0x12340001,
             original_876cbc_reached_position_byte=0x0b)
        self.assertEqual(x.role_and_position_status_source_writes.source_status_after_two_stores,
                         b"\x10\x20\x30\x01\xfb")
        self.assertEqual(x.player_flag_bit4_first_source_store.source_native_player_pointer,0x500000)
        self.assertTrue(x.original_40a1f8_native_stack_cmp_equal_one)
        self.assertFalse(x.native_409c90_executed)
        self.assertFalse(x.complete_original_mutable_world_qualified)

    def test_unreached_original_status_owner_and_types_fail_closed(self):
        good=dict(original_40a1f8_reached_stack_eax=1,
             original_native_player_pointer=0x500000,
             original_native_player_record_at_40a211=original_player(),
             original_native_player_status_record_at_40a21d=bytes(5),
             original_876cb8_reached_role_dword=1,
             original_876cbc_reached_position_byte=1)
        for change in (
            {"original_40a1f8_reached_stack_eax":0},
            {"original_40a1f8_reached_stack_eax":True},
            {"original_native_player_pointer":0},
            {"original_native_player_record_at_40a211":bytes(10)},
            {"original_native_player_record_at_40a211":original_player(status_pointer=0)},
            {"original_native_player_status_record_at_40a21d":bytearray(5)},
            {"original_native_player_status_record_at_40a21d":bytes(4)},
            {"original_876cb8_reached_role_dword":-1},
            {"original_876cb8_reached_role_dword":0x100000000},
            {"original_876cbc_reached_position_byte":True},
            {"original_876cbc_reached_position_byte":256},
        ):
            with self.subTest(change=change),self.assertRaises(Original409C90SourceError):
                compose(**(good|change))
        for change in (
            {"original_source_status_pointer":0},
            {"original_source_status_record_before":bytes(4)},
            {"original_4ea330_reached_role_argument_byte":True},
            {"original_4ea350_reached_position_argument_byte":-1},
        ):
            with self.subTest(change=change),self.assertRaises(Original409C90SourceError):
                status_write(**(dict(original_source_status_pointer=0x550000,
                     original_source_status_record_before=bytes(5),
                     original_4ea330_reached_role_argument_byte=1,
                     original_4ea350_reached_position_argument_byte=1)|change))

    def test_private_original_pe_exact_4ea33x_4ea35x_4182f0_409c90_sites(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("licensed original exe intentionally omitted from CI")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x4EA330:"8a 41 03",0x4EA334:"8a 5c 24 08",
            0x4EA33A:"32 d3",0x4EA33D:"80 e2 1f",
            0x4EA342:"88 51 03",
            0x4EA350:"8a 41 04",0x4EA354:"8a 5c 24 08",
            0x4EA35A:"32 d3",0x4EA35D:"80 e2 0f",
            0x4EA362:"88 51 04",
            0x4182F3:"83 4e 14 10",
            0x4182F7:"e8 64 fe ff ff",
            0x4182FE:"e8 7d fe ff ff",
            0x418305:"e8 66 fe ff ff",
            0x41830C:"e8 2f f0 ff ff",
            0x40A1F8:"83 f8 01",
            0x40A211:"8b 88 48 02 00 00",
            0x40A21E:"e8 0d 01 0e 00",
            0x40A234:"e8 17 01 0e 00",
            0x40A23B:"e8 b0 e0 00 00",
            0x409BD0:"89 be d8 01 00 00",
            0x40A2A0:"8b 44 24 2c",
            0x40A2A4:"89 46 34",
        }
        for va,expected in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(expected)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)

    def test_source_41fa50_signed_team_key_and_early_return(self):
        from original_native_409c90_assignment_status import source_original_41fa50_player_club_link_predicate as query
        def player(word10,word72):
            b=bytearray(original_player())
            pack_into("<h",b,0x10,word10)
            pack_into("<h",b,0x72,word72)
            return bytes(b)
        base=dict(original_global_8755d0_dword=15,original_reached_club_key_dword=7)
        yes=query(original_player_record=player(3,7),**base)
        self.assertEqual((yes.source_original_return_eax,yes.original_player_signed_word72_if_reached),(1,7))
        for first,second in ((7,7),(15,7),(3,8)):
            with self.subTest(first=first,second=second):
                self.assertEqual(query(original_player_record=player(first,second),**base).source_original_return_eax,0)
        negative=query(original_player_record=player(-1,7),
             original_global_8755d0_dword=0xffffffff,original_reached_club_key_dword=7)
        self.assertEqual(negative.source_original_return_eax,0)
        self.assertIsNone(negative.original_player_signed_word72_if_reached)

    def test_source_4181b0_reset_no_418220_and_reject_bit0_true(self):
        from original_native_409c90_assignment_status import source_original_4181b0_reset_bit0_clear_branch as reset
        p=bytearray(original_player(flags14=0xffffffff))
        pack_into("<I",p,0x174,0xfffffffe)
        v=reset(original_player_native_pointer=0x500000,
                original_player_record_before=bytes(p),
                original_status_record_before=b"\x17\x22\x33\xe5\xb7")
        self.assertEqual(unpack_from("<I",v.source_player_after_literal_stores,0x14)[0],0xffffffcf)
        self.assertEqual(unpack_from("<I",v.source_player_after_literal_stores,0x174)[0],0xfffffffc)
        self.assertEqual(v.source_status_after_4ea370,b"\x17\x22\x33\xf7\xb0")
        self.assertFalse(v.original_418220_called)
        self.assertFalse(v.original_native_4181b0_executed)
        wrong=bytearray(p);pack_into("<I",wrong,0x174,1)
        for changed in (dict(original_player_record_before=bytes(wrong)),
                        dict(original_player_native_pointer=True),
                        dict(original_status_record_before=bytes(3))):
            with self.subTest(changed=changed),self.assertRaises(Original409C90SourceError):
                reset(**(dict(original_player_native_pointer=0x500000,
                         original_player_record_before=bytes(p),
                         original_status_record_before=bytes(5))|changed))

    def test_private_original_reset_and_club_source_pe_sites(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("private original executable not provided")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x41FA50:"0f bf 41 10",0x41FA54:"8b 15 d0 55 87 00",
            0x41FA66:"0f bf 41 72",0x41FA6E:"b8 01 00 00 00",
            0x418150:"8b 41 14",0x418153:"24 ef",0x418160:"8b 41 14",
            0x418163:"24 df",0x418170:"8b 81 74 01 00 00",
            0x418183:"f6 86 74 01 00 00 01",0x41818C:"e8 8f 00 00 00",
            0x4181B3:"e8 98 ff ff ff",0x4181C8:"e8 a3 ff ff ff",
            0x4181D3:"e8 98 21 0d 00",0x4EA370:"8a 41 03",
            0x4EA380:"8a 41 04",0x4EA385:"88 51 03",
            0x4EA388:"88 41 04",
        }
        for va,expected in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(expected)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)

    def test_original_409c90_41fa50_gate_only_calls_4181b0_when_false(self):
        from original_native_409c90_assignment_status import (
            source_original_409c90_reached_41fa50_then_optional_4181b0 as decide)
        def player(owner,linked,extras=0):
            b=bytearray(original_player(flags14=0x33))
            pack_into("<h",b,0x10,owner)
            pack_into("<h",b,0x72,linked)
            pack_into("<I",b,0x174,extras)
            return bytes(b)
        common=dict(original_native_player_pointer=0x500000,
                    original_global_8755d0_dword=12,
                    original_team_club_key_dword=7)
        yes=decide(original_player_record_before_41fa50=player(3,7),
                   original_reached_status_record_for_4181b0_if_called=None,**common)
        self.assertEqual(yes.original_41fa50_source_decision.source_original_return_eax,1)
        self.assertIsNone(yes.original_4181b0_reset_if_reached)
        false=decide(original_player_record_before_41fa50=player(7,7,extras=2),
                     original_reached_status_record_for_4181b0_if_called=b"\x17\x00\x00\x80\xf5",
                     **common)
        self.assertEqual(false.original_41fa50_source_decision.source_original_return_eax,0)
        self.assertEqual(unpack_from("<I",false.original_4181b0_reset_if_reached
                         .source_player_after_reset,0x14)[0],0x03)
        self.assertEqual(false.original_4181b0_reset_if_reached
                         .source_status_after_reset[3:],b"\x97\xf0")
        self.assertFalse(false.live_game_state_modified)
        with self.assertRaises(Original409C90SourceError):
            decide(original_player_record_before_41fa50=player(3,7),
                   original_reached_status_record_for_4181b0_if_called=bytes(5),**common)
        positive=decide(original_player_record_before_41fa50=player(7,7,extras=1),
                        original_reached_status_record_for_4181b0_if_called=bytes(5),**common)
        self.assertTrue(positive.original_4181b0_reset_if_reached.original_418220_was_reached)
        self.assertFalse(positive.live_game_state_modified)
        with self.assertRaises(Original409C90SourceError):
            decide(original_player_record_before_41fa50=player(7,7),
                   original_reached_status_record_for_4181b0_if_called=None,**common)

    def test_418220_status_low_fields_exchange_and_full_saved_byte_replace(self):
        from original_native_409c90_assignment_status import (
            source_original_418220_exact_role_position_exchange as swap)
        raw=bytearray(original_player(flags14=0x23))
        raw[0x152]=0xA6
        raw[0x153]=0xB9
        status=b"\x07\x18\x00\xe5\xc3"
        v=swap(original_native_player_pointer=0x500000,
               original_player_record_before_418220=bytes(raw),
               original_status_record_before_418220=status)
        # Masked old status getters 4EA3C0/4EA3D0 become FULL saved
        # player bytes; old full saved bytes become status LOW bits.
        self.assertEqual(v.original_status_role_low5_before,0x05)
        self.assertEqual(v.original_status_position_low4_before,0x03)
        self.assertEqual(v.original_player_saved_role_byte_before,0xA6)
        self.assertEqual(v.original_player_saved_position_byte_before,0xB9)
        self.assertEqual(v.source_player_after_418220[0x152:0x154],b"\x05\x03")
        self.assertEqual(v.source_status_after_418220[3:],b"\xe6\xc9")
        self.assertEqual(unpack_from("<I",v.source_player_after_418220,0x14),
                         unpack_from("<I",bytes(raw),0x14))
        self.assertFalse(v.native_418220_executed)
        self.assertFalse(v.original_world_committed)
        for changed in (
            {"original_native_player_pointer":0},
            {"original_player_record_before_418220":bytes(3)},
            {"original_player_record_before_418220":original_player(status_pointer=0)},
            {"original_status_record_before_418220":bytes(3)},
            {"original_status_record_before_418220":bytearray(5)},
        ):
            with self.subTest(changed=str(changed)[:90]),self.assertRaises(Original409C90SourceError):
                swap(**(dict(original_native_player_pointer=0x500000,
                     original_player_record_before_418220=bytes(raw),
                     original_status_record_before_418220=status)|changed))

    def test_4181b0_full_status_reset_both_418180_exchange_paths(self):
        from original_native_409c90_assignment_status import (
            source_original_4181b0_full_player_reset as full)
        p=bytearray(original_player(flags14=0xFFFFFFFF))
        p[0x152]=0xA6;p[0x153]=0xB9
        original_status=b"\x17\x18\x00\xe5\xc3"
        for flags174,expect_saved in (
            (0x00000002,b"\xa6\xb9"),
            (0x00000003,b"\x05\x03"),
            (0x80000001,b"\x05\x03"),
        ):
            with self.subTest(flags174=flags174):
                pack_into("<I",p,0x174,flags174)
                r=full(original_native_player_pointer=0x500000,
                    original_player_record_before=bytes(p),
                    original_status_record_before=original_status)
                self.assertEqual(r.original_418220_was_reached,bool(flags174&1))
                self.assertEqual(r.original_418220_source_exchange_if_reached is not None,
                                 bool(flags174&1))
                self.assertEqual(r.source_player_after_reset[0x152:0x154],expect_saved)
                self.assertEqual(unpack_from("<I",r.source_player_after_reset,0x14)[0],
                                 0xFFFFFFCF)
                self.assertEqual(unpack_from("<I",r.source_player_after_reset,0x174)[0],
                                 flags174 & ~3)
                self.assertEqual(r.source_status_after_reset,
                                 b"\x17\x18\x00\xf7\xc0")
                self.assertEqual(r.original_player_before_reset,bytes(p))
                self.assertFalse(r.native_original_4181b0_executed)
                self.assertFalse(r.live_game_state_modified)

    def test_original_418220_exchange_private_pe_opcode_chain(self):
        p=environ.get("FM2001_ORIGINAL_EXE")
        if not p:self.skipTest("private original executable not available")
        b=Path(p).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x418183:"f6 86 74 01 00 00 01",
            0x41818c:"e8 8f 00 00 00",
            0x418197:"24 fe",
            0x418199:"89 86 74 01 00 00",
            0x418220:"51 53 56",
            0x418225:"8b 8e 48 02 00 00",
            0x41822b:"e8 90 21 0d 00",
            0x418236:"8a d8",
            0x418238:"e8 93 21 0d 00",
            0x418243:"88 44 24 0b",
            0x418249:"8a 86 52 01 00 00",
            0x418250:"e8 db 20 0d 00",
            0x418255:"8a 8e 53 01 00 00",
            0x418262:"e8 e9 20 0d 00",
            0x418267:"8a 54 24 0b",
            0x41826b:"88 9e 52 01 00 00",
            0x418271:"88 96 53 01 00 00",
            0x4EA3C0:"8a 41 03",
            0x4EA3C3:"83 e0 1f",
            0x4EA3D0:"8a 41 04",
            0x4EA3D3:"24 0f",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(hx)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)

    def test_original_409c90_class2_or3_418130_per_player_mask(self):
        from original_native_409c90_assignment_status import (
            source_original_409c90_class23_initial_roster_mask as source)
        from original_native_406be0_roster_count import SourceOriginal406BE0Player
        team=bytearray(0x298)
        team[0x74]=2
        pack_into("<i",team,0x294,4)
        rows=[]
        for i,(pid,flags) in enumerate(((51,0),(52,1),(53,2),(54,3))):
            pack_into("<H",team,0x244+2*i,pid)
            player=bytearray(original_player(flags14=flags))
            rows.append(SourceOriginal406BE0Player(
                pid,0x40000000+pid*0x250,bytes(player),bytes(5)))
        args=dict(original_team_record_at_409c90=bytes(team),
                  original_409b50_reached_roster_count_argument=4,
                  original_global_875640_player_base=0x40000000,
                  original_ordered_player_records=tuple(rows))
        x=source(**args)
        self.assertEqual(x.original_native_team_type_byte74,2)
        self.assertEqual(x.original_ordered_source_player_ids,(51,52,53,54))
        self.assertEqual(x.original_418130_return_byte_values,(0,1,1,1))
        self.assertEqual(x.source_second_allocated_mask_bytes,b"\x00\x01\x01\x01")
        self.assertFalse(x.native_418130_executed)
        self.assertFalse(x.native_409c90_executed)
        self.assertFalse(x.live_game_state_modified)
        for cls in (3,):
            team[0x74]=cls
            self.assertEqual(source(**(args|{"original_team_record_at_409c90":bytes(team)}))
                             .source_second_allocated_mask_bytes,b"\x00\x01\x01\x01")
        for changed in (
            {"original_global_875640_player_base":0},
            {"original_409b50_reached_roster_count_argument":True},
            {"original_409b50_reached_roster_count_argument":361},
            {"original_ordered_player_records":tuple(rows[:-1])},
            {"original_ordered_player_records":tuple(reversed(rows))},
        ):
            with self.subTest(changed=str(changed)[:75]),self.assertRaises(Original409C90SourceError):
                source(**(args|changed))
        team[0x74]=0
        with self.assertRaises(Original409C90SourceError):
            source(**(args|{"original_team_record_at_409c90":bytes(team)}))

    def test_original_409c90_418130_source_byte_mask_private_pe(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("private source executable unavailable in CI")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x409CEA:"8b 4c 24 1c",
            0x409CEE:"e8 4d 99 ff ff",
            0x409D12:"e8 29 99 ff ff",
            0x409D17:"3c 01",
            0x409D19:"74 29",
            0x409D44:"33 c0",
            0x409D46:"66 8b 07",
            0x409D4F:"a1 40 56 87 00",
            0x409D59:"e8 d2 e3 00 00",
            0x409D5E:"88 04 2e",
            0x418130:"f6 41 14 03",
            0x418134:"0f 95 c0",
            0x418137:"c3",
        }
        for va,sig in sites.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(sig)
                self.assertEqual(b[va-0x400000:va-0x400000+len(bs)],bs)

    def test_source_4182f0_assignment_authentic_417340_gate_and_two_bit0_paths(self):
        from dataclasses import replace
        from original_native_409c90_assignment_status import (
            source_original_4182f0_assignment_without_reached_41edf0 as assign)
        from original_native_417340_registered_user_gate import Original417340RegisteredUserReceipt

        def source_receipt(p,matched):
            return Original417340RegisteredUserReceipt(
                original_native_player_at_call=p,
                original_native_player_id=unpack_from("<H",p,4)[0],
                original_current_club_index_signed=unpack_from("<h",p,0x10)[0],
                original_source_club_pointer=0x600000,
                original_source_club_owner_key=7,
                original_visited_manager_link_pointers=(0x700000,) if matched else (),
                original_matching_user_pointer=0x500000 if matched else None,
                original_417340_return_al=int(matched))

        for flag174,flag14,matched in ((0,0,True),(1,0,True),(3,0x2000,False)):
            with self.subTest(flag174=flag174,flag14=flag14,matched=matched):
                original=bytearray(original_player(flags14=flag14))
                pack_into("<h",original,0x10,7)
                pack_into("<I",original,0x174,flag174)
                original[0x152]=0xA6
                original[0x153]=0xB9
                status=b"\x17\x00\x00\xe5\xc3"
                post=bytearray(original)
                pack_into("<I",post,0x14,(flag14|0x10)&~0x20)
                pack_into("<I",post,0x174,flag174&~3)
                if flag174&1:
                    post[0x152]=5
                    post[0x153]=3
                args=dict(original_native_player_pointer=0x500000,
                    original_player_record_before_4182f0=bytes(original),
                    original_status_record_before_4182f0=status,
                    original_417340_source_receipt_after_mutations=source_receipt(bytes(post),matched))
                r=assign(**args)
                self.assertEqual(r.original_player_after_4182f0,bytes(post))
                self.assertEqual(r.original_417340_registered_user_al,int(matched))
                self.assertEqual(r.original_418220_exchange_if_reached is not None,bool(flag174&1))
                self.assertEqual(r.original_status_after_4182f0[3:],
                                 b"\xe6\xc9" if flag174&1 else b"\xe5\xc3")
                self.assertFalse(r.original_41edf0_was_reached)
                self.assertFalse(r.native_4182f0_executed)
                self.assertFalse(r.live_game_state_modified)
                if not matched:
                    wrong=bytearray(post)
                    pack_into("<I",wrong,0x14,0x10)
                    with self.assertRaises(Original409C90SourceError):
                        assign(**(args|{"original_417340_source_receipt_after_mutations":
                            source_receipt(bytes(wrong),False)}))
                with self.assertRaises(Original409C90SourceError):
                    assign(**(args|{"original_417340_source_receipt_after_mutations":
                        replace(source_receipt(bytes(post),matched),
                            original_417340_return_al=int(not matched))}))
                with self.assertRaises(Original409C90SourceError):
                    assign(**(args|{"original_417340_source_receipt_after_mutations":None}))

        # Native 418321 calls 41EDF0 when non-human AND +14 bit13 is clear.
        p=original_player(flags14=0)
        post=bytearray(p);pack_into("<I",post,0x14,0x10)
        with self.assertRaises(Original409C90SourceError):
            assign(original_native_player_pointer=0x500000,
                original_player_record_before_4182f0=p,
                original_status_record_before_4182f0=bytes(5),
                original_417340_source_receipt_after_mutations=source_receipt(bytes(post),False))

    def test_private_original_4182f0_postassignment_callback_branch(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("private PE source optional in CI")
        b=Path(path).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x4182F3:"83 4e 14 10",
            0x4182F7:"e8 64 fe ff ff",
            0x4182FE:"e8 7d fe ff ff",
            0x418305:"e8 66 fe ff ff",
            0x41830C:"e8 2f f0 ff ff",
            0x418311:"84 c0",
            0x418313:"75 11",
            0x418315:"8b 46 14",
            0x418318:"c1 e8 0d",
            0x41831B:"a8 01",
            0x41831D:"75 07",
            0x418321:"e8 ca 6a 00 00",
            0x418326:"5e c3",
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(bs)],bs)
