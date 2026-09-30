"""Original .444 format tests using two tiny byte-identical source files."""
from hashlib import sha256
import os
from pathlib import Path
import struct
import unittest

from ea444_header import (
    EA444FormatError,
    ORIGINAL_DESCRIPTOR,
    parse_ea444_file,
    parse_ea444_header,
)


class EA444HeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_root = (
            Path(__file__).resolve().parent.parent
            / "original_assets/source/FM2001_Art/Generic/GenericButtonsAndBars"
        )

    def test_real_scroll_end_assets_share_identical_compressed_payload(self):
        a = (self.original_root / "hscroll_end.444").read_bytes()
        b = (self.original_root / "vscroll_end.444").read_bytes()

        self.assertEqual(len(a), 20)
        self.assertEqual(len(b), 20)
        self.assertEqual(
            sha256(a).hexdigest(),
            "a8ccf6c5a9f9705ebe54650e5a25146791ac3ec2d886e60a9ff249dba7b962b0",
        )
        self.assertEqual(
            sha256(b).hexdigest(),
            "c05393b27221b8951b15fcc4e096290851e9414020ae2e94091c18a66a110783",
        )
        h = parse_ea444_header(a)
        v = parse_ea444_header(b)
        self.assertEqual((h.width, h.height), (1, 18))
        self.assertEqual((v.width, v.height), (18, 1))
        self.assertEqual(h.descriptor, ORIGINAL_DESCRIPTOR)
        self.assertEqual(h.rgb_triplet, (255, 0, 255))
        self.assertEqual(h.payload_size, 12)
        self.assertEqual(a[8:], b[8:])
        self.assertEqual(h.padded_size, (8, 24))
        self.assertEqual(v.padded_size, (24, 8))
        self.assertEqual((h.encoded_block_count, v.encoded_block_count), (3, 3))
        self.assertEqual(parse_ea444_file(self.original_root / "vscroll_end.444"), v)

    def test_original_tall_atlas_geometry_remains_legal(self):
        # Real source includes a 30 x 4845 animation atlas.
        header = parse_ea444_header(
            struct.pack("<HH", 30, 4845) + ORIGINAL_DESCRIPTOR + b"fixture"
        )
        self.assertEqual(header.padded_size, (32, 4848))
        self.assertEqual(header.encoded_block_count, 4 * 606)

    def test_header_error_cases_fail_closed(self):
        for data in (
            b"",
            b"\x01\x00\x01\x00",
            struct.pack("<HH", 0, 8) + ORIGINAL_DESCRIPTOR + b"data",
            struct.pack("<HH", 8, 0) + ORIGINAL_DESCRIPTOR + b"data",
            struct.pack("<HH", 8, 8) + ORIGINAL_DESCRIPTOR,
            struct.pack("<HH", 8, 8) + b"????" + b"data",
        ):
            with self.subTest(data=data[:8]):
                with self.assertRaises(EA444FormatError):
                    parse_ea444_header(data)

    def test_nonstandard_descriptor_is_only_allowed_when_explicit(self):
        data = struct.pack("<HH", 1, 2) + b"test" + b"compressed"
        with self.assertRaises(EA444FormatError):
            parse_ea444_header(data)
        self.assertEqual(
            parse_ea444_header(data, require_original_descriptor=False).descriptor,
            b"test",
        )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Licensed original loose art tree is intentionally omitted from CI",
    )
    def test_optional_actual_full_size_original_background(self):
        path = (
            Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
            / "Generic/bground.444"
        )
        data = path.read_bytes()
        self.assertEqual(
            sha256(data).hexdigest(),
            "9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9",
        )
        h = parse_ea444_header(data)
        self.assertEqual((h.width, h.height), (800, 600))
        self.assertEqual(h.padded_size, (800, 600))
        self.assertEqual(h.encoded_block_count, 100 * 75)


if __name__ == "__main__":
    unittest.main()
