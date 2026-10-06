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

# Source-closed PPreMatch identity/text contracts recovered from the canonical
# executable.  Keep the two match sides neutral here: their structural halves
# are proven, while presentation naming belongs to the higher-level match model.
PREMATCH_DATE_FORMAT = "%Df %Mf %Yf"
PREMATCH_DATE_FORMAT_VA = 0x81D5B8
PREMATCH_DATE_BUFFER_OFFSET = 0x70
PREMATCH_WEATHER_TEMPERATURE_FORMAT = "%s %d°C"
PREMATCH_WEATHER_TEMPERATURE_FORMAT_VA = 0x81D5B0
PREMATCH_DATE_WEATHER_FORMAT = "%s %s"
PREMATCH_DATE_WEATHER_LANGUAGE_GLOBAL_VA = 0x98204C
PREMATCH_DATE_WEATHER_BUFFER_OFFSET = 0x270

PREMATCH_FIXTURE_HEADER_FORMAT = "%s MATCH TODAY AT %s"
PREMATCH_FIXTURE_HEADER_LANGUAGE_GLOBAL_VA = 0x982050
PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET = 0x170
PREMATCH_FRIENDLY_LABEL = "Friendly"
PREMATCH_FRIENDLY_LANGUAGE_GLOBAL_VA = 0x9830C8
PREMATCH_VERSUS_LABEL = "V"
PREMATCH_VERSUS_LANGUAGE_GLOBAL_VA = 0x9830C4

PREMATCH_WEATHER_LABELS = ("Clear", "Sunny", "Raining", "Sleet", "Snowy")
PREMATCH_WEATHER_LANGUAGE_GLOBALS = (
    0x98252C,
    0x982534,
    0x982524,
    0x9821E0,
    0x982520,
)
PREMATCH_RATING_LABELS = ("GK", "DEF", "MID", "ATT")
PREMATCH_RATING_LANGUAGE_GLOBALS = (0x983BE4, 0x983B70, 0x983B6C, 0x983B68)

PREMATCH_FIXTURE_HEADER_RECT = OriginalRect(250, 45, 300, 30)
PREMATCH_DATE_WEATHER_RECT = OriginalRect(250, 70, 300, 16)
PREMATCH_BADGE_RECTS = (
    OriginalRect(38, 1, 135, 93),
    OriginalRect(627, 1, 135, 93),
)
PREMATCH_TEAM_IDENTITY_RECTS = (
    OriginalRect(184, 4, 185, 39),
    OriginalRect(374, 5, 52, 37),
    OriginalRect(429, 4, 185, 39),
)
PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA = 0x87BE30
PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS = (0x87BE80, 0x87BE70, 0x87BE80)
PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA = 0x87BEA0
PREMATCH_RATING_CAPTION_RECTS = tuple(
    OriginalRect(x, y, 25, 14)
    for x in (37, 737)
    for y in (498, 516, 534, 552)
)

# PPreMatchPanel::0x4967F0 allocates exactly 0x2D8 bytes for 182 child
# pointers, stores that array at +0x1C, stores count 0xB6 at +0x38, and fills
# every index 0..181. Generic traversal 0x6533A0 is already source-closed as
# forward index order, so these ranges are native paint order rather than
# constructor-order inference.
PREMATCH_CHILD_SETUP_VA = 0x4967F0
PREMATCH_CHILD_ARRAY_OFFSET = 0x1C
PREMATCH_CHILD_COUNT_OFFSET = 0x38
PREMATCH_CHILD_ARRAY_BYTES = 0x2D8
PREMATCH_CHILD_COUNT = 0xB6
PREMATCH_GENERIC_FORWARD_TRAVERSAL_VA = 0x6533A0
PREMATCH_CHILD_ORDER_RANGES = (
    ("live_background", 0, 0),
    ("pitch", 1, 1),
    ("top_bar", 2, 2),
    ("fixture_header", 3, 3),
    ("date_weather_line", 4, 4),
    ("team_badges", 5, 6),
    ("team_identity_text", 7, 9),
    ("starting_xi_pitch_markers", 10, 31),
    ("side0_starter_rows", 32, 64),
    ("side0_slots_11_17", 65, 92),
    ("side1_starter_rows", 93, 125),
    ("side1_slots_11_17", 126, 153),
    ("rating_bar_layers", 154, 169),
    ("rating_captions", 170, 177),
    ("match_detail_selectors", 178, 181),
)
PREMATCH_SELECTOR_CHILD_MODES = (
    MatchDetailMode.QUICK_MATCH,
    MatchDetailMode.FASTVIEW,
    MatchDetailMode.THREE_D_HIGHLIGHTS,
    MatchDetailMode.THREE_D_MATCH,
)

PREMATCH_TEAM_BADGE_ROOT = r"FM2001_art\generic\team_badge_stills"
PREMATCH_TEAM_BADGE_VARIANT_KEY = "badge_2"
PREMATCH_TEAM_BADGE_FALLBACK = (
    r"fm2001_art\generic\team_badge_stills\generic.444"
)
PREMATCH_TEAM_BADGE_RESOURCE_OFFSETS = (0x600, 0x624)
PREMATCH_TEAM_BADGE_ACTIVE_OFFSETS = (0x840, 0x890)

PREMATCH_PLAYER_SLOTS_PER_SIDE = 18
PREMATCH_STARTERS_PER_SIDE = 11
PREMATCH_SIDE_PLAYER_COUNT_MATCH_OFFSETS = (0x5A4, 0xB54)
PREMATCH_SIDE_PLAYER_ARRAY_MATCH_OFFSETS = (0x004, 0x5B4)
PREMATCH_PLAYER_NAME_LENGTH_FUNCTION_VA = 0x417A90
PREMATCH_PLAYER_NAME_FORMAT_FUNCTION_VA = 0x417AE0
PREMATCH_PLAYER_FULL_NAME_FORMAT = "%s %s"
PREMATCH_PLAYER_FULL_NAME_FORMAT_VA = 0x81858C

# Recovery 370 source-closes the 22 starting-XI pitch-marker controls.
# Native 0x499820 positions exactly eleven markers per side from normalized
# formation coordinates produced by 0x499A50. Pixel conversion uses 0x668350,
# which forces x87 truncation toward zero before the integer placement math.
PREMATCH_PITCH_MARKER_POSITIONER_VA = 0x499820
PREMATCH_PITCH_MARKER_COORD_BUILDER_VA = 0x499A50
PREMATCH_PITCH_MARKER_FORMATION_LOOKUP_VA = 0x5F0CC0
PREMATCH_PITCH_MARKER_COORD_TRANSFORM_VA = 0x5F0BD0
PREMATCH_PITCH_MARKER_PLAYER_RESOLVE_VA = 0x417F50
PREMATCH_PITCH_MARKER_INT_CONVERSION_VA = 0x668350
PREMATCH_PITCH_MARKER_SIZE = (36, 32)
PREMATCH_PITCH_MARKER_BASE = (270, 153)
PREMATCH_PITCH_MARKER_SIDE_SCALES = (
    (-261.0, -187.0),
    (261.0, 187.0),
)
PREMATCH_PITCH_MARKER_SIDE_OFFSETS = (
    (-18, 163),
    (0x30E, 179),
)
PREMATCH_PITCH_MARKER_COORD_BUFFER_OFFSET = 0x6D8
PREMATCH_PITCH_MARKER_COORD_STRIDE = 8
PREMATCH_PITCH_MARKER_TEAM_CONTROL_OFFSETS = (0xC60, 0xE70)
PREMATCH_PITCH_MARKER_CONTROL_STRIDE = 0x30
PREMATCH_PITCH_MARKER_WRAPPER_OFFSETS = (0x9A0, 0xB00)
PREMATCH_PITCH_MARKER_WRAPPER_STRIDE = 0x20
PREMATCH_PITCH_MARKER_TEAM_RESOURCE_OFFSETS = (0x668, 0x68C)
PREMATCH_PITCH_MARKER_TEAM_RESOURCE_STORAGE_OFFSETS = (0x648, 0x66C)
PREMATCH_PITCH_MARKER_TEAM_RESOURCE_BUILDER_VA = 0x408320
PREMATCH_PITCH_MARKER_GOALKEEPER_RESOURCE_VA = 0x9460D0
PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_PATH = (
    r"fm2001_art\generic\front-end-shirts\custom\goalkeeper.444"
)
PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_VA = 0x835DF0
PREMATCH_PITCH_MARKER_GENERIC_SHIRT_ROOT = (
    r"fm2001_art\Generic\front-end-shirts\generic"
)
PREMATCH_PITCH_MARKER_CUSTOM_SHIRT_ROOT = (
    r"fm2001_art\Generic\front-end-shirts\custom"
)
PREMATCH_PITCH_MARKER_GENERIC_SHIRT_FORMAT = "Team%.2d.bmp"
PREMATCH_PITCH_MARKER_SLOTS_PER_SIDE = 11
PREMATCH_PITCH_MARKER_CHILD_RANGE = (10, 31)
PREMATCH_PITCH_MARKER_GOALKEEPER_CHILDREN = (10, 21)
PREMATCH_PITCH_MARKER_OUTFIELD_CHILDREN = (
    tuple(range(11, 21)),
    tuple(range(22, 32)),
)
PREMATCH_PITCH_MARKER_FORMATION_TABLE_GLOBAL_VA = 0x87AE64
PREMATCH_PITCH_MARKER_MANAGER_SHAPE_BYTE_OFFSETS = (0x180, 0x183)
PREMATCH_PITCH_MARKER_MANAGER_SHAPE_SCALE = 0.01


def _truncate_toward_zero(value: float) -> int:
    # Python int(float) has the same truncation-toward-zero contract as the
    # native x87 conversion wrapper 0x668350 for the bounded marker inputs.
    return int(float(value))


def prematch_pitch_marker_origin(
    side: int,
    normalized_x: float,
    normalized_y: float,
    *,
    base_x: int = PREMATCH_PITCH_MARKER_BASE[0],
    base_y: int = PREMATCH_PITCH_MARKER_BASE[1],
) -> tuple[int, int]:
    """Return the exact native top-left origin for one visible XI marker.

    The normalized coordinates are the output of the source formation builder
    0x499A50. This seam intentionally does not invent those coordinates from a
    modern formation model; it preserves only the now-proven native transform.
    """
    if type(side) is not int or side not in (0, 1):
        raise OriginalPrematchPanelError("pre-match pitch-marker side must be 0 or 1")
    if isinstance(normalized_x, bool) or isinstance(normalized_y, bool):
        raise OriginalPrematchPanelError("pre-match pitch-marker coordinates must be numeric")
    try:
        x = float(normalized_x)
        y = float(normalized_y)
    except (TypeError, ValueError) as exc:
        raise OriginalPrematchPanelError(
            "pre-match pitch-marker coordinates must be numeric"
        ) from exc

    if side == 0:
        scaled_y = _truncate_toward_zero(y * -187.0)
        py = int(base_y) - scaled_y + 0xA3
        scaled_x = _truncate_toward_zero(x * -261.0)
        px = int(base_x) - scaled_x - 0x12
    else:
        scaled_y = _truncate_toward_zero(y * 187.0)
        py = int(base_y) - scaled_y + 0xB3
        scaled_x = _truncate_toward_zero(x * 261.0)
        px = 0x30E - scaled_x - int(base_x)
    return px, py


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
        "date_format": PREMATCH_DATE_FORMAT,
        "date_format_va": PREMATCH_DATE_FORMAT_VA,
        "date_buffer_offset": PREMATCH_DATE_BUFFER_OFFSET,
        "weather_temperature_format": PREMATCH_WEATHER_TEMPERATURE_FORMAT,
        "weather_temperature_format_va": PREMATCH_WEATHER_TEMPERATURE_FORMAT_VA,
        "date_weather_format": PREMATCH_DATE_WEATHER_FORMAT,
        "date_weather_language_global_va": PREMATCH_DATE_WEATHER_LANGUAGE_GLOBAL_VA,
        "date_weather_buffer_offset": PREMATCH_DATE_WEATHER_BUFFER_OFFSET,
        "fixture_header_format": PREMATCH_FIXTURE_HEADER_FORMAT,
        "fixture_header_language_global_va": PREMATCH_FIXTURE_HEADER_LANGUAGE_GLOBAL_VA,
        "fixture_header_buffer_offset": PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET,
        "friendly_label": PREMATCH_FRIENDLY_LABEL,
        "friendly_language_global_va": PREMATCH_FRIENDLY_LANGUAGE_GLOBAL_VA,
        "versus_label": PREMATCH_VERSUS_LABEL,
        "versus_language_global_va": PREMATCH_VERSUS_LANGUAGE_GLOBAL_VA,
        "weather_labels": PREMATCH_WEATHER_LABELS,
        "weather_language_globals": PREMATCH_WEATHER_LANGUAGE_GLOBALS,
        "rating_labels": PREMATCH_RATING_LABELS,
        "rating_language_globals": PREMATCH_RATING_LANGUAGE_GLOBALS,
        "fixture_header_rect": (
            PREMATCH_FIXTURE_HEADER_RECT.x,
            PREMATCH_FIXTURE_HEADER_RECT.y,
            PREMATCH_FIXTURE_HEADER_RECT.width,
            PREMATCH_FIXTURE_HEADER_RECT.height,
        ),
        "date_weather_rect": (
            PREMATCH_DATE_WEATHER_RECT.x,
            PREMATCH_DATE_WEATHER_RECT.y,
            PREMATCH_DATE_WEATHER_RECT.width,
            PREMATCH_DATE_WEATHER_RECT.height,
        ),
        "badge_rects": tuple(
            (r.x, r.y, r.width, r.height) for r in PREMATCH_BADGE_RECTS
        ),
        "team_identity_rects": tuple(
            (r.x, r.y, r.width, r.height) for r in PREMATCH_TEAM_IDENTITY_RECTS
        ),
        "rating_caption_rects": tuple(
            (r.x, r.y, r.width, r.height) for r in PREMATCH_RATING_CAPTION_RECTS
        ),
        "header_text_style_wrapper_va": PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA,
        "team_text_style_wrapper_vas": PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS,
        "rating_text_style_wrapper_va": PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA,
        "child_setup_va": PREMATCH_CHILD_SETUP_VA,
        "child_array_offset": PREMATCH_CHILD_ARRAY_OFFSET,
        "child_count_offset": PREMATCH_CHILD_COUNT_OFFSET,
        "child_array_bytes": PREMATCH_CHILD_ARRAY_BYTES,
        "child_count": PREMATCH_CHILD_COUNT,
        "generic_forward_traversal_va": PREMATCH_GENERIC_FORWARD_TRAVERSAL_VA,
        "child_order_ranges": PREMATCH_CHILD_ORDER_RANGES,
        "selector_child_modes": tuple(int(mode) for mode in PREMATCH_SELECTOR_CHILD_MODES),
        "child_draw_order_source_closed": True,
        "team_badge_root": PREMATCH_TEAM_BADGE_ROOT,
        "team_badge_variant_key": PREMATCH_TEAM_BADGE_VARIANT_KEY,
        "team_badge_fallback": PREMATCH_TEAM_BADGE_FALLBACK,
        "team_badge_resource_offsets": PREMATCH_TEAM_BADGE_RESOURCE_OFFSETS,
        "team_badge_active_offsets": PREMATCH_TEAM_BADGE_ACTIVE_OFFSETS,
        "player_slots_per_side": PREMATCH_PLAYER_SLOTS_PER_SIDE,
        "starters_per_side": PREMATCH_STARTERS_PER_SIDE,
        "side_player_count_match_offsets": PREMATCH_SIDE_PLAYER_COUNT_MATCH_OFFSETS,
        "side_player_array_match_offsets": PREMATCH_SIDE_PLAYER_ARRAY_MATCH_OFFSETS,
        "player_name_length_function_va": PREMATCH_PLAYER_NAME_LENGTH_FUNCTION_VA,
        "player_name_format_function_va": PREMATCH_PLAYER_NAME_FORMAT_FUNCTION_VA,
        "player_full_name_format": PREMATCH_PLAYER_FULL_NAME_FORMAT,
        "player_full_name_format_va": PREMATCH_PLAYER_FULL_NAME_FORMAT_VA,
        "identity_controls_source_closed": True,
        "pitch_marker_positioner_va": PREMATCH_PITCH_MARKER_POSITIONER_VA,
        "pitch_marker_coord_builder_va": PREMATCH_PITCH_MARKER_COORD_BUILDER_VA,
        "pitch_marker_formation_lookup_va": PREMATCH_PITCH_MARKER_FORMATION_LOOKUP_VA,
        "pitch_marker_coord_transform_va": PREMATCH_PITCH_MARKER_COORD_TRANSFORM_VA,
        "pitch_marker_player_resolve_va": PREMATCH_PITCH_MARKER_PLAYER_RESOLVE_VA,
        "pitch_marker_size": PREMATCH_PITCH_MARKER_SIZE,
        "pitch_marker_child_range": PREMATCH_PITCH_MARKER_CHILD_RANGE,
        "pitch_marker_goalkeeper_children": PREMATCH_PITCH_MARKER_GOALKEEPER_CHILDREN,
        "pitch_marker_outfield_children": PREMATCH_PITCH_MARKER_OUTFIELD_CHILDREN,
        "pitch_marker_team_resource_offsets": PREMATCH_PITCH_MARKER_TEAM_RESOURCE_OFFSETS,
        "pitch_marker_team_resource_builder_va": PREMATCH_PITCH_MARKER_TEAM_RESOURCE_BUILDER_VA,
        "pitch_marker_goalkeeper_resource_va": PREMATCH_PITCH_MARKER_GOALKEEPER_RESOURCE_VA,
        "pitch_marker_goalkeeper_source_path": PREMATCH_PITCH_MARKER_GOALKEEPER_SOURCE_PATH,
        "pitch_marker_generic_shirt_root": PREMATCH_PITCH_MARKER_GENERIC_SHIRT_ROOT,
        "pitch_marker_custom_shirt_root": PREMATCH_PITCH_MARKER_CUSTOM_SHIRT_ROOT,
        "pitch_marker_generic_shirt_format": PREMATCH_PITCH_MARKER_GENERIC_SHIRT_FORMAT,
        "pitch_marker_slots_per_side": PREMATCH_PITCH_MARKER_SLOTS_PER_SIDE,
        "pitch_marker_visibility_source_closed": True,
        "pitch_marker_formation_coordinates_source_closed": True,
        "pitch_marker_pixel_transform_source_closed": True,
        "pitch_marker_team_shirt_pixels_staged": False,
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
