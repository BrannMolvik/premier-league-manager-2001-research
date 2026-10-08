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
import json
import os
from pathlib import Path
import platform
import subprocess
import time
from typing import Callable

from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_input import startup_input_allowed, parse_native_skip_receipt


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
        self.user32.IsWindow.argtypes = (wintypes.HWND,)
        self.user32.IsWindow.restype = wintypes.BOOL
        self.user32.SetWindowPos.argtypes = (wintypes.HWND, wintypes.HWND,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           wintypes.UINT)
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT,
                                           wintypes.WPARAM, wintypes.LPARAM)
        self.user32.PostMessageW.restype = wintypes.BOOL
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
        parent = self.user32.GetParent(self.child_hwnd)
        if pid.value != self.player_pid or parent != self.parent_hwnd:
            if pid.value == 0 and not parent and not self.user32.IsWindow(self.child_hwnd):
                # MediaEnded disposes HwndSource before PowerShell exits. Do
                # not resize a dead HWND, or mistake disposal for completion:
                # the caller still requires the player's verified exit code.
                return
            raise WindowsStartupMediaBackendError('Media child ownership changed')
        if rect == self.last_rect:
            return
        # SWP_NOZORDER | SWP_NOACTIVATE: this transport cannot take focus.
        if not self.user32.SetWindowPos(self.child_hwnd, None, *rect, 0x0014):
            error = ctypes.get_last_error()
            if error == 1400 and not self.user32.IsWindow(self.child_hwnd):
                return  # Teardown raced the ownership check; no HWND was moved.
            raise ctypes.WinError(error)
        self.last_rect = rect

    def post_native_input(self, message: int, wparam: int = 0) -> bool:
        if not startup_input_allowed(True, message) or type(wparam) is not int or not 0 <= wparam <= 255:
            raise WindowsStartupMediaBackendError('Invalid native startup input')
        if self.child_hwnd is None:
            return False  # No live child yet; never post to an unrelated HWND.
        pid = self.pid_type()
        self.user32.GetWindowThreadProcessId(self.child_hwnd, ctypes.byref(pid))
        parent = self.user32.GetParent(self.child_hwnd)
        if pid.value != self.player_pid or parent != self.parent_hwnd:
            if pid.value == 0 and not parent and not self.user32.IsWindow(self.child_hwnd):
                return False
            raise WindowsStartupMediaBackendError('Media child ownership changed')
        if not self.user32.PostMessageW(self.child_hwnd, message, wparam, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        return True


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


_TRANSPORT_RECEIPT_PREFIX = "FM2001_TRANSPORT_RECEIPT:"


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
$captureTransport = [Environment]::GetEnvironmentVariable(
    'FM2001_STARTUP_CAPTURE_TRANSPORT',
    'Process'
)

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
$script:mediaOpened = $false
$script:skipMessage = 0
$inputFlag = [Environment]::GetEnvironmentVariable('FM2001_STARTUP_INPUT_BIT0', 'Process')
if ($inputFlag -ne '0' -and $inputFlag -ne '1') { exit 2 }
$script:allowNativeInput = $inputFlag -eq '1'
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
$media.Add_MediaOpened({ $script:mediaOpened = $true })
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

# This is only a hook on this player's game-owned child; no global keyboard
# hooks, desktop policy changes, invented polling timer or media restart.
$inputHook = [Windows.Interop.HwndSourceHook]{
    param([IntPtr]$hwnd, [int]$message, [IntPtr]$wParam, [IntPtr]$lParam, [ref]$handled)
    if ($script:allowNativeInput -and $script:mediaOpened -and
        -not $script:mediaFailed -and -not $script:mediaEnded -and
        $message -in @(0x100, 0x201, 0x204)) {
        try {
            $media.Stop()
            $script:skipMessage = $message
        } catch {
            $script:mediaFailed = $true
            [Console]::Error.WriteLine($_.Exception.Message)
        }
        $script:frame.Continue = $false
    }
    return [IntPtr]::Zero
}
$source.AddHook($inputHook)

[void]$grid.Children.Add($media)
$source.RootVisual = $grid

if ($captureTransport -eq '1') {
    try {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class FM2001TransportProbe {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct POINT {
        public int X;
        public int Y;
    }

    [DllImport("user32.dll", SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll", SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll", SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool ClientToScreen(IntPtr hWnd, ref POINT point);

    [DllImport("user32.dll")]
    public static extern uint GetDpiForWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetWindowDpiAwarenessContext(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetThreadDpiAwarenessContext();

    [DllImport("user32.dll")]
    public static extern int GetAwarenessFromDpiAwarenessContext(IntPtr value);
}
"@

        $parentHwnd = [IntPtr]::new($parentValue)
        $childHwnd = $source.Handle
        if ($childHwnd -eq [IntPtr]::Zero) {
            throw "HwndSource did not expose a child HWND"
        }

        $parentWindowRect = New-Object FM2001TransportProbe+RECT
        $childWindowRect = New-Object FM2001TransportProbe+RECT
        $parentClientRect = New-Object FM2001TransportProbe+RECT
        $childClientRect = New-Object FM2001TransportProbe+RECT
        $parentClientOrigin = New-Object FM2001TransportProbe+POINT
        $childClientOrigin = New-Object FM2001TransportProbe+POINT

        if (-not [FM2001TransportProbe]::GetWindowRect($parentHwnd, [ref]$parentWindowRect)) {
            throw "GetWindowRect(parent) failed"
        }
        if (-not [FM2001TransportProbe]::GetWindowRect($childHwnd, [ref]$childWindowRect)) {
            throw "GetWindowRect(child) failed"
        }
        if (-not [FM2001TransportProbe]::GetClientRect($parentHwnd, [ref]$parentClientRect)) {
            throw "GetClientRect(parent) failed"
        }
        if (-not [FM2001TransportProbe]::GetClientRect($childHwnd, [ref]$childClientRect)) {
            throw "GetClientRect(child) failed"
        }
        if (-not [FM2001TransportProbe]::ClientToScreen($parentHwnd, [ref]$parentClientOrigin)) {
            throw "ClientToScreen(parent) failed"
        }
        if (-not [FM2001TransportProbe]::ClientToScreen($childHwnd, [ref]$childClientOrigin)) {
            throw "ClientToScreen(child) failed"
        }

        $parentContext = [FM2001TransportProbe]::GetWindowDpiAwarenessContext($parentHwnd)
        $childContext = [FM2001TransportProbe]::GetWindowDpiAwarenessContext($childHwnd)
        $threadContext = [FM2001TransportProbe]::GetThreadDpiAwarenessContext()

        $receipt = [ordered]@{
            parent_hwnd = $parentValue
            child_hwnd = $childHwnd.ToInt64()
            requested_child_rect = [ordered]@{
                x = $x
                y = $y
                width = $width
                height = $height
            }
            parent_window_rect = [ordered]@{
                left = $parentWindowRect.Left
                top = $parentWindowRect.Top
                right = $parentWindowRect.Right
                bottom = $parentWindowRect.Bottom
                width = $parentWindowRect.Right - $parentWindowRect.Left
                height = $parentWindowRect.Bottom - $parentWindowRect.Top
            }
            parent_client_rect = [ordered]@{
                left = $parentClientRect.Left
                top = $parentClientRect.Top
                right = $parentClientRect.Right
                bottom = $parentClientRect.Bottom
                width = $parentClientRect.Right - $parentClientRect.Left
                height = $parentClientRect.Bottom - $parentClientRect.Top
            }
            parent_client_origin_screen = [ordered]@{
                x = $parentClientOrigin.X
                y = $parentClientOrigin.Y
            }
            child_window_rect = [ordered]@{
                left = $childWindowRect.Left
                top = $childWindowRect.Top
                right = $childWindowRect.Right
                bottom = $childWindowRect.Bottom
                width = $childWindowRect.Right - $childWindowRect.Left
                height = $childWindowRect.Bottom - $childWindowRect.Top
            }
            child_client_rect = [ordered]@{
                left = $childClientRect.Left
                top = $childClientRect.Top
                right = $childClientRect.Right
                bottom = $childClientRect.Bottom
                width = $childClientRect.Right - $childClientRect.Left
                height = $childClientRect.Bottom - $childClientRect.Top
            }
            child_client_origin_screen = [ordered]@{
                x = $childClientOrigin.X
                y = $childClientOrigin.Y
            }
            child_offset_from_parent_client = [ordered]@{
                x = $childWindowRect.Left - $parentClientOrigin.X
                y = $childWindowRect.Top - $parentClientOrigin.Y
            }
            parent_dpi = [int][FM2001TransportProbe]::GetDpiForWindow($parentHwnd)
            child_dpi = [int][FM2001TransportProbe]::GetDpiForWindow($childHwnd)
            parent_dpi_awareness_context = $parentContext.ToInt64()
            child_dpi_awareness_context = $childContext.ToInt64()
            probe_thread_dpi_awareness_context = $threadContext.ToInt64()
            parent_dpi_awareness = [int][FM2001TransportProbe]::GetAwarenessFromDpiAwarenessContext($parentContext)
            child_dpi_awareness = [int][FM2001TransportProbe]::GetAwarenessFromDpiAwarenessContext($childContext)
            probe_thread_dpi_awareness = [int][FM2001TransportProbe]::GetAwarenessFromDpiAwarenessContext($threadContext)
        }
        $json = $receipt | ConvertTo-Json -Compress -Depth 5
        [Console]::Out.WriteLine('FM2001_TRANSPORT_RECEIPT:' + $json)
    } catch {
        [Console]::Error.WriteLine(
            'FM2001 startup transport probe failed: ' + $_.Exception.Message
        )
        $source.RootVisual = $null
        $source.Dispose()
        exit 4
    }
}

[Windows.Threading.Dispatcher]::PushFrame($script:frame)

try { $media.Stop() } catch {}
$source.RootVisual = $null
$source.RemoveHook($inputHook)
$source.Dispose()
if (-not $script:mediaFailed -and $script:skipMessage -ne 0) {
    [Console]::Out.WriteLine('FM2001_STARTUP_SKIPPED=' + $script:skipMessage)
    exit 4
}
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
    game-owned WPF child reaches MediaEnded, a qualified input stop or MediaFailed. The Tk owner must
    service Windows messages while that cross-process child is created/played.
    """
    source_input_contract_recovered = True

    def __init__(
        self,
        *,
        platform_system: str | None = None,
        runner: Callable[..., object] = subprocess.run,
        powershell_executable: str = "powershell.exe",
        process_factory: Callable[..., object] = subprocess.Popen,
        viewport_factory: Callable[..., object] = _GameOwnedChildViewport,
        capture_transport_receipts: bool = False,
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
        self._active_viewport = None
        self._active_input_bit0 = False
        self.last_native_input_message = None
        self._presentation_geometry = None
        if not callable(viewport_factory):
            raise WindowsStartupMediaBackendError('Media viewport factory must be callable')
        self._viewport_factory = viewport_factory
        if type(capture_transport_receipts) is not bool:
            raise WindowsStartupMediaBackendError(
                "transport-receipt capture flag must be boolean"
            )
        self._capture_transport_receipts = capture_transport_receipts
        self._transport_receipts = []
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

    def request_native_input(self, message: int, wparam: int = 0) -> bool:
        """Forward human input only to the verified owned player, never its parent."""
        if not startup_input_allowed(self._active_input_bit0, message):
            return False
        if self._active_viewport is None:
            return False
        return self._active_viewport.post_native_input(message, wparam)

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
                self._active_viewport = viewport
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
        finally:
            self._active_viewport = None

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

    def enable_transport_receipt_capture(self) -> None:
        """Enable diagnostic-only HWND/DPI capture for subsequent playback."""
        self._capture_transport_receipts = True
        self._transport_receipts.clear()

    @property
    def transport_receipts(self) -> tuple[dict, ...]:
        """Return detached copies of diagnostic transport evidence."""
        return tuple(json.loads(json.dumps(row)) for row in self._transport_receipts)

    @staticmethod
    def _require_int_mapping(payload: dict, key: str, fields: tuple[str, ...]) -> dict:
        value = payload.get(key)
        if type(value) is not dict or any(type(value.get(field)) is not int for field in fields):
            raise WindowsStartupMediaBackendError(
                f"startup-media transport receipt has invalid {key}"
            )
        return value

    def _record_transport_receipt(
        self,
        completed,
        item: VerifiedStartupMediaDerivative,
    ) -> None:
        if not self._capture_transport_receipts:
            return
        stdout = str(getattr(completed, "stdout", "") or "")
        lines = [
            line[len(_TRANSPORT_RECEIPT_PREFIX):]
            for line in stdout.splitlines()
            if line.startswith(_TRANSPORT_RECEIPT_PREFIX)
        ]
        if len(lines) != 1:
            raise WindowsStartupMediaBackendError(
                "startup-media transport probe did not return exactly one receipt"
            )
        try:
            payload = json.loads(lines[0])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt is not valid JSON"
            ) from exc
        if type(payload) is not dict:
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt must be a JSON object"
            )

        for key in (
            "parent_hwnd",
            "child_hwnd",
            "parent_dpi",
            "child_dpi",
            "parent_dpi_awareness_context",
            "child_dpi_awareness_context",
            "probe_thread_dpi_awareness_context",
            "parent_dpi_awareness",
            "child_dpi_awareness",
            "probe_thread_dpi_awareness",
        ):
            if type(payload.get(key)) is not int:
                raise WindowsStartupMediaBackendError(
                    f"startup-media transport receipt has invalid {key}"
                )
        if payload["parent_hwnd"] <= 0 or payload["child_hwnd"] <= 0:
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt has invalid HWND"
            )
        if payload["parent_dpi"] <= 0 or payload["child_dpi"] <= 0:
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt has invalid window DPI"
            )

        requested = self._require_int_mapping(
            payload, "requested_child_rect", ("x", "y", "width", "height")
        )
        if (
            requested["x"] < 0
            or requested["y"] < 0
            or requested["width"] <= 0
            or requested["height"] <= 0
        ):
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt has invalid requested child geometry"
            )

        for key in (
            "parent_window_rect",
            "parent_client_rect",
            "child_window_rect",
            "child_client_rect",
        ):
            rect = self._require_int_mapping(
                payload,
                key,
                ("left", "top", "right", "bottom", "width", "height"),
            )
            if rect["width"] <= 0 or rect["height"] <= 0:
                raise WindowsStartupMediaBackendError(
                    f"startup-media transport receipt has invalid {key} dimensions"
                )
            # These are structural Win32 RECT identities, not comparisons
            # with the requested movie size (which may differ under DPI).
            if (
                rect["right"] - rect["left"] != rect["width"]
                or rect["bottom"] - rect["top"] != rect["height"]
            ):
                raise WindowsStartupMediaBackendError(
                    f"startup-media transport receipt has inconsistent {key} edges"
                )
            # GetClientRect is defined in client coordinates, with (0,0)
            # at the origin even when the containing window is positioned.
            if key.endswith("_client_rect") and (
                rect["left"] != 0 or rect["top"] != 0
            ):
                raise WindowsStartupMediaBackendError(
                    f"startup-media transport receipt has nonzero {key} origin"
                )
        for key in (
            "parent_client_origin_screen",
            "child_client_origin_screen",
            "child_offset_from_parent_client",
        ):
            self._require_int_mapping(payload, key, ("x", "y"))
        for key in (
            "parent_dpi_awareness",
            "child_dpi_awareness",
            "probe_thread_dpi_awareness",
        ):
            if payload[key] not in (0, 1, 2):
                raise WindowsStartupMediaBackendError(
                    f"startup-media transport receipt has invalid {key} enumeration"
                )

        origin = payload["parent_client_origin_screen"]
        child_rect = payload["child_window_rect"]
        offset = payload["child_offset_from_parent_client"]
        if (
            offset["x"] != child_rect["left"] - origin["x"]
            or offset["y"] != child_rect["top"] - origin["y"]
        ):
            raise WindowsStartupMediaBackendError(
                "startup-media transport receipt has inconsistent child offset"
            )

        # Record observable comparisons without enforcing requested geometry
        # as original visual equivalence: mismatches are precisely the
        # transport evidence that the private Windows probe must preserve.
        child_client = payload["child_client_rect"]
        payload["transport_comparison"] = {
            "offset_matches_request": (
                offset["x"] == requested["x"] and offset["y"] == requested["y"]
            ),
            "window_size_matches_request": (
                child_rect["width"] == requested["width"]
                and child_rect["height"] == requested["height"]
            ),
            "client_size_matches_request": (
                child_client["width"] == requested["width"]
                and child_client["height"] == requested["height"]
            ),
            "parent_child_dpi_equal": payload["parent_dpi"] == payload["child_dpi"],
            "visual_equivalence_assessed": False,
        }

        payload["sequence"] = int(item.sequence)
        payload["source_path"] = str(item.spec.source_path)
        self._transport_receipts.append(payload)

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
        self.last_native_input_message = None
        env = os.environ.copy()
        env["FM2001_STARTUP_MEDIA_PATH"] = str(Path(item.path))
        env["FM2001_STARTUP_PARENT_HWND"] = str(self._parent_hwnd)
        env["FM2001_STARTUP_MEDIA_X"] = str(x)
        env["FM2001_STARTUP_MEDIA_Y"] = str(y)
        env["FM2001_STARTUP_MEDIA_WIDTH"] = str(width)
        env["FM2001_STARTUP_MEDIA_HEIGHT"] = str(height)
        env["FM2001_STARTUP_INPUT_BIT0"] = '1' if item.spec.playback_flag_bit0 is True else '0'
        if self._capture_transport_receipts:
            env["FM2001_STARTUP_CAPTURE_TRANSPORT"] = "1"
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
            self._active_input_bit0 = item.spec.playback_flag_bit0 is True
            completed = self._run_player(command, env=env,
                timeout=self._timeout_seconds(item))
        except subprocess.TimeoutExpired as exc:
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback timed out: {item.path}"
            ) from exc
        except WindowsStartupMediaBackendError:
            raise
        except Exception as exc:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media player failed to launch"
            ) from exc
        finally:
            self._active_input_bit0 = False

        returncode = getattr(completed, "returncode", None)
        if type(returncode) is not int:
            raise WindowsStartupMediaBackendError(
                "Windows WPF startup-media player returned no integer exit code"
            )
        if returncode == 4:
            try:
                self.last_native_input_message = parse_native_skip_receipt(
                    getattr(completed, 'stdout', ''), item.spec.playback_flag_bit0)
            except ValueError as exc:
                raise WindowsStartupMediaBackendError(str(exc)) from exc
            return True
        if returncode != 0:
            stderr = str(getattr(completed, "stderr", "") or "").strip()
            detail = f": {stderr}" if stderr else ""
            raise WindowsStartupMediaBackendError(
                f"Windows WPF startup-media playback failed with exit code "
                f"{returncode}{detail}"
            )
        self._record_transport_receipt(completed, item)
        return True
