"""Prepare a clearly non-final, single-extraction Windows diagnostic build.

This tool only annotates an existing frozen PyInstaller onedir tree. It does
not create a new source binary, alter executable/runtime resources, download
original game files, or claim Windows 11 gameplay acceptance. The entire
already-existing dist tree is uploaded as a flat GitHub Actions artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


class PlaytestDistributionError(ValueError):
    """The frozen release tree cannot safely serve as a direct-layout test."""


def prepare_playtest_distribution(dist_root: str | Path, commit: str) -> dict:
    """Validate and annotate an existing frozen onedir output, in place.

    The original game's disc and data files must remain external. The
    repository-authorized original_assets copies inside PyInstaller
    _internal are a separate, provenance-controlled source asset category.
    """
    if type(commit) is not str or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise PlaytestDistributionError("Require exact lowercase 40-hex Git commit")
    root = Path(dist_root)
    if not root.is_dir() or root.is_symlink():
        raise PlaytestDistributionError("Existing PyInstaller onedir root required")
    exe = root / "FM2001-Windows11.exe"
    internal = root / "_internal"
    if not exe.is_file() or exe.is_symlink() or not internal.is_dir() or internal.is_symlink():
        raise PlaytestDistributionError("Frozen Windows EXE and _internal directory required")
    if not any(internal.iterdir()):
        raise PlaytestDistributionError("Frozen _internal directory is empty")
    if (root / "footballmanager.exe").exists() or (root / "FM2001").exists():
        raise PlaytestDistributionError("The original game installation may not be bundled")
    if any(p.suffix.lower() == ".zip" for p in root.iterdir() if p.is_file()):
        raise PlaytestDistributionError("Direct-layout artifact must not contain a nested ZIP")

    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    receipt = {
        "schema_version": 1,
        "repository_commit": commit,
        "artifact_kind": "direct_layout_diagnostic_playtest",
        "original_executable_bundled": False,
        "external_original_game_data_required": True,
        "original_game_executed_during_build": False,
        "windows11_interactive_acceptance_verified": False,
        "relative_executable": exe.name,
        "executable_sha256": digest,
    }
    note = (
        "FM2001 Windows 11 diagnostic playtest — not an approved release\n"
        "Extract this artifact once, preferably into a short path such as "
        "C:\\FM2001-Test.\n"
        "Run FM2001-Windows11.exe from this directory. Keep the _internal "
        "directory beside it.\n"
        "Provide your own legitimately obtained original FM2001 installation "
        "files separately when prompted.\n"
        "The original footballmanager.exe and original disc data are not "
        "included in this diagnostic distribution.\n"
        "A successful automated package smoke test is not proof of an "
        "original-faithful playable Windows 11 release.\n"
        f"Git revision: {commit}\n"
    )
    (root / "PLAYTEST-README.txt").write_text(note, encoding="utf-8")
    (root / "PLAYTEST-RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-root", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    print(json.dumps(prepare_playtest_distribution(args.dist_root, args.commit),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
