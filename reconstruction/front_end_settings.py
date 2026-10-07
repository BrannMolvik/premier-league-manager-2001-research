"""Source-styled modernization Settings extension for the FM2001 front end.

This is intentionally separate from the recovered PStartMenu facts. The four
original menu controls retain their exact source IDs/rectangles. Settings uses
the same provenance-verified Zurich font and Button@ease atlas so the extension
fits the restored visual language without being misrepresented as shipped
FM2001 behavior.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

from ea_font import EAFont
from front_end_state import (
    FrontEndScreen,
    ModernStartMenuControl,
    SettingsControl,
)
from original_front_end_layout import (
    OriginalRect,
    PSTARTMENU_ACTION_FRAME_SIZE,
)
from original_pstartmenu_labels import PStartMenuCaption
from original_pstartmenu_resources import ZURICH_FONT20_SHA256


SETTINGS_FONT_RELATIVE_PATH = Path("Fonts") / "Zurich_BdXCn_BT_20pixel.fnt"

# Intentional modernization placement. Original recovered controls are not
# moved or resized. This occupies the unused right-hand slot beneath Load Game.
SETTINGS_MENU_RECT = OriginalRect(355, 508, 169, 25)

# The first Settings surface remains deliberately narrow for Gate 13. Advanced
# rendering/upscaling belongs to Gate 17.
SETTINGS_PROFILE_RECT = OriginalRect(181, 448, 169, 25)
SETTINGS_FULLSCREEN_RECT = OriginalRect(181, 478, 169, 25)
SETTINGS_BACK_RECT = OriginalRect(181, 508, 169, 25)


class FrontEndSettingsError(ValueError):
    """Settings visual/state data violates the bounded Gate-13 contract."""


@dataclass
class FrontEndSettings:
    """Application/presentation settings only; never simulation state."""

    fullscreen: bool = True

    @property
    def original_baseline(self) -> bool:
        return self.fullscreen is True

    @property
    def profile_name(self) -> str:
        return "Original" if self.original_baseline else "Custom"

    def reset_original(self) -> None:
        self.fullscreen = True

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen


@dataclass(frozen=True)
class SettingsActionSpec:
    event: int
    rect: OriginalRect
    text: str


@dataclass
class SourceStyledSettingsResources:
    """Verified Zurich font used with the already-verified PStartMenu atlas."""

    font: EAFont
    _caption_cache: dict[tuple[int, str, OriginalRect], PStartMenuCaption] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def caption(
        self,
        event: int,
        text: str,
        rect: OriginalRect,
    ) -> PStartMenuCaption:
        key = (int(event), str(text), rect)
        cached = self._caption_cache.get(key)
        if cached is not None:
            return cached
        if (rect.width, rect.height) != PSTARTMENU_ACTION_FRAME_SIZE:
            raise FrontEndSettingsError(
                "Settings control must reuse the exact PStartMenu button geometry"
            )
        glyph_mask = self.font.render_text_alpha(text)
        measured_width = self.font.measure_text(text)
        if glyph_mask.width != measured_width:
            raise FrontEndSettingsError("Zurich Settings mask/measure disagreement")
        line_height = self.font.native_line_height()
        if measured_width > rect.width or line_height > rect.height:
            raise FrontEndSettingsError(
                f"Settings caption does not fit source button: {text!r}"
            )
        caption = PStartMenuCaption(
            event=int(event),
            source_idx_position=-1,
            original_text=str(text),
            control_rect=rect,
            glyph_mask=glyph_mask,
            line_origin_x=rect.x + (rect.width - measured_width) // 2,
            line_origin_y=rect.y + (rect.height - line_height) // 2,
            clip_rect=rect,
            modern_extension=True,
        )
        self._caption_cache[key] = caption
        return caption


def load_source_styled_settings_resources(
    source_root: str | Path,
) -> SourceStyledSettingsResources:
    path = Path(source_root) / SETTINGS_FONT_RELATIVE_PATH
    data = path.read_bytes()
    if sha256(data).hexdigest() != ZURICH_FONT20_SHA256:
        raise FrontEndSettingsError(
            "Settings requires the exact provenance-tracked Zurich 20px font"
        )
    return SourceStyledSettingsResources(EAFont.from_bytes(data))


def start_menu_settings_action() -> SettingsActionSpec:
    return SettingsActionSpec(
        int(ModernStartMenuControl.SETTINGS),
        SETTINGS_MENU_RECT,
        "Settings",
    )


def settings_surface_actions(
    settings: FrontEndSettings,
) -> tuple[SettingsActionSpec, ...]:
    return (
        SettingsActionSpec(
            int(SettingsControl.RESET_ORIGINAL),
            SETTINGS_PROFILE_RECT,
            f"Profile: {settings.profile_name}",
        ),
        SettingsActionSpec(
            int(SettingsControl.TOGGLE_FULLSCREEN),
            SETTINGS_FULLSCREEN_RECT,
            f"Fullscreen: {'On' if settings.fullscreen else 'Off'}",
        ),
        SettingsActionSpec(
            int(SettingsControl.BACK),
            SETTINGS_BACK_RECT,
            "Back",
        ),
    )


def _inside(rect: OriginalRect, x: int, y: int) -> bool:
    return rect.x <= x < rect.right and rect.y <= y < rect.bottom


def candidate_settings_event(
    screen: FrontEndScreen,
    x: int,
    y: int,
) -> int | None:
    if type(x) is not int or type(y) is not int:
        raise TypeError("Settings pointer coordinates must be integer pixels")
    if screen is FrontEndScreen.START_MENU:
        action = start_menu_settings_action()
        return action.event if _inside(action.rect, x, y) else None
    if screen is FrontEndScreen.SETTINGS:
        # Geometry is state-independent; use the original baseline just to
        # materialize the three fixed action rectangles.
        for action in settings_surface_actions(FrontEndSettings()):
            if _inside(action.rect, x, y):
                return action.event
        return None
    return None
