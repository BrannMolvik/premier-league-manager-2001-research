"""Original EA444 coefficient order and tiered Huffman-table regressions."""
from hashlib import sha256
import os
from pathlib import Path
import struct
import unittest

from ea444_tables import (
    EA444TableError, EA444Tables, EA444VLCEntry,
    tables_from_verified_exe_path,
)


def fixture_section():
    data = bytearray(0x420)
    struct.pack_into("<64I", data, 0xa0, *range(64))
    struct.pack_into("<160I", data, 0x1a0, *([0x00040102] * 160))
    struct.pack_into("<I", data, 0x1b0, 0x00024100)
    return bytes(data)


class EA444TableTests(unittest.TestCase):
    def test_tiered_17bit_dispatch_uses_original_executable_offsets(self):
        tab = EA444Tables.from_section(fixture_section())
        self.assertEqual(tab.lookup(0x10040), EA444VLCEntry(0, 0x41, 2))
        self.assertTrue(tab.lookup(0x10040).end_of_block)
        self.assertIsNone(tab.lookup(0))
        self.assertIsNone(tab.lookup(0x1f))
        for prefix in (
            0x20, 0x40, 0x80, 0x100, 0x200, 0x400,
            0x800, 0x8000, 0x1ffff,
        ):
            self.assertIsInstance(tab.lookup(prefix), EA444VLCEntry)
        for bad in (-1, 1 << 17):
            with self.assertRaises(EA444TableError):
                tab.lookup(bad)

    def test_fail_closed_on_truncated_or_invalid_tables(self):
        data = fixture_section()
        for bad in (data[:-1], data + b"x"):
            with self.assertRaises(EA444TableError):
                EA444Tables.from_section(bad)
        altered = bytearray(data)
        struct.pack_into("<I", altered, 0xa0, 99)
        with self.assertRaises(EA444TableError):
            EA444Tables.from_section(bytes(altered))
        altered = bytearray(data)
        struct.pack_into("<I", altered, 0x1a0, 0x00000102)
        with self.assertRaises(EA444TableError):
            EA444Tables.from_section(bytes(altered))

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE"),
        "Private licensed original exe unavailable in standard CI",
    )
    def test_actual_verified_original_executable_embeds_exact_tables(self):
        tab = tables_from_verified_exe_path(
            Path(os.environ["FM2001_ORIGINAL_EXE"])
        )
        self.assertEqual(len(tab.zigzag), 64)
        self.assertEqual(tab.zigzag[:4], (0, 63, 55, 62))
        self.assertEqual(tab.zigzag[-4:], (9, 2, 1, 8))
        self.assertEqual(
            sha256(tab.raw_section).hexdigest(),
            "c62a13efbb812fb2157c067aaa3eae8afbbb52283dc5dc3eaf6cb86c5a11e8da",
        )
        self.assertEqual(tab.lookup(0x10040), EA444VLCEntry(0, 65, 2))
        self.assertEqual(tab.lookup(0x800), EA444VLCEntry(0, 66, 6))
        self.assertEqual(tab.lookup(0x8000), EA444VLCEntry(2, 1, 4))
        self.assertEqual(tab.lookup(0x1ffff), EA444VLCEntry(1, 1, 2))
        for prefix in range(0x20, 1 << 17):
            self.assertIsNotNone(tab.lookup(prefix))


if __name__ == "__main__":
    unittest.main()
