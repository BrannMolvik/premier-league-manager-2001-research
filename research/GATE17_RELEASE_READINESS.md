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


### Clean Windows 11 install receipt producer

`reconstruction/gate17_clean_windows_install.py` is the separate producer for
`clean_windows_install.json`. It must be run on the actual Windows 11 release
candidate environment and is deliberately not invoked by hosted packaging CI.

The producer is archive-first rather than source-tree-first:

1. require a real Windows 11 **client workstation** through the shared
   Gate-17 guard; GitHub Actions and Windows Server/non-workstation product
   types are rejected even when their build number is modern;
2. hash the exact release archive and bind the receipt to its release version and
   full repository commit;
3. require a **new, non-existing install directory outside the Git checkout**;
4. reject archive traversal, symlinks and case-insensitive Windows path
   collisions before extraction;
5. extract the candidate archive into that fresh external directory;
6. require the installed `PACKAGE-MANIFEST.json` to match the requested
   release version, repository commit and executable name;
7. hash and size-check every installed payload file and reject both missing and
   unexpected files;
8. launch the frozen `FM2001-Windows11.exe --package-smoke` with the extracted
   package as its working directory;
9. only after all checks pass, write a new
   `clean_windows_install.json` outside Git without overwriting prior evidence.

Example on the Windows 11 validation machine:

```powershell
python reconstruction/gate17_clean_windows_install.py `
  --release-version "<version>" `
  --repository-commit "<40-char release commit>" `
  --release-archive "C:\FM2001-release\FM2001-Windows11-<version>.zip" `
  --install-root "C:\FM2001-clean-install-<version>" `
  --output-dir "C:\FM2001-release\receipts"
```

The normal `windows-package.yml` workflow runs this module's **unit tests**
because package-format changes must not silently break the external validator.
It does not run the producer and therefore cannot create or substitute the
required real-Windows-11 clean-install receipt.

The same external-workstation guard is shared by the gameplay receipt producer
and the final release-readiness audit. Consequently, none of the four required
external receipts, nor the final Gate-17 sign-off, can be generated by
GitHub-hosted Windows CI or a Windows Server host.


### Transactional external validation runner

`reconstruction/gate17_external_validation.py` is the final one-command
coordinator for the real Windows 11 client workstation. It is intentionally
stricter than running the receipt producers manually.

Before it creates an install tree or any immutable receipt file, it requires:

- the shared Windows 11 client-workstation guard to pass;
- a clean repository at the exact release commit;
- every Gate 1-16 completion criterion in `ROADMAP.md` to be checked;
- `research/RELEASE_LIMITATIONS.md` to have left its pre-release state;
- the exact release archive and canonical user-owned FM2001 directory to be
  outside the Git checkout;
- a fresh external validation work root that does not already exist.

Only after that preflight succeeds does it execute, in order, the clean-install
receipt, all three gameplay receipts, release-evidence assembly and the final
release-readiness audit. The complete evidence bundle lives below the one
external work root. If any post-preflight step fails, that newly created work
root is removed so a partial set of receipts cannot be mistaken for final
release evidence.

The runner therefore **cannot pass today** while Gates 13-16 remain open and
the limitations ledger is intentionally marked pre-release. That is the desired
fail-closed behavior, not a missing bypass.

Intended final command:

```powershell
python reconstruction/gate17_external_validation.py `
  --release-version "<final-version>" `
  --repository-commit "<40-char final release commit>" `
  --release-archive "C:\FM2001-release\FM2001-Windows11-<version>.zip" `
  --canonical-game-dir "C:\Games\FM2001" `
  --work-root "C:\FM2001-release\final-validation-<version>"
```

Hosted Windows CI runs only this coordinator's synthetic unit tests. The
coordinator itself still refuses GitHub Actions and does not convert hosted
packaging into external Windows 11 release evidence.
