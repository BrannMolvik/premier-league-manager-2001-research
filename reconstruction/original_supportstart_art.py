"""Authentic shipped FM2001 PSupportStart source sprites, no fake UI states.

Byte-identical owners extracted from authorized private original disc.
Validate source size, SHA-256 and native EA444 header before rendering.
No sprite placement, text glyph alignment, hover or mouse acceptance is
deduced from these file dimensions alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_supportstart_stars import STAR_RESOURCE


class OriginalSupportStartArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalSupportStartArtSpec:
    relative_source: str
    size: int
    sha256: str
    width: int
    height: int


ORIGINAL_SUPPORTSTART_ART_SPECS = (
    OriginalSupportStartArtSpec("FM2001_Art/Generic/user_entry/background.444", 176016,
                                "a7536fe303e6a340bf6f30a345ce77b7f396b91c8330957e6fd7a30915a3f6c4", 760, 500),
    OriginalSupportStartArtSpec("FM2001_Art/Generic/user_entry/text_bars.444", 11124,
                                "8c569018962a7084c33e5f4fda5d67e63f384d2e18d778281a7ad5aba2cba723", 306, 68),
    OriginalSupportStartArtSpec("FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444", 19720,
                                "7eb9df5610dade0d32cde3051e457216be1fb5062dcc66209012ca969203d1bc", 17, 851),
    OriginalSupportStartArtSpec("FM2001_Art/Generic/GenericButtonsAndBars/exit_button.444", 4864,
                                "3c317bbb4449a03efbeb867d1de4fd2e5b7d936f29d31f1c11af2092556fa0f9", 30, 90),
    OriginalSupportStartArtSpec("FM2001_Art/Generic/GenericButtonsAndBars/tick_button.444", 4372,
                                "119178ce89378df72f917f7fee4e17fb7edb5d43a5a5dee6229a89fbcf6be5c4", 30, 90),
    OriginalSupportStartArtSpec("FM2001_Art/Support/stars.444", 2776,
                                "16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633", 75, 10),
)
ORIGINAL_SUPPORTSTART_IMAGE_SIZE = (760, 500)
ORIGINAL_SUPPORTSTART_ROW_BAR_FRAME_SOURCE = (0, 0, 306, 17)
ORIGINAL_SUPPORTSTART_BUTTON_FIRST_FRAME_SOURCE = (0, 0, 30, 30)


def verified_original_supportstart_art(repo_root: Path) -> dict[str, bytes]:
    """Read only six exact authorized originals under their canonical path.

    The supplied repo_root is the repository root. Never fall back to
    unrelated lookalike source art or fabricated bytes on missing input.
    """
    root = Path(repo_root) / "original_assets" / "source"
    result = {}
    for spec in ORIGINAL_SUPPORTSTART_ART_SPECS:
        path = root / spec.relative_source
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise OriginalSupportStartArtError(
                f"Original SupportStart source art unavailable: {spec.relative_source}"
            ) from exc
        if len(data) != spec.size or sha256(data).hexdigest() != spec.sha256:
            raise OriginalSupportStartArtError(
                f"Original SupportStart art bytes mismatch: {spec.relative_source}"
            )
        try:
            header = parse_ea444_header(data)
        except ValueError as exc:
            raise OriginalSupportStartArtError(
                f"Original SupportStart EA444 header invalid: {spec.relative_source}"
            ) from exc
        if (header.width, header.height) != (spec.width, spec.height):
            raise OriginalSupportStartArtError(
                f"Original SupportStart native size mismatch: {spec.relative_source}"
            )
        result[spec.relative_source] = data
    if STAR_RESOURCE not in result:
        raise OriginalSupportStartArtError("Authentic stars.444 not available")
    return result
