"""Read-only display/window diagnostics for bounded native-original probes.

No display-mode, window-position, foreground, input or audio mutation APIs.
Window rectangles/styles are private test observations, not UI automation.
"""
from __future__ import annotations

import ctypes as c
import os
import time


class DisplayWatchError(ValueError):
    pass


def compare_desktop(before: dict, after: dict, probe_pid: int) -> list[str]:
    problems = []
    if before['displays'] != after['displays']:
        problems.append('desktop_display_mode_changed')
    current = {w['hwnd']: w for w in after['windows']}
    for window in before['windows']:
        other = current.get(window['hwnd'])
        if window['pid'] != probe_pid and other and other['pid'] == window['pid']:
            if other['rect'] != window['rect']:
                problems.append('unrelated_window_geometry_changed')
                break
    for window in after['windows']:
        if window['pid'] == probe_pid:
            if window['topmost']:
                problems.append('probe_window_always_on_top')
            if window['mouse_capture']:
                problems.append('probe_window_mouse_capture')
    if after['foreground_pid'] == probe_pid:
        problems.append('probe_took_foreground')
    if after.get('focus_pid') == probe_pid:
        problems.append('probe_took_focus')
    return sorted(set(problems))


def has_normal_probe_window(snapshot: dict, probe_pid: int) -> bool:
    return any(w['pid'] == probe_pid and w['caption'] and not w['topmost']
               and w['rect'][2] > w['rect'][0] and w['rect'][3] > w['rect'][1]
               for w in snapshot['windows'])


class DisplayWatch:
    def __init__(self):
        if os.name != 'nt':
            raise DisplayWatchError('Windows display diagnostics required')
        from ctypes import wintypes as w
        self.w = w
        self.user = c.WinDLL('user32', use_last_error=True)

        class Device(c.Structure):
            _fields_ = [('size', w.DWORD), ('name', w.WCHAR * 32),
                        ('description', w.WCHAR * 128), ('flags', w.DWORD),
                        ('identifier', w.WCHAR * 128), ('key', w.WCHAR * 128)]

        class Mode(c.Structure):
            _fields_ = [('name', w.WCHAR * 32), ('spec', w.WORD), ('driver', w.WORD),
                        ('size', w.WORD), ('extra', w.WORD), ('fields', w.DWORD),
                        ('display_union', c.c_byte * 16), ('color', w.SHORT),
                        ('duplex', w.SHORT), ('yresolution', w.SHORT), ('ttoption', w.SHORT),
                        ('collate', w.SHORT), ('form', w.WCHAR * 32), ('logpixels', w.WORD)]
            _fields_ += [(n, w.DWORD) for n in ('bits', 'width', 'height', 'flags', 'frequency',
                        'icmmethod', 'icmintent', 'media', 'dither', 'reserved1', 'reserved2',
                        'panningwidth', 'panningheight')]

        class GuiInfo(c.Structure):
            _fields_ = [('size', w.DWORD), ('flags', w.DWORD)]
            _fields_ += [(n, w.HWND) for n in ('active', 'focus', 'capture', 'menu', 'move', 'caret')]
            _fields_ += [('caret_rect', w.RECT)]

        if c.sizeof(Device) != 840 or c.sizeof(Mode) != 220 or c.sizeof(GuiInfo) != 72:
            raise DisplayWatchError('Unexpected x64 display diagnostic ABI')
        self.Device, self.Mode, self.GuiInfo = Device, Mode, GuiInfo
        self.callback_type = c.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        prototypes = {
            'EnumDisplayDevicesW': ([w.LPCWSTR, w.DWORD, c.POINTER(Device), w.DWORD], w.BOOL),
            'EnumDisplaySettingsW': ([w.LPCWSTR, w.DWORD, c.POINTER(Mode)], w.BOOL),
            'EnumWindows': ([self.callback_type, w.LPARAM], w.BOOL),
            'IsWindowVisible': ([w.HWND], w.BOOL),
            'GetWindowRect': ([w.HWND, c.POINTER(w.RECT)], w.BOOL),
            'GetWindowThreadProcessId': ([w.HWND, c.POINTER(w.DWORD)], w.DWORD),
            'GetWindowLongPtrW': ([w.HWND, c.c_int], c.c_ssize_t),
            'GetClassNameW': ([w.HWND, w.LPWSTR, c.c_int], c.c_int),
            'GetForegroundWindow': ([], w.HWND),
            'GetGUIThreadInfo': ([w.DWORD, c.POINTER(GuiInfo)], w.BOOL),
        }
        for name, (args, result) in prototypes.items():
            function = getattr(self.user, name)
            function.argtypes, function.restype = args, result
        self.baseline = self.snapshot(0)
        self.last = self.baseline
        self.samples = 0
        self.window_samples = 0
        self.first_window_time = None
        self.problems = []
        self.failure_snapshot = None
        self.visible_window_observations = {}

    def snapshot(self, probe_pid: int) -> dict:
        displays = []
        for index in range(32):
            device = self.Device()
            device.size = c.sizeof(device)
            if not self.user.EnumDisplayDevicesW(None, index, c.byref(device), 0):
                break
            if device.flags & 1:  # DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
                mode = self.Mode()
                mode.size = c.sizeof(mode)
                if not self.user.EnumDisplaySettingsW(device.name, 0xFFFFFFFF, c.byref(mode)):
                    raise DisplayWatchError('Cannot query an attached desktop display')
                displays.append(dict(device=device.name, bits=mode.bits, width=mode.width,
                                     height=mode.height, frequency=mode.frequency, flags=mode.flags,
                                     position_union=bytes(mode.display_union).hex()))
        if not displays:
            raise DisplayWatchError('No observable desktop displays')
        windows = []

        @self.callback_type
        def collect(hwnd, _):
            if self.user.IsWindowVisible(hwnd):
                pid, rect = self.w.DWORD(), self.w.RECT()
                tid = self.user.GetWindowThreadProcessId(hwnd, c.byref(pid))
                if self.user.GetWindowRect(hwnd, c.byref(rect)):
                    style = self.user.GetWindowLongPtrW(hwnd, -16)
                    exstyle = self.user.GetWindowLongPtrW(hwnd, -20)
                    capture = False
                    class_name = None
                    if pid.value == probe_pid:
                        name = c.create_unicode_buffer(256)
                        if self.user.GetClassNameW(hwnd, name, len(name)):
                            class_name = name.value
                        gui = self.GuiInfo()
                        gui.size = c.sizeof(gui)
                        # A failed query is retained as unqualified capture state.
                        capture = (not self.user.GetGUIThreadInfo(tid, c.byref(gui))) or bool(gui.capture)
                    windows.append(dict(hwnd=int(hwnd), pid=pid.value,
                        rect=[rect.left, rect.top, rect.right, rect.bottom],
                        caption=(style & 0xC00000) == 0xC00000,
                        topmost=bool(exstyle & 8), mouse_capture=capture,
                        probe_class_name=class_name))
            return len(windows) < 1024

        if not self.user.EnumWindows(collect, 0):
            raise DisplayWatchError('Window inventory incomplete')
        foreground = self.user.GetForegroundWindow()
        pid = self.w.DWORD()
        if foreground:
            self.user.GetWindowThreadProcessId(foreground, c.byref(pid))
        foreground_gui = self.GuiInfo()
        foreground_gui.size = c.sizeof(foreground_gui)
        if not self.user.GetGUIThreadInfo(0, c.byref(foreground_gui)):
            raise DisplayWatchError('Cannot qualify foreground focus ownership')
        focus_pid = self.w.DWORD()
        if foreground_gui.focus:
            self.user.GetWindowThreadProcessId(foreground_gui.focus, c.byref(focus_pid))
        return dict(displays=displays, windows=windows, foreground_pid=pid.value, focus_pid=focus_pid.value)

    def check(self, probe_pid: int):
        self.last = self.snapshot(probe_pid)
        self.samples += 1
        self.record_visible_windows(probe_pid)
        self.problems = sorted(set(self.problems + compare_desktop(self.baseline, self.last, probe_pid)))
        if self.problems:
            if self.failure_snapshot is None:
                self.failure_snapshot = self.last
            raise DisplayWatchError(', '.join(self.problems))
        if has_normal_probe_window(self.last, probe_pid):
            self.record_normal_window(probe_pid)

    def record_normal_window(self, probe_pid: int):
        if has_normal_probe_window(self.last, probe_pid):
            self.window_samples += 1
            if self.first_window_time is None:
                self.first_window_time = time.monotonic()

    def record_visible_windows(self, probe_pid: int):
        # Visibility is NOT proof of non-exclusive presentation. Retain it for
        # independent, loss-free DXGI Windowed adjudication of borderless HWNDs.
        observations = getattr(self, 'visible_window_observations', {})
        self.visible_window_observations = observations
        now = time.monotonic()
        for window in self.last['windows']:
            if (window['pid'] == probe_pid and not window['topmost'] and not window['mouse_capture']
                    and window['rect'][2] > window['rect'][0] and window['rect'][3] > window['rect'][1]):
                row = observations.setdefault(str(window['hwnd']), dict(samples=0, first=now, last=now))
                row['samples'] += 1
                row['last'] = now

    def ready(self) -> bool:
        return not self.problems and self.normal_window_ready()

    def normal_window_ready(self) -> bool:
        return (self.window_samples >= 3 and self.first_window_time is not None
                and time.monotonic() - self.first_window_time >= 1)

    def receipt(self) -> dict:
        return dict(baseline=self.baseline, final=self.last, sample_count=self.samples,
                    failure_snapshot=self.failure_snapshot,
                    normal_probe_window_samples=self.window_samples, problems=self.problems,
                    visible_window_observations={hwnd: dict(samples=row['samples'],
                        duration_seconds=row['last'] - row['first']) for hwnd, row in
                        getattr(self, 'visible_window_observations', {}).items()},
                    normal_window_observed=self.normal_window_ready(), resolution_mutation_api_used=False,
                    window_or_foreground_mutation_api_used=False, audio_condition='user_managed_volume_mixer')
