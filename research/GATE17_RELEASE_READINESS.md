# Gate 17 release-readiness audit

_Date: 1 October 2026 KST_

## Status

This is release-audit groundwork. Gate 17 is not complete, and Gate 13 remains the earliest incomplete validation gate.

The final audit in reconstruction/gate17_release_readiness.py is designed to run on the actual Windows 11 release candidate. It joins repository checks with separate clean-install and gameplay evidence rather than treating hosted CI as proof of a successful Windows release.

## Required final evidence

The evidence contract requires four **distinct** external JSON receipt files, all tied to the same repository commit and stored outside Git: clean Windows 11 installation outside the development environment; new-game plus management-loop smoke; season progression; and save/reload. Reusing one receipt file for multiple criteria is rejected even if that file happens to contain several true flags.

Every receipt must also identify the exact `release_version` and
`release_archive_sha256` from the final evidence contract. This prevents a
source-tree or older-build smoke result from being paired with a different
archive merely because both share a repository commit.

The audit also verifies a clean Git working tree, repository asset policy, canonical FM2001 source-data verification, the full unittest suite, an archived release file with exact size and SHA-256, and the final release-limitations document.

Recovery 188 additionally makes the roadmap prerequisite chain machine-checkable:
the final Gate-17 audit refuses to pass unless **every completion criterion in
Gates 1 through 16 is checked in `ROADMAP.md`**. Gate 17 itself is
deliberately excluded from that prerequisite check because this release audit is
one of Gate 17's own completion steps. Missing gate sections, prerequisite gates
with no checkbox criteria, and any unchecked Gate 1-16 criterion all fail
closed.

## Fail-closed boundary

research/RELEASE_LIMITATIONS.md is deliberately marked pre-release today. The final audit rejects a limitations document that still carries that marker. This prevents the Gate 17 tool from passing until earlier gate work and the real Windows release checks have actually been completed.

Gate 17 must still produce and test the installable build itself. This harness only makes the final evidence requirements machine-checkable and consistent with one known repository state.

## Current prerequisite snapshot

Gate 16 is no longer missing canonical real-data multi-season evidence. Its
work-ahead readiness audit records two independent shipped-data seeds, each
completing three annual qualification/regeneration cycles, plus the synthetic,
save/reload, transfer-churn, mixed-primary, and state-growth stress coverage.
Those criteria remain prevalidated rather than complete because Gates 13-15
are still open and the final current-runtime rerun has not happened.

The pre-release limitations ledger must therefore describe Gate 16 as
prevalidated-but-blocked-by-prerequisites, not as lacking canonical
multi-season evidence. Gate 13 remains the earliest incomplete validation gate,
and Gate 14/15 work remains unfinished.


### Windows gameplay receipt producer

`reconstruction/gate17_windows_gameplay_receipts.py` creates the three runtime-verifiable gameplay receipts on Windows 11:

- `new_game_management_loop.json`: constructs the canonical shipped-data runtime, selects a Premier League club, produces a legal 11+5 lineup, reaches the first human fixture, plays it through the shared backend and requires the result to persist;
- `save_reload.json`: starts an independent canonical game, plays one matchday, writes the current schema save, reloads it against the canonical database and requires an exact logical gameplay snapshot round-trip;
- `season_progression.json`: reuses the canonical Gate-12 annual-rollover audit, requiring a completed live season and a complete 380-fixture year-two Premier League regeneration.

The runner hashes the release archive itself and writes all three receipts only after all three audits have passed. Its output directory must be outside Git and must not contain prior receipt files. Every produced receipt carries the exact release version, repository commit and archive SHA-256.

Example from the release-candidate environment:

```powershell
python reconstruction/gate17_windows_gameplay_receipts.py `
  --game-dir "C:\\Games\\FM2001" `
  --release-version "<version>" `
  --repository-commit "<40-char release commit>" `
  --release-archive "C:\\FM2001-release\\FM2001-Windows11-<version>.zip" `
  --output-dir "C:\\FM2001-release\\receipts"
```

This tool intentionally does **not** create `clean_windows_install.json`. That receipt must be produced by the separate clean-install procedure after the candidate archive has actually been installed or extracted outside the development environment.


### Hosted Windows release-candidate packaging

`reconstruction/gate17_windows_package.py` builds a bounded PyInstaller `onedir` candidate using pinned `pyinstaller==6.22.3`. Build/work/spec directories and final release output remain outside the Git checkout. The builder requires the exact candidate commit and a clean repository before packaging, runs a silent frozen-import smoke through `FM2001-Windows11.exe --package-smoke`, then writes a sorted/fixed-timestamp ZIP plus a separate SHA-256 manifest.

The package contains the modern runtime and the provenance-tracked `original_assets` tree only. It explicitly rejects bundled `FOOTBAL.EXE`, `Master.dat`, `Static.dat`, and raw disc-image formats. Users supply an authorized original FM2001 installation on first launch.

`.github/workflows/windows-release-candidate.yml` runs this build on GitHub-hosted `windows-latest`, uploads the candidate folder/ZIP/manifest as a temporary Actions artifact, and is a **build/smoke path only**. GitHub documents `windows-latest` as Windows Server 2025, so this hosted workflow must never be treated as the required consumer Windows 11 clean-install receipt. Reference: https://github.com/actions/runner-images/blob/main/README.md

The final Windows 11 evidence gate therefore also verifies Windows workstation product type in addition to build >= 22000. Windows Server can build the candidate but cannot satisfy Gate 17 end-user validation.
