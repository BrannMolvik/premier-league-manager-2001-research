"""Raw DBRUser+180..186 ownership; not an AI formation or guessed diagram.

4258D0 resets these bytes at fresh club binding. Saved users restore the actual
seven bytes instead (4240A0/4246A0); absence is unknown, never a reset request.
See research/GATE13_USER_SHAPE_LIFECYCLE.md for scope and unresolved writers.
"""
from dataclasses import dataclass
import struct


_NATIVE_SCALE = struct.unpack('<f', bytes.fromhex('0ad7233c'))[0]


def _scaled_byte(value):
    # Integer<=255 times this binary32 constant is exact in binary64; the pack
    # performs the original FSTP binary32 rounding. Do not replace with /100.
    return struct.unpack('<f', struct.pack('<f', value * _NATIVE_SCALE))[0]


@dataclass(frozen=True)
class NativeUserShapeState:
    bytes_180_186: tuple[int, ...]

    def __post_init__(self):
        if (type(self.bytes_180_186) is not tuple
                or len(self.bytes_180_186) != 7
                or any(type(value) is not int or not 0 <= value <= 255
                       for value in self.bytes_180_186)):
            raise ValueError('DBRUser shape requires seven explicit unsigned bytes')

    @classmethod
    def fresh_club_binding(cls):
        """425904/425910/425916/42591C, not an ordinary load default."""
        return cls((50, 50, 50, 50, 50, 0, 0))

    def squad_pitch_scalars(self):
        """4B622A's two explicit shape arguments, byte180 then byte183."""
        return (_scaled_byte(self.bytes_180_186[0]),
                _scaled_byte(self.bytes_180_186[3]))
