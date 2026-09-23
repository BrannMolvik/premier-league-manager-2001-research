# Premier League Manager 2001 Reverse-Engineering Progress

_Last updated: 23 September 2026_

## Purpose

This file is the canonical resume point for the project. Any ChatGPT, Codex, or local-agent session working on this repository should read this file before starting new investigation.

## Current Goal

Reverse engineer Premier League Manager 2001 sufficiently to understand why it no longer launches correctly on modern Windows, recover as much of the original game's behavior as practical, and determine whether the best route is compatibility work, binary patching/wrapping, partial reconstruction, or a broader reimplementation.

## Current State

Repository initialized for persistent reverse-engineering research.

The game investigation itself was started in another ChatGPT conversation before this repository existed. Some earlier attempts timed out. Their findings have not yet been imported here and should not be assumed lost or confirmed until they are copied into this repository.

## Confirmed Findings

- None imported yet.

## Active Investigation

- Import the earlier Premier League Manager 2001 investigation from the previous chat/session.
- Identify all files, commands, compatibility tests, errors, and technical observations already established.
- Record confirmed results in FINDINGS.md.
- Record unsuccessful approaches in FAILED_APPROACHES.md.
- Continue from the latest verified point rather than repeating completed work.

## Next Steps

1. Recover the previous chat's concrete findings and attempted fixes.
2. Inventory the original game files available for analysis.
3. Establish executable architecture, imports, graphics/audio dependencies, and startup path.
4. Reproduce the current launch failure and document it precisely.
5. Build small analysis tools/scripts as needed under tools/.
6. Checkpoint this file after every meaningful investigation block.

## Checkpoint Rule

Do not perform a long investigation without saving intermediate progress.

After each substantial finding or failed approach:
1. Update the relevant research note.
2. Update this file with the current investigation state and next step.
3. Commit the changes to GitHub.

If a session is approaching a timeout or context limit, checkpoint immediately even if the investigation is incomplete.

## Resume Rule

A new session should:
1. Read research/CONTINUATION_INSTRUCTIONS.md.
2. Read this file completely.
3. Read any research files relevant to the current task.
4. Inspect recent commits if needed.
5. Continue from the documented next step.

Do not repeat an earlier experiment solely because the conversation restarted.
