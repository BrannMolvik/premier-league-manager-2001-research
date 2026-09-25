# Authorized Original Asset Policy

## Project direction

This project is a **Windows 11 modernization/port of The F.A. Premier League Football Manager 2001**.

The project owner has explicitly confirmed that the contents of the supplied FM2001 archive/disc image are authorized for use in this project. The development goal is therefore to **reuse as much of the original game as is technically practical**, rather than replacing original presentation/data assets without need.

## Preservation priority

When choosing between rebuilding an original resource and reusing it, prefer this order:

1. reuse the original asset byte-for-byte if the modern runtime can consume it;
2. convert the original asset to a modern format when required for compatibility;
3. recreate behavior/code around the asset while preserving the original content;
4. make a replacement asset only when the original cannot reasonably be used.

This applies to resources such as:

- music and menu/login audio;
- sound effects;
- interface graphics and backgrounds;
- icons, badges, logos, and other UI imagery;
- strings and localization resources;
- databases and fixture data;
- fonts or font resources when technically usable;
- match-presentation resources;
- other packaged resources from the authorized source archive.

## Code versus assets

The existing `reconstruction/` directory remains the modern replacement/runtime implementation. Its name is historical and does not imply that original assets must be excluded.

The intended architecture is:

- **original behavior/data/assets where reusable**;
- **modern replacement code/runtime where Windows 11 compatibility requires it**;
- conversion/adaptation layers where old formats or APIs are no longer practical.

## Repository placement

Intentionally imported original resources belong under:

`original_assets/`

Do not scatter source assets through `research/`, `tools/`, or `reconstruction/`.

Derived/converted resources should normally use a clear subdirectory such as:

`original_assets/converted/`

and should retain provenance back to their source asset.

## Provenance

When assets are imported, maintain a manifest that records at least:

- repository path;
- original archive/disc path;
- whether the file is byte-identical or converted;
- source SHA-256 where practical;
- conversion tool/command or notes for derived files.

This makes it possible to distinguish original FM2001 content from modernization code and generated artifacts.

## What should still stay out of Git

Even though the project is authorized to reuse the game contents, avoid committing unnecessarily large packaging/container artifacts that duplicate the useful files:

- full disc images;
- raw BIN/CUE/ISO copies;
- temporary extraction directories;
- decompiler databases;
- cache/build outputs;
- duplicate archive copies.

Extract the useful resources instead.

## Executables

The original executable may continue to be used as reverse-engineering/reference material. The modernization target is **not** to depend on the legacy executable running successfully on Windows 11.

If the executable is ever intentionally stored under `original_assets/`, document why. Prefer recovered behavior in the modern runtime over shipping a fragile legacy executable dependency.

## Fidelity goal

For player-visible behavior, the default target is:

> preserve the original FM2001 experience unless modern compatibility requires a change.

That includes startup/menu flow, music, sounds, screen structure, timing, graphics, data, and gameplay behavior where they can be recovered and reused.
