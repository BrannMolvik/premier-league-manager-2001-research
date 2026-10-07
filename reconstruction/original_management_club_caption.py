"""Application+2A4 club caption: native setup 43062D, refresh 432B44.

40DA50 prefers a nonempty human-user+D0 caption, otherwise DBRClub+8.
424F3F explicitly writes the fresh user caption's terminating zero. This
contract does not invent imported/renamed-user state when it is unavailable.
"""
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from original_squad_row_style import _clip_mask, _rgb_rgba

CLUB_CAPTION_RECT = (172, 1, 378, 32)
CLUB_CAPTION_FLAGS = 0x2102
CLUB_CAPTION_NATIVE_COLOR = 0xFFFF
CLUB_CAPTION_FONT_PATH = "Fonts/Zurich_BdXCn_BT_32pixel.fnt"
CLUB_CAPTION_FONT_SHA256 = "27b5e4c42518bef0e000a5878939f859c2c1b1e635e4fd200752e23c468c3e36"
CLUB_CAPTION_FONT_SIZE = 136128


def load_verified_management_club_font(source_root: str | Path) -> EAFont:
    raw = (Path(source_root) / CLUB_CAPTION_FONT_PATH).read_bytes()
    if len(raw) != CLUB_CAPTION_FONT_SIZE or sha256(raw).hexdigest() != CLUB_CAPTION_FONT_SHA256:
        raise ValueError("Management club-caption font identity mismatch")
    font = EAFont.from_bytes(raw)
    if (font.atlas_width, font.atlas_height, font.native_line_height()) != (2422, 34, 37):
        raise ValueError("Management club-caption native font geometry mismatch")
    return font


def management_club_caption_pixels(font, club_name: str, user_caption: str | None):
    """Return clipped white RGBA, or withhold an unknown user-caption context.

    6522A4 right-aligns by measured width; 65230B vertically centers by the
    two native integer halves, NOT by the visible glyph bounding box.
    """
    if user_caption is None:
        return None
    if not isinstance(user_caption, str) or not isinstance(club_name, str) or not club_name:
        raise ValueError("Management club-caption source strings are invalid")
    text = user_caption or club_name
    x, y, width, height = CLUB_CAPTION_RECT
    line_x = x + width - font.measure_text(text)
    line_y = y + height // 2 - font.native_line_height() // 2
    clipped = _clip_mask(font.render_text_alpha(text), line_x=line_x,
                         line_y=line_y, rect=CLUB_CAPTION_RECT)
    if clipped is None:
        return None
    left, top, out_width, out_height, alpha = clipped
    return left, top, out_width, out_height, _rgb_rgba(alpha, (255, 255, 255))
