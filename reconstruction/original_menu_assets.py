"""Use the authentic original main-menu button strip without altering its bytes.

The original PE at 0x5F33A4 passes the exact filename
reused_art\\generic\\main_menu_windows_buttons.png to the resource loader
at 0x64D750. The authorized disc supplies a 136 x 19 RGB PNG whose visible
layout consists of four adjacent 34 x 19 sprite cells. Their exact input
control/state bindings remain unresolved; do not invent that mapping here.

This module does NOT implement or substitute the still-undecoded .444 menu
backgrounds, panel geometry or original button-control placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct
from typing import Callable


SOURCE_PATH = "reused_art/generic/main_menu_windows_buttons.png"
REPOSITORY_PATH = "original_assets/source/" + SOURCE_PATH
SOURCE_SHA256 = (
    "663051a12745e144a26aa773d034902754b90f44f7fdb3e7a1a217b19eb3252d"
)
SOURCE_SIZE = 2775
SOURCE_DIMENSIONS = (136, 19)
FRAME_COUNT = 4
PNG_SIGNATURE = b"\\x89PNG\\r\\n\\x1a\\n"


class OriginalMenuAssetError(ValueError):
    """An expected original resource was absent or changed."""


@dataclass(frozen=True)
class OriginalMenuButtonStrip:
    path: Path
    sha256: str
    width: int
    height: int
    frame_count: int

    @property
    def frame_rectangles(self) -> tuple[tuple[int, int, int, int], ...]:
        """Original PNG pixel rectangles, not unproven screen coordinates."""
        frame_width = self.width // self.frame_count
        return tuple(
            (i * frame_width, 0, (i + 1) * frame_width, self.height)
            for i in range(self.frame_count)
        )


def validate_original_menu_button_strip(path: Path) -> OriginalMenuButtonStrip:
    """Fail closed if an arbitrary or redesigned asset replaces the original."""
    path = Path(path)
    data = path.read_bytes()
    if len(data) != SOURCE_SIZE or sha256(data).hexdigest() != SOURCE_SHA256:
        raise OriginalMenuAssetError(
            "Original main-menu sprite checksum/size mismatch."
        )
    if data[:8] != PNG_SIGNATURE or len(data) < 33:
        raise OriginalMenuAssetError("Original main-menu sprite is not a PNG.")
    chunk_length = struct.unpack_from(">I", data, 8)[0]
    chunk_name = data[12:16]
    width, height, depth, color_type, compression, filtering, interlace = (
        struct.unpack_from(">IIBBBBB", data, 16)
    )
    if (
        chunk_name != b"IHDR"
        or chunk_length != 13
        or (width, height) != SOURCE_DIMENSIONS
        or (depth, color_type, compression, filtering, interlace)
        != (8, 2, 0, 0, 0)
    ):
        raise OriginalMenuAssetError(
            "Original main-menu sprite PNG header is unsupported."
        )
    return OriginalMenuButtonStrip(
        path=path, sha256=SOURCE_SHA256,
        width=width, height=height, frame_count=FRAME_COUNT,
    )


@dataclass
class OriginalTkButtonFrames:
    """Keep the parent strip referenced while Tk displays frame images."""
    source: object
    frames: tuple[object, ...]


def load_tk_button_frames(
    strip: OriginalMenuButtonStrip,
    *,
    master: object = None,
    photo_factory: Callable[..., object] | None = None,
) -> OriginalTkButtonFrames:
    """Render authentic pixel cells in Tk; never assign unproven button IDs.

    Requires a Tk display only when called. Metadata tests and source
    verification remain completely headless. photo_factory injection lets
    tests check exact copies without a graphical desktop.
    """
    if photo_factory is None:
        from tkinter import PhotoImage
        photo_factory = PhotoImage

    source = photo_factory(master=master, file=str(strip.path))
    images = []
    for left, top, right, bottom in strip.frame_rectangles:
        frame = photo_factory(master=master, width=right-left, height=bottom-top)
        frame.tk.call(
            str(frame), "copy", str(source),
            "-from", left, top, right, bottom,
            "-to", 0, 0,
        )
        images.append(frame)
    return OriginalTkButtonFrames(source=source, frames=tuple(images))


def repo_source_path(repo_root: Path) -> Path:
    """Explicitly opt into assets checked in under original_assets/."""
    return Path(repo_root).joinpath(*REPOSITORY_PATH.split("/"))
