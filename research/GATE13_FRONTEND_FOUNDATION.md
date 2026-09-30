# Gate 13 Front-End Foundation

_Date: 30 September 2026_

## Scope

Gate 13 begins with the original FM2001 front end, specifically the initial
`PStartMenu` and the New Game transition into `PMain@TeamSelect`.

This checkpoint intentionally records only presentation behavior already
supported by repository evidence. It does not invent labels, graphics,
coordinates, or styling that still need to be extracted from the authorized
source archive.

## Already recovered original startup resources

Existing presentation research confirms these original disc resources:

- `FMV/easp.tgq`;
- `FMV/premintro.tgq`;
- `FMV/bground.444`;
- `FMV/Credits2.txt`.

The EA Sports and Premier League TGQ files contain their own synchronized audio.
The ordinary startup path plays the intro presentation before entering the
front end. See `research/STARTUP_PRESENTATION.md`.

Gate 13 starts at the front end after that intro path. Audio/FastView expansion
remains Gate 14 unless a specific startup dependency is required.

## Verified PStartMenu contract

The initial ordinary menu is constructed inline immediately after
`PREMINTRO.TGQ`.

Confirmed executable evidence:

- startup allocates a **0x2E0-byte** PStartMenu object;
- PStartMenu vtable: **0x7C64E0**;
- the inline constructor calls `0x4C3470` three times for three embedded
  controls;
- later front-end navigation/factory use identifies PStartMenu as screen
  **0x323**;
- navigation handler `0x47AD60` resolves a navigation record's screen ID,
  calls the generic factory at `0x47AEC0`, then registers/activates the
  resulting panel;
- PStartMenu event/control ID **2** enters the recovered New Game path
  `0x4C37C7`, which loads the runtime database and constructs TeamSelect.

The exact labels, graphics, rectangles and presentation resources for the
three start-menu controls are **not yet promoted** because they have not been
source-inventoried in this gate.

## Verified TeamSelect contract

Confirmed executable evidence:

- TeamSelect object allocation size: **0x36DC bytes**;
- constructor: **0x4D9290**;
- RTTI/vtable family: `PMain@TeamSelect`, vtable **0x7C7650**;
- control/event ID **0x29** returns to PStartMenu;
- control/event ID **0x2A** enters `0x4C41C0`, the recovered
  Start/Continue/new-game construction path;
- the embedded `Button@ease_2001` at TeamSelect **+0x3690** carries control
  ID `0x2A`;
- construction, registration, activation, idle waiting and the Start/Continue
  dispatch are deterministic with respect to the recovered game CRT stream.

This establishes the navigation contract needed by a modern presentation layer
without duplicating any simulation code.

## Application handoff implementation

`reconstruction/front_end_session.py` now owns the application boundary
between the existing presentation-only `FrontEndState` and the stable
`HumanGameplayController` backend. It does **not** implement or substitute
the missing original artwork, layout, or TeamSelect hierarchy.

- Confirmed PStartMenu New Game control `2` runs the gameplay factory
  **before** leaving the start menu. Failed canonical database loading
  leaves PStartMenu active so the failure remains recoverable.
- Team selection is initially presentation state. It does not mutate
  the backend merely because a user highlights a club.
- Confirmed TeamSelect Start/Continue `0x2A` delegates to
  `HumanGameplayController.select_club` with the explicit choice and
  returns the backend-selected manager plus the proven navigation command.
  Backend rejection leaves TeamSelect active with a retryable choice.
- Confirmed TeamSelect Back `0x29` navigates to PStartMenu and clears the
  presentation choice, without synthesizing an undocumented gameplay reset.
  A subsequent New Game event creates a new backend via the factory.
- Duplicate Start cannot submit the selected club twice within one
  handoff. Unrecovered control IDs still fail closed.
- The `FrontEndSession.for_canonical_game_dir(...)` factory connects
  the actual canonical backend lazily, avoiding simulation imports into
  the screen-state module. Tests also inject a lightweight backend.
- Only the Premier League club subset currently supported by the
  reconstructed backend is usable at this boundary. This **does not**
  claim the original multi-country TeamSelect hierarchy is complete.

This is a tested *headless application seam*, not an original-looking
presentation. Do not declare the first visual slice complete until original
assets have been inventoried, decoded/rendered and correlated with the
recovered button IDs.

## Presentation/runtime separation

The current `reconstruction/app.py` is still a temporary Tk prototype. It
builds widgets and directly calls `HumanGameplayController` from the same
module. That surface remains useful for development but is not the Gate-13
architecture target.

Gate 13 should introduce a presentation/navigation layer whose responsibilities
are limited to:

1. rendering original FM2001 resources and recovered layout;
2. preserving original control IDs/navigation/timing;
3. translating confirmed front-end actions into backend commands;
4. reading backend state for display.

Competition, transfer, finance, match, save and other simulation rules remain in
their existing backend modules.

## Authorized source status

The authorized source archive
`The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image(1).zip`
is available again as project source material.

In this recovery session the file service can materialize the archive, but the
local execution runtime cannot open the mounted ZIP bytes and the file service
does not parse ZIP contents. Therefore no new graphic/string/layout asset from
inside the archive is claimed or imported in this checkpoint.

This is a tooling/access boundary, **not evidence that the resources are absent**.
Per `research/ASSET_POLICY.md`, do not replace those resources merely because
this session cannot yet inspect them.

`original_assets/MANIFEST.md` therefore correctly remains empty until a
specific source asset is actually extracted and provenance-checked.

## Exact next task

1. regain byte-level access to the authorized archive/disc contents;
2. inventory the PStartMenu and TeamSelect resource dependencies, including the
   three PStartMenu control labels/resources and TeamSelect controls/layout;
3. identify the exact original source paths and hashes for the minimum first
   slice;
4. import only those intentionally reused resources under `original_assets/`
   and update `original_assets/MANIFEST.md`;
5. then bind the recovered control IDs/navigation contract to a presentation
   module and regression-test the first recognizably original main-menu ->
   TeamSelect flow.

No placeholder visual redesign should be promoted as Gate-13 fidelity while the
authorized originals remain recoverable.
