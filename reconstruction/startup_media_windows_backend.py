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
import os
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
        if (
            item.container != "mp4"
            or item.video_codec != "h264"
            or item.audio_codec != "aac"
            or item.pixel_format != "yuv420p"
        ):
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


_WPF_PLAYBACK_SCRIPT = r"""
Add-Type -AssemblyName PresentationFramework

$path = [Environment]::GetEnvironmentVariable(
    'FM2001_STARTUP_MEDIA_PATH',
    'Process'
)
if ([string]::IsNullOrWhiteSpace($path) -or -not [IO.File]::Exists($path)) {
    exit 2
}

$script:mediaFailed = $false
$script:mediaEnded = $false
$window = New-Object Windows.Window
$window.WindowStyle = [Windows.WindowStyle]::None
$window.ResizeMode = [Windows.ResizeMode]::NoResize
$window.WindowState = [Windows.WindowState]::Maximized
$window.Topmost = $true
$window.ShowInTaskbar = $false
$window.Background = [Windows.Media.Brushes]::Black

$media = New-Object Windows.Controls.MediaElement
$media.LoadedBehavior = [Windows.Controls.MediaState]::Manual
$media.UnloadedBehavior = [Windows.Controls.MediaState]::Stop
$media.Stretch = [Windows.Media.Stretch]::Uniform
$media.Volume = 1.0
try {
    $media.Source = [Uri]::new([IO.Path]::GetFullPath($path), [UriKind]::Absolute)
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 2
}

$media.Add_MediaEnded({
    $script:mediaEnded = $true
    $window.Close()
})
$media.Add_MediaFailed({
    param($sender, $eventArgs)
    $script:mediaFailed = $true
    if ($eventArgs -and $eventArgs.ErrorException) {
        [Console]::Error.WriteLine($eventArgs.ErrorException.Message)
    }
    $window.Close()
})
$window.Add_ContentRendered({
    try {
        $media.Play()
    } catch {
        $script:mediaFailed = $true
        [Console]::Error.WriteLine($_.Exception.Message)
        $window.Close()
    }
})
$window.Content = $media

[void]$window.ShowDialog()
try { $media.Stop() } catch {}
if ($script:mediaFailed -or -not $script:mediaEnded) {
    exit 3
}
exit 0
""".strip()


class WindowsWpfStartupMediaBackend:
    """Play verified H.264/AAC MP4s through stock Windows WPF MediaElement.

    This transport deliberately avoids MCI, whose MP4 open path fails with
    native status 277 on the external Windows 11 client. The media path is
    passed through a process environment variable rather than interpolated into
    PowerShell source, and the child process does not return until the
    full-screen WPF window reaches MediaEnded or MediaFailed.
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
                "built-in startup-media playback requires Windows"
            )
        if not callable(runner):
            raise WindowsStartupMediaBackendError(
                "Windows startup-media process runner must be callable"
            )
        if not isinstance(powershell_executable, str) or not powershell_executable.strip():
            raise WindowsStartupMediaBackendError(
                "Windows PowerShell executable must be non-empty"
            )
        self._runner = runner
        self._powershell_executable = powershell_executable

    @staticmethod
    def _encoded_script() -> str:
        return base64.b64encode(
            _WPF_PLAYBACK_SCRIPT.encode("utf-16le")
        ).decode("ascii")

    @staticmethod
    def _timeout_seconds(item: VerifiedStartupMediaDerivative) -> float:
        frames = int(item.spec.decoded_video_frames)
        rate = int(item.spec.frame_rate)
        if frames <= 0 or rate <= 0:
            raise WindowsStartupMediaBackendError(
                "startup-media timing contract is invalid"
            )
        # Bound a broken WPF/media stack without constraining the source-proven
        # clip duration. Both startup clips receive at least 30 seconds of
        # initialization headroom beyond their decoded duration.
        return max(30.0, frames / rate + 30.0)

    def play(self, item: VerifiedStartupMediaDerivative) -> bool:
        if not isinstance(item, VerifiedStartupMediaDerivative):
            return False
        if item.container != "mp4" or item.video_codec != "h264" or item.audio_codec != "aac":
            return False

        env = os.environ.copy()
        env["FM2001_STARTUP_MEDIA_PATH"] = str(Path(item.path))
        command = (
            self._powershell_executable,
            "-NoProfile",
            "-NonInteractive",
            "-Sta",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-EncodedCommand",
            self._encoded_script(),
        )
        try:
            completed = self._runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=self._timeout_seconds(item),
            )
        except subprocess.TimeoutExpired as exc:
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback timed out: {item.path}"
            ) from exc
        except Exception as exc:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media player failed to launch"
            ) from exc

        returncode = getattr(completed, "returncode", None)
        if type(returncode) is not int:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media player returned no integer exit code"
            )
        if returncode != 0:
            stderr = str(getattr(completed, "stderr", "") or "").strip()
            detail = f": {stderr}" if stderr else ""
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback failed with exit code "
                f"{returncode}{detail}"
            )
        return True
