#!/usr/bin/env python3
"""Fail if tracked files cross the FM2001 clean-room repository boundary."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


FORBIDDEN_BASENAMES = {
    "footballmanager.exe",
    "footbal.exe",
    "editor.exe",
    "master.dat",
    "static.dat",
    "core.str",
    "english.str",
    "famg2001.bin",
    "famg2001.cue",
}

FORBIDDEN_DISC_EXTENSIONS = {
    ".iso",
    ".bin",
    ".cue",
    ".img",
    ".mdf",
    ".mds",
    ".nrg",
    ".ccd",
    ".sub",
}

# Exact canonical originals documented in research/FINDINGS.md.
FORBIDDEN_CANONICAL_HASHES = {
    "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3": "footballmanager.exe",
    "0dd121f1e27906b7c839374288cfb497e38c87595b4736ee2c9febbe956408c5": "Editor.exe",
    "183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8": "Master.dat",
    "e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8": "Static.dat",
    "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601": "English.str",
    "b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06": "Core.str",
}


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return [Path(p.decode("utf-8")) for p in result.stdout.split(b"\0") if p]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []

    for path in tracked_paths():
        lower_name = path.name.lower()
        suffix = path.suffix.lower()

        if lower_name in FORBIDDEN_BASENAMES:
            failures.append(f"{path}: forbidden original-game filename")
            continue

        if suffix in FORBIDDEN_DISC_EXTENSIONS:
            failures.append(f"{path}: raw/disc-image extension is not allowed")
            continue

        # Hashing the small clean-room repository also catches renamed canonical
        # originals without depending on their filenames.
        if path.is_file():
            digest = sha256(path)
            original_name = FORBIDDEN_CANONICAL_HASHES.get(digest)
            if original_name:
                failures.append(
                    f"{path}: byte-identical to canonical original {original_name}"
                )

    if failures:
        print("Clean-room guard FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print(
            "Remove original/copyrighted game artifacts from Git history/worktree "
            "and keep them outside the repository.",
            file=sys.stderr,
        )
        return 1

    print("Clean-room guard passed: no forbidden tracked FM2001 originals detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
