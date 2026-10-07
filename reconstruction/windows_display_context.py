"""Process-local DPI compatibility for the Tk-owned WPF media child.

Initialize before creating any Tk HWND. This does not change desktop settings
or the original 800x600 presentation coordinates.
"""
import ctypes
import platform


def initialize_windows_display_context(*, platform_system=None, user32_factory=None):
    if (platform_system or platform.system()) != 'Windows':
        return
    if user32_factory is None:
        user32_factory = lambda: ctypes.WinDLL('user32', use_last_error=True)
    user32 = user32_factory()
    user32.GetThreadDpiAwarenessContext.argtypes = ()
    user32.GetThreadDpiAwarenessContext.restype = ctypes.c_void_p
    user32.GetAwarenessFromDpiAwarenessContext.argtypes = (ctypes.c_void_p,)
    user32.GetAwarenessFromDpiAwarenessContext.restype = ctypes.c_int
    user32.SetProcessDPIAware.argtypes = ()
    user32.SetProcessDPIAware.restype = ctypes.c_int

    def awareness():
        return user32.GetAwarenessFromDpiAwarenessContext(
            user32.GetThreadDpiAwarenessContext())

    current = awareness()
    if current == 0:
        # Match WPF's system-aware rendering before cross-process parenting.
        # Existing manifest/embedding awareness must not be downgraded.
        user32.SetProcessDPIAware()
        current = awareness()
    if current not in (1, 2):
        raise RuntimeError('Cannot qualify Windows DPI context before game window creation')
