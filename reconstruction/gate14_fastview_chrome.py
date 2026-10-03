"""Exact source-backed FastView top/bottom chrome resources.

Recovery 203 binds only two directly owned image controls from FastViewPanel:
- top_bar.444 at (0, 0), 800x95;
- ticker.444 at (0, 557), 800x33.

Both are passed directly to the live FastView image-control constructor
0x527730. Path setup occurs at 0x51FD63 / 0x51FDF0 and the constructor calls
themselves are at 0x51FDA3 / 0x51FE31. This is deliberately stronger
than filename-only association and deliberately narrower than a complete
800x600 FastView frame.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct


SOURCE_IMAGE_CONTROL_CONSTRUCTOR_VA = 0x527730
SOURCE_TOP_BAR_PATH_SETUP_VA = 0x51FD63
SOURCE_TICKER_PATH_SETUP_VA = 0x51FDF0
SOURCE_TOP_BAR_CONTROL_CALL_VA = 0x51FDA3
SOURCE_TICKER_CONTROL_CALL_VA = 0x51FE31


class FastViewChromeError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewChromeResource:
    name: str
    source_path: str
    byte_size: int
    sha256_hex: str
    width: int
    height: int
    x: int
    y: int
    source_path_setup_va: int
    source_control_call_va: int

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


TOP_BAR = FastViewChromeResource(
    name="top_bar.444",
    source_path="FM2001_Art/FastView/top_bar.444",
    byte_size=19268,
    sha256_hex="f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a",
    width=800,
    height=95,
    x=0,
    y=0,
    source_path_setup_va=SOURCE_TOP_BAR_PATH_SETUP_VA,
    source_control_call_va=SOURCE_TOP_BAR_CONTROL_CALL_VA,
)

TICKER = FastViewChromeResource(
    name="ticker.444",
    source_path="FM2001_Art/FastView/ticker.444",
    byte_size=6352,
    sha256_hex="b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257",
    width=800,
    height=33,
    x=0,
    y=557,
    source_path_setup_va=SOURCE_TICKER_PATH_SETUP_VA,
    source_control_call_va=SOURCE_TICKER_CONTROL_CALL_VA,
)

FASTVIEW_CHROME_RESOURCES = (TOP_BAR, TICKER)


def imported_chrome_path(repo_root: str | Path, resource: FastViewChromeResource) -> Path:
    return Path(repo_root) / "original_assets/source" / resource.source_path


def validate_imported_fastview_chrome(repo_root: str | Path) -> None:
    """Validate exact bytes plus the EA444 width/height header."""
    for resource in FASTVIEW_CHROME_RESOURCES:
        path = imported_chrome_path(repo_root, resource)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise FastViewChromeError(f"missing FastView chrome asset: {resource.source_path}") from exc
        if len(data) != resource.byte_size:
            raise FastViewChromeError(f"FastView chrome byte-size mismatch: {resource.name}")
        if sha256(data).hexdigest() != resource.sha256_hex:
            raise FastViewChromeError(f"FastView chrome checksum mismatch: {resource.name}")
        if len(data) < 4:
            raise FastViewChromeError(f"FastView chrome header truncated: {resource.name}")
        width, height = struct.unpack_from("<HH", data, 0)
        if (width, height) != (resource.width, resource.height):
            raise FastViewChromeError(
                f"FastView chrome geometry mismatch: {resource.name}: {(width, height)}"
            )
