"""Partial original EA444 coefficient entropy decoding regression coverage."""
from pathlib import Path
import os
import struct
import unittest

from ea444_bits import EA444BitReader, reader_for_ea444
from ea444_coefficients import EA444CoefficientBlock, read_coefficient_block
from ea444_tables import EA444Tables, tables_from_verified_exe_path


def fixture_tables():
    section = bytearray(0x420)
    struct.pack_into("<64I", section, 0xA0, *range(64))
    struct.pack_into("<160I", section, 0x1A0, *([0x00040102] * 160))
    struct.pack_into("<I", section, 0x1B0, 0x00024100)
    struct.pack_into("<I", section, 0x1C8, 0x00064200)
    return EA444Tables.from_section(bytes(section))


def stream(logical_bits):
    logical_bits += "0" * ((-len(logical_bits)) % 32)
    return b"".join(
        int(logical_bits[i:i+32], 2).to_bytes(4, "little")
        for i in range(0, len(logical_bits), 32)
    )


class EA444CoefficientTests(unittest.TestCase):
    def test_first_real_tiny_fixture_matches_original_end_marker(self):
        root = (Path(__file__).resolve().parent.parent
                / "original_assets/source/FM2001_Art/Generic/GenericButtonsAndBars")
        for name in ("hscroll_end.444", "vscroll_end.444"):
            with self.subTest(name=name):
                _, bits = reader_for_ea444((root / name).read_bytes())
                result = read_coefficient_block(bits, fixture_tables())
                self.assertEqual(
                    result, EA444CoefficientBlock(0, (), 10, "table-end-marker")
                )

    def test_signed_normal_coefficient_and_explicit_end_marker(self):
        bits = EA444BitReader(
            stream("00000111" + "1111" + "1" + f"{0x10040:017b}")
        )
        result = read_coefficient_block(bits, fixture_tables())
        self.assertEqual(
            result, EA444CoefficientBlock(
                7, ((63, -2),), 15, "table-end-marker",
            )
        )

    def test_original_escape_signed_extension_and_zigzag_rank(self):
        bits = EA444BitReader(
            stream(
                "00000011" + "111000" + f"{(3 << 8) | 0x80:014b}"
                + "00000101" + f"{0x10040:017b}"
            )
        )
        result = read_coefficient_block(bits, fixture_tables())
        self.assertEqual(
            result, EA444CoefficientBlock(
                3, ((60, -251),), 38, "table-end-marker",
            )
        )

    def test_immediate_short_end_marker_does_not_consume_bits(self):
        bits = EA444BitReader(stream("00000111" + "0" * 24))
        result = read_coefficient_block(bits, fixture_tables())
        self.assertEqual(
            result, EA444CoefficientBlock(
                7, (), 8, "short-end-marker",
            )
        )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Private licensed original graphic and executable required",
    )
    def test_actual_main_menu_first_component_sparse_coefficients(self):
        tables = tables_from_verified_exe_path(
            Path(os.environ["FM2001_ORIGINAL_EXE"])
        )
        source = (
            Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
            / "Generic/main_menu/main_menu_bground.444"
        ).read_bytes()
        _, bits = reader_for_ea444(source)
        result = read_coefficient_block(bits, tables)
        self.assertEqual(result.scale_code, 15)
        self.assertEqual(result.consumed_bits, 93)
        self.assertEqual(
            result.coefficients,
            (
                (8, 1), (1, 1), (9, 1), (3, 1), (18, -2), (19, -1),
                (35, -1), (28, -1), (7, 1), (36, -2), (37, -1),
                (53, -1), (54, -1), (55, -1),
            ),
        )


if __name__ == "__main__":
    unittest.main()
