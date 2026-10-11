"""Source-authentic original PBg direct Inbox *initial idle* sprite.

Canonical owner-authorized PE (SHA256 833bf95e...b7cc3):
- 0x5FA5C0 -> 0x64E500 installs source (0,0,40,95) of back_3.444
  into native bitmap descriptor 0x943B10; shipped atlas 40x380;
- 0x43092B child ID1 at (558,0), 0x431850 has 0x943B10 bitmap;
- base native 0x64F300 initializes control+0x18 to 0x183;
- 0x64FDB0 (control vft+0x90) yields frame 0 for these initial
  flags independent of image flags.

Frame changes on pointer hover/press/disabled are not yet integrated.
Do NOT render the idle crop for other native state flags or invent
modern hover transitions. The original game executable is read only.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from original_pbg_back3_source import (
    PBG_EAMAIL_BACK3_NATIVE_ATLAS,
    PBG_EAMAIL_BACK3_NATIVE_CROP,
    verified_original_pbg_back3_bytes,
)
from original_pbg_direct_inbox import PBG_DIRECT_EAMAIL_RECT


PBG_MAIL_NATIVE_BITMAP_DESCRIPTOR_VA = 0x943B10
PBG_MAIL_NATIVE_LOADER_VA = 0x5FA5C0
PBG_MAIL_NATIVE_FRAME_DISPATCH_VA = 0x64FDB0
PBG_MAIL_NATIVE_CONTROL_DEFAULT_FLAGS = 0x183
PBG_MAIL_NATIVE_SOURCE_IDLE_RECT = (0, 0, 40, 95)


class OriginalPBgMailArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalPBgMailArt:
    image: EA444DecodedImage

    def __post_init__(self):
        if ((self.image.width, self.image.height)
                != PBG_EAMAIL_BACK3_NATIVE_ATLAS):
            raise OriginalPBgMailArtError("Original PBg mail bitmap atlas geometry differs")
        if len(self.image.rgba) != self.image.width * self.image.height * 4:
            raise OriginalPBgMailArtError("Original PBg mail bitmap alpha data differs")


def native_pbg_mail_bitmap_frame(control_flags: int, image_flags: int) -> int:
    """Exact 0x64FDB0 state precedence, not yet normal-host pointer wiring.

    Native 0x64E5D0 calls virtual+0x90 on the image-owning child to
    select the source strip; frame 4 is a possible generic result but
    cannot be sampled from the four-frame PBg back_3 atlas.
    """
    if (type(control_flags) is not int
            or type(image_flags) is not int
            or not 0 <= control_flags <= 0xFFFFFFFF
            or not 0 <= image_flags <= 0xFFFFFFFF):
        raise OriginalPBgMailArtError("Native PBg state requires DWORD flags")
    if not control_flags & 0x2:
        return 3 if image_flags & 0x8 else 0
    if (control_flags & 0x10 and image_flags & 0x2
            or control_flags & 0x20 and image_flags & 0x2):
        return 1
    if control_flags & 0x4 and image_flags & 0x10:
        return 4
    if control_flags & 0x8 and image_flags & 0x4:
        return 2
    return 0


def load_verified_original_pbg_mail_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalPBgMailArt:
    raw = verified_original_pbg_back3_bytes(source_root)
    executable = Path(original_executable).read_bytes()
    return OriginalPBgMailArt(decode_staged_or_original(
        raw,
        tables=tables_from_original_executable(executable),
        quant=quantization_from_verified_executable(executable),
    ))


def native_pbg_mail_idle_bitmap_pixels(
    art: OriginalPBgMailArt,
    *,
    control_flags: int = PBG_MAIL_NATIVE_CONTROL_DEFAULT_FLAGS,
) -> tuple[int, int, int, int, bytes]:
    """Only draw the original initial/default frame, not unproven hover.

    Resource's original 0x5FA5C0 initial image selection is (0,0,40,95).
    Dynamic flags other than native constructor defaults are unsupported.
    """
    if type(art) is not OriginalPBgMailArt:
        raise OriginalPBgMailArtError("Verified original PBg image required")
    if control_flags != PBG_MAIL_NATIVE_CONTROL_DEFAULT_FLAGS:
        raise OriginalPBgMailArtError(
            "Original PBg hover/pressed state has not been accepted"
        )
    if native_pbg_mail_bitmap_frame(control_flags, 0) != 0:
        raise OriginalPBgMailArtError("Original PBg initial strip changed")
    if PBG_DIRECT_EAMAIL_RECT != (558, 0, 40, 95):
        raise OriginalPBgMailArtError("Original PBg button bounds changed")
    x, y, w, h = PBG_DIRECT_EAMAIL_RECT
    return x, y, w, h, art.image.rgba[:w * h * 4]
