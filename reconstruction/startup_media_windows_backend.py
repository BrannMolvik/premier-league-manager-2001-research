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
import time
from typing import Callable

from startup_media_derivatives import VerifiedStartupMediaDerivative


class WindowsStartupMediaBackendError(RuntimeError):
    pass


class _GameOwnedChildViewport:
    """Resize only this player's child of the bound game HWND, never its owner.

    The WPF child processes WM_SIZE itself, including its physical-pixel to DIP
    conversion. No media restart, desktop/display change, activation or z-order
    change is performed. Discovery is qualified by both parent and owned PID.
    """
    def __init__(self, parent_hwnd: int, player_pid: int):
        from ctypes import wintypes
        if type(player_pid) is not int or player_pid <= 0:
            raise WindowsStartupMediaBackendError('Invalid owned media-player PID')
        self.parent_hwnd = parent_hwnd
        self.player_pid = player_pid
        self.last_rect = None
        self.child_hwnd = None
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumChildWindows.argtypes = (wintypes.HWND, self.callback_type, wintypes.LPARAM)
        self.user32.EnumChildWindows.restype = wintypes.BOOL
        self.user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.GetParent.argtypes = (wintypes.HWND,)
        self.user32.GetParent.restype = wintypes.HWND
        self.user32.SetWindowPos.argtypes = (wintypes.HWND, wintypes.HWND,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           wintypes.UINT)
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.pid_type = wintypes.DWORD

    def __call__(self, rect: tuple[int, int, int, int]) -> None:
        if self.child_hwnd is None:
            candidates = []
            def capture(hwnd, _parameter):
                pid = self.pid_type()
                self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value == self.player_pid and self.user32.GetParent(hwnd) == self.parent_hwnd:
                    candidates.append(hwnd)
                return True
            self.user32.EnumChildWindows(self.parent_hwnd, self.callback_type(capture), 0)
            if not candidates:
                return  # HwndSource has not been constructed yet.
            if len(candidates) != 1:
                raise WindowsStartupMediaBackendError('Ambiguous game-owned media child')
            self.child_hwnd = candidates[0]
        pid = self.pid_type()
        self.user32.GetWindowThreadProcessId(self.child_hwnd, ctypes.byref(pid))
        if pid.value != self.player_pid or self.user32.GetParent(self.child_hwnd) != self.parent_hwnd:
            raise WindowsStartupMediaBackendError('Media child ownership changed')
        if rect == self.last_rect:
            return
        # SWP_NOZORDER | SWP_NOACTIVATE: this transport cannot take focus.
        if not self.user32.SetWindowPos(self.child_hwnd, None, *rect, 0x0014):
            raise ctypes.WinError(ctypes.get_last_error())
        self.last_rect = rect


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
$parentText = [Environment]::GetEnvironmentVariable(
    'FM2001_STARTUP_PARENT_HWND',
    'Process'
)
$xText = [Environment]::GetEnvironmentVariable('FM2001_STARTUP_MEDIA_X', 'Process')
$yText = [Environment]::GetEnvironmentVariable('FM2001_STARTUP_MEDIA_Y', 'Process')
$widthText = [Environment]::GetEnvironmentVariable('FM2001_STARTUP_MEDIA_WIDTH', 'Process')
$heightText = [Environment]::GetEnvironmentVariable('FM2001_STARTUP_MEDIA_HEIGHT', 'Process')

if ([string]::IsNullOrWhiteSpace($path) -or -not [IO.File]::Exists($path)) {
    exit 2
}

$parentValue = 0L
$x = 0
$y = 0
$width = 0
$height = 0
if (
    -not [Int64]::TryParse($parentText, [ref]$parentValue) -or $parentValue -le 0 -or
    -not [Int32]::TryParse($xText, [ref]$x) -or
    -not [Int32]::TryParse($yText, [ref]$y) -or
    -not [Int32]::TryParse($widthText, [ref]$width) -or $width -le 0 -or
    -not [Int32]::TryParse($heightText, [ref]$height) -or $height -le 0
) {
    exit 2
}

$script:mediaFailed = $false
$script:mediaEnded = $false
$script:frame = New-Object Windows.Threading.DispatcherFrame

$params = New-Object Windows.Interop.HwndSourceParameters('FM2001StartupMedia')
$params.ParentWindow = [IntPtr]::new($parentValue)
$params.WindowStyle = 0x50000000
$params.PositionX = $x
$params.PositionY = $y
$params.Width = $width
$params.Height = $height

$source = New-Object Windows.Interop.HwndSource($params)
$grid = New-Object Windows.Controls.Grid
$grid.Background = [Windows.Media.Brushes]::Black

$media = New-Object Windows.Controls.MediaElement
$media.LoadedBehavior = [Windows.Controls.MediaState]::Manual
$media.UnloadedBehavior = [Windows.Controls.MediaState]::Stop
$media.Stretch = [Windows.Media.Stretch]::Fill
$media.Volume = 1.0
$media.SnapsToDevicePixels = $true
[Windows.Media.RenderOptions]::SetBitmapScalingMode(
    $media,
    [Windows.Media.BitmapScalingMode]::NearestNeighbor
)
try {
    $media.Source = [Uri]::new([IO.Path]::GetFullPath($path), [UriKind]::Absolute)
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    $source.Dispose()
    exit 2
}

$media.Add_MediaEnded({
    $script:mediaEnded = $true
    $script:frame.Continue = $false
})
$media.Add_MediaFailed({
    param($sender, $eventArgs)
    $script:mediaFailed = $true
    if ($eventArgs -and $eventArgs.ErrorException) {
        [Console]::Error.WriteLine($eventArgs.ErrorException.Message)
    }
    $script:frame.Continue = $false
})
$media.Add_Loaded({
    try {
        $media.Play()
    } catch {
        $script:mediaFailed = $true
        [Console]::Error.WriteLine($_.Exception.Message)
        $script:frame.Continue = $false
    }
})

[void]$grid.Children.Add($media)
$source.RootVisual = $grid
[Windows.Threading.Dispatcher]::PushFrame($script:frame)

try { $media.Stop() } catch {}
$source.RootVisual = $null
$source.Dispose()
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
    game-owned WPF child reaches MediaEnded or MediaFailed. The Tk owner must
    service Windows messages while that cross-process child is created/played.
    """

    def __init__(
        self,
        *,
        platform_system: str | None = None,
        runner: Callable[..., object] = subprocess.run,
        powershell_executable: str = "powershell.exe",
        process_factory: Callable[..., object] = subprocess.Popen,
        viewport_factory: Callable[..., object] = _GameOwnedChildViewport,
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
        self._parent_hwnd = None
        self._presentation_rect = None
        self._event_pump = None
        self._presentation_geometry = None
        if not callable(viewport_factory):
            raise WindowsStartupMediaBackendError('Media viewport factory must be callable')
        self._viewport_factory = viewport_factory
        if not callable(process_factory):
            raise WindowsStartupMediaBackendError("Windows player process factory must be callable")
        self._process_factory = process_factory

    def bind_event_pump(self, event_pump: Callable[[], None]) -> None:
        """Bind the owning Tk thread's pump; this is not a media/frame timer.

        HwndSource construction sends synchronous messages to its parent. A
        blocking subprocess.run on that parent thread prevents construction,
        before any MediaElement event can fire (Gate13 issue482).
        """
        if not callable(event_pump):
            raise WindowsStartupMediaBackendError("startup-media event pump must be callable")
        self._event_pump = event_pump

    def bind_presentation_geometry(self, provider: Callable[[], dict]) -> None:
        """Bind the owner's realized viewport, sampled after servicing Tk events."""
        if not callable(provider):
            raise WindowsStartupMediaBackendError('Media geometry provider must be callable')
        self._presentation_geometry = provider

    def _run_player(self, command, *, env, timeout):
        if self._event_pump is None:
            return self._runner(command, check=False, capture_output=True, text=True,
                env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=timeout)
        process = self._process_factory(command, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        deadline = time.monotonic() + timeout
        viewport = None
        try:
            if self._presentation_geometry is not None:
                viewport = self._viewport_factory(self._parent_hwnd, process.pid)
            while True:
                self._event_pump()  # Always on the calling/owning Tk thread.
                if viewport is not None and process.poll() is None:
                    binding = self._presentation_geometry()
                    if binding.get('parent_hwnd') != self._parent_hwnd:
                        raise WindowsStartupMediaBackendError('Media parent changed during playback')
                    rect = tuple(binding.get(key) for key in ('x', 'y', 'width', 'height'))
                    if (any(type(value) is not int for value in rect)
                            or min(rect[:2]) < 0 or min(rect[2:]) <= 0):
                        raise WindowsStartupMediaBackendError('Invalid live media viewport')
                    viewport(rect)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                try:
                    stdout, stderr = process.communicate(timeout=min(0.02, remaining))
                except subprocess.TimeoutExpired:
                    continue
                return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        except BaseException:
            # Closing the game/pump failure/timeout must not orphan a player or
            # leave its game-owned child behind. No other process is touched.
            if process.poll() is None:
                process.kill()
            process.communicate()
            raise

    def bind_parent_window(
        self,
        parent_hwnd: int,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        values = (parent_hwnd, x, y, width, height)
        if any(type(value) is not int for value in values):
            raise WindowsStartupMediaBackendError(
                "startup-media parent binding requires integer HWND/geometry"
            )
        if parent_hwnd <= 0 or x < 0 or y < 0 or width <= 0 or height <= 0:
            raise WindowsStartupMediaBackendError(
                "startup-media parent binding geometry is invalid"
            )
        self._parent_hwnd = parent_hwnd
        self._presentation_rect = (x, y, width, height)

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

        if self._parent_hwnd is None or self._presentation_rect is None:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media backend is not bound to the game window"
            )
        x, y, width, height = self._presentation_rect
        env = os.environ.copy()
        env["FM2001_STARTUP_MEDIA_PATH"] = str(Path(item.path))
        env["FM2001_STARTUP_PARENT_HWND"] = str(self._parent_hwnd)
        env["FM2001_STARTUP_MEDIA_X"] = str(x)
        env["FM2001_STARTUP_MEDIA_Y"] = str(y)
        env["FM2001_STARTUP_MEDIA_WIDTH"] = str(width)
        env["FM2001_STARTUP_MEDIA_HEIGHT"] = str(height)
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
            completed = self._run_player(command, env=env,
                timeout=self._timeout_seconds(item))
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
