"""Built-in Windows startup-media backend for verified FM2001 derivatives.

The port uses the Windows Multimedia Command Interface only as a compatibility
transport for the already-verified MP4 derivatives. MCI returns zero on
success; any open/play/close error stays visible to the higher-level startup
playback contract. The source-proven startup order and media identities remain
owned by startup_media_playback.py and bundled_startup_media.py.

This does not claim the original skip-input or transition/fade semantics.
"""
from __future__ import annotations

import ctypes
from pathlib import Path
import platform
from typing import Callable

from startup_media_derivatives import VerifiedStartupMediaDerivative


class WindowsStartupMediaBackendError(RuntimeError):
    pass


def _default_mci_sender() -> tuple[Callable[[str], int], Callable[[int], str]]:
    try:
        winmm = ctypes.WinDLL("winmm")
    except (AttributeError, OSError) as exc:
        raise WindowsStartupMediaBackendError(
            "Windows winmm.dll is unavailable for startup-media playback"
        ) from exc
    sender = winmm.mciSendStringW
    sender.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p)
    sender.restype = ctypes.c_uint

    error_string = winmm.mciGetErrorStringW
    error_string.argtypes = (ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint)
    error_string.restype = ctypes.c_bool

    def call(command: str) -> int:
        return int(sender(command, None, 0, None))

    def describe(status: int) -> str:
        buffer = ctypes.create_unicode_buffer(512)
        if error_string(int(status), buffer, len(buffer)):
            return buffer.value.strip()
        return "Unknown Windows MCI error"

    return call, describe


class WindowsMciStartupMediaBackend:
    """Play one verified derivative full-screen and synchronously on Windows."""

    def __init__(
        self,
        *,
        platform_system: str | None = None,
        sender: Callable[[str], int] | None = None,
        error_describer: Callable[[int], str] | None = None,
    ):
        system = platform.system() if platform_system is None else platform_system
        if system != "Windows":
            raise WindowsStartupMediaBackendError(
                "built-in startup-media playback requires Windows"
            )
        if sender is None:
            self._sender, self._error_describer = _default_mci_sender()
        else:
            self._sender = sender
            self._error_describer = (
                error_describer
                if error_describer is not None
                else lambda status: f"MCI status {int(status)}"
            )
        if not callable(self._sender):
            raise WindowsStartupMediaBackendError("MCI sender must be callable")
        if not callable(self._error_describer):
            raise WindowsStartupMediaBackendError("MCI error describer must be callable")

    @staticmethod
    def _alias(item: VerifiedStartupMediaDerivative) -> str:
        if type(item.sequence) is not int or item.sequence < 0:
            raise WindowsStartupMediaBackendError(
                "startup-media sequence must be a non-negative integer"
            )
        return f"fm2001_startup_{item.sequence}"

    @staticmethod
    def _quoted_path(item: VerifiedStartupMediaDerivative) -> str:
        path = str(Path(item.path))
        if not path or '"' in path or "\n" in path or "\r" in path:
            raise WindowsStartupMediaBackendError(
                "startup-media path cannot be represented safely as an MCI command"
            )
        return f'"{path}"'

    def _send(self, command: str) -> None:
        try:
            result = self._sender(command)
        except Exception as exc:
            raise WindowsStartupMediaBackendError(
                f"Windows MCI command failed to execute: {command}"
            ) from exc
        if type(result) is not int:
            raise WindowsStartupMediaBackendError(
                "Windows MCI sender returned a non-integer status"
            )
        if result != 0:
            try:
                detail = str(self._error_describer(result)).strip()
            except Exception:
                detail = f"MCI status {result}"
            if not detail:
                detail = f"MCI status {result}"
            raise WindowsStartupMediaBackendError(
                f"Windows MCI command failed ({result}: {detail}): {command}"
            )

    def play(self, item: VerifiedStartupMediaDerivative) -> bool:
        if not isinstance(item, VerifiedStartupMediaDerivative):
            return False
        if item.container != "mp4" or item.video_codec != "h264" or item.audio_codec != "aac":
            return False

        alias = self._alias(item)
        quoted = self._quoted_path(item)
        opened = False
        try:
            self._send(f"open {quoted} alias {alias}")
            opened = True
            # Digital-video MCI recognizes the fullscreen play flag. wait keeps
            # the source-proven startup sequence synchronous.
            self._send(f"play {alias} fullscreen wait")
            return True
        finally:
            if opened:
                try:
                    self._send(f"close {alias}")
                except WindowsStartupMediaBackendError:
                    # Preserve the primary open/play failure if one is already
                    # unwinding; a close failure after successful playback is
                    # not evidence that the media itself failed to complete.
                    pass
