import struct
import unittest

from match_coefficients import (
    ATTACK_MATRIX_VA,
    DEFENCE_MATRIX_VA,
    MATRIX_VALUE_COUNT,
    _absolute_va_to_file_offset,
)


def synthetic_pe():
    data = bytearray(0x800)
    data[0:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x86, 1)      # one section
    struct.pack_into("<H", data, 0x94, 0xE0)   # optional-header size

    optional = 0x98
    struct.pack_into("<H", data, optional, 0x10B)
    struct.pack_into("<I", data, optional + 28, 0x400000)

    section = optional + 0xE0
    data[section:section + 8] = b".data\0\0\0"
    struct.pack_into("<IIII", data, section + 8, 0x400, 0x1000, 0x400, 0x200)
    return bytes(data)


class PeAddressTests(unittest.TestCase):
    def test_absolute_va_maps_into_section_raw_data(self):
        data = synthetic_pe()
        self.assertEqual(_absolute_va_to_file_offset(data, 0x401000), 0x200)
        self.assertEqual(_absolute_va_to_file_offset(data, 0x401123), 0x323)

    def test_invalid_image_is_rejected(self):
        with self.assertRaises(ValueError):
            _absolute_va_to_file_offset(b"not a pe", 0x401000)

    def test_known_matrix_geometry(self):
        self.assertEqual(MATRIX_VALUE_COUNT, 4 * 20 * 17)
        self.assertEqual(DEFENCE_MATRIX_VA - ATTACK_MATRIX_VA, MATRIX_VALUE_COUNT * 8)


if __name__ == "__main__":
    unittest.main()
