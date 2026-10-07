"""Verified source loader for PPreMatch starting-XI shirt resources.

This joins the source-closed 0x408320 custom/generic decision to original bytes.
Primary custom .444 atlases are decoded directly. Alternate context, or a
missing primary custom atlas, uses the native TeamNN.bmp palette-recolor path.
The goalkeeper remains the dedicated 36x32 original .444 resource.

No team selection, formation, or player-frame policy is invented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_prematch_generic_shirt import recolor_prematch_generic_shirt
from gate14_prematch_shirt_selection import (
    PREMATCH_PLAYER_ALTERNATE_SHIRT_NUMBER_OFFSET,
    PREMATCH_PLAYER_PRIMARY_SHIRT_NUMBER_OFFSET,
    PREMATCH_SHIRT_FRAME_HEIGHT,
    PREMATCH_SHIRT_FRAME_WIDTH,
    PrematchClubShirtState,
    PrematchSideKitContext,
    prematch_player_shirt_frame_offset,
)
from original_prematch_panel import PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_PATH


class PrematchShirtResourceError(ValueError):
    pass


PREMATCH_NUMBERED_ATLAS_SIZE = (36, 1280)
PREMATCH_NUMBERED_FRAME_COUNT = 40
PREMATCH_GOALKEEPER_SIZE = (36, 32)


@dataclass(frozen=True)
class PrematchNumberedShirtAtlas:
    source_kind: str
    source_path: str
    source_sha256: str
    rgba: bytes
    club_id: int
    use_alternate: bool
    source_pixels_verified: bool = True

    def __post_init__(self) -> None:
        if self.source_kind not in ("custom_ea444", "generated_generic_bmp"):
            raise PrematchShirtResourceError("unknown numbered-shirt source kind")
        if not self.source_path or len(self.source_sha256) != 64:
            raise PrematchShirtResourceError("numbered-shirt source identity is incomplete")
        if len(self.rgba) != 36 * 1280 * 4:
            raise PrematchShirtResourceError("numbered-shirt atlas must remain 36x1280")
        if type(self.club_id) is not int or self.club_id < 0:
            raise PrematchShirtResourceError("numbered-shirt club id is invalid")
        if not self.source_pixels_verified:
            raise PrematchShirtResourceError("numbered-shirt pixels must remain source-backed")
        if self.use_alternate and self.source_kind == "custom_ea444":
            raise PrematchShirtResourceError(
                "alternate context cannot promote a custom primary atlas"
            )


@dataclass(frozen=True)
class PrematchGoalkeeperShirt:
    source_path: str
    source_sha256: str
    rgba: bytes
    source_pixels_verified: bool = True

    def __post_init__(self) -> None:
        if not self.source_path or len(self.source_sha256) != 64:
            raise PrematchShirtResourceError("goalkeeper source identity is incomplete")
        if len(self.rgba) != 36 * 32 * 4:
            raise PrematchShirtResourceError("goalkeeper shirt must remain 36x32")
        if not self.source_pixels_verified:
            raise PrematchShirtResourceError("goalkeeper pixels must be verified originals")


@dataclass(frozen=True)
class PrematchShirtFrame:
    source_kind: str
    source_path: str
    frame_number: int
    source_y: int
    rgba: bytes

    def __post_init__(self) -> None:
        if self.source_kind not in ("custom_ea444", "generated_generic_bmp"):
            raise PrematchShirtResourceError("unknown cropped shirt-frame source kind")
        if not 1 <= self.frame_number <= PREMATCH_NUMBERED_FRAME_COUNT:
            raise PrematchShirtResourceError("shirt frame number must be in native 1..40")
        if self.source_y != (self.frame_number - 1) * PREMATCH_SHIRT_FRAME_HEIGHT:
            raise PrematchShirtResourceError("shirt frame y offset differs from native rule")
        if len(self.rgba) != PREMATCH_SHIRT_FRAME_WIDTH * PREMATCH_SHIRT_FRAME_HEIGHT * 4:
            raise PrematchShirtResourceError("shirt frame must remain 36x32")


def _source_parts(source_path: str) -> tuple[str, ...]:
    return tuple(
        part for part in source_path.replace("\\", "/").split("/") if part
    )


def _resolve_casefold_source(root: Path, source_path: str) -> Path:
    """Resolve original Windows paths safely on a case-sensitive analysis host."""
    current = root
    for part in _source_parts(source_path):
        direct = current / part
        if direct.exists():
            current = direct
            continue
        if not current.is_dir():
            raise FileNotFoundError(source_path)
        matches = [item for item in current.iterdir() if item.name.casefold() == part.casefold()]
        if len(matches) != 1:
            raise FileNotFoundError(source_path)
        current = matches[0]
    if not current.is_file():
        raise FileNotFoundError(source_path)
    return current


def _read_optional_source(root: Path, source_path: str) -> bytes | None:
    try:
        return _resolve_casefold_source(root, source_path).read_bytes()
    except FileNotFoundError:
        return None


def _decoder_state(original_executable: str | Path):
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise PrematchShirtResourceError(
            "canonical original executable is unavailable"
        ) from exc
    try:
        tables = tables_from_original_executable(executable)
        quant = quantization_from_verified_executable(executable)
    except Exception as exc:
        raise PrematchShirtResourceError(
            "shirt decode state is not from the canonical original executable"
        ) from exc
    return executable, tables, quant


def load_prematch_numbered_shirt_atlas(
    *,
    club: PrematchClubShirtState,
    context: PrematchSideKitContext,
    source_root: str | Path,
    original_executable: str | Path,
) -> PrematchNumberedShirtAtlas:
    if type(club) is not PrematchClubShirtState:
        raise PrematchShirtResourceError("exact club shirt state is required")
    if type(context) is not PrematchSideKitContext:
        raise PrematchShirtResourceError("exact side kit context is required")
    root = Path(source_root)
    if not root.is_dir():
        raise PrematchShirtResourceError("original source root is unavailable")

    executable, tables, quant = _decoder_state(original_executable)

    if context.custom_source_path is not None:
        custom_raw = _read_optional_source(root, context.custom_source_path)
        if custom_raw is not None:
            try:
                decoded = decode_ea444(custom_raw, tables=tables, quant=quant)
            except Exception as exc:
                raise PrematchShirtResourceError(
                    "custom numbered-shirt atlas failed original EA444 decode"
                ) from exc
            if (decoded.width, decoded.height) != PREMATCH_NUMBERED_ATLAS_SIZE:
                raise PrematchShirtResourceError(
                    "custom numbered-shirt atlas geometry differs from 36x1280"
                )
            return PrematchNumberedShirtAtlas(
                source_kind="custom_ea444",
                source_path=context.custom_source_path,
                source_sha256=sha256(custom_raw).hexdigest(),
                rgba=decoded.rgba,
                club_id=club.club_id,
                use_alternate=False,
            )

    generic_raw = _read_optional_source(root, context.generic_source_path)
    if generic_raw is None:
        raise PrematchShirtResourceError(
            "native generic numbered-shirt BMP fallback is unavailable"
        )
    try:
        generated = recolor_prematch_generic_shirt(
            generic_raw,
            executable=executable,
            club=club,
            context=context,
        )
    except Exception as exc:
        raise PrematchShirtResourceError(
            "generic numbered-shirt BMP could not be reproduced"
        ) from exc
    return PrematchNumberedShirtAtlas(
        source_kind="generated_generic_bmp",
        source_path=context.generic_source_path,
        source_sha256=sha256(generic_raw).hexdigest(),
        rgba=generated.rgba,
        club_id=club.club_id,
        use_alternate=context.use_alternate,
    )


def load_prematch_goalkeeper_shirt(
    *,
    source_root: str | Path,
    original_executable: str | Path,
) -> PrematchGoalkeeperShirt:
    root = Path(source_root)
    if not root.is_dir():
        raise PrematchShirtResourceError("original source root is unavailable")
    _executable, tables, quant = _decoder_state(original_executable)
    raw = _read_optional_source(root, PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_PATH)
    if raw is None:
        raise PrematchShirtResourceError("original goalkeeper shirt is unavailable")
    try:
        decoded = decode_ea444(raw, tables=tables, quant=quant)
    except Exception as exc:
        raise PrematchShirtResourceError(
            "goalkeeper shirt failed original EA444 decode"
        ) from exc
    if (decoded.width, decoded.height) != PREMATCH_GOALKEEPER_SIZE:
        raise PrematchShirtResourceError(
            "goalkeeper shirt geometry differs from native 36x32"
        )
    return PrematchGoalkeeperShirt(
        source_path=PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_PATH,
        source_sha256=sha256(raw).hexdigest(),
        rgba=decoded.rgba,
    )


def crop_prematch_numbered_shirt_frame(
    atlas: PrematchNumberedShirtAtlas,
    *,
    player_registered_club_id: int,
    team_club_id: int,
    primary_shirt_number: int,
    alternate_shirt_number: int | None = None,
) -> PrematchShirtFrame:
    if type(atlas) is not PrematchNumberedShirtAtlas:
        raise PrematchShirtResourceError("exact numbered-shirt atlas is required")
    if alternate_shirt_number is None:
        # 0x418E27..0x418E31 initializes +0x76 directly from +0x70.
        # This default is valid until a later recovered 0x41E400 update is supplied.
        alternate_shirt_number = primary_shirt_number
    source_y = prematch_player_shirt_frame_offset(
        player_registered_club_id=player_registered_club_id,
        team_club_id=team_club_id,
        primary_shirt_number=primary_shirt_number,
        alternate_shirt_number=alternate_shirt_number,
    )
    if source_y < 0 or source_y + PREMATCH_SHIRT_FRAME_HEIGHT > PREMATCH_NUMBERED_ATLAS_SIZE[1]:
        raise PrematchShirtResourceError(
            "source-selected shirt number is outside the native 40-frame atlas"
        )
    frame_number = source_y // PREMATCH_SHIRT_FRAME_HEIGHT + 1
    row_bytes = PREMATCH_SHIRT_FRAME_WIDTH * 4
    frame = bytearray(PREMATCH_SHIRT_FRAME_WIDTH * PREMATCH_SHIRT_FRAME_HEIGHT * 4)
    for y in range(PREMATCH_SHIRT_FRAME_HEIGHT):
        src = ((source_y + y) * PREMATCH_SHIRT_FRAME_WIDTH) * 4
        dst = y * row_bytes
        frame[dst:dst + row_bytes] = atlas.rgba[src:src + row_bytes]
    return PrematchShirtFrame(
        source_kind=atlas.source_kind,
        source_path=atlas.source_path,
        frame_number=frame_number,
        source_y=source_y,
        rgba=bytes(frame),
    )


def prematch_shirt_resource_contract() -> dict:
    return {
        "numbered_atlas_size": PREMATCH_NUMBERED_ATLAS_SIZE,
        "numbered_frame_count": PREMATCH_NUMBERED_FRAME_COUNT,
        "goalkeeper_size": PREMATCH_GOALKEEPER_SIZE,
        "primary_custom_then_generic_fallback": True,
        "alternate_generic_only": True,
        "goalkeeper_dedicated_original": True,
        "player_primary_number_offset": PREMATCH_PLAYER_PRIMARY_SHIRT_NUMBER_OFFSET,
        "player_alternate_number_offset": PREMATCH_PLAYER_ALTERNATE_SHIRT_NUMBER_OFFSET,
        "alternate_number_initializes_from_primary": True,
        "alternate_number_initializer_va": 0x418E27,
        "alternate_number_update_va": 0x41E400,
        "source_pixels_staged": True,
        "marker_binding_complete": False,
        "gate14_complete": False,
    }
