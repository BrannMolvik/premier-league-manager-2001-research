from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from app import App


def install_dir() -> Path:
    """Return the portable build directory in source and frozen builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def choose_game_dir() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(
        title="Select FM2001 game-data folder"
    )
    root.destroy()
    return Path(selected) if selected else None


def resolve_game_dir(base: Path, explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit)
        return candidate if (candidate / "Master.dat").is_file() else None

    for candidate in (
        base / "GameData",
        base / "gamedata",
        base,
    ):
        if (candidate / "Master.dat").is_file():
            return candidate
    return choose_game_dir()


def play_intro(base: Path, *, skip: bool) -> None:
    """Play the authorized converted FM2001 intro when bundled."""
    if skip:
        return

    player = base / "IntroPlayer.exe"
    intro = base / "Assets" / "premintro.mp4"
    if not player.is_file() or not intro.is_file():
        return

    try:
        subprocess.run(
            [str(player), str(intro)],
            cwd=str(base),
            check=False,
        )
    except OSError:
        # Intro playback is presentation-only. Never prevent the game from
        # starting because a kiosk/security policy blocked the helper.
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game-dir",
        help="Override the portable GameData folder.",
    )
    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Skip the original FM2001 intro.",
    )
    args = parser.parse_args()

    base = install_dir()
    play_intro(base, skip=bool(args.skip_intro))

    game_dir = resolve_game_dir(base, args.game_dir)
    if game_dir is None:
        return 0

    try:
        App(game_dir).mainloop()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("FM2001 feasibility build", str(exc))
        root.destroy()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
