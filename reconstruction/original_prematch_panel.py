"""Source-backed original FM2001 PPreMatchPanel resources and geometry.

This module contains only first-hand recovered presentation facts. It does not
launch a fixture, simulate a match, or substitute FastView for the two native
3D modes.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont
from match_detail_mode import MATCH_DETAIL_LABELS, MatchDetailMode
from original_button_frames import (
    ButtonAtlasSpec,
    OriginalButtonAtlas,
    decode_verified_original_button_atlas,
)
from original_front_end_layout import OriginalRect


class OriginalPrematchPanelError(ValueError):
    pass


@dataclass(frozen=True)
class PrematchAssetSpec:
    source_path: str
    source_sha256: str
    width: int
    height: int


@dataclass(frozen=True)
class PrematchSelectorSpec:
    mode: MatchDetailMode
    event_id: int
    rect: OriginalRect
    language_global_va: int

    @property
    def label(self) -> str:
        return MATCH_DETAIL_LABELS[self.mode]


@dataclass(frozen=True)
class PrematchPlacement:
    role: str
    spec: PrematchAssetSpec
    rect: OriginalRect


@dataclass(frozen=True)
class PrematchPlayerStripRowSpec:
    side: str
    roster_group: str
    row_index: int
    rect: OriginalRect
    active_spec: PrematchAssetSpec
    disabled_spec: PrematchAssetSpec | None = None

    def __post_init__(self) -> None:
        if self.side not in ("left", "right"):
            raise OriginalPrematchPanelError("pre-match player row side must be left/right")
        if self.roster_group not in ("starter", "reserve"):
            raise OriginalPrematchPanelError(
                "pre-match player row group must be starter/reserve"
            )
        if self.row_index < 0:
            raise OriginalPrematchPanelError("pre-match player row index must be non-negative")
        if self.roster_group == "starter" and self.disabled_spec is not None:
            raise OriginalPrematchPanelError(
                "native starter rows do not construct a disabled strip variant"
            )
        if self.roster_group == "reserve" and self.disabled_spec is None:
            raise OriginalPrematchPanelError(
                "native reserve rows require the co-located disabled strip variant"
            )


@dataclass(frozen=True)
class PrematchRatingRowSpec:
    native_width_function_va: int
    native_record_discriminator: int
    y: int
    left_x: int = 65
    right_x: int = 564
    full_width: int = 171
    height: int = 16


# Shipped and initialized globally, but first-hand tracing of PPreMatchPanel
# proves that its live 800x600 background is instead built dynamically from
# Generic/Team_Backgrounds. Keep this exact source identity as negative evidence
# and do not silently promote it to a required/rendered panel asset.
PREMATCH_SHIPPED_BACKGROUND = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/prematch_bground.444",
    "964d6765d7eedd7d064b3c439ed144c851ab102ec029e8fc198df0c9adb31576",
    800,
    600,
)
PREMATCH_TOP_BAR = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/top_bar.444",
    "e3fb5f772784dd3608774aae44620e1ab932682b1f06d8153157d981ff869534",
    800,
    95,
)
PREMATCH_PITCH = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/pitch.444",
    "23a776bf9445818ac5356d6c4fa8ca0595affdaf5980bbbe6cdf9df2030a82dd",
    261,
    374,
)
PREMATCH_ACTIVE_LEFT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/playername_active_left.444",
    "da3bc727a6980b267165dcf8c63b235e12b07cd6aa446b7875b1e19519652a00",
    200,
    16,
)
PREMATCH_ACTIVE_RIGHT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/playername_active_right.444",
    "af809c7bb2961cc46b011fe8c7557b4eb23e97fffee6d99bd36178b48bd8b0d9",
    200,
    16,
)
PREMATCH_DISABLED_LEFT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/playername_disabled_left.444",
    "59e1a1e1714b1e9dab0929112246b59c6dcd9344841aab764ef87a1850b564cd",
    200,
    16,
)
PREMATCH_DISABLED_RIGHT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/playername_disabled_right.444",
    "c9138b788561b7c47082755cdaa26a432ca8ce41ec3b7d6373ba63f9ef75c2df",
    200,
    16,
)
PREMATCH_RATING_LEFT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/rating_bar_left.444",
    "3a7f14cee9067971c5267210bd235e457171aa9438b40be992a9009942fbc07c",
    171,
    16,
)
PREMATCH_RATING_RIGHT = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/rating_bar_right.444",
    "579421a7677aedae39663fe5e14a48f3b44eb053546ffa472407f0b639ea3652",
    171,
    16,
)
PREMATCH_RATING_RIGHT2 = PrematchAssetSpec(
    "FM2001_Art/Generic/pre_match/rating_bar_right2.444",
    "dae7d2a3649c199fdc5e8829c6c0cf603c0186747c0ee8671d6e9061f7b9f7b3",
    171,
    16,
)

PREMATCH_SELECTOR_ATLAS = ButtonAtlasSpec(
    "FM2001_Art/Generic/GenericButtonsAndBars/button_type_14.444",
    "7b0148bfa65adaa7cabf08e000050ba9add3cf852a03e66423051603c4b85930",
    106,
    575,
    106,
    25,
)
PREMATCH_FONT_PATH = "Fonts/Zurich_BdXCn_BT_20pixel.fnt"
PREMATCH_FONT_SHA256 = (
    "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166"
)

PREMATCH_LIVE_BACKGROUND_ROOT = "FM2001_Art/Generic/Team_Backgrounds"
PREMATCH_LIVE_BACKGROUND_RECT = OriginalRect(0, 0, 800, 600)
PREMATCH_LIVE_BACKGROUND_BUILDER_VA = 0x5D3490
PREMATCH_LIVE_BACKGROUND_SOURCE_ACCESSOR_VA = 0x5D3510
PREMATCH_LIVE_BACKGROUND_WRAPPER_OFFSET = 0x6B4
PREMATCH_LIVE_BACKGROUND_CACHE_OFFSET = 0x6D4

PREMATCH_SELECTORS = (
    PrematchSelectorSpec(
        MatchDetailMode.THREE_D_MATCH,
        4,
        OriginalRect(176, 107, 106, 25),
        0x981DD4,
    ),
    PrematchSelectorSpec(
        MatchDetailMode.THREE_D_HIGHLIGHTS,
        3,
        OriginalRect(290, 107, 106, 25),
        0x981DD0,
    ),
    PrematchSelectorSpec(
        MatchDetailMode.FASTVIEW,
        2,
        OriginalRect(404, 107, 106, 25),
        0x981DCC,
    ),
    PrematchSelectorSpec(
        MatchDetailMode.QUICK_MATCH,
        1,
        OriginalRect(518, 107, 106, 25),
        0x981DC8,
    ),
)

PREMATCH_STATIC_PLACEMENTS = (
    PrematchPlacement("top_bar", PREMATCH_TOP_BAR, OriginalRect(0, 0, 800, 95)),
    PrematchPlacement("pitch", PREMATCH_PITCH, OriginalRect(269, 152, 261, 374)),
    PrematchPlacement(
        "active_left", PREMATCH_ACTIVE_LEFT, OriginalRect(36, 152, 200, 16)
    ),
    PrematchPlacement(
        "active_right", PREMATCH_ACTIVE_RIGHT, OriginalRect(563, 152, 200, 16)
    ),
    PrematchPlacement(
        "disabled_left", PREMATCH_DISABLED_LEFT, OriginalRect(36, 358, 200, 16)
    ),
    PrematchPlacement(
        "disabled_right", PREMATCH_DISABLED_RIGHT, OriginalRect(563, 358, 200, 16)
    ),
)


# Recovery 368 expands the earlier first-row placement anchors into the full
# constructor-proven player-strip layout. The 11 starters use only the active
# side-specific strip. Each of the seven reserve rows constructs both the
# active and disabled side-specific strip at the same 200x16 rectangle; which
# variant is live is state-dependent and remains a separate control-state trace.
PREMATCH_STARTER_ROW_YS = tuple(152 + 18 * index for index in range(11))
PREMATCH_RESERVE_ROW_YS = tuple(358 + 18 * index for index in range(7))
PREMATCH_PLAYER_STRIP_ROWS = tuple(
    PrematchPlayerStripRowSpec(
        side=side,
        roster_group="starter",
        row_index=index,
        rect=OriginalRect(x, y, 200, 16),
        active_spec=active_spec,
    )
    for side, x, active_spec in (
        ("left", 36, PREMATCH_ACTIVE_LEFT),
        ("right", 563, PREMATCH_ACTIVE_RIGHT),
    )
    for index, y in enumerate(PREMATCH_STARTER_ROW_YS)
) + tuple(
    PrematchPlayerStripRowSpec(
        side=side,
        roster_group="reserve",
        row_index=index,
        rect=OriginalRect(x, y, 200, 16),
        active_spec=active_spec,
        disabled_spec=disabled_spec,
    )
    for side, x, active_spec, disabled_spec in (
        ("left", 36, PREMATCH_ACTIVE_LEFT, PREMATCH_DISABLED_LEFT),
        ("right", 563, PREMATCH_ACTIVE_RIGHT, PREMATCH_DISABLED_RIGHT),
    )
    for index, y in enumerate(PREMATCH_RESERVE_ROW_YS)
)


# Four native rating-width calculators test record discriminator 3, 0, 1, 2
# respectively and cap their integer result at the 171-pixel bar width. Calls
# made with side selector 0 size the left rating_bar_left overlay directly.
# Calls made with side selector 1 subtract that width from the right-side
# rating_bar_right object's right edge, mirroring the dynamic length.
PREMATCH_RATING_ROWS = (
    PrematchRatingRowSpec(0x49A3D0, 3, 497),
    PrematchRatingRowSpec(0x49A460, 0, 515),
    PrematchRatingRowSpec(0x49A4F0, 1, 533),
    PrematchRatingRowSpec(0x49A580, 2, 551),
)

# These are the source-proven resources the first panel seam may actually load.
# prematch_bground.444 is intentionally excluded because the live constructor
# uses Generic/Team_Backgrounds instead.
PREMATCH_ALL_EA444_SPECS = (
    PREMATCH_TOP_BAR,
    PREMATCH_PITCH,
    PREMATCH_ACTIVE_LEFT,
    PREMATCH_ACTIVE_RIGHT,
    PREMATCH_DISABLED_LEFT,
    PREMATCH_DISABLED_RIGHT,
    PREMATCH_RATING_LEFT,
    PREMATCH_RATING_RIGHT,
    PREMATCH_RATING_RIGHT2,
)


@dataclass(frozen=True)
class OriginalPrematchPanelResources:
    decoded_assets: tuple[tuple[PrematchAssetSpec, EA444DecodedImage], ...]
    selector_atlas: OriginalButtonAtlas
    font: EAFont
    source_bytes_verified: bool = True
    selector_geometry_source_closed: bool = True
    live_background_contract_source_closed: bool = True
    rating_bar_layout_source_closed: bool = True
    management_launch_trigger_recovered: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if len(self.decoded_assets) != len(PREMATCH_ALL_EA444_SPECS):
            raise OriginalPrematchPanelError("Prematch resource set is incomplete")
        for expected, (spec, decoded) in zip(
            PREMATCH_ALL_EA444_SPECS, self.decoded_assets
        ):
            if spec != expected:
                raise OriginalPrematchPanelError("Prematch resource order changed")
            if (decoded.width, decoded.height) != (spec.width, spec.height):
                raise OriginalPrematchPanelError(
                    f"Decoded geometry differs for {spec.source_path}"
                )
        if self.selector_atlas.spec != PREMATCH_SELECTOR_ATLAS:
            raise OriginalPrematchPanelError("Wrong pre-match selector atlas")
        if len(self.selector_atlas.frames) != 23:
            raise OriginalPrematchPanelError("Pre-match selector atlas must have 23 frames")
        if (
            not self.source_bytes_verified
            or not self.selector_geometry_source_closed
            or not self.live_background_contract_source_closed
            or not self.rating_bar_layout_source_closed
            or self.management_launch_trigger_recovered
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise OriginalPrematchPanelError(
                "Prematch resources cannot promote unresolved runtime/fidelity claims"
            )

    def decoded(self, source_path: str) -> EA444DecodedImage:
        for spec, image in self.decoded_assets:
            if spec.source_path == source_path:
                return image
        raise KeyError(source_path)


def _source_path(root: Path, source_path: str) -> Path:
    parts = tuple(part for part in source_path.replace("\\", "/").split("/") if part)
    return root.joinpath(*parts)


def _read_verified(root: Path, source_path: str, expected_sha256: str) -> bytes:
    try:
        data = _source_path(root, source_path).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalPrematchPanelError(
            f"Original pre-match source is unavailable: {source_path}"
        ) from exc
    actual = sha256(data).hexdigest()
    if actual != expected_sha256:
        raise OriginalPrematchPanelError(
            f"Original pre-match source checksum mismatch: {source_path}"
        )
    return data


def load_verified_original_prematch_resources(
    *,
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalPrematchPanelResources:
    """Load only exact hash-pinned original assets actually used by the seam."""
    root = Path(source_root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalPrematchPanelError(
            "Canonical original executable is unavailable"
        ) from exc

    try:
        tables = tables_from_original_executable(executable)
        quant = quantization_from_verified_executable(executable)
    except Exception as exc:
        raise OriginalPrematchPanelError(
            "Pre-match EA444 tables are not from the canonical executable"
        ) from exc

    decoded_assets = []
    for spec in PREMATCH_ALL_EA444_SPECS:
        raw = _read_verified(root, spec.source_path, spec.source_sha256)
        try:
            decoded = decode_ea444(raw, tables=tables, quant=quant)
        except Exception as exc:
            raise OriginalPrematchPanelError(
                f"Original pre-match resource failed EA444 decode: {spec.source_path}"
            ) from exc
        if (decoded.width, decoded.height) != (spec.width, spec.height):
            raise OriginalPrematchPanelError(
                f"Original pre-match geometry mismatch: {spec.source_path}"
            )
        decoded_assets.append((spec, decoded))

    selector_raw = _read_verified(
        root,
        PREMATCH_SELECTOR_ATLAS.source_path,
        PREMATCH_SELECTOR_ATLAS.source_sha256,
    )
    try:
        selector_atlas = decode_verified_original_button_atlas(
            selector_raw,
            spec=PREMATCH_SELECTOR_ATLAS,
            tables=tables,
            quant=quant,
        )
    except Exception as exc:
        raise OriginalPrematchPanelError(
            "Original pre-match selector atlas could not be decoded exactly"
        ) from exc

    font_raw = _read_verified(root, PREMATCH_FONT_PATH, PREMATCH_FONT_SHA256)
    try:
        font = EAFont.from_bytes(font_raw)
    except Exception as exc:
        raise OriginalPrematchPanelError(
            "Original pre-match Zurich font could not be parsed"
        ) from exc

    return OriginalPrematchPanelResources(
        decoded_assets=tuple(decoded_assets),
        selector_atlas=selector_atlas,
        font=font,
    )


def prematch_panel_contract() -> dict:
    return {
        "native_surface": (800, 600),
        "selector_modes_left_to_right": tuple(
            int(selector.mode) for selector in PREMATCH_SELECTORS
        ),
        "selector_labels_left_to_right": tuple(
            selector.label for selector in PREMATCH_SELECTORS
        ),
        "selector_events_left_to_right": tuple(
            selector.event_id for selector in PREMATCH_SELECTORS
        ),
        "selector_rects": tuple(
            (
                selector.rect.x,
                selector.rect.y,
                selector.rect.width,
                selector.rect.height,
            )
            for selector in PREMATCH_SELECTORS
        ),
        "selector_atlas_path": PREMATCH_SELECTOR_ATLAS.source_path,
        "selector_atlas_frames": PREMATCH_SELECTOR_ATLAS.frame_count,
        "selector_font_path": PREMATCH_FONT_PATH,
        "static_placement_roles": tuple(
            placement.role for placement in PREMATCH_STATIC_PLACEMENTS
        ),
        "starter_row_ys": PREMATCH_STARTER_ROW_YS,
        "reserve_row_ys": PREMATCH_RESERVE_ROW_YS,
        "player_strip_row_count": len(PREMATCH_PLAYER_STRIP_ROWS),
        "player_strip_starter_count_per_side": 11,
        "player_strip_reserve_count_per_side": 7,
        "reserve_rows_construct_active_and_disabled_variants": True,
        "reserve_variant_state_source_closed": False,
        "live_background_root": PREMATCH_LIVE_BACKGROUND_ROOT,
        "live_background_rect": (
            PREMATCH_LIVE_BACKGROUND_RECT.x,
            PREMATCH_LIVE_BACKGROUND_RECT.y,
            PREMATCH_LIVE_BACKGROUND_RECT.width,
            PREMATCH_LIVE_BACKGROUND_RECT.height,
        ),
        "live_background_builder_va": PREMATCH_LIVE_BACKGROUND_BUILDER_VA,
        "live_background_source_accessor_va": PREMATCH_LIVE_BACKGROUND_SOURCE_ACCESSOR_VA,
        "shipped_prematch_background_path": PREMATCH_SHIPPED_BACKGROUND.source_path,
        "shipped_prematch_background_is_live_panel_background": False,
        "rating_rows": tuple(
            (
                row.native_width_function_va,
                row.native_record_discriminator,
                row.left_x,
                row.right_x,
                row.y,
                row.full_width,
                row.height,
            )
            for row in PREMATCH_RATING_ROWS
        ),
        "rating_left_dynamic_asset": PREMATCH_RATING_LEFT.source_path,
        "rating_left_base_asset": PREMATCH_RATING_RIGHT.source_path,
        "rating_right_base_asset": PREMATCH_RATING_RIGHT2.source_path,
        "rating_right_mask_asset": PREMATCH_RATING_RIGHT.source_path,
        "live_background_contract_source_closed": True,
        "rating_bar_layout_source_closed": True,
        "management_launch_trigger_recovered": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
