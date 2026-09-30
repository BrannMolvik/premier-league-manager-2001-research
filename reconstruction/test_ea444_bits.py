"""Firsthand original source and cross-word bit-order regressions."""
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

from ea444_bits import EA444BitReader, EA444BitstreamError, reader_for_ea444

ASSETS = (Path(__file__).resolve().parent.parent
          / "original_assets/source/FM2001_Art/Generic/GenericButtonsAndBars")


class EA444OriginalBitstreamTests(unittest.TestCase):
    def test_original_orthogonal_scroll_ends_have_identical_bitstream(self):
        results = []
        for filename, dimensions, digest in (
            ("hscroll_end.444", (1, 18),
             "a8ccf6c5a9f9705ebe54650e5a25146791ac3ec2d886e60a9ff249dba7b962b0"),
            ("vscroll_end.444", (18, 1),
             "c05393b27221b8951b15fcc4e096290851e9414020ae2e94091c18a66a110783"),
        ):
            source = (ASSETS / filename).read_bytes()
            self.assertEqual(sha256(source).hexdigest(), digest)
            header, bits = reader_for_ea444(source)
            self.assertEqual((header.width, header.height), dimensions)
            self.assertEqual(bits.bits_remaining, 96)
            values = [bits.read(8) for _ in range(12)]
            self.assertEqual(bits.bits_remaining, 0)
            results.append(values)
        self.assertEqual(results[0], [0, 128, 32, 8, 1, 0, 64, 16, 2, 0, 128, 32])
        self.assertEqual(results[0], results[1])

    def test_executable_style_bitreader_handles_cross_word_lookups(self):
        payload = bytes.fromhex("08 20 80 00 10 40 00 01 20 80 00 02")
        reference = "".join(
            f"{int.from_bytes(payload[i:i+4], 'little'):032b}"
            for i in range(0, len(payload), 4)
        )
        for offset, width in (
            (0, 8), (6, 11), (23, 10), (28, 8),
            (31, 32), (50, 19), (92, 4),
        ):
            with self.subTest(offset=offset, width=width):
                reader = EA444BitReader(payload, bit_position=offset)
                self.assertEqual(reader.read(width), int(reference[offset:offset+width], 2))
                self.assertEqual(reader.bit_position, offset + width)

    def test_rejects_truncation_invalid_width_and_unaligned_payloads(self):
        with self.assertRaises(EA444BitstreamError):
            EA444BitReader(b"abc")
        for value in (-1, 33):
            with self.assertRaises(EA444BitstreamError):
                EA444BitReader(b"\\0\\0\\0\\0", bit_position=value)
        reader = EA444BitReader(b"\\0\\0\\0\\0")
        for width in (0, 33, -1):
            with self.assertRaises(EA444BitstreamError):
                reader.read(width)
        reader.read(29)
        with self.assertRaises(EA444BitstreamError):
            reader.read(4)

    @unittest.skipUnless(
        os.environ.get("FM2001_GATE13_CATALOG"),
        "Private original disc catalog unavailable in standard CI",
    )
    def test_optional_full_actual_disc_all_444_payloads_dword_aligned(self):
        report = json.loads(Path(os.environ["FM2001_GATE13_CATALOG"]).read_text())
        found = [(path, size) for path, size, *_ in report["disc_files"]
                 if path.lower().endswith(".444")]
        self.assertEqual(len(found), 1354)
        self.assertTrue(all(size > 8 and (size - 8) % 4 == 0
                            for _, size in found))


if __name__ == "__main__":
    unittest.main()
