"""Built-in Windows startup-media backend for verified FM2001 derivatives.

The port uses the Windows Multimedia Command Interface only as a compatibility
transport for the already-verified MP4 derivatives. MCI returns zero on
success; any open/play/close error stays visible to the higher-level startup
playback contract. The source-proven startup order and media identities remain
owned by startup_media_playback.py and bundled_startup_media.py.

This does not claim the original skip-input or transition/fade semantics.
"""
from __future__ import annotations

import base64
import ctypes
from pathlib import Path
import platform
import subprocess
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


class WindowsWpfStartupMediaBackend:
    """Play verified MP4 derivatives through the stock Windows WPF media stack.

    This deliberately replaces MCI only as the compatibility transport. The
    source-proven sequence, derivative identities, and verification contracts
    remain outside this adapter. Native skip/fade/display semantics remain open.
    """

    def __init__(
        self,
        *,
        platform_system: str | None = None,
        runner: Callable[..., object] = subprocess.run,
        powershell_executable: str = "powershell.exe",
    ):
        system = platform.system() if platform_system is None else platform_system
        if system != "Windows":
            raise WindowsStartupMediaBackendError(
                "built-in WPF startup-media playback requires Windows"
            )
        if not callable(runner):
            raise WindowsStartupMediaBackendError(
                "WPF startup-media process runner must be callable"
            )
        if not isinstance(powershell_executable, str) or not powershell_executable.strip():
            raise WindowsStartupMediaBackendError(
                "PowerShell executable must be non-empty"
            )
        self._runner = runner
        self.powershell_executable = powershell_executable

    @staticmethod
    def _encoded_script(item: VerifiedStartupMediaDerivative) -> str:
        path = str(Path(item.path))
        if not path or "\x00" in path or "\n" in path or "\r" in path:
            raise WindowsStartupMediaBackendError(
                "startup-media path cannot be represented safely for WPF playback"
            )
        # The media path is separately encoded so no user-controlled path text
        # becomes PowerShell syntax.
        path_payload = base64.b64encode(path.encode("utf-16le")).decode("ascii")
        script = f"""$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
$path = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{path_payload}'))
$window = New-Object System.Windows.Window
$window.WindowStyle = [System.Windows.WindowStyle]::None
$window.WindowState = [System.Windows.WindowState]::Maximized
$window.ResizeMode = [System.Windows.ResizeMode]::NoResize
$window.Background = [System.Windows.Media.Brushes]::Black
$window.Topmost = $true
$window.ShowInTaskbar = $false
$media = New-Object System.Windows.Controls.MediaElement
$media.LoadedBehavior = [System.Windows.Controls.MediaState]::Manual
$media.UnloadedBehavior = [System.Windows.Controls.MediaState]::Manual
$media.Stretch = [System.Windows.Media.Stretch]::Uniform
$media.Volume = 1.0
$window.Content = $media
$script:fm2001Ended = $false
$script:fm2001Failed = $false
$media.add_MediaEnded({{
    param($sender, $eventArgs)
    $script:fm2001Ended = $true
    $window.Close()
}})
$media.add_MediaFailed({{
    param($sender, $eventArgs)
    $script:fm2001Failed = $true
    if ($eventArgs -and $eventArgs.ErrorException) {{
        [Console]::Error.WriteLine($eventArgs.ErrorException.Message)
    }}
    $window.Close()
}})
try {{
    $media.Source = [System.Uri]::new($path, [System.UriKind]::Absolute)
}} catch {{
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 2
}}
$window.add_ContentRendered({{
    param($sender, $eventArgs)
    try {{
        $media.Play()
    }} catch {{
        $script:fm2001Failed = $true
        [Console]::Error.WriteLine($_.Exception.Message)
        $window.Close()
    }}
}})
$null = $window.ShowDialog()
try {{ $media.Stop() }} catch {{}}
if ($script:fm2001Failed -or -not $script:fm2001Ended) {{ exit 1 }}
exit 0
"""
        return base64.b64encode(script.encode("utf-16le")).decode("ascii")

    @staticmethod
    def _timeout_seconds(item: VerifiedStartupMediaDerivative) -> float:
        frames = int(item.spec.decoded_video_frames)
        rate = int(item.spec.frame_rate)
        if frames <= 0 or rate <= 0:
            raise WindowsStartupMediaBackendError(
                "startup-media timing contract is invalid"
            )
        # Give stock Windows ample time for media initialization while still
        # preventing a broken player window from hanging application startup.
        return max(30.0, frames / rate + 30.0)

    def play(self, item: VerifiedStartupMediaDerivative) -> bool:
        if not isinstance(item, VerifiedStartupMediaDerivative):
            return False
        if (
            item.container != "mp4"
            or item.video_codec != "h264"
            or item.audio_codec != "aac"
            or item.pixel_format != "yuv420p"
        ):
            return False

        command = (
            self.powershell_executable,
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-STA",
            "-EncodedCommand",
            self._encoded_script(item),
        )
        try:
            completed = self._runner(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self._timeout_seconds(item),
            )
        except subprocess.TimeoutExpired as exc:
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback timed out: {item.path}"
            ) from exc
        except OSError as exc:
            raise WindowsStartupMediaBackendError(
                "Windows PowerShell could not start WPF startup-media playback"
            ) from exc

        returncode = getattr(completed, "returncode", None)
        if type(returncode) is not int:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media process returned no exit status"
            )
        if returncode != 0:
            detail = str(getattr(completed, "stderr", "") or "").strip()
            suffix = f": {detail[-2000:]}" if detail else ""
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback failed ({returncode}){suffix}"
            )
        return True
