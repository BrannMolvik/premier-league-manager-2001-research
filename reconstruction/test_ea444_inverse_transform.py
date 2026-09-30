import hashlib
import os
from pathlib import Path
import struct
import unittest

from ea444_bits import reader_for_ea444
from ea444_coefficients import read_coefficient_block
from ea444_inverse_transform import (
    EA444InverseTransformError,
    EA444TransformConstants,
    inverse_8x8,
    inverse_first_pass_1d,
    inverse_second_pass_1d,
)
from ea444_quantization import quantization_from_verified_exe_path
from ea444_quantized_block import make_quantized_block
from ea444_tables import EA444Tables, tables_from_verified_exe_path


def synthetic_tables():
    section = bytearray(0x420)
    section[0x10:0x20] = bytes.fromhex(
        "9a79825ad48b0a3f753da73f15efc33e"
    )
    struct.pack_into("<64I", section, 0xA0, *range(64))
    struct.pack_into("<160I", section, 0x1A0, *([0x00040102] * 160))
    return EA444Tables.from_section(bytes(section))


class EA444InverseTransformTests(unittest.TestCase):
    def setUp(self):
        self.constants = EA444TransformConstants.from_tables(synthetic_tables())

    def test_original_constants_are_exact_tqia_dat_values(self):
        self.assertEqual(float(self.constants.odd_1), 0.5411961078643799)
        self.assertEqual(float(self.constants.odd_2), 1.3065630197525024)
        self.assertEqual(float(self.constants.odd_3), 0.3826834261417389)

    def test_first_pass_dc_shortcut_and_second_pass_general_dc_match(self):
        source = (983040, 0, 0, 0, 0, 0, 0, 0)
        expected = (983040,) * 8
        self.assertEqual(
            inverse_first_pass_1d(source, self.constants), expected
        )
        self.assertEqual(
            inverse_second_pass_1d(source, self.constants), expected
        )
        grid = (983040,) + (0,) * 63
        self.assertEqual(inverse_8x8(grid, self.constants), (983040,) * 64)

    def test_literal_transcription_vectors_preserve_signed_x86_butterfly(self):
        self.assertEqual(
            inverse_first_pass_1d(
                (1, 2, 3, 4, 5, 6, 7, 8), self.constants
            ),
            (27, -13, -1, -1, -1, -1, -1, -1),
        )
        self.assertEqual(
            inverse_second_pass_1d(
                (100, -200, 300, -400, 500, -600, 700, -800),
                self.constants,
            ),
            (-52, -52, -72, -72, -162, -162, -1314, 2686),
        )

    def test_rejects_wrong_sizes_and_noncanonical_constants(self):
        with self.assertRaises(EA444InverseTransformError):
            inverse_first_pass_1d((1, 2), self.constants)
        with self.assertRaises(EA444InverseTransformError):
            inverse_8x8((0,) * 63, self.constants)
        broken = bytearray(synthetic_tables().raw_section)
        broken[0x14] ^= 1
        with self.assertRaisesRegex(EA444InverseTransformError, "constants"):
            EA444TransformConstants.from_tables(
                EA444Tables.from_section(bytes(broken))
            )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Original licensed menu asset and executable not bundled with CI",
    )
    def test_real_first_main_menu_component_inverse_transform(self):
        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        tables = tables_from_verified_exe_path(exe)
        constants = EA444TransformConstants.from_tables(tables)
        quant = quantization_from_verified_exe_path(exe)
        _, reader = reader_for_ea444(
            (root / "Generic/main_menu/main_menu_bground.444").read_bytes()
        )
        grid = make_quantized_block(
            read_coefficient_block(reader, tables), quant
        ).signed_fixed
        output = inverse_8x8(grid, constants)
        self.assertEqual(len(output), 64)
        self.assertEqual(
            hashlib.sha256(struct.pack("<64i", *output)).hexdigest(),
            "26123d428acd76002b78c70ce21f66f44c9e06b3e57f30c02385c1d1acf8e0e7",
        )


if __name__ == "__main__":
    unittest.main()
