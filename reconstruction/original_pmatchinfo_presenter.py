"""Read-only source-art presentation seam for recovered FM2001 PMatchInfo.

This module composes only source-proven PMatchInfo presentation inputs. It does
not simulate a match, translate reconstructed MatchEvent objects into original
event-record semantics, or invent missing controls. The full 760x500 dialog now requires the complete
byte-identical staged runtime presentation set, including info_popup.444.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_league_fixtures_resources import LEAGUE_FIXTURES_MATCH_INFO_SIZE
from original_pmatchinfo_resources import (
    OriginalPMatchInfoPlacement,
    OriginalPMatchInfoResourceError,
    OriginalPMatchInfoTab,
    OriginalPMatchInfoTextPlacement,
    PMATCHINFO_DEFAULT_TAB_EVENT_ID,
    PMATCHINFO_DYNAMIC_INCIDENT_RECT,
    PMATCHINFO_PENDING_PRESENTATION_RESOURCE_NAMES,
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_RESOURCE_PLACEMENTS,
    PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES,
    PMATCHINFO_TABS,
    PMATCHINFO_TEXT_PLACEMENTS,
    pmatchinfo_import_path,
    pmatchinfo_script_incident_selection,
    validate_staged_pmatchinfo_presentation_assets,
)


class OriginalPMatchInfoPresentationError(ValueError):
    """The source-backed PMatchInfo presentation cannot be constructed safely."""


@dataclass(frozen=True)
class OriginalPMatchInfoArt:
    resource_name: str
    source_size: tuple[int, int]
    rgba: bytes


@dataclass(frozen=True)
class OriginalPMatchInfoArtPlacement:
    resource_name: str
    rect: tuple[int, int, int, int]
    source_size: tuple[int, int]
    rgba: bytes

    def __post_init__(self) -> None:
        x, y, width, height = self.rect
        if width <= 0 or height <= 0:
            raise OriginalPMatchInfoPresentationError(
                f"Invalid PMatchInfo placement geometry for {self.resource_name}"
            )
        if len(self.rgba) != width * height * 4:
            raise OriginalPMatchInfoPresentationError(
                f"RGBA size does not match placement for {self.resource_name}"
            )
        if width > self.source_size[0] or height > self.source_size[1]:
            raise OriginalPMatchInfoPresentationError(
                f"Placement exceeds source art for {self.resource_name}"
            )


@dataclass(frozen=True)
class OriginalPMatchInfoStaticSnapshot:
    dialog_size: tuple[int, int]
    complete_dialog_background_available: bool
    selected_tab_event_id: int
    tabs: tuple[OriginalPMatchInfoTab, ...]
    text_slots: tuple[OriginalPMatchInfoTextPlacement, ...]
    art: tuple[OriginalPMatchInfoArtPlacement, ...]


def _crop_top_left(
    image: EA444DecodedImage,
    width: int,
    height: int,
) -> bytes:
    if width > image.width or height > image.height:
        raise OriginalPMatchInfoPresentationError(
            "PMatchInfo source crop exceeds decoded EA444 geometry"
        )
    if width == image.width and height == image.height:
        return image.rgba
    out = bytearray(width * height * 4)
    for row in range(height):
        src_start = row * image.width * 4
        src_end = src_start + width * 4
        dst_start = row * width * 4
        out[dst_start:dst_start + width * 4] = image.rgba[src_start:src_end]
    return bytes(out)


def build_staged_pmatchinfo_snapshot(
    decoded_art: dict[str, EA444DecodedImage],
    *,
    require_complete_dialog: bool = False,
    selected_tab_event_id: int = PMATCHINFO_DEFAULT_TAB_EVENT_ID,
) -> OriginalPMatchInfoStaticSnapshot:
    """Build the source-proven PMatchInfo static presentation contract.

    The nine recovered resource placements are owner-local. The one negative
    y-origin is preserved rather than clamped. The disabled player strip is
    source-proven as a 274x16 image placed through a 252x16 control, so only
    that top-left source rectangle is exposed for rendering.
    """
    if type(require_complete_dialog) is not bool:
        raise OriginalPMatchInfoPresentationError(
            "require_complete_dialog must be boolean"
        )
    tabs = tuple(PMATCHINFO_TABS)
    if selected_tab_event_id not in {tab.event_id for tab in tabs}:
        raise OriginalPMatchInfoPresentationError(
            "selected PMatchInfo tab event is outside the recovered tab set"
        )

    missing_staged = [
        name
        for name in PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES
        if name not in decoded_art
    ]
    if missing_staged:
        raise OriginalPMatchInfoPresentationError(
            "Missing decoded staged PMatchInfo art: " + ", ".join(missing_staged)
        )

    popup_available = "info_popup" in decoded_art
    if require_complete_dialog and not popup_available:
        raise OriginalPMatchInfoPresentationError(
            "Complete PMatchInfo dialog requires exact info_popup.444"
        )

    placements = []
    for placement in PMATCHINFO_RESOURCE_PLACEMENTS:
        image = decoded_art.get(placement.resource_name)
        if image is None:
            if placement.resource_name in PMATCHINFO_PENDING_PRESENTATION_RESOURCE_NAMES:
                continue
            raise OriginalPMatchInfoPresentationError(
                f"Decoded PMatchInfo art missing for {placement.resource_name}"
            )
        resource = PMATCHINFO_RESOURCE_BY_NAME[placement.resource_name]
        if (image.width, image.height) != resource.size:
            raise OriginalPMatchInfoPresentationError(
                f"Decoded PMatchInfo source geometry mismatch: {placement.resource_name}"
            )
        placements.append(
            OriginalPMatchInfoArtPlacement(
                resource_name=placement.resource_name,
                rect=placement.rect,
                source_size=resource.size,
                rgba=_crop_top_left(image, placement.width, placement.height),
            )
        )

    return OriginalPMatchInfoStaticSnapshot(
        dialog_size=LEAGUE_FIXTURES_MATCH_INFO_SIZE,
        complete_dialog_background_available=popup_available,
        selected_tab_event_id=selected_tab_event_id,
        tabs=tabs,
        text_slots=tuple(PMATCHINFO_TEXT_PLACEMENTS),
        art=tuple(placements),
    )


def load_staged_pmatchinfo_snapshot(
    repo_root: Path,
    original_executable: Path,
    *,
    require_complete_dialog: bool = False,
    selected_tab_event_id: int = PMATCHINFO_DEFAULT_TAB_EVENT_ID,
) -> OriginalPMatchInfoStaticSnapshot:
    """Decode the exact staged source files and build the static snapshot."""
    root = Path(repo_root)
    validate_staged_pmatchinfo_presentation_assets(root)

    exe = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)

    decoded: dict[str, EA444DecodedImage] = {}
    for name in PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES:
        path = pmatchinfo_import_path(root, name)
        decoded[name] = decode_ea444(path.read_bytes(), tables=tables, quant=quant)

    popup_path = pmatchinfo_import_path(root, "info_popup")
    if popup_path.exists():
        resource = PMATCHINFO_RESOURCE_BY_NAME["info_popup"]
        data = popup_path.read_bytes()
        from hashlib import sha256
        if len(data) != resource.byte_size or sha256(data).hexdigest() != resource.sha256:
            raise OriginalPMatchInfoPresentationError(
                "Staged info_popup.444 differs from source-proven bytes"
            )
        decoded["info_popup"] = decode_ea444(data, tables=tables, quant=quant)

    return build_staged_pmatchinfo_snapshot(
        decoded,
        require_complete_dialog=require_complete_dialog,
        selected_tab_event_id=selected_tab_event_id,
    )


def build_dynamic_incident_art(
    decoded_art: dict[str, EA444DecodedImage],
    event_type: int,
    *,
    row_field_74: int = 0,
    row_field_78: int = 0,
    event_field_20: int = 0,
    event_field_18: int = 0,
    event_field_1c: int = 0,
) -> OriginalPMatchInfoArtPlacement | None:
    """Select only the already source-proven incident label/resource branch."""
    selection = pmatchinfo_script_incident_selection(
        event_type,
        row_field_74=row_field_74,
        row_field_78=row_field_78,
        event_field_20=event_field_20,
        event_field_18=event_field_18,
        event_field_1c=event_field_1c,
    )
    if selection is None:
        return None
    image = decoded_art.get(selection.resource_name)
    if image is None:
        raise OriginalPMatchInfoPresentationError(
            f"Missing decoded incident art: {selection.resource_name}"
        )
    resource = PMATCHINFO_RESOURCE_BY_NAME[selection.resource_name]
    if (image.width, image.height) != resource.size:
        raise OriginalPMatchInfoPresentationError(
            f"Incident art geometry mismatch: {selection.resource_name}"
        )
    x, y, width, height = PMATCHINFO_DYNAMIC_INCIDENT_RECT
    return OriginalPMatchInfoArtPlacement(
        selection.resource_name,
        (x, y, width, height),
        resource.size,
        _crop_top_left(image, width, height),
    )
