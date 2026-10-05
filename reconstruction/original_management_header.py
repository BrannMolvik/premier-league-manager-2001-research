"""Verified source staging for the final application-owned management header.

This module deliberately separates exact source identity/geometry from the still
private state-selection adjudication.  It may decode the two original atlases
and Zurich 24px font, but it does not choose a frame, caption string, color, or
update cadence unless that value is supplied by a separately source-qualified
adapter.

The fixed geometry comes from the canonical footballmanager.exe compound
constructor at 0x4313B0..0x4314C3.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_header import parse_ea444_header
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont


class OriginalManagementHeaderError(ValueError):
    """The final management-header source contract is incomplete or invalid."""


HEADER_COMPOUND_RECT = (599, 0, 100, 95)
HEADER_LEFT_RECT = (599, 0, 30, 95)
HEADER_RIGHT_RECT = (629, 0, 70, 95)
HEADER_CAPTION_RECT = (631, 62, 70, 30)
HEADER_CAPTION_STYLE = 10
HEADER_FRAME_HEIGHT = 95


@dataclass(frozen=True)
class OriginalManagementHeaderResource:
    role: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    destination_rect: tuple[int, int, int, int]

    @property
    def frame_count(self) -> int:
        width, height = self.size
        del width
        if height % HEADER_FRAME_HEIGHT:
            raise OriginalManagementHeaderError(
                f"{self.source_path} is not a whole 95px source-frame stack"
            )
        return height // HEADER_FRAME_HEIGHT


HEADER_LEFT_RESOURCE = OriginalManagementHeaderResource(
    role="left_anim",
    source_path="FM2001_Art/Generic/Background_buttons/back_4_anim.444",
    sha256="867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69",
    byte_size=99968,
    size=(30, 4845),
    destination_rect=HEADER_LEFT_RECT,
)
HEADER_RIGHT_RESOURCE = OriginalManagementHeaderResource(
    role="right_state",
    source_path="FM2001_Art/Generic/Background_buttons/back_4.444",
    sha256="710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb",
    byte_size=5476,
    size=(70, 380),
    destination_rect=HEADER_RIGHT_RECT,
)
HEADER_RESOURCES = (HEADER_LEFT_RESOURCE, HEADER_RIGHT_RESOURCE)

HEADER_FONT_SOURCE_PATH = "Fonts/Zurich_XCn_BT_24pixel.fnt"
HEADER_FONT_SHA256 = "f165d39423a9f20532132d2bd9a3c53aba4244531aa3291a73502fa956a46405"
HEADER_FONT_BYTE_SIZE = 95276
HEADER_FONT_OBJECT_VA = 0x8B0760
HEADER_CAPTION_GLOBAL_VA = 0x9820F4


@dataclass(frozen=True)
class OriginalManagementHeaderResources:
    left_anim: EA444DecodedImage
    right_state: EA444DecodedImage
    font: EAFont

    def __post_init__(self) -> None:
        if (self.left_anim.width, self.left_anim.height) != HEADER_LEFT_RESOURCE.size:
            raise OriginalManagementHeaderError("back_4_anim decoded geometry mismatch")
        if (self.right_state.width, self.right_state.height) != HEADER_RIGHT_RESOURCE.size:
            raise OriginalManagementHeaderError("back_4 decoded geometry mismatch")


@dataclass(frozen=True)
class OriginalManagementHeaderFrame:
    """One explicitly source-qualified pair of atlas rows.

    The row indices are intentionally not inferred here.  The final private
    adjudication owns the mapping from native state bits/update behavior to
    these physical atlas rows.
    """

    left_source_row: int
    right_source_row: int

    def __post_init__(self) -> None:
        if type(self.left_source_row) is not int or not 0 <= self.left_source_row < HEADER_LEFT_RESOURCE.frame_count:
            raise OriginalManagementHeaderError("left management-header source row is outside back_4_anim")
        if type(self.right_source_row) is not int or not 0 <= self.right_source_row < HEADER_RIGHT_RESOURCE.frame_count:
            raise OriginalManagementHeaderError("right management-header source row is outside back_4")


@dataclass(frozen=True)
class OriginalManagementHeaderOverlay:
    role: str
    source_path: str
    source_row: int
    x: int
    y: int
    width: int
    height: int
    rgba: bytes


def _validate_source_file(root: Path, resource: OriginalManagementHeaderResource) -> bytes:
    path = root / resource.source_path
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementHeaderError(
            f"Missing exact original management-header resource: {resource.source_path}"
        ) from exc
    if len(raw) != resource.byte_size:
        raise OriginalManagementHeaderError(
            f"Management-header byte-size mismatch: {resource.source_path}"
        )
    if sha256(raw).hexdigest() != resource.sha256:
        raise OriginalManagementHeaderError(
            f"Management-header checksum mismatch: {resource.source_path}"
        )
    header = parse_ea444_header(raw)
    if (header.width, header.height) != resource.size:
        raise OriginalManagementHeaderError(
            f"Management-header geometry mismatch: {resource.source_path}"
        )
    return raw


def validate_management_header_font(source_root: str | Path) -> EAFont:
    root = Path(source_root)
    path = root / HEADER_FONT_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementHeaderError(
            f"Missing exact original management-header font: {HEADER_FONT_SOURCE_PATH}"
        ) from exc
    if len(raw) != HEADER_FONT_BYTE_SIZE:
        raise OriginalManagementHeaderError("Management-header font byte-size mismatch")
    if sha256(raw).hexdigest() != HEADER_FONT_SHA256:
        raise OriginalManagementHeaderError("Management-header font checksum mismatch")
    return EAFont.from_bytes(raw)


def load_verified_management_header_resources(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalManagementHeaderResources:
    """Checksum-gate and decode only the exact source-qualified header family."""
    root = Path(source_root)
    left_raw = _validate_source_file(root, HEADER_LEFT_RESOURCE)
    right_raw = _validate_source_file(root, HEADER_RIGHT_RESOURCE)
    font = validate_management_header_font(root)

    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    left = decode_ea444(left_raw, tables=tables, quant=quant)
    right = decode_ea444(right_raw, tables=tables, quant=quant)
    return OriginalManagementHeaderResources(left, right, font)


def _crop_frame(image: EA444DecodedImage, source_row: int) -> bytes:
    if type(source_row) is not int or source_row < 0:
        raise OriginalManagementHeaderError("Management-header source row must be a non-negative integer")
    if image.height % HEADER_FRAME_HEIGHT:
        raise OriginalManagementHeaderError("Decoded management-header atlas has non-native frame height")
    frame_count = image.height // HEADER_FRAME_HEIGHT
    if source_row >= frame_count:
        raise OriginalManagementHeaderError("Management-header source row exceeds decoded atlas")
    stride = image.width * 4
    start = source_row * HEADER_FRAME_HEIGHT * stride
    end = start + HEADER_FRAME_HEIGHT * stride
    return image.rgba[start:end]


def management_header_overlays(
    resources: OriginalManagementHeaderResources,
    frame: OriginalManagementHeaderFrame,
) -> tuple[OriginalManagementHeaderOverlay, OriginalManagementHeaderOverlay]:
    """Crop one already-qualified native frame pair for host composition."""
    if not isinstance(resources, OriginalManagementHeaderResources):
        raise OriginalManagementHeaderError("Header overlay rendering requires verified source resources")
    if not isinstance(frame, OriginalManagementHeaderFrame):
        raise OriginalManagementHeaderError("Header overlay rendering requires a qualified source frame")

    left_rgba = _crop_frame(resources.left_anim, frame.left_source_row)
    right_rgba = _crop_frame(resources.right_state, frame.right_source_row)
    lx, ly, lw, lh = HEADER_LEFT_RECT
    rx, ry, rw, rh = HEADER_RIGHT_RECT
    return (
        OriginalManagementHeaderOverlay(
            "left_anim", HEADER_LEFT_RESOURCE.source_path, frame.left_source_row,
            lx, ly, lw, lh, left_rgba,
        ),
        OriginalManagementHeaderOverlay(
            "right_state", HEADER_RIGHT_RESOURCE.source_path, frame.right_source_row,
            rx, ry, rw, rh, right_rgba,
        ),
    )
