"""Check EA444 pre-IDCT grids against firsthand original source data."""
import hashlib
import os
from pathlib import Path
import struct
import unittest

from ea444_bits import reader_for_ea444
from ea444_coefficients import EA444CoefficientBlock, read_coefficient_block
from ea444_quantization import EA444Quantization, quantization_from_verified_exe_path
from ea444_quantized_block import (
    EA444BlockGridError, EA444QuantizedBlock, make_quantized_block,
)
from ea444_tables import EA444Tables, tables_from_verified_exe_path

ORIGINAL_SCROLL_DIR = (Path(__file__).resolve().parent.parent
                       / "original_assets/source/FM2001_Art/Generic/GenericButtonsAndBars")


def synthetic_tables():
    section = bytearray(0x420)
    struct.pack_into("<64I", section, 0xA0, *range(64))
    struct.pack_into("<160I", section, 0x1A0, *([0x00040102] * 160))
    struct.pack_into("<I", section, 0x1B0, 0x00024100)
    return EA444Tables.from_section(bytes(section))


def synthetic_quant():
    return EA444Quantization(
        tuple(range(1, 65)),
        tuple(8 * x for x in range(1, 65)),
    )


class EA444QuantizedBlockTests(unittest.TestCase):
    def test_zero_ac_original_orthogonal_scroll_caps_remain_zero_grids(self):
        for name in ("hscroll_end.444", "vscroll_end.444"):
            with self.subTest(name=name):
                header, reader = reader_for_ea444(
                    (ORIGINAL_SCROLL_DIR / name).read_bytes()
                )
                raw = read_coefficient_block(reader, synthetic_tables())
                grid = make_quantized_block(raw, synthetic_quant())
                self.assertEqual(grid.nonzero, ())
                self.assertEqual(grid.signed_fixed, (0,) * 64)
                self.assertEqual(raw.consumed_bits, 10)

    def test_sparse_source_coefficients_map_to_source_positions_and_signs(self):
        raw = EA444CoefficientBlock(
            scale_code=7, coefficients=((8, 1), (19, -2), (63, 3)),
            consumed_bits=30, termination="table-end-marker",
        )
        grid = make_quantized_block(raw, synthetic_quant())
        self.assertEqual(grid.nonzero, (
            (0, 56), (8, 72), (19, -320), (63, 1536),
        ))

    def test_rejects_duplicate_dc_and_corrupted_positions(self):
        for entries in (((0, 1),), ((8, 1), (8, 2)), ((64, 1),), ((-1, 1),)):
            with self.subTest(entries=entries):
                raw = EA444CoefficientBlock(2, entries, 10, "table-end-marker")
                with self.assertRaises(EA444BlockGridError):
                    make_quantized_block(raw, synthetic_quant())
        with self.assertRaises(EA444BlockGridError):
            EA444QuantizedBlock((0,))

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Original licensed menu asset and executable not bundled with CI",
    )
    def test_real_first_menu_component_has_exact_quantized_grid(self):
        original_root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        tables = tables_from_verified_exe_path(exe)
        quant = quantization_from_verified_exe_path(exe)
        source = (
            original_root / "Generic/main_menu/main_menu_bground.444"
        ).read_bytes()
        _, reader = reader_for_ea444(source)
        block = make_quantized_block(
            read_coefficient_block(reader, tables), quant
        )
        self.assertEqual(block.nonzero[:7], (
            (0, 983040), (1, 47248), (3, 55736),
            (7, 237536), (8, 47248), (9, 34064),
            (18, -76784),
        ))
        self.assertEqual(len(block.nonzero), 15)
        self.assertEqual(
            hashlib.sha256(struct.pack("<64i", *block.signed_fixed)).hexdigest(),
            "d074fa03f380438bfccbdf88dc2375f700434891889399e4750fc7bc2c75c2d7",
        )


if __name__ == "__main__":
    unittest.main()
