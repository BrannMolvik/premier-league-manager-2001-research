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
