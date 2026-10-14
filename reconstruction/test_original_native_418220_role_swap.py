"""Original 418220 first/reserve native role exchange regression."""
from __future__ import annotations
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest
from original_native_418220_role_swap import (
    Original418220RoleSourceError,source_original_418220_role_swap_from_reached,
)


def player(active=0,role=29,aux=14,ptr=0x3000):
    b=bytearray(0x24c)
    pack_into("<H",b,4,77)
    pack_into("<I",b,0x248,ptr)
    pack_into("<I",b,0x174,active)
    b[0x152]=role
    b[0x153]=aux
    return bytes(b)


def swap(raw=None,object_raw=b"\x11\x22\x33\xb3\xa7",pointer=0x3000):
    return source_original_418220_role_swap_from_reached(
        original_player_at_418220=player() if raw is None else raw,
        original_source_role_object_pointer=pointer,
        original_source_role_object_at_418220=object_raw,
    )


class Original418220RoleSwapTests(unittest.TestCase):
    def test_low5_and_low4_replaced_while_object_high_bits_preserved(self):
        p=player(role=0x9d,aux=0xbe,active=3)
        r=swap(raw=p,object_raw=b"\x11\x22\x33\xb3\xa7")
        self.assertEqual(r.original_player_id,77)
        self.assertEqual(r.original_former_active_role_code,0x13)
        self.assertEqual(r.original_former_active_aux_code,7)
        self.assertEqual((r.original_former_reserve_role_152,r.original_former_reserve_aux_153),
                         (0x9d,0xbe))
        self.assertEqual(r.original_player_after_418220[0x152:0x154],bytes((0x13,7)))
        # Masked 4EA330/4EA350 changes only 3 low5 and 4 low4.
        self.assertEqual(r.original_source_role_object_after_418220,b"\x11\x22\x33\xbd\xae")
        self.assertEqual(unpack_from("<I",r.original_player_after_418220,0x174)[0],3)
        self.assertFalse(r.native_418220_executed)
        self.assertFalse(r.live_game_state_updated)

    def test_identical_or_zero_native_roles_are_not_special_cased(self):
        r=swap(raw=player(role=0,aux=0,active=1),
               object_raw=b"\x00\x00\x00\xf0\xf0")
        self.assertEqual(r.original_source_role_object_after_418220[3:5],b"\xe0\xf0")
        self.assertEqual(r.original_player_after_418220[0x152:0x154],b"\x10\x00")

    def test_failclosed_native_player_pointer_and_object_size(self):
        with self.assertRaisesRegex(Original418220RoleSourceError,"through"):
            swap(raw=b"")
        with self.assertRaisesRegex(Original418220RoleSourceError,"object bytes"):
            swap(object_raw=b"")
        with self.assertRaisesRegex(Original418220RoleSourceError,"identity"):
            swap(pointer=0x9000)
        with self.assertRaisesRegex(Original418220RoleSourceError,"pointer"):
            swap(pointer=0)
        with self.assertRaisesRegex(Original418220RoleSourceError,"pointer"):
            swap(pointer=True)

    def test_private_exact_original_opcode_signatures_when_available(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("original executable kept private outside GitHub")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
             "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        source={
            0x418220:"51 53 56 8b f1",
            0x418225:"8b 8e 48 02 00 00",
            0x41822b:"e8 90 21 0d 00",
            0x418230:"8b 8e 48 02 00 00",
            0x418236:"8a d8",
            0x418238:"e8 93 21 0d 00",
            0x418249:"8a 86 52 01 00 00",
            0x418250:"e8 db 20 0d 00",
            0x418255:"8a 8e 53 01 00 00",
            0x418262:"e8 e9 20 0d 00",
            0x41826b:"88 9e 52 01 00 00",
            0x418271:"88 96 53 01 00 00",
            0x4ea330:"8a 41 03 53 8a 5c 24 08",
            0x4ea340:"32 d0 88 51 03",
            0x4ea350:"8a 41 04 53 8a 5c 24 08",
            0x4ea360:"32 d0 88 51 04",
        }
        for va,pattern in source.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(pattern)
                self.assertEqual(data[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
