import hashlib
import os
from pathlib import Path
import unittest

from ea444_decoder import _sample_u8, decode_ea444_file
from ea444_quantization import quantization_from_verified_exe_path
from ea444_tables import tables_from_verified_exe_path


class EA444DecoderTests(unittest.TestCase):
    def test_original_16_16_sample_clamp_boundary(self):
        for source, expected in (
            (-65536, 0), (-1, 0), (0, 0),
            (65535, 0), (65536, 1),
            (255 << 16, 255), (256 << 16, 255),
        ):
            with self.subTest(source=source):
                self.assertEqual(_sample_u8(source), expected)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Original licensed graphics and executable not bundled with CI",
    )
    def test_real_original_main_menu_and_team_select_decode_exact_rgba(self):
        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        tables = tables_from_verified_exe_path(exe)
        quant = quantization_from_verified_exe_path(exe)
        cases = (
            (
                "Generic/main_menu/main_menu_bground.444",
                (532, 532),
                1649222,
                "d67036a03a5138f0789f429209c154ec67c1ee7b690a42b5e72fb90335fb21cd",
            ),
            (
                "Generic/team_choice/background.444",
                (800, 558),
                1437951,
                "65346a785e9470b32dbdf7dc5858a4c5e3f7c4b49920fc811ffc599dfdc16acf",
            ),
        )
        for relative, size, consumed_bits, digest in cases:
            with self.subTest(relative=relative):
                decoded = decode_ea444_file(
                    root / relative, tables=tables, quant=quant
                )
                self.assertEqual((decoded.width, decoded.height), size)
                self.assertEqual(decoded.consumed_bits, consumed_bits)
                self.assertEqual(decoded.transparent_pixels, 0)
                self.assertEqual(
                    hashlib.sha256(decoded.rgba).hexdigest(), digest
                )


if __name__ == "__main__":
    unittest.main()
