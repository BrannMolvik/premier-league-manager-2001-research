"""x86-accurate original EA444 coefficient quantization regressions."""
import os
from pathlib import Path
import unittest

from ea444_quantization import (
    EA444Quantization, EA444QuantizationError,
    original_imul_scale, quantization_from_verified_exe_path,
)


class EA444QuantizationTests(unittest.TestCase):
    def test_exact_imul_shl_shr_adc_on_signed_32bit_inputs(self):
        for value, expected in (
            (0, 0), (1, 8), (-1, -8),
            (8192, 65536), (5906, 47248),
            (107619, 860952),
            (0x3fffffff, -8),
        ):
            with self.subTest(value=value):
                self.assertEqual(original_imul_scale(value), expected)
        for invalid in (1 << 31, -(1 << 31)-1):
            with self.assertRaises(EA444QuantizationError):
                original_imul_scale(invalid)

    def test_signed_lower_dword_ac_product_and_position_bounds(self):
        table = EA444Quantization(tuple(range(1, 65)), tuple(range(8, 520, 8)))
        self.assertEqual(table.scaled_coefficient(0, 15), 120)
        self.assertEqual(table.scaled_coefficient(18, -2), -304)
        self.assertEqual(table.scaled_coefficient(63, 1 << 22), -2147483648)
        for bad in (-1, 64):
            with self.assertRaises(EA444QuantizationError):
                table.scaled_coefficient(bad, 1)

    def test_never_accept_unverified_or_malformed_source_table(self):
        with self.assertRaisesRegex(EA444QuantizationError, "64 int32"):
            EA444Quantization.from_source_bytes(bytes(12))
        with self.assertRaisesRegex(EA444QuantizationError, "verified original"):
            EA444Quantization.from_source_bytes(bytes(256))
        with self.assertRaisesRegex(EA444QuantizationError, "not the verified"):
            quantization_from_verified_exe_path(Path(__file__))

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE"),
        "Actual licensed original EXE is not bundled into standard CI",
    )
    def test_firsthand_verified_original_matrix_and_main_menu_component(self):
        table = quantization_from_verified_exe_path(
            Path(os.environ["FM2001_ORIGINAL_EXE"])
        )
        self.assertEqual(len(table.original_source), 64)
        self.assertEqual(table.original_source[:8],
                         (8192, 5906, 6270, 6967, 8192, 10426, 15137, 29692))
        self.assertEqual(table.original_source[-8:],
                         (29692, 21407, 22725, 25251, 29692, 37791, 54864, 107619))
        self.assertEqual(table.fixed_point[:8],
                         (65536, 47248, 50160, 55736, 65536, 83408, 121096, 237536))
        self.assertEqual((min(table.fixed_point), max(table.fixed_point)),
                         (34064, 860952))
        self.assertEqual(table.scaled_coefficient(0, 15), 983040)
        self.assertEqual(table.scaled_coefficient(8, 1), 47248)
        self.assertEqual(table.scaled_coefficient(18, -2), -76784)


if __name__ == "__main__":
    unittest.main()
