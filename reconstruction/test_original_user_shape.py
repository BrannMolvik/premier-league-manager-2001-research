import unittest
from hashlib import sha256
import struct

from human_gameplay import HumanManagerState
from original_user_shape import NativeUserShapeState


class NativeUserShapeTests(unittest.TestCase):
    def test_only_explicit_fresh_binding_has_original_reset_bytes(self):
        self.assertEqual(NativeUserShapeState.fresh_club_binding().bytes_180_186,
                         (50, 50, 50, 50, 50, 0, 0))
        self.assertIsNone(HumanManagerState(club_id=1).native_shape)

    def test_all_unsigned_byte_values_are_retained_without_clamping(self):
        for seed in range(256):
            raw = tuple((seed + offset * 37) & 255 for offset in range(7))
            self.assertEqual(NativeUserShapeState(raw).bytes_180_186, raw)

    def test_invalid_or_coerced_values_are_rejected(self):
        for raw in (None, (0,) * 6, (0,) * 8, [0] * 7,
                    (-1,) + (0,) * 6, (256,) + (0,) * 6,
                    (True,) + (0,) * 6, (50.0,) + (0,) * 6,
                    ('50',) + (0,) * 6):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                NativeUserShapeState(raw)
        with self.assertRaises(ValueError):
            HumanManagerState(club_id=1, native_shape=(50,) * 7)

    def test_actual_x87_conversion_vectors_not_division_by_100(self):
        # Independent canonical execution of both read blocks, all256 inputs.
        raw = []
        for value in range(256):
            state = NativeUserShapeState((value, 0, 0, value, 0, 0, 0))
            first, second = state.squad_pitch_scalars()
            self.assertEqual(first, second)
            raw.append(struct.pack('<f', first))
        self.assertEqual(sha256(b''.join(raw)).hexdigest(),
                         '7a565e4085af53d243a92099257dc2c19573ca12366aeaffb1ec6ef9ffd656ef')
        self.assertEqual(raw[49].hex(), '47e1fa3e')
        self.assertEqual(raw[99].hex(), 'a3707d3f')
        state = NativeUserShapeState((50, 0, 0, 99, 0, 0, 0))
        self.assertEqual(state.squad_pitch_scalars(), (0.5, struct.unpack('<f', raw[99])[0]))


if __name__ == '__main__':
    unittest.main()
