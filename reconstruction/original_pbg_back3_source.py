"""Exact original PBg header ID1 back_3.444 source art validation.

Original PE 0x43092B/0x431850 binds wrapper 0x943B10 (40x95 viewport),
and 0x5FA570/0x5FA5C0 loads the 40x380 four-frame asset. The native
frame state/hover/pressed source is NOT yet mapped; do not pick row 0
as a decorative fallback or present an inaccurate PBg control.
"""
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header

PBG_EAMAIL_BACK3_SOURCE_PATH = (
    "FM2001_Art/Generic/Background_buttons/back_3.444"
)
PBG_EAMAIL_BACK3_SHA256 = (
    "f369e73c2a7f9149661d66cf3c781ddc8eabf01f80ef924b423d46d57cf628e6"
)
PBG_EAMAIL_BACK3_SIZE = 5932
PBG_EAMAIL_BACK3_NATIVE_ATLAS = (40, 380)
PBG_EAMAIL_BACK3_NATIVE_CROP = (40, 95)


class OriginalPBgBack3SourceError(ValueError):
    pass


def verified_original_pbg_back3_bytes(source_root: str | Path) -> bytes:
    path = Path(source_root) / PBG_EAMAIL_BACK3_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalPBgBack3SourceError(
            "Original PBg direct Inbox back_3.444 is missing"
        ) from exc
    if len(raw) != PBG_EAMAIL_BACK3_SIZE or (
        sha256(raw).hexdigest() != PBG_EAMAIL_BACK3_SHA256
    ):
        raise OriginalPBgBack3SourceError(
            "Original PBg direct Inbox back_3.444 bytes differ"
        )
    try:
        header = parse_ea444_header(raw)
    except ValueError as exc:
        raise OriginalPBgBack3SourceError(
            "Original PBg direct Inbox back_3.444 header invalid"
        ) from exc
    if (header.width, header.height) != PBG_EAMAIL_BACK3_NATIVE_ATLAS:
        raise OriginalPBgBack3SourceError(
            "Original PBg direct Inbox back_3.444 geometry differs"
        )
    return raw
