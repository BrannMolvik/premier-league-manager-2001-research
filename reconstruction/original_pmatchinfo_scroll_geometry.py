"""Source-qualified 64EBE0 vertical thumb rectangles, not invented pixels/input.

Source rectangles are for the 946FB0 descriptor (18x25, caps 3+3). A native
surface Blt stretches the middle; choosing a replacement resampling algorithm,
hover acceptance, held-repeat or drag semantics is deliberately outside this
geometry seam. No report metadata or capacity value is manufactured here.
"""
from dataclasses import dataclass
from fractions import Fraction
import struct


THUMB_BIAS_FLOAT32_BITS = 0x3EFF7CEE  # canonical 7BD70C: NOT 0.5
THUMB_BIAS = Fraction(struct.unpack('<f', struct.pack('<I', THUMB_BIAS_FLOAT32_BITS))[0])
PAGE, TRACK_HEIGHT, CAP = 6, 163, 3


@dataclass(frozen=True)
class NativeThumbBlit:
    source_rect: tuple[int, int, int, int]
    destination_rect: tuple[int, int, int, int]
    clip_rect: tuple[int, int, int, int]


def native_vertical_thumb_rectangles(count, first_row, list_side, *,
                                    source_hover=False, masked_x87_invalid=None):
    """Three original cap/middle/cap Blt rects in PMatchInfo-local coordinates.

    A zero-range native calculation reaches 0/0. 668350 uses FISTP QWORD and
    returns its LOW dword; masked invalid yields 8000000000000000 -> low 0,
    not INT32_MIN. Require an explicit qualified mask state for that branch.
    The canonical native startup receipt observes control word 027F, but this
    API does not assume an arbitrary caller retains that environment.
    """
    if type(count) is not int or not 0 <= count <= 2046:
        raise ValueError('Count must fit the packed script/duplicated-entry boundary')
    maximum = max(count - PAGE, 0)
    if type(first_row) is not int or not 0 <= first_row <= maximum:
        raise ValueError('Native list offset outside scroll bounds')
    if type(list_side) is not int or list_side not in (0, 1):
        raise ValueError('Native list side must be 0 or 1')
    if type(source_hover) is not bool or (masked_x87_invalid is not None and type(masked_x87_invalid) is not bool):
        raise ValueError('Source control/FPU state must be explicit')
    height = max(CAP * 2, PAGE * TRACK_HEIGHT // (PAGE + maximum))
    if maximum:
        # Native FILD/FIDIV/FIMUL/FADD, then round-toward-zero conversion.
        # Bounded source inputs keep the positive rational away from any
        # integer by much more than an extended-precision rounding error.
        offset = int(Fraction(first_row * (TRACK_HEIGHT - height), maximum) + THUMB_BIAS)
    elif masked_x87_invalid is True:
        offset = 0
    else:
        raise ValueError('Zero-range native x87 invalid mask is not qualified')
    # 64FF90 disables the thumb exactly when min==max. 64FDB0/64FE27
    # map disabled -> frame3 and source control hover -> frame2; descriptor
    # flags D do not authorize a pressed-frame transform.
    frame = 3 if maximum == 0 else (2 if source_hover else 0)
    x, y, source_x = (17 if list_side else 389), 291 + offset, frame * 18
    clip = (x, 291, 18, TRACK_HEIGHT)
    middle = height - CAP * 2
    return (
        NativeThumbBlit((source_x, 0, 18, CAP), (x, y, 18, CAP), clip),
        NativeThumbBlit((source_x, CAP, 18, 25 - CAP * 2),
                        (x, y + CAP, 18, middle), clip),
        NativeThumbBlit((source_x, 25 - CAP, 18, CAP),
                        (x, y + height - CAP, 18, CAP), clip),
    )
