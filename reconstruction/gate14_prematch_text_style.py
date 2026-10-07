"""First-hand text-style/font contracts used by PPreMatchPanel.

This module records exact style-wrapper -> font-object -> source-font mappings
and the raw control flags observed at PPreMatch construction callsites. It
deliberately keeps alignment semantics neutral until the TextControl render path
is independently closed.
"""
from __future__ import annotations

from dataclasses import dataclass


class PrematchTextStyleError(ValueError):
    pass


TEXT_NATIVE_COLOR_16 = 0xFFFF
TEXT_STYLE_OBJECT_VTABLE_VA = 0x7D7034


@dataclass(frozen=True)
class PrematchTextStyle:
    semantic: str
    wrapper_va: int
    wrapper_initializer_va: int
    font_object_va: int
    source_path_va: int
    source_path_use_va: int
    font_loader_call_va: int
    source_path: str
    source_size: int
    source_sha256: str
    atlas_size: tuple[int, int]
    native_line_height: int

    def __post_init__(self) -> None:
        if not self.semantic:
            raise PrematchTextStyleError("text style semantic must be non-empty")
        for name in (
            "wrapper_va",
            "wrapper_initializer_va",
            "font_object_va",
            "source_path_va",
            "source_path_use_va",
            "font_loader_call_va",
        ):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise PrematchTextStyleError(f"{name} must be a source VA")
        if not self.source_path.startswith("Fonts\\"):
            raise PrematchTextStyleError("text style source must be an original Fonts path")
        if type(self.source_size) is not int or self.source_size <= 0:
            raise PrematchTextStyleError("font source size must be positive")
        if (
            not isinstance(self.source_sha256, str)
            or len(self.source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_sha256)
        ):
            raise PrematchTextStyleError("font SHA-256 must be lowercase hex")
        if (
            type(self.atlas_size) is not tuple
            or len(self.atlas_size) != 2
            or any(type(value) is not int or value <= 0 for value in self.atlas_size)
        ):
            raise PrematchTextStyleError("font atlas size must be a positive pair")
        if type(self.native_line_height) is not int or self.native_line_height <= 0:
            raise PrematchTextStyleError("font native line height must be positive")


PREMATCH_HEADER_STYLE = PrematchTextStyle(
    semantic="header_date_regular_16",
    wrapper_va=0x87BE30,
    wrapper_initializer_va=0x603790,
    font_object_va=0x8CAB80,
    source_path_va=0x839E30,
    source_path_use_va=0x6044AC,
    font_loader_call_va=0x6044F9,
    source_path=r"Fonts\Zurich_XCn_BT_16pixel.fnt",
    source_size=75_217,
    source_sha256="e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18",
    atlas_size=(1261, 17),
    native_line_height=18,
)

PREMATCH_TEAM_STYLE = PrematchTextStyle(
    semantic="team_identity_bold_20",
    wrapper_va=0x87BE80,
    wrapper_initializer_va=0x6036A0,
    font_object_va=0x90C5D0,
    source_path_va=0x839EDC,
    source_path_use_va=0x6042FE,
    font_loader_call_va=0x60434B,
    source_path=r"Fonts\Zurich_BdXCn_BT_20pixel.fnt",
    source_size=91_349,
    source_sha256="47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166",
    atlas_size=(1789, 21),
    native_line_height=21,
)

PREMATCH_VERSUS_STYLE = PrematchTextStyle(
    semantic="versus_bold_25",
    wrapper_va=0x87BE70,
    wrapper_initializer_va=0x6036D0,
    font_object_va=0x8FF3C0,
    source_path_va=0x839EB8,
    source_path_use_va=0x604354,
    font_loader_call_va=0x6043A1,
    source_path=r"Fonts\Zurich_BdXCn_BT_25pixel.fnt",
    source_size=99_705,
    source_sha256="b16bc57d81f35f38e02db102bd17af0032295328cf6c04251c89f4feb021f2de",
    atlas_size=(1837, 25),
    native_line_height=26,
)

PREMATCH_ROW_STYLE = PrematchTextStyle(
    semantic="row_caption_bold_16",
    wrapper_va=0x87BEA0,
    wrapper_initializer_va=0x603640,
    font_object_va=0x9269F0,
    source_path_va=0x839F24,
    source_path_use_va=0x604252,
    font_loader_call_va=0x60429F,
    source_path=r"Fonts\Zurich_BdXCn_BT_16pixel.fnt",
    source_size=79_722,
    source_sha256="9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732",
    atlas_size=(1526, 17),
    native_line_height=18,
)

PREMATCH_TEXT_STYLES = (
    PREMATCH_HEADER_STYLE,
    PREMATCH_TEAM_STYLE,
    PREMATCH_VERSUS_STYLE,
    PREMATCH_ROW_STYLE,
)


# Raw flags passed directly to 0x6503F0 by PPreMatchPanel::0x4967F0.
# TextStyle draw routine 0x64F090 source-closes the ordinary orientation:
# 0x01 left, 0x02 right, 0x04 horizontal center;
# 0x08 top, 0x10 bottom, 0x20 vertical center.
PREMATCH_FIXTURE_HEADER_FLAGS = 0x24
PREMATCH_DATE_WEATHER_FLAGS = 0x24
PREMATCH_LEFT_TEAM_IDENTITY_FLAGS = 0x22
PREMATCH_VERSUS_FLAGS = 0x24
PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS = 0x21
PREMATCH_LEFT_PLAYER_NAME_FLAGS = 0x21
PREMATCH_RIGHT_PLAYER_NAME_FLAGS = 0x22
PREMATCH_PLAYER_NUMBER_FLAGS = 0x24
PREMATCH_RATING_CAPTION_FLAGS = 0x24

TEXT_ALIGN_LEFT = 0x01
TEXT_ALIGN_RIGHT = 0x02
TEXT_ALIGN_HCENTER = 0x04
TEXT_ALIGN_TOP = 0x08
TEXT_ALIGN_BOTTOM = 0x10
TEXT_ALIGN_VCENTER = 0x20
TEXT_ROTATED_ORIENTATION = 0x40
TEXT_ALIGNMENT_DRAW_VA = 0x64F090
TEXT_MEASURE_WIDTH_VA = 0x6574E0
TEXT_LINE_HEIGHT_VA = 0x6574D0


@dataclass(frozen=True)
class PrematchTextControlStyleUse:
    semantic: str
    wrapper_va: int
    raw_flags: int
    native_color_16: int = TEXT_NATIVE_COLOR_16

    def __post_init__(self) -> None:
        if not self.semantic:
            raise PrematchTextStyleError("text-control style use must be named")
        if self.wrapper_va not in {style.wrapper_va for style in PREMATCH_TEXT_STYLES}:
            raise PrematchTextStyleError("text-control style wrapper is not source-closed")
        if type(self.raw_flags) is not int or not 0 <= self.raw_flags <= 0xFFFFFFFF:
            raise PrematchTextStyleError("text-control flags must be native integer")
        if self.native_color_16 != TEXT_NATIVE_COLOR_16:
            raise PrematchTextStyleError("PPreMatch text color must remain 0xFFFF")


PREMATCH_TEXT_CONTROL_STYLE_USES = (
    PrematchTextControlStyleUse(
        "fixture_header",
        PREMATCH_HEADER_STYLE.wrapper_va,
        PREMATCH_FIXTURE_HEADER_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "date_weather",
        PREMATCH_HEADER_STYLE.wrapper_va,
        PREMATCH_DATE_WEATHER_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "left_team_identity",
        PREMATCH_TEAM_STYLE.wrapper_va,
        PREMATCH_LEFT_TEAM_IDENTITY_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "versus",
        PREMATCH_VERSUS_STYLE.wrapper_va,
        PREMATCH_VERSUS_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "right_team_identity",
        PREMATCH_TEAM_STYLE.wrapper_va,
        PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "left_player_name",
        PREMATCH_ROW_STYLE.wrapper_va,
        PREMATCH_LEFT_PLAYER_NAME_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "right_player_name",
        PREMATCH_ROW_STYLE.wrapper_va,
        PREMATCH_RIGHT_PLAYER_NAME_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "player_number",
        PREMATCH_ROW_STYLE.wrapper_va,
        PREMATCH_PLAYER_NUMBER_FLAGS,
    ),
    PrematchTextControlStyleUse(
        "rating_caption",
        PREMATCH_ROW_STYLE.wrapper_va,
        PREMATCH_RATING_CAPTION_FLAGS,
    ),
)


def prematch_text_style_contract() -> dict:
    return {
        "style_object_vtable_va": TEXT_STYLE_OBJECT_VTABLE_VA,
        "styles": PREMATCH_TEXT_STYLES,
        "control_style_uses": PREMATCH_TEXT_CONTROL_STYLE_USES,
        "native_color_16": TEXT_NATIVE_COLOR_16,
        "font_identity_source_closed": True,
        "raw_control_flags_source_closed": True,
        "alignment_draw_va": TEXT_ALIGNMENT_DRAW_VA,
        "measure_width_va": TEXT_MEASURE_WIDTH_VA,
        "line_height_va": TEXT_LINE_HEIGHT_VA,
        "horizontal_alignment_bits": {
            "left": TEXT_ALIGN_LEFT,
            "right": TEXT_ALIGN_RIGHT,
            "center": TEXT_ALIGN_HCENTER,
        },
        "vertical_alignment_bits": {
            "top": TEXT_ALIGN_TOP,
            "bottom": TEXT_ALIGN_BOTTOM,
            "center": TEXT_ALIGN_VCENTER,
        },
        "rotated_orientation_bit": TEXT_ROTATED_ORIENTATION,
        "alignment_bit_semantics_source_closed": True,
        "text_pixels_rasterized": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
