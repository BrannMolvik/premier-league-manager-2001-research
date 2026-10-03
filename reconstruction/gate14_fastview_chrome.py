"""Source-closed directly bound FastView top and ticker chrome.

Unlike the rejected loose FastView/background.444 path, these two EA444 files
are passed directly to generic PictureControl construction inside FastViewPanel.
This module records only that exact ownership, identity and geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct


class FastViewChromeError(ValueError):
    pass


SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
SOURCE_PICTURE_CONTROL_VFTABLE = 0x7CAA5C
SOURCE_PICTURE_CONTROL_RTTI = ".?AVPictureControl@@"

IMPORT_ROOT = Path("original_assets/source")


@dataclass(frozen=True)
class FastViewChromeResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    rect: tuple[int, int, int, int]
    path_literal_va: int
    string_init_va: int
    picture_control_call_va: int

    def __post_init__(self) -> None:
        left, top, right, bottom = self.rect
        if (right - left, bottom - top) != self.size:
            raise FastViewChromeError(
                f"{self.name} source dimensions do not match screen rectangle"
            )


TOP_BAR = FastViewChromeResource(
    name="top_bar",
    source_path="FM2001_Art/FastView/top_bar.444",
    sha256="f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a",
    byte_size=19268,
    size=(800, 95),
    rect=(0, 0, 800, 95),
    path_literal_va=0x829734,
    string_init_va=0x51FD63,
    picture_control_call_va=0x51FDA3,
)

TICKER = FastViewChromeResource(
    name="ticker",
    source_path="FM2001_Art/FastView/ticker.444",
    sha256="b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257",
    byte_size=6352,
    size=(800, 33),
    rect=(0, 557, 800, 590),
    path_literal_va=0x829714,
    string_init_va=0x51FDF0,
    picture_control_call_va=0x51FE31,
)

FASTVIEW_DIRECT_CHROME_RESOURCES = (TOP_BAR, TICKER)

# Recovery 202 proved this separate file is not bound to the live panel.
REJECTED_UNBOUND_BACKGROUND_PATH = "FM2001_Art/FastView/background.444"


def imported_resource_path(repo_root: str | Path, resource: FastViewChromeResource) -> Path:
    return Path(repo_root) / IMPORT_ROOT / resource.source_path


def validate_imported_fastview_chrome(
    repo_root: str | Path,
) -> tuple[FastViewChromeResource, ...]:
    """Require byte-identical directly owned FastView chrome when staged."""
    for resource in FASTVIEW_DIRECT_CHROME_RESOURCES:
        path = imported_resource_path(repo_root, resource)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise FastViewChromeError(
                f"Missing staged FastView chrome resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise FastViewChromeError(
                f"FastView chrome byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise FastViewChromeError(
                f"FastView chrome checksum mismatch: {resource.source_path}"
            )
        if len(data) < 4:
            raise FastViewChromeError(
                f"FastView chrome resource has no EA444 header: {resource.source_path}"
            )
        width, height = struct.unpack_from("<HH", data, 0)
        if (width, height) != resource.size:
            raise FastViewChromeError(
                f"FastView chrome geometry mismatch: {resource.source_path}"
            )
    return FASTVIEW_DIRECT_CHROME_RESOURCES
