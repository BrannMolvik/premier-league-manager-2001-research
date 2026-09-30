"""Load the authentic source-backed PStartMenu inputs as a single resource bundle.

This is intentionally NOT a final screenshot renderer. The original global/menu
background overlay is recovered, as are the four action rectangles, English
IDX mappings, Zurich bitmap glyphs, and 23 true source button frames. Native
Button@ease_2001 frame-state selection, caption placement/color and unrelated
PStartMenu events 5..7 still require executable evidence. This module leaves
them unassigned instead of replacing them with a visually approximate UI.

It accepts independently extracted, authorized original files. No original
executable, font, or large atlas is silently shipped with test fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont
from ea_language_strings import parse_language_pair
from original_button_frames import (
    OriginalButtonAtlas,
    PSTARTMENU_BUTTON_ATLAS,
    decode_verified_original_button_atlas,
)
from original_front_end_layout import (
    GLOBAL_BACKGROUND_PATH,
    PSTARTMENU_ACTIONS,
    PSTARTMENU_BACKGROUND_PATH,
    SCREEN_SIZE,
    compose_pstartmenu_background,
)
from original_pstartmenu_labels import (
    PStartMenuCaption,
    prepare_original_pstartmenu_captions,
)


GLOBAL_BACKGROUND_SHA256 = (
    "9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9"
)
MENU_BACKGROUND_SHA256 = (
    "297b54dbee7d7d31a081b1459ed497b251c2bf1aa00092976557d5b8065e7e4b"
)
ZURICH_FONT20_SHA256 = (
    "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166"
)
ENGLISH_STR_SHA256 = (
    "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601"
)
ENGLISH_IDX_SHA256 = (
    "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1"
)
# Source-derived exact 800x600 background composition; excludes ALL buttons/text.
COMPOSED_BACKGROUND_RGBA_SHA256 = (
    "e5b9190b830440a340f162a81eab59270182b74a15bae0a3f24660a7c5d21046"
)
ENGLISH_ACTION_TEXTS = (
    "Continue", "Start New Game", "Load Game", "Quit to Windows"
)


class OriginalPStartMenuResourceError(ValueError):
    """An expected original source resource differs or is incomplete."""


@dataclass(frozen=True)
class OriginalPStartMenuResources:
    background_rgba: bytes
    button_atlas: OriginalButtonAtlas
    captions: tuple[PStartMenuCaption, ...]

    def __post_init__(self) -> None:
        if len(self.background_rgba) != SCREEN_SIZE[0] * SCREEN_SIZE[1] * 4:
            raise OriginalPStartMenuResourceError(
                "Original menu background must be a complete 800x600 RGBA image"
            )
        if self.button_atlas.spec != PSTARTMENU_BUTTON_ATLAS:
            raise OriginalPStartMenuResourceError("Wrong original menu button atlas")
        if len(self.button_atlas.frames) != PSTARTMENU_BUTTON_ATLAS.frame_count:
            raise OriginalPStartMenuResourceError(
                "Original menu button atlas is missing source frames"
            )
        if any(
            (frame.width, frame.height) != (
                PSTARTMENU_BUTTON_ATLAS.frame_width,
                PSTARTMENU_BUTTON_ATLAS.frame_height,
            )
            for frame in self.button_atlas.frames
        ):
            raise OriginalPStartMenuResourceError(
                "Original menu button source frames have incorrect geometry"
            )
        if tuple((caption.event, caption.source_idx_position, caption.control_rect)
                 for caption in self.captions) != tuple(
            (action.event, action.language_index, action.rect)
            for action in PSTARTMENU_ACTIONS
        ):
            raise OriginalPStartMenuResourceError(
                "Menu caption binding differs from recovered executable layout"
            )


def assemble_original_pstartmenu_inputs(
    global_background: EA444DecodedImage,
    menu_background: EA444DecodedImage,
    button_atlas: OriginalButtonAtlas,
    captions: tuple[PStartMenuCaption, ...],
) -> OriginalPStartMenuResources:
    """Compose only proven background layers; keep source controls unrendered."""
    return OriginalPStartMenuResources(
        compose_pstartmenu_background(global_background, menu_background),
        button_atlas,
        captions,
    )


def _read_verified(path: Path, expected_sha256: str) -> bytes:
    data = Path(path).read_bytes()
    if sha256(data).hexdigest() != expected_sha256:
        raise OriginalPStartMenuResourceError(
            f"Original asset checksum mismatch: {path}"
        )
    return data


def _read_art(original_art_dir: Path, path: str, sha: str) -> bytes:
    # The caller supplies the FM2001_Art root; the canonical relative paths
    # are explicitly recorded in original_front_end_layout.py.
    return _read_verified(
        Path(original_art_dir) / path.removeprefix("FM2001_Art/"), sha
    )


def load_verified_english_pstartmenu_inputs(
    *,
    original_art_dir: Path,
    original_language_dir: Path,
    original_zurich_font20: Path,
    original_executable: Path,
) -> OriginalPStartMenuResources:
    """Build render-ready original resources from the authorized source bytes.

    Every named original asset has a pinned first-hand SHA-256. The original
    executable is separately verified by the EA444 table/quantization parsers.
    Unrecovered button-state selection and label alignment stay unset.
    """
    exe = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)

    base = decode_ea444(
        _read_art(original_art_dir, GLOBAL_BACKGROUND_PATH, GLOBAL_BACKGROUND_SHA256),
        tables=tables, quant=quant,
    )
    menu = decode_ea444(
        _read_art(original_art_dir, PSTARTMENU_BACKGROUND_PATH, MENU_BACKGROUND_SHA256),
        tables=tables, quant=quant,
    )
    raw_atlas = _read_art(
        original_art_dir,
        PSTARTMENU_BUTTON_ATLAS.source_path,
        PSTARTMENU_BUTTON_ATLAS.source_sha256,
    )
    buttons = decode_verified_original_button_atlas(
        raw_atlas, spec=PSTARTMENU_BUTTON_ATLAS, tables=tables, quant=quant,
    )
    font = EAFont.from_bytes(
        _read_verified(original_zurich_font20, ZURICH_FONT20_SHA256)
    )
    language_dir = Path(original_language_dir)
    strings, index = parse_language_pair(
        _read_verified(language_dir / "English.str", ENGLISH_STR_SHA256),
        _read_verified(language_dir / "English.idx", ENGLISH_IDX_SHA256),
    )
    captions = prepare_original_pstartmenu_captions(font, strings, index)
    if tuple(item.original_text for item in captions) != ENGLISH_ACTION_TEXTS:
        raise OriginalPStartMenuResourceError(
            "Verified English resources no longer map to original menu captions"
        )

    result = assemble_original_pstartmenu_inputs(base, menu, buttons, captions)
    if sha256(result.background_rgba).hexdigest() != COMPOSED_BACKGROUND_RGBA_SHA256:
        raise OriginalPStartMenuResourceError(
            "Source-backed original menu background RGBA regression"
        )
    return result
