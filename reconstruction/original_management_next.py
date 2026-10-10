"""Original PBg +524 NEXT/MATCH bitmap and companion caption.

430992..A04; 5D3900 sets vertical state discriminator40; 5D3AC0 chooses
disabled/pressed/hover/default rows3/2/1/0. Action/queued-user binding is
separate; these pixels do not manufacture a match or accept an unknown route.
"""
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from ea444_tables import tables_from_original_executable
from ea444_quantization import quantization_from_verified_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from original_management_header import _right_centered_text_rgba


NEXT_SOURCE_PATH = 'FM2001_Art/Generic/Background_buttons/back_5.444'
NEXT_SOURCE_SHA256 = '171257f958b9fa15115476814a31de2d86bbdd2beb4767e42b3181d83e7ba605'
NEXT_SOURCE_SIZE = 10940
NEXT_RECT = (700, 0, 100, 95)
NEXT_CAPTION_RECT = (700, 62, 73, 30)
NEXT_CAPTION_RAW_STYLE = 18


def native_next_source_row(flags: int) -> int:
    if type(flags) is not int or not 0 <= flags <= 0xFFFFFFFF:
        raise ValueError('Original NEXT flags must be a DWORD')
    if not flags & 2:
        return 3
    if flags & 0x10:
        return 2
    return 1 if flags & 8 else 0


def native_next_at_point(x: int, y: int) -> bool:
    # The background owner is rooted at0/0; native hit edges are half-open.
    return 700 <= x < 800 and 0 <= y < 95


def native_next_press(x: int, y: int, flags: int) -> bool:
    """Concrete Back5 ->64F7A0; PBg7BEE8C's parent guard is42DE00 (true)."""
    if type(x) is not int or type(y) is not int:
        raise ValueError('Original NEXT requires exact pointer coordinates')
    native_next_source_row(flags)  # Shared DWORD boundary validation.
    return native_next_at_point(x, y) and bool(flags & 2) and not flags & 0x10


def native_next_caption(current_date: date, retained_match_date: date | None) -> str:
    if type(current_date) is not date or (
            retained_match_date is not None and type(retained_match_date) is not date):
        raise ValueError('Original NEXT caption requires exact retained dates')
    # 432760 initializes NEXT; only the retained native wrapper date can
    # select MATCH. Missing header context is not a search by completion/score.
    return 'MATCH' if retained_match_date == current_date + timedelta(days=1) else 'NEXT'


def load_verified_management_next_art(source_root, original_executable):
    raw = (Path(source_root) / NEXT_SOURCE_PATH).read_bytes()
    if len(raw) != NEXT_SOURCE_SIZE or sha256(raw).hexdigest() != NEXT_SOURCE_SHA256:
        raise ValueError('Original NEXT bitmap identity mismatch')
    header = parse_ea444_header(raw)
    if (header.width, header.height) != (100, 380):
        raise ValueError('Original NEXT bitmap geometry mismatch')
    executable = Path(original_executable).read_bytes()
    return decode_staged_or_original(raw,
        tables=tables_from_original_executable(executable),
        quant=quantization_from_verified_executable(executable))


def native_next_bitmap_pixels(art, flags: int):
    if (art.width, art.height, len(art.rgba)) != (100, 380, 100*380*4):
        raise ValueError('Original NEXT decoded geometry mismatch')
    row = native_next_source_row(flags)
    size = 100*95*4
    return (*NEXT_RECT, art.rgba[row*size:(row+1)*size])


def native_next_caption_pixels(font, current_date, retained_match_date):
    # Raw style18: bit2 right-alignment and bit10 vertical centering, with
    # the same exact 24px source font already verified for the MENU caption.
    return _right_centered_text_rgba(font,
        native_next_caption(current_date, retained_match_date), NEXT_CAPTION_RECT)
