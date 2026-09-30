import hashlib
import os
from pathlib import Path
import struct
import unittest

from ea_language_strings import (
    EALanguageFormatError,
    EAStringIndex,
    EAStringTable,
    parse_language_pair,
)


def make_str(values: tuple[str, ...]) -> bytes:
    blob = bytearray()
    offsets = []
    for item in values:
        offsets.append(len(blob))
        blob.extend(item.encode("cp1252") + b"\x00")
    return (
        struct.pack("<II", len(blob), len(values))
        + blob
        + struct.pack(f"<{len(offsets)}I", *offsets)
    )


class EAOriginalLanguageTests(unittest.TestCase):
    def test_str_offsets_and_idx_are_distinct_layers(self):
        original = ("Europe", "Start New Game", "Quit to Windows", "Team Selection")
        strings, index = parse_language_pair(
            make_str(original),
            struct.pack("<5H", 1, 0, 3, 2, 1),
        )
        self.assertEqual(strings.payload_size, sum(len(x) + 1 for x in original))
        self.assertEqual(strings.offsets, (0, 7, 22, 38))
        self.assertEqual(strings[2], "Quit to Windows")
        self.assertEqual(index.string_ids, (1, 0, 3, 2, 1))
        self.assertEqual(index.resolve(strings, 0), "Start New Game")
        self.assertEqual(index.resolve(strings, 4), "Start New Game")

    def test_cp1252_smart_punctuation_is_preserved(self):
        strings = EAStringTable.from_bytes(make_str(("Player’s wage", "Café")))
        self.assertEqual(strings.strings, ("Player’s wage", "Café"))

    def test_rejects_truncated_or_overlong_str(self):
        data = make_str(("Menu", "Team"))
        for bad in (data[:7], data[:-1], data + b"junk"):
            with self.subTest(bad=bad[-8:]):
                with self.assertRaises(EALanguageFormatError):
                    EAStringTable.from_bytes(bad)

    def test_rejects_out_of_order_and_mid_string_offsets(self):
        data = bytearray(make_str(("Menu", "Team")))
        payload_size, _ = struct.unpack_from("<II", data)
        for wrong_offset in (1, 0, payload_size + 1):
            bad = bytearray(data)
            struct.pack_into("<I", bad, 8 + payload_size + 4, wrong_offset)
            with self.subTest(offset=wrong_offset):
                with self.assertRaises(EALanguageFormatError):
                    EAStringTable.from_bytes(bad)

    def test_rejects_unterminated_and_unindexed_trailing_strings(self):
        broken = bytearray(make_str(("Menu", "Team")))
        broken[-9] = ord("!")
        with self.assertRaises(EALanguageFormatError):
            EAStringTable.from_bytes(broken)

        broken = bytearray(make_str(("Menu", "Team")))
        blob_size = struct.unpack_from("<I", broken)[0]
        # Append an otherwise valid payload byte that is not covered by an
        # offset, keeping the index table aligned with the changed header.
        broken.insert(8 + blob_size, 0)
        struct.pack_into("<I", broken, 0, blob_size + 1)
        with self.assertRaises(EALanguageFormatError):
            EAStringTable.from_bytes(broken)

    def test_rejects_malformed_or_out_of_range_idx(self):
        table = EAStringTable.from_bytes(make_str(("A", "B")))
        for data in (b"", b"\x00", struct.pack("<H", 2)):
            with self.subTest(data=data):
                with self.assertRaises(EALanguageFormatError):
                    EAStringIndex.from_bytes(data, table)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_LANGUAGE_DIR"),
        "Original licensed language assets are intentionally absent from CI",
    )
    def test_optional_firsthand_original_english_asset_evidence(self):
        root = Path(os.environ["FM2001_ORIGINAL_LANGUAGE_DIR"])
        raw_strings = (root / "English.str").read_bytes()
        raw_idx = (root / "English.idx").read_bytes()
        self.assertEqual(
            hashlib.sha256(raw_strings).hexdigest(),
            "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601",
        )
        self.assertEqual(
            hashlib.sha256(raw_idx).hexdigest(),
            "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1",
        )
        strings, index = parse_language_pair(raw_strings, raw_idx)
        self.assertEqual((strings.payload_size, len(strings.strings)), (282212, 21856))
        self.assertEqual(len(index.string_ids), 2714)
        self.assertEqual(
            tuple(index.resolve(strings, i) for i in range(9)),
            (
                "Continue", "Start New Game", "Load Game", "Save Game",
                "Settings", "Virtual Managers", "Quit to Windows",
                "Main Menu", "Team Selection",
            ),
        )


if __name__ == "__main__":
    unittest.main()
