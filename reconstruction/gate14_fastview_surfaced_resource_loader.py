"""Verified original-source loader for one FastView surfaced selection.

This loader consumes only FastViewSurfacedResourceSelection. It never chooses a
club, month, badge variant or background fallback independently. It tries the
already recovered candidate paths in order, records the chosen source identity,
decodes with tables/quantization extracted from the canonical executable, and
requires native geometry.

If all three recovered background attempts are absent, loading fails closed:
the source terminal background fallback remains unresolved and is not replaced
with a guessed file.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
)


class FastViewSurfacedResourceLoadError(ValueError):
    pass


BACKGROUND_GEOMETRY = (800, 600)
BADGE_GEOMETRY = (135, 93)


@dataclass(frozen=True)
class VerifiedFastViewSurfacedResource:
    role: str
    source_path: str
    byte_size: int
    sha256: str
    geometry: tuple[int, int]
    rgba: bytes
    transparent_pixels: int

    def __post_init__(self) -> None:
        if self.role not in {"background", "home_badge", "away_badge"}:
            raise FastViewSurfacedResourceLoadError("unknown surfaced resource role")
        if not isinstance(self.source_path, str) or not self.source_path:
            raise FastViewSurfacedResourceLoadError("source_path must be non-empty")
        if type(self.byte_size) is not int or self.byte_size <= 0:
            raise FastViewSurfacedResourceLoadError("byte_size must be positive")
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)
        ):
            raise FastViewSurfacedResourceLoadError("sha256 must be lowercase hex")
        if (
            type(self.geometry) is not tuple
            or len(self.geometry) != 2
            or any(type(value) is not int or value <= 0 for value in self.geometry)
        ):
            raise FastViewSurfacedResourceLoadError("geometry must be positive pair")
        if len(self.rgba) != self.geometry[0] * self.geometry[1] * 4:
            raise FastViewSurfacedResourceLoadError("RGBA geometry mismatch")
        if type(self.transparent_pixels) is not int or self.transparent_pixels < 0:
            raise FastViewSurfacedResourceLoadError(
                "transparent_pixels must be non-negative"
            )


@dataclass(frozen=True)
class VerifiedFastViewSurfacedResourceSet:
    selection: FastViewSurfacedResourceSelection
    background: VerifiedFastViewSurfacedResource
    home_badge: VerifiedFastViewSurfacedResource
    away_badge: VerifiedFastViewSurfacedResource
    source_bytes_loaded: bool = True
    ea444_decoded: bool = True
    surfaced_picture_pixels_staged: bool = False
    complete_fastview_frame_recovered: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.selection) is not FastViewSurfacedResourceSelection:
            raise FastViewSurfacedResourceLoadError(
                "resource set requires exact surfaced selection"
            )
        if (
            self.background.role != "background"
            or self.home_badge.role != "home_badge"
            or self.away_badge.role != "away_badge"
        ):
            raise FastViewSurfacedResourceLoadError("resource roles are misordered")
        if not self.source_bytes_loaded or not self.ea444_decoded:
            raise FastViewSurfacedResourceLoadError(
                "verified resource set must represent loaded decoded originals"
            )
        if (
            self.surfaced_picture_pixels_staged
            or self.complete_fastview_frame_recovered
            or self.gate14_complete
        ):
            raise FastViewSurfacedResourceLoadError(
                "source loading cannot promote raster/frame/gate completion"
            )


def _native_path(source_root: Path, source_path: str) -> Path:
    parts = tuple(part for part in source_path.replace("/", "\\").split("\\") if part)
    if not parts:
        raise FastViewSurfacedResourceLoadError("empty source candidate path")
    return source_root.joinpath(*parts)


def _read_first_existing(
    source_root: Path,
    candidates: tuple[str, ...],
    *,
    role: str,
    unresolved_terminal_background: bool = False,
) -> tuple[str, bytes]:
    if type(candidates) is not tuple or not candidates:
        raise FastViewSurfacedResourceLoadError(
            f"{role} candidates must be a non-empty tuple"
        )
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate:
            raise FastViewSurfacedResourceLoadError(
                f"{role} candidate path must be non-empty"
            )
        path = _native_path(source_root, candidate)
        if path.is_file():
            return candidate, path.read_bytes()
    if unresolved_terminal_background:
        raise FastViewSurfacedResourceLoadError(
            "all recovered background attempts are absent; terminal original "
            "background fallback remains unresolved"
        )
    raise FastViewSurfacedResourceLoadError(
        f"all source-backed {role} attempts are absent"
    )


def _decode_verified(
    role: str,
    source_path: str,
    raw: bytes,
    *,
    expected_geometry: tuple[int, int],
    tables,
    quant,
) -> VerifiedFastViewSurfacedResource:
    if not isinstance(raw, bytes) or not raw:
        raise FastViewSurfacedResourceLoadError(
            f"{role} original source payload is empty"
        )
    try:
        image: EA444DecodedImage = decode_ea444(raw, tables=tables, quant=quant)
    except Exception as exc:
        raise FastViewSurfacedResourceLoadError(
            f"{role} selected original resource failed EA444 decode"
        ) from exc
    geometry = (image.width, image.height)
    if geometry != expected_geometry:
        raise FastViewSurfacedResourceLoadError(
            f"{role} decoded geometry {geometry} != source {expected_geometry}"
        )
    return VerifiedFastViewSurfacedResource(
        role=role,
        source_path=source_path,
        byte_size=len(raw),
        sha256=sha256(raw).hexdigest(),
        geometry=geometry,
        rgba=image.rgba,
        transparent_pixels=image.transparent_pixels,
    )



def _load_selected_background_with_decoder(
    selection: FastViewSurfacedResourceSelection,
    source_root: Path,
    *,
    tables,
    quant,
) -> VerifiedFastViewSurfacedResource:
    """Decode the already-selected background with caller-verified decoder state."""
    background_path, background_raw = _read_first_existing(
        source_root,
        selection.background_source_candidates,
        role="background",
        unresolved_terminal_background=True,
    )
    return _decode_verified(
        "background",
        background_path,
        background_raw,
        expected_geometry=BACKGROUND_GEOMETRY,
        tables=tables,
        quant=quant,
    )


def load_verified_selected_background(
    selection: FastViewSurfacedResourceSelection,
    *,
    source_root: str | Path,
    original_executable: str | Path,
) -> VerifiedFastViewSurfacedResource:
    """Load/decode only the source-selected Team_Backgrounds resource.

    PPreMatchPanel and FastView share the recovered background selector. This
    helper deliberately stops at the common background seam so pre-match does
    not need to load FastView-only club badges or duplicate candidate/fallback
    rules.
    """
    if type(selection) is not FastViewSurfacedResourceSelection:
        raise FastViewSurfacedResourceLoadError(
            "background loader requires exact FastViewSurfacedResourceSelection"
        )
    root = Path(source_root)
    if not root.is_dir():
        raise FastViewSurfacedResourceLoadError(
            "original source root is unavailable"
        )
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise FastViewSurfacedResourceLoadError(
            "canonical original executable is unavailable"
        ) from exc

    try:
        tables = tables_from_original_executable(executable)
        quant = quantization_from_verified_executable(executable)
    except Exception as exc:
        raise FastViewSurfacedResourceLoadError(
            "EA444 decode tables are not from the canonical original executable"
        ) from exc

    return _load_selected_background_with_decoder(
        selection,
        root,
        tables=tables,
        quant=quant,
    )


def load_verified_selected_badges(
    selection: FastViewSurfacedResourceSelection,
    *,
    source_root: str | Path,
    original_executable: str | Path,
) -> tuple[VerifiedFastViewSurfacedResource, VerifiedFastViewSurfacedResource]:
    """Load/decode only the source-selected home/away badge resources.

    PPreMatchPanel and FastView call the same native club-art selector 0x40C850
    for badge_2 and share the same generic fallback. This helper preserves that
    shared selector/loader contract without requiring the caller to load the
    unrelated Team_Backgrounds surface.
    """
    if type(selection) is not FastViewSurfacedResourceSelection:
        raise FastViewSurfacedResourceLoadError(
            "badge loader requires exact FastViewSurfacedResourceSelection"
        )
    root = Path(source_root)
    if not root.is_dir():
        raise FastViewSurfacedResourceLoadError(
            "original source root is unavailable"
        )
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise FastViewSurfacedResourceLoadError(
            "canonical original executable is unavailable"
        ) from exc

    try:
        tables = tables_from_original_executable(executable)
        quant = quantization_from_verified_executable(executable)
    except Exception as exc:
        raise FastViewSurfacedResourceLoadError(
            "EA444 decode tables are not from the canonical original executable"
        ) from exc

    home_path, home_raw = _read_first_existing(
        root,
        selection.home_badge_source_candidates,
        role="home_badge",
    )
    away_path, away_raw = _read_first_existing(
        root,
        selection.away_badge_source_candidates,
        role="away_badge",
    )
    return (
        _decode_verified(
            "home_badge",
            home_path,
            home_raw,
            expected_geometry=BADGE_GEOMETRY,
            tables=tables,
            quant=quant,
        ),
        _decode_verified(
            "away_badge",
            away_path,
            away_raw,
            expected_geometry=BADGE_GEOMETRY,
            tables=tables,
            quant=quant,
        ),
    )


def load_verified_fastview_surfaced_resources(
    selection: FastViewSurfacedResourceSelection,
    *,
    source_root: str | Path,
    original_executable: str | Path,
) -> VerifiedFastViewSurfacedResourceSet:
    """Load/decode only resources already selected by source-backed state."""
    if type(selection) is not FastViewSurfacedResourceSelection:
        raise FastViewSurfacedResourceLoadError(
            "loader requires exact FastViewSurfacedResourceSelection"
        )
    root = Path(source_root)
    exe_path = Path(original_executable)
    if not root.is_dir():
        raise FastViewSurfacedResourceLoadError(
            "original source root is unavailable"
        )
    try:
        executable = exe_path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewSurfacedResourceLoadError(
            "canonical original executable is unavailable"
        ) from exc

    # Both helpers independently verify the canonical executable identity.
    try:
        tables = tables_from_original_executable(executable)
        quant = quantization_from_verified_executable(executable)
    except Exception as exc:
        raise FastViewSurfacedResourceLoadError(
            "EA444 decode tables are not from the canonical original executable"
        ) from exc

    background = _load_selected_background_with_decoder(
        selection,
        root,
        tables=tables,
        quant=quant,
    )
    home_path, home_raw = _read_first_existing(
        root,
        selection.home_badge_source_candidates,
        role="home_badge",
    )
    away_path, away_raw = _read_first_existing(
        root,
        selection.away_badge_source_candidates,
        role="away_badge",
    )

    return VerifiedFastViewSurfacedResourceSet(
        selection=selection,
        background=background,
        home_badge=_decode_verified(
            "home_badge",
            home_path,
            home_raw,
            expected_geometry=BADGE_GEOMETRY,
            tables=tables,
            quant=quant,
        ),
        away_badge=_decode_verified(
            "away_badge",
            away_path,
            away_raw,
            expected_geometry=BADGE_GEOMETRY,
            tables=tables,
            quant=quant,
        ),
    )


def surfaced_resource_loader_contract() -> dict:
    return {
        "selection_only_input": True,
        "background_candidate_order_preserved": True,
        "badge_candidate_order_preserved": True,
        "background_geometry": BACKGROUND_GEOMETRY,
        "badge_geometry": BADGE_GEOMETRY,
        "canonical_executable_tables_required": True,
        "canonical_executable_quantization_required": True,
        "chosen_source_path_retained": True,
        "chosen_source_sha256_retained": True,
        "background_only_reusable_seam": True,
        "badge_only_reusable_seam": True,
        "terminal_background_fallback_recovered": False,
        "source_bytes_loaded": True,
        "ea444_decoded": True,
        "surfaced_picture_pixels_staged": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
