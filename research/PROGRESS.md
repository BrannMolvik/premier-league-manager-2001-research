# Premier League Manager 2001 Reverse-Engineering Progress

_Last updated: 23 September 2026_

## Purpose

This file is the canonical resume point for the project. Any ChatGPT, Codex, or local-agent session working on this repository should read this file before starting new investigation.

## Current Goal

Reverse engineer Premier League Manager 2001 as completely as practical, including:

- executable startup and subsystem layout
- database and string-table formats
- clubs, players, managers, squads, competitions, fixtures, transfers, finances, training and scouting
- save-game format
- season progression and AI
- match engine and match-day presentation
- clean-room reimplementation experiments that read the user's original game data without depending on the legacy executable

The fallback remains a persistent VM if a faithful native reimplementation becomes disproportionate.

## Current State

GitHub persistence is active. The connected GitHub account is `BrannMolvik` and has push/admin access to this repository.

A Windows 11 modernization attempt successfully reconstructed the game installation without the obsolete 16-bit installer, but Windows Smart App Control / Code Integrity blocks the unsigned legacy `footballmanager.exe` before execution. Event ID 3077 in the Code Integrity Operational log explicitly identified the executable as blocked.

A clean-room reimplementation prototype has therefore been started alongside executable reverse engineering.

## Confirmed Findings

### Original media / executable

- The available disc image is a FairLight-era release containing the original game data plus an already-decrypted/cracked `footballmanager.exe`.
- The game is a 32-bit Windows application, not DOS.
- It uses old DirectX-era APIs including DirectDraw, DirectInput and DirectSound.
- The original setup path includes a 16-bit installer that cannot run natively on 64-bit Windows.
- The executable contains extensive leftover C++ source-path/type information, including paths under:
  - `D:\Projects\FM2001\Applications\FootballManager\...`
  - `D:\Projects\FM2001\Libraries\Database\...`
- Match-related source-path strings include:
  - `Libraries\Database\Match.cpp`
  - `Applications\FootballManager\FastView\MatchController.cpp`

### Windows 11 compatibility

- A modernized game folder was built successfully without the original 16-bit installer.
- The original 3D setup utility runs and writes graphics configuration.
- Launching `footballmanager.exe` produces only a very brief shell spinner.
- Running from Command Prompt returned exit code `-1`, but later Code Integrity logging showed that Windows itself blocks the executable.
- Running as administrator does not bypass the block.
- Windows Code Integrity Operational Event ID 3077 explicitly names `C:\Games\FM2001\footballmanager.exe`.
- Binary patching the executable also remains subject to Smart App Control, so compatibility mode/CMD/admin rights are not sufficient solutions on the host OS.

### String tables

- `Core.str` has been decoded as an indexed string table with approximately 29,033 strings.
- `English.str` has been decoded as an indexed string table with approximately 21,856 strings.
- These tables contain real player names, club/stadium strings, UI text, competition/world text and asset paths.
- Example early `Core.str` entries resolve to Arsenal-era player names including David Seaman, Lee Dixon and Nigel Winterburn.

### Master.dat

The file is structured and directly parseable rather than encrypted.

Confirmed top-level record blocks:

- 1,246 club records
- club record size: 181 bytes
- 30,064 player records
- player record size: 103 bytes
- final 1,612 records identified as manager records

Confirmed relationships/examples:

- The first club record resolves to Arsenal and references strings/assets including Highbury and Arsenal map/texture data.
- The first player records resolve to David Seaman, Lee Dixon, Nigel Winterburn, Steve Bould and Tony Adams.
- Player records include a direct club relationship field, so authentic squads can be reconstructed.
- Player records expose date-of-birth and physical data such as height/weight.
- A block of one-byte player attributes has been located with values on an apparent 0-30 scale, but exact attribute-name ordering is not yet considered proven.
- Club records link to manager records.
- Manager record 10 resolves to Alex Ferguson, born 31 December 1941, joined Manchester United 6 November 1986.
- Arsenal's club record points to manager record 204, which resolves to Arsène Wenger.

### Clean-room prototype

A prototype has already been produced that:

- does not execute or embed EA's `footballmanager.exe`
- reads the user's existing `Master.dat`, `English.str` and `Core.str`
- reconstructs clubs and players from the original data
- provides a modern searchable database-viewer proof of concept

The prototype proves the original football database can be consumed by a modern application.

## Active Investigation

Reverse engineer the entire game incrementally while preserving every substantial result in this repository.

Priority order:

1. Finish formal documentation of `Master.dat` record layouts.
2. Fully map player-to-club/squad relationships and player attribute semantics.
3. Map manager record layout.
4. Locate and decode competition/league structures, schedules and rules.
5. Identify contracts, transfers, finances, training, scouting and board-state data.
6. Reverse engineer save-game serialization.
7. Map high-level executable subsystem/function graph using source-path and RTTI/string clues.
8. Trace season advancement and AI-management logic.
9. Trace match creation, simulation and event generation.
10. Trace `FastView` / match-day presentation and renderer-facing structures.
11. Implement decoded behavior in the clean-room reimplementation as understanding improves.

## Persistence / Checkpoint Rule

Do not perform a long investigation without saving intermediate progress.

For future work in ChatGPT:

- Work in small reverse-engineering blocks.
- After each meaningful subsystem discovery, write the result to the appropriate file in `research/` and/or code in `tools/` or `reconstruction/`.
- Commit to GitHub before moving into another long investigation block.
- If a task may time out, checkpoint partial findings before the expensive step.
- Never rely on conversation state as the only copy of a discovered offset, record layout, algorithm, failed experiment or next-step hypothesis.

If a session is interrupted, the repository is the canonical state.

## Resume Rule

A new session should:

1. Read `research/CONTINUATION_INSTRUCTIONS.md`.
2. Read this file completely.
3. Read `research/FINDINGS.md`, `research/FILE_FORMATS.md`, `research/EXECUTABLE_ANALYSIS.md` and `research/FAILED_APPROACHES.md` as relevant.
4. Inspect recent commits.
5. Continue from the current Active Investigation section.

Do not repeat an earlier experiment solely because the conversation restarted.
