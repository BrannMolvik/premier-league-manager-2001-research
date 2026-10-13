"""Verified original EAMail ten filter labels and native text font identity.

Private original EXE SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.

0x46EA57..0x46F05F passes original English idx ordinals177..186 to
0x5D4F00. 0x5D4F50 adds +30 to x=22 for child text x=52; the
original y is 30+30*i, relative to PEAMail panel y148.
0x5D4FD1 pushes font object 0x9197E0, wrapper0x945BB0, flags0x2001.
Original 0x6042F0 maps this font slot into 0x657650 using the
shipped Zurich_BdXCn_BT_18pixel.fnt file.
No original text draw rectangles, glyph colors, clipping, hover, radio
art or native Win32 event-delivery are inferred by this source receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from original_eamail_main_language import (
    VerifiedOriginalMainEAMLanguage,
)
from original_eamail_filter_controls import (
    NATIVE_FILTER_COUNT,
)

NATIVE_EAM_FILTER_FONT_OBJECT = 0x9197E0
NATIVE_EAM_FILTER_TEXT_WRAPPER = 0x945BB0
NATIVE_EAM_FILTER_TEXT_FLAGS = 0x2001
NATIVE_EAM_FILTER_LABEL_FIRST_IDX_ORDINAL = 177
NATIVE_EAM_FILTER_TEXT_FIRST_X = 52
NATIVE_EAM_FILTER_TEXT_FIRST_Y = 30
NATIVE_EAM_FILTER_TEXT_PITCH = 30
ORIGINAL_EAM_FILTER_FONT_PATH = "Fonts/Zurich_BdXCn_BT_18pixel.fnt"
ORIGINAL_EAM_FILTER_FONT_LENGTH = 83174
ORIGINAL_EAM_FILTER_FONT_SHA256 = (
    "4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd"
)


class OriginalEAMailFilterLabelError(ValueError):
    """Native Inbox filter text/font source identity or ownership mismatch."""


@dataclass(frozen=True)
class SourceOriginalEAMailFilterLabel:
    index: int
    english_idx_ordinal: int
    text: str
    native_font_va: int
    native_text_wrapper_va: int
    native_text_flags: int
    panel_local_text_origin: tuple[int, int]
    # Important: origin is not a source-complete rendered glyph rectangle.


@dataclass(frozen=True)
class SourceOriginalEAMailFilterLabels:
    native_font: EAFont
    entries: tuple[SourceOriginalEAMailFilterLabel, ...]


def load_source_original_eam_filter_labels(
    source_root: str | Path,
    language: VerifiedOriginalMainEAMLanguage,
) -> SourceOriginalEAMailFilterLabels:
    """Bind exact original English and native 18px font, not substitute font.

    The original text glyph rendering/scale/clip logic (0x651E30 and
    0x6528D0) needs further source completion BEFORE drawing these labels
    in the normal player screen. This loader does not create UI sprites.
    """
    if type(language) is not VerifiedOriginalMainEAMLanguage:
        raise OriginalEAMailFilterLabelError(
            "Require exact shipped original main English STR/IDX pair"
        )
    path = Path(source_root) / ORIGINAL_EAM_FILTER_FONT_PATH
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise OriginalEAMailFilterLabelError(
            "Missing original EAMail Zurich 18 pixel font"
        ) from exc
    if (len(data) != ORIGINAL_EAM_FILTER_FONT_LENGTH
            or sha256(data).hexdigest() != ORIGINAL_EAM_FILTER_FONT_SHA256):
        raise OriginalEAMailFilterLabelError(
            "Original EAMail filter font length/digest mismatch"
        )
    original = ("New", "All", "Finance", "Building", "Events",
                "Player/Team", "Transfer Market", "Youth Team",
                "Contracts", "FA")
    items = []
    for i in range(NATIVE_FILTER_COUNT):
        ordinal = NATIVE_EAM_FILTER_LABEL_FIRST_IDX_ORDINAL + i
        text = language.index.resolve(language.strings, ordinal)
        if text != original[i]:
            raise OriginalEAMailFilterLabelError(
                "Original EAMail 177..186 language index mapping changed"
            )
        items.append(SourceOriginalEAMailFilterLabel(
            i, ordinal, text, NATIVE_EAM_FILTER_FONT_OBJECT,
            NATIVE_EAM_FILTER_TEXT_WRAPPER,
            NATIVE_EAM_FILTER_TEXT_FLAGS,
            (NATIVE_EAM_FILTER_TEXT_FIRST_X,
             NATIVE_EAM_FILTER_TEXT_FIRST_Y + i * NATIVE_EAM_FILTER_TEXT_PITCH),
        ))
    return SourceOriginalEAMailFilterLabels(
        native_font=EAFont.from_bytes(data), entries=tuple(items),
    )
