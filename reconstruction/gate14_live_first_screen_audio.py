"""Live Windows integration for source-verified FM2001 first-screen menu PCM.

This composes already-recovered Gate-14 pieces only:
* canonical DATA/AUDIO/SFXS/menus.bnk source identity;
* the verified first-screen Button numeric press route;
* the Windows in-memory WAV backend;
* the fullscreen-aware host binding.

Missing/invalid audio remains a presentation failure and must never block the
gameplay click path.
"""
from __future__ import annotations

from hashlib import sha256
import platform
from pathlib import Path
from typing import Callable

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_first_screen_audio_binding import install_first_screen_press_audio
from gate14_windows_menu_pcm_backend import WindowsMemoryWaveMenuPcmBackend


CANONICAL_MENUS_RELATIVE_PATH = Path("DATA") / "AUDIO" / "SFXS" / "menus.bnk"


class Gate14LiveFirstScreenAudioError(RuntimeError):
    pass


def load_canonical_menus_bnk(game_dir: str | Path) -> bytes:
    """Read and reverify the exact original menus.bnk from the installed game."""
    path = Path(game_dir) / CANONICAL_MENUS_RELATIVE_PATH
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise Gate14LiveFirstScreenAudioError(
            f"canonical menus.bnk could not be read: {path}: {exc}"
        ) from exc

    profile = CANONICAL_FM2001_BANK_PROFILES["menus.bnk"]
    if (
        len(data) != profile["size_bytes"]
        or sha256(data).hexdigest() != profile["sha256"]
    ):
        raise Gate14LiveFirstScreenAudioError(
            "menus.bnk does not match the verified FM2001 source identity"
        )
    return data


def install_live_first_screen_audio(
    host,
    game_dir: str | Path,
    *,
    platform_system: str | None = None,
    backend_factory: Callable[[], object] = WindowsMemoryWaveMenuPcmBackend,
):
    """Install verified press audio on Windows; leave non-Windows hosts unchanged."""
    system = platform.system() if platform_system is None else platform_system
    if system != "Windows":
        return None
    try:
        menus_bnk = load_canonical_menus_bnk(game_dir)
        backend = backend_factory()
        return install_first_screen_press_audio(host, menus_bnk, backend)
    except Gate14LiveFirstScreenAudioError:
        raise
    except Exception as exc:
        raise Gate14LiveFirstScreenAudioError(
            f"live first-screen audio integration failed: {type(exc).__name__}: {exc}"
        ) from exc
