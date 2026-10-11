# Original-game source-first workflow after the 11 October 2026 Drive upload

**Current rule for the continuous autonomous FM2001 worker.** The user has supplied a directly navigable, private, extracted copy of the original disc filesystem. **USE THIS FIRST** when investigating missing or mismatched original game behavior, graphics, text, data and interfaces. Do not revert to automatic 511 MB ZIP / 632 MB BIN materialization merely because an old recovery prompt names those containers. Read `research/ORIGINAL_SOURCE_LOCATOR.md` for primary exact URLs, verified sizes, hashes and Drive folder IDs.

## What changed, and what was actually confirmed

- New original extracted filesystem:
  `02 — EXTRACTED ORIGINAL GAME FILES — FOLDERS AND ASSETS/FM2001/`
  https://drive.google.com/drive/folders/1pQy4V8tq5COGhtIMgNPVSDFjSRqiqnTC
  (15 subfolders and 37 files at its root, not a proved recursive complete-file census).
- Byte-verified original disc-root `footballmanager.exe` is also separately
  accessible under `03 — AUTOWORKER DIRECT ACCESS`:
  https://drive.google.com/file/d/1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q/view?usp=drivesdk
  with **4,714,541 bytes; SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**.
- Examples of visible extracted first-party game resources:
  `FM2001/Master.dat`, `Static.dat`, `English.str`,
  `EnglishEAM.str`, `Resource.res`, `FM2001_Art/`, `DataInGame/`,
  `ArtInGame/`, `FMV/`, `Fonts/`, `FormationFiles/`.
- Original `FM2001_Art/Generic/EAMail/`:
  https://drive.google.com/drive/folders/1WhzWAPpa7j10wQKG-OItGRhC5YsUpmyX
  contains all four separately *raw-byte fetched and hash verified* row sprites:
  `text_grid_nor.444`, `text_grid_sel.444`,
  `text_grid_high.444`, `text_grid_des.444`.
  Sizes and SHA-256 hashes exactly match
  `reconstruction/original_eamail_source_contract.py`. The verified
  original sprites are evidence/assets, NOT proof the Inbox is playable.
- Google Drive listing reported examined source items as **not shared**.
  Preserve privacy. Do not embed original proprietary binary data in code,
  GitHub issues, PR descriptions, comments or public releases.
- `01 — ORIGINAL DISC ARCHIVE ZIP` currently contains a **71 MB Windows11
  reconstruction release-candidate ZIP**, not the canonical original disc
  source ZIP; do NOT use that RC as evidence of original behavior.
  Canonical original ZIP still exists in private ChatGPT Library as in the
  source locator.
- Full extracted-folder parity with the original 2,456-file/211-folder
  catalog was **not exhaustively verified**; verify missing paths or
  hashes case by case rather than claiming every file is proven intact.

## Mandatory practical source workflow for every original-feature investigation

1. **Fresh repository:** inspect current `main` SHA, `research/CURRENT_STATE.md`,
   the active gate, `research/WORK_OWNERSHIP.json`, and open PRs before edits.
   Worker owns *all* implementation, including former Codex R1. Codex is
   optional and not a merge prerequisite.
2. **Define a *complete original player journey*** relevant to the task:
   screen/entrypoint, click/keyboard ownership, states and alternate controls,
   data producer and ownership, result and side effects, navigation/return,
   persistence, multiple managers and competition contexts. Use original
   source evidence and `research/ORIGINAL_REFERENCE_PLAYABILITY_AUDIT_PROTOCOL.md`.
3. **Find the exact original file via the extracted Drive tree:** start from
   its original relative path and query/list only the containing folder,
   reusing stable folder/file IDs from `research/ORIGINAL_SOURCE_LOCATOR.md`.
   For a small required artifact, use the connected Google Drive raw-file
   fetch with streamed `file_uri` if processing in a compatible tool; do not
   request inline/base64 entire image or large archives. Check the actual
   file bytes and provenance where the conclusion depends on them.
4. **Validate identity and interpretation:** check SHA-256/size against the
   published original-source receipts where available, distinguish
   `footballmanager.exe` from `FOOTBALLMANAGER.ICD`/`BAk`, inspect relevant
   PE/native code, original strings, tables, graphics dimensions/fonts and
   control geometry. Reuse already trustworthy hash receipts; do not burn
   tools repeating full-catalog checks. If evidence conflicts, preserve the
   conflict as `UNKNOWN` and investigate.
5. **Implement the original player-visible result** in the current Windows 11
   reconstruction (not only a data adapter, synthetic test, missing-feature
   warning, or fail-closed guard). No inventions or Premier-League-only release
   substitutions. Preserve original selectable leagues/countries, 2–6 human
   managers and all match modes as applicable. Follow asset policy: stage
   intentionally used original resources with provenance only through
   approved paths; never add uncontrolled full extraction/binary dumps to Git.
6. **Verify four separate evidence levels:**
   (a) native shipped-original byte/source proof;
   (b) reconstructed implementation tests on exact code;
   (c) original-vs-port GUI/input/layout/transition observations where
   available;
   (d) genuine interactive Windows 11 gameplay/installation acceptance.
   Labels (a)/(b) never imply (c)/(d). Gate 13 and Gates 14–17 remain open
   until their actual acceptance criteria are satisfied.
7. **Checkpoint economically:** pursue high-impact end-to-end functionality,
   batch local tests/CI around meaningful verified milestones, use reviewed
   fresh-main PRs, do not overwrite concurrently active worker branches, and
   keep `CURRENT_STATE.md` current with evidence, blockers, exact next step.

## If the execution sandbox fails

- Run a *harmless* trivial shell/Python health check **before** bulk
  materialization. A `caas.internal.errors.ClientError` even for trivial
  commands is an execution environment failure, not proof original source
  is absent.
- The Drive connector has independently returned original executable and
  individual .444 **actual raw bytes**, so smaller provider-side byte reads
  are possible even when the separate CAAS shell cannot execute. Work
  within supported connector limits; where supported, source data can be
  hashed/inspected without huge disc-image downloads.
- If native disassembly or graphical tests require unavailable execution,
  identify the precise unavailable capability and isolate it; work on
  genuinely independent source-qualified tasks rather than generating
  documentation churn or extrapolating unknown behavior.
- Never claim a successful original EXE execution, file-wide checksum sweep,
  usable headless runner, GUI parity or verified Win11 release from a
  Google Drive metadata listing, byte read, GitHub CI or simulated input.

## Priority: put the source access to work

Use the new `EAMail/` art, original string files and the verified executable
to close actual player-visible Inbox behavior beyond PR #595. Use original
`FM2001_Art/Generic/pre_match/`, `match_results/`, `FMV/`,
`FastView/` and original match state evidence to complete the previously
Codex-owned R1 NEXT -> all original PPreMatch modes -> match -> PResults ->
return (the merged partial R1 is already on `main`). Continue Squad/
formations, original Save/Load, every league and multi-human career.
**The game being fully playable and faithful is the objective, not the
number of hashes, research files, pull requests or green synthetic tests.**

## User request and recording

The user personally extracted and uploaded the original game filesystem to
private Google Drive on **11 October 2026**, then explicitly asked whether
this would speed development and aid correctness, and asked us to make the
benefit durable for the autonomous worker. This protocol is the resulting
permanent, source-backed action directive. Do not ask the user to repeat
the extraction/upload unless a **specific missing file** is independently
established.
