"""Gate-14 wrapper binding verified first-screen press audio to the live host.

The current OriginalGameTkHost draws START_MENU / TEAM_SELECT action controls
from original source frame index 0 and binds Tk <Button-1> to host.on_click.
This wrapper leaves Gate-13-owned host code unchanged: it replaces only that
canvas binding, delivers the source-closed numeric Button press audio for
recovered action rectangles, then always delegates to the original click
handler.

Expected audio-delivery failures are recorded and do not block gameplay.
Hover audio is not integrated because the current host has no native Button
state tracker or <Motion> binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from front_end_state import FrontEndScreen
from gate14_audiohooks_menu_playback import (
    Gate14MenuPcmPlaybackError,
    MenuPcmPlaybackBackend,
    MenuPcmPlaybackSummary,
)
from gate14_first_screen_button_audio import (
    play_verified_first_screen_action_press,
)
from original_button_frames import button_group_subframe_for_source_index
from original_front_end_input import candidate_original_event


class Gate14FirstScreenAudioBindingError(ValueError):
    pass


LIVE_FIRST_SCREEN_SOURCE_FRAME_INDEX = 0
LIVE_FIRST_SCREEN_NATIVE_GROUP, LIVE_FIRST_SCREEN_NATIVE_SUBFRAME = (
    button_group_subframe_for_source_index(LIVE_FIRST_SCREEN_SOURCE_FRAME_INDEX)
)
FIRST_SCREEN_AUDIO_SCREENS = (
    FrontEndScreen.START_MENU,
    FrontEndScreen.TEAM_SELECT,
)


@dataclass
class Gate14FirstScreenAudioHostBinding:
    host: object
    menus_bnk: bytes
    backend: MenuPcmPlaybackBackend | None
    original_click_handler: Callable
    installed: bool = False
    audio_attempt_count: int = 0
    audio_success_count: int = 0
    last_audio_summary: MenuPcmPlaybackSummary | None = None
    last_audio_error: str | None = None
    press_binding_integrated: bool = True
    hover_binding_integrated: bool = False
    audible_windows_verified: bool = False
    login_menu_audio_integrated: bool = False

    def __post_init__(self) -> None:
        if LIVE_FIRST_SCREEN_NATIVE_GROUP != 0 or LIVE_FIRST_SCREEN_NATIVE_SUBFRAME != 0:
            raise Gate14FirstScreenAudioBindingError(
                "live first-screen frame 0 must remain native group 0 / subframe 0"
            )
        if not isinstance(self.menus_bnk, bytes):
            raise Gate14FirstScreenAudioBindingError("menus_bnk must be bytes")
        if not callable(self.original_click_handler):
            raise Gate14FirstScreenAudioBindingError(
                "original_click_handler must be callable"
            )
        if not self.press_binding_integrated or self.hover_binding_integrated:
            raise Gate14FirstScreenAudioBindingError(
                "binding may integrate only the current fixed-frame press seam"
            )
        if self.audible_windows_verified or self.login_menu_audio_integrated:
            raise Gate14FirstScreenAudioBindingError(
                "host binding cannot promote Windows audibility or Gate-14 integration"
            )

    def _screen(self) -> FrontEndScreen:
        try:
            screen = self.host.presenter.session.navigation.screen
        except AttributeError as exc:
            raise Gate14FirstScreenAudioBindingError(
                "host must expose presenter.session.navigation.screen"
            ) from exc
        if not isinstance(screen, FrontEndScreen):
            raise Gate14FirstScreenAudioBindingError(
                "host navigation screen must be FrontEndScreen"
            )
        return screen

    def _candidate_action_event(self, event) -> int | None:
        screen = self._screen()
        if screen not in FIRST_SCREEN_AUDIO_SCREENS:
            return None
        normalizer = getattr(self.host, "_normalize_pointer_event", None)
        native_event = normalizer(event) if callable(normalizer) else event
        try:
            x = int(native_event.x)
            y = int(native_event.y)
        except (AttributeError, TypeError, ValueError) as exc:
            raise Gate14FirstScreenAudioBindingError(
                "Tk click event must expose integer-compatible x/y"
            ) from exc
        return candidate_original_event(screen, x, y)

    def on_click(self, event):
        candidate = self._candidate_action_event(event)
        if candidate is not None:
            self.audio_attempt_count += 1
            self.last_audio_summary = None
            self.last_audio_error = None
            try:
                self.last_audio_summary = play_verified_first_screen_action_press(
                    self.menus_bnk,
                    self.backend,
                    native_group=LIVE_FIRST_SCREEN_NATIVE_GROUP,
                )
                self.audio_success_count += 1
            except Gate14MenuPcmPlaybackError as exc:
                # Presentation/audio failure must not block core management play.
                self.last_audio_error = f"{type(exc).__name__}: {exc}"
        return self.original_click_handler(event)

    def install(self) -> "Gate14FirstScreenAudioHostBinding":
        if self.installed:
            raise Gate14FirstScreenAudioBindingError(
                "first-screen audio binding is already installed"
            )
        try:
            bind = self.host.canvas.bind
        except AttributeError as exc:
            raise Gate14FirstScreenAudioBindingError(
                "host must expose canvas.bind"
            ) from exc
        bind("<Button-1>", self.on_click)
        self.installed = True
        return self


def install_first_screen_press_audio(
    host,
    menus_bnk: bytes,
    backend: MenuPcmPlaybackBackend | None,
) -> Gate14FirstScreenAudioHostBinding:
    """Wrap an already-created OriginalGameTkHost-compatible object."""
    try:
        original = host.on_click
    except AttributeError as exc:
        raise Gate14FirstScreenAudioBindingError(
            "host must expose original on_click handler"
        ) from exc
    return Gate14FirstScreenAudioHostBinding(
        host=host,
        menus_bnk=menus_bnk,
        backend=backend,
        original_click_handler=original,
    ).install()
