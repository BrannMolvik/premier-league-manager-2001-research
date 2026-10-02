# Gate 13 Windows first-screen graphical audit

_Date: 1 October 2026 KST_

## Purpose

The PStartMenu/TeamSelect source slice now has exact original backgrounds,
action atlases, PStartMenu Zurich captions, native Button group mapping,
proven action rectangles and 16 TeamSelect hierarchy row origins. Synthetic
and source-byte tests do not prove that the actual Windows graphical path
opens and routes these recovered inputs correctly.

`reconstruction/gate13_windows_first_screen_audit.py` is the fail-closed
real-Windows/Tk audit for that gap. It is deliberately narrower than a Gate-13
completion audit.

## What a passing run proves

The command:

- refuses non-Windows execution;
- loads the canonical original executable and first-screen resources through
  the existing checksum-gated loaders;
- creates the real Tk developer viewer with an unscaled **800x600** canvas;
- verifies the live Tk `PhotoImage` dimensions match the source-backed
  PStartMenu composition;
- renders source frame 11 through the real Tk path and verifies the recovered
  group-1 `0x0000` PStartMenu caption endpoint;
- drives the actual Tk `<Button-1>` binding through **Start New Game ->
  TeamSelect -> Back**;
- verifies the TeamSelect live Tk images include the two proven action
  controls plus the two independent hierarchy source-strip previews;
- clicks a source-position-proven hierarchy row and requires it to remain
  inert, because row identity/event semantics are still unresolved;
- clicks TeamSelect Start without a selected club and requires fail-closed
  rejection rather than an invented selection;
- writes a bounded JSON receipt **outside Git** and refuses to overwrite an
  earlier receipt.

The receipt explicitly records `gate13_complete: false`.

## Canonical private run

Use the same independently verified original source/executable path as the
other first-screen source audits. Example:

```text
python reconstruction/gate13_windows_first_screen_audit.py ^
  --original-exe "<private-footballmanager.exe>" ^
  --original-art-root "<private-staging>/FM2001_Art" ^
  --original-language-root "<private-staging>" ^
  --original-font20 "<private-staging>/Fonts/Zurich_BdXCn_BT_20pixel.fnt" ^
  --canonical-game-dir "<verified-installed-game-data-directory>" ^
  --output-receipt "<private-folder-outside-Git>/gate13-windows-first-screen-audit.json"
```

The original executable must still hash to:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The source loaders also re-check every relevant imported original against its
pinned SHA-256 before Tk opens.

## Evidence boundary

A passing receipt closes the **real Windows first-screen graphical smoke**
item. It does not recover TeamSelect hierarchy item identity, native hierarchy
selection/frame semantics, hierarchy captions, or the remaining management
screens. Those facts must still come from canonical executable/resource/direct
graphical evidence.

## Canonical Windows 11 result (Recovery 138)

The audit passed on the real local Windows 11 path on 1 October 2026 after
re-verifying the authorized ZIP and executable and extracting the four
checksum-locked gameplay inputs into private staging. The first attempt failed
closed because that staging directory lacked `FOOTBAL.EXE`; adding the already
verified canonical executable closed the backend dependency and the unchanged
harness then passed.

Verified runtime facts:

- platform `Windows-11-10.0.26200-SP0`, Python 3.12.14, Tk 8.6.12;
- DPI awareness requested successfully;
- all four PStartMenu caption/image overlays matched the live Tk dimensions at
  source frames 0 and 11, with the proven `0xFFFF`/`0x0000` text endpoints;
- real Tk New Game reached TeamSelect and real Tk Back returned to PStartMenu;
- the two TeamSelect action images and two hierarchy source-strip previews had
  their exact expected live dimensions;
- unresolved hierarchy input remained inert and Start without a selected club
  was rejected.

The bounded private receipt remains outside Git and has SHA-256
`b61d56dde7fc3ee7d25451cc993f545c28217cb28347a05921d379efe932e9b4`.
No screen dump, executable, disc image, or raw proprietary data is committed.
This closes the Windows first-screen graphical smoke item, not Gate 13.

Hosted CI only tests the audit contract and fail-closed receipt rules. It
cannot substitute for this real Windows run because the licensed executable is
not present in hosted CI and the hosted Gate-13 job is Linux/headless.

## Exact follow-on work

After the real Windows receipt passes:

1. trace TeamSelect hierarchy control input/state data flow from the already
   proven constructor row origins and source art;
2. bind only directly proven country/league/club item identities and events;
3. integrate those semantics into the first-screen presenter/viewer;
4. rerun the Windows graphical audit with hierarchy behavior no longer inert;
5. continue the remaining Gate-13 management-screen resource/layout/navigation
   correlations before considering Gate 14.

## Corrected Windows 11 result (Recovery 164)

The current schema-3 audit passed on 2 October 2026 using the normal Windows
installation at Python **3.13.15**, Tk **8.6.15**, platform
`Windows-11-10.0.26200-SP0`. It exercised the corrected TeamSelect hierarchy:
13 default English country/competition rows, 20 F.A. Premier League clubs,
country clear, competition repopulation, canonical clicked-club identity,
ACTIVE frame 11, deselection, and Start rejection with no selected user.

The receipt is private at
`windows-first-screen-audit-recovery164.json` outside Git. All inputs were
loaded through checksum-gated source loaders; the executable remained canonical
SHA-256 `833bf95e...cc3`. This supersedes the obsolete inert-hierarchy portion
of Recovery 138 while retaining `gate13_complete: false` for broader management
presentation.


## Recovery 172 schema-5 clean-host audit contract

The audit harness now extends beyond the developer viewer and explicitly
exercises the default `OriginalGameTkHost` used by normal `app.py` launch.

The schema-5 run must:

- create a fresh clean-host session in a real Tk window;
- drive New Game through the clean host;
- click the first source-backed native TeamSelect club row;
- drive TeamSelect Start into `FrontEndScreen.MANAGEMENT`;
- require the exact fixed **800x600** canvas;
- require PMenu **(599,96,201,504)** and fresh PSquadScreen
  **(0,79,800,520)** with panel code **0xCE**;
- require **zero management PhotoImages** while the surrounding management
  background and exact PMenu text placement remain unresolved;
- click inside the proven PMenu rectangle and require candidate-row feedback;
- require that candidate feedback dispatches **no** navigation and leaves the
  selected PSquadScreen panel unchanged.

Hosted Gate-13 CI verifies this contract but cannot produce the Windows result.
The new schema-5 local Windows 11 receipt remains **pending**. The prior
Recovery-164 schema-3 receipt remains valid evidence for the corrected
first-screen path, but it does not prove the new clean MANAGEMENT host.
