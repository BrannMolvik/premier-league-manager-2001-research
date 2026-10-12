"""Prepare a direct-layout diagnostic artifact; retain the formal RC checks."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from gate17_package_candidate import validate_distribution


LAUNCHER = r'''@echo off
setlocal
cd /d "%~dp0"
set "MEDIA=--skip-startup-media"
if /i "%~1"=="videos" (
  set "MEDIA="
  shift
)
"%~dp0FM2001-Windows11.exe" %MEDIA%
if errorlevel 1 pause
'''


def prepare_playtest(root, commit):
    root = Path(root)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Exact repository commit required")
    validate_distribution(root, "FM2001-Windows11.exe")
    # Validate BEFORE writing: Explorer extraction needs no long-path setting.
    paths = [p.relative_to(root).as_posix() for p in root.rglob('*')]
    paths += ['PLAYTEST.cmd', 'PLAYTEST_README.txt', 'PLAYTEST-MANIFEST.json']
    longest = max(paths, key=len)
    if len('C:\\FMTest\\') + len(longest) > 240:
        raise ValueError("Playtest extraction path exceeds 240 characters: " + longest)
    (root / 'PLAYTEST.cmd').write_bytes(LAUNCHER.replace('\n', '\r\n').encode('ascii'))
    (root / 'PLAYTEST_README.txt').write_text(
        f"FM2001 diagnostic playtest - commit {commit}\n\n"
        "Download the FM2001-Playtest artifact ZIP from the linked Actions run.\n"
        "Extract ONCE into C:\\FMTest. PLAYTEST.cmd must be directly in that folder.\n"
        "Double-click PLAYTEST.cmd. No Python installation or rebuild is needed.\n"
        "This starts the ORIGINAL-STYLE interface, skipping startup FMVs for diagnosis.\n"
        "Optional: from Command Prompt run PLAYTEST.cmd videos to include startup FMVs.\n"
        "If asked, select your ORIGINAL game folder containing Master.dat.\n"
        "The original disc/game database is not bundled. Keep your original files private.\n"
        "Unsigned executable: Windows Smart App Control may block execution.\n"
        "This package does not change or bypass Windows security policies.\n\n"
        "Try New Game > England > Conference > Southport > Start; inspect Squad,\n"
        "management menu, Inbox names/subjects/dates/unread icons, selection and arrows.\n"
        "Inbox previews/actions and some controls remain incomplete; Gate13 is OPEN.\n"
        "Report delays, rendering errors and inactive controls. Use a separate test save.\n"
        "Packaging smoke is not interactive Windows acceptance.\n"
        f"Longest extracted path under C:\\FMTest: {len('C:/FMTest/') + len(longest)} characters.\n",
        encoding='utf-8',
    )
    files = [{"path": p.relative_to(root).as_posix(), "size": p.stat().st_size,
              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(root.rglob('*')) if p.is_file()
             and p.name != 'PLAYTEST-MANIFEST.json']
    manifest = {"repository_commit": commit, "diagnostic_only": True,
                "longest_relative_path": longest,
                "max_extracted_path_length": len('C:/FMTest/') + len(longest),
                "files": files}
    (root / 'PLAYTEST-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dist-root', required=True)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    receipt = prepare_playtest(args.dist_root, args.commit)
    print(json.dumps({key: value for key, value in receipt.items() if key != 'files'}))
