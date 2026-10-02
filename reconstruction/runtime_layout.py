"""Runtime filesystem layout for source and frozen FM2001 builds.

Development runs resolve resources from the repository root. Frozen builds
resolve bundled resources from PyInstaller extraction/application roots rather
than from the reconstruction source directory, which is absent in an installed
release.
"""
from __future__ import annotations

from pathlib import Path
import sys


def application_root() -> Path:
    """Return the root containing bundled runtime resources."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass).resolve()
    if bool(getattr(sys, "frozen", False)):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def bundled_original_assets_root() -> Path:
    return application_root() / "original_assets"


def bundled_source_root() -> Path:
    return bundled_original_assets_root() / "source"
