#!/usr/bin/env python3
"""Validate FM2001 modernization repository asset placement and hygiene."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ORIGINAL_ASSET_ROOT = Path("original_assets")
MANIFEST_PATH = ORIGINAL_ASSET_ROOT / "MANIFEST.md"

# Known original files may be committed intentionally, but only in the
# provenance-tracked original_assets/ tree.
KNOWN_ORIGINAL_BASENAMES = {
    "footballmanager.exe",
    "footbal.exe",
    "editor.exe",
    "master.dat",
    "static.dat",
    "core.str",
    "english.str",
}

# Packaging/container artifacts duplicate extracted useful resources and bloat
# Git history. Keep these outside the repository even though their contents are
# authorized for use.
FORBIDDEN_CONTAINER_BASENAMES = {
    "famg2001.bin",
    "famg2001.cue",
}

FORBIDDEN_CONTAINER_EXTENSIONS = {
    ".iso",
    ".cue",
    ".mdf",
    ".mds",
    ".nrg",
    ".ccd",
    ".sub",
    ".zip",
    ".7z",
    ".rar",
}

TEMP_RE_EXTENSIONS = {
    ".idb",
    ".i64",
    ".id0",
    ".id1",
    ".id2",
    ".nam",
    ".til",
}

MAX_TRACKED_FILE_BYTES = 95 * 1024 * 1024

POLICY_FILES = {
    ORIGINAL_ASSET_ROOT / "README.md",
    MANIFEST_PATH,
}


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return [Path(p.decode("utf-8")) for p in result.stdout.split(b"\0") if p]


def is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def main() -> int:
    failures: list[str] = []
    paths = tracked_paths()

    manifest_text = ""
    if MANIFEST_PATH.is_file():
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8", errors="replace")

    for path in paths:
        lower_name = path.name.lower()
        suffix = path.suffix.lower()

        if lower_name in FORBIDDEN_CONTAINER_BASENAMES:
            failures.append(f"{path}: raw source disc container must stay out of Git")
            continue

        if suffix in FORBIDDEN_CONTAINER_EXTENSIONS:
            failures.append(f"{path}: archive/disc-image container is not allowed")
            continue

        if suffix in TEMP_RE_EXTENSIONS:
            failures.append(f"{path}: reverse-engineering temporary database is not allowed")
            continue

        if path.is_file() and path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            failures.append(
                f"{path}: tracked file exceeds 95 MiB; extract/store only the useful resources"
            )
            continue

        if lower_name in KNOWN_ORIGINAL_BASENAMES and not is_under(path, ORIGINAL_ASSET_ROOT):
            failures.append(
                f"{path}: intentional original FM2001 files belong under original_assets/"
            )
            continue

        if is_under(path, ORIGINAL_ASSET_ROOT) and path not in POLICY_FILES:
            normalized = path.as_posix()
            if normalized not in manifest_text:
                failures.append(
                    f"{path}: original/derived asset is not listed in original_assets/MANIFEST.md"
                )

    if failures:
        print("Repository asset policy FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print(
            "Authorized original resources are allowed, but place them under "
            "original_assets/ and record them in the manifest. Keep raw disc/archive "
            "containers and temporary reverse-engineering artifacts out of Git.",
            file=sys.stderr,
        )
        return 1

    print(
        "Repository asset policy passed: authorized original assets are controlled "
        "and no forbidden packaging/temp artifacts are tracked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
