# Gate 13 Closure Audit

_Audit date: 2 October 2026 KST_  
_Last reconciled during Recovery 179 after live PMenu composition and the source-proven League Fixtures grid integration._

## Decision

**Gate 13 remains active.** Normal `app.py` launch uses the fixed 800x600
source-backed host, PStartMenu/TeamSelect are live, TeamSelect Start reaches the
original PMenu management route, ordinary PMenu pointer presses are source-
backed, and the clean host now renders recovered PMenu row pixels instead of an
intentionally blank management canvas.

Recovery 179 also re-recovered the canonical authorized source through
`research/ORIGINAL_SOURCE_LOCATOR.md`, reverified the six PLeagueFixtures
graphics byte-for-byte, provenance-imported them, and integrated only the two
grid families whose 36 screen-space placements are exact. The four fixture-box
assets remain intentionally unrendered because their screen-pixel placement is
not yet source-closed.

Gate 13 still cannot pass because the source-backed Squad/tactics ->
League Fixtures -> PMatchInfo/result -> League Tables path is not yet one
recognizable usable visual loop, the application-owned surrounding management
background is still unresolved, and the new management pixels have not yet
passed an updated real-Windows audit. Keyboard equivalence remains unproven and
fail-closed; it is not itself required for Gate 13 closure.

This audit remains criterion-driven. It does not require every obscure panel,
secondary screen, or neutral bit name before Gate 13 can close.

## Roadmap criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Simulation logic remains separated from presentation | **PASS** | `GATE13_PRESENTATION_SEPARATION_AUDIT.md`, `ManagementSourceDataBridge`, `OriginalManagementPresenter`, and the clean host keep gameplay mutation behind controller/session boundaries. The PMenu/fixtures renderers consume snapshots and decoded original art only. |
| Accessible original resources and recoverable layout/navigation are reused or converted | **PARTIAL - required work remains** | First-screen, PMenu, Squad, League Fixtures, PMatchInfo, League Tables and Scouting resources/contracts are source-bound in substantial part. PMenu row art/fonts are live, and the source-proven League Fixtures grid art is now imported/integrated. Remaining required work is the smallest source-backed Squad/tactics, PMatchInfo/result and League Tables visual composition plus any management-shell pixels actually needed for recognizability. |
| Main-menu/login presentation, structure, navigation and timing closely follow the original | **PARTIAL - Windows refresh pending** | PStartMenu -> TeamSelect -> MANAGEMENT is integrated with native assets, hierarchy population, club selection, Back/Start behavior and fixed management geometry. Recovery 177's real Windows schema-7 receipt passes Calendar -> League Fixtures -> TABLES -> League Tables through actual Tk presses. Recovery 179 adds source-backed PMenu pixels and upgrades the repository audit contract to schema 8; a fresh real-Windows schema-8 run is required before this criterion is treated as current for the rendered path. |
| Normal play feels recognizably like FM2001 rather than a generic replacement UI | **FAIL - improving** | The default host no longer falls back to the ttk notebook or a blank PMenu. It now renders original PMenu rows and the exact League Fixtures grid when that panel is selected. The fresh Squad landing and the representative management loop still lack enough integrated source-backed panel pixels/interaction to satisfy this criterion. |

## Closed blockers

The following earlier blockers are closed and must not be reintroduced:

1. **Default launch path:** normal `app.py` launch uses
   `OriginalGameTkHost`; the generic ttk notebook is explicit
   `--prototype-ui` only.
2. **TeamSelect Start handoff:** a valid native club selection reaches
   `FrontEndScreen.MANAGEMENT` and creates the source-proven fresh
   `PMenu -> PSquadScreen` presenter.
3. **Fixed management geometry:** the live management host preserves the exact
   **800x600** surface, PMenu **(599,96,201,504)** and fresh PSquadScreen
   **(0,79,800,520)**.
4. **Source-backed management routing model:** `OriginalManagementPresenter`
   projects PSquadScreen (`0xCE`), PLeagueFixtures (`0x25C`) and
   PLeagueTables (`0x25A`) without importing simulation logic.
5. **PMenu pointer acceptance:** both concrete whole-row SelectBmp controls use
   the recovered `0x64F7A0` press path, half-open 201x29 bounds and concrete
   row callbacks. Matching Tk `<Button-1>` presses use that seam.
6. **PMenu title/child actions:** title expansion and supported child-panel
   navigation are source-closed and integrated transactionally.
7. **Exact PMenu row text geometry:** title and child captions use the
   source-bound `Zurich_XCn_BT_25pixel.fnt` / `Zurich_XCn_BT_16pixel.fnt`,
   local line origins **(30,1)** / **(30,17)** and half-open clip rectangle
   **(30,0)-(198,29)**.
8. **Static PMenu row visual state:** title/child background state, title arrow
   expansion state, child selected/unselected state, and native black/white
   label endpoints are source-backed.
9. **Live PMenu pixel composition:** merge `57e3342` composes the four exact
   imported row atlases plus native font masks in the normal clean host. It
   deliberately does not fill unrecovered surrounding pixels.
10. **Existing pointer-route Windows validation:** Recovery 177 schema 7 passed
    on real Windows 11 with receipt SHA-256
    `6e1a43e01a43ccbf7bfe92c3088ee446c40a92d51add3ba9660f20cb76f0bef2`.
11. **League Fixtures source-byte availability:** Recovery 179 reverified the
    canonical 511,121,336-byte source ZIP, its canonical executable and all six
    PLeagueFixtures graphics. The six exact assets are now provenance-imported;
    the vertical/horizontal grid families are rendered only at their 36
    source-proven placements.

## Required before Gate 13 can pass

The smallest sufficient remaining closure slice is:

1. **Make the fresh management landing recognizable.** Integrate the
   source-backed Squad/tactics pixels and controls that are already recoverable.
   The unresolved application-owned background may remain a bounded gap only if
   the resulting normal landing is still recognizably FM2001 and no substitute
   pixels are invented.
2. **Complete one representative clean-host management loop.** The user must be
   able to move through a source-backed Squad/tactics -> League Fixtures ->
   PMatchInfo/result -> League Tables path while gameplay mutations continue to
   flow through the reconstructed backend.
3. **Keep unrecovered details fail-closed.** In particular, do not place the
   four 24x13 League Fixtures cell resources until their screen placement is
   source-proven, do not guess unresolved Squad icons/text styling, and do not
   enable PMenu keyboard activation without native evidence.
4. **Keep real-Windows coverage aligned with rendered pixels.** Schema 8 is the
   repository contract for live PMenu pixels. Extend it with each required
   management-panel visual slice and obtain a fresh real-Windows receipt before
   Gate 13 closes.
5. **Re-audit every ROADMAP criterion after the representative loop is live.**
   Presenter snapshots or diagnostic status strings alone are insufficient.

## Current evidence boundaries

### Application-owned surrounding management background

PMenu itself has a negative direct resource-ownership result. Recovery 179 also
reverified the immediate application owner around `0x4C2FB0`: it constructs
PMenu and places it at **(599,96,201,504)** but does not bind a new PMenu-
specific image in that bounded owner path. This does **not** prove that the
whole management screen has no background; any wider application-owned layer
still requires its own owner/resource trace.

The canonical **800x600** `FM2001_Art/Generic/bground.444` must not be reused
here merely because its dimensions fit. Persisted evidence binds it to startup/
front-end loading, not to the ordinary management shell.

### Keyboard equivalence

Ordinary pointer presses are source-backed and integrated. Native PMenu keyboard
event equivalence remains unproven, is disabled/unclaimed, and is not a Gate-13
blocker unless later evidence makes it part of the required normal path.

### Real Windows validation

Recovery 177's schema-7 receipt remains valid for the pointer route that existed
then. Recovery 179 added PMenu PhotoImages and the repository audit contract is
now schema **8**, requiring those images to match the exact live row
composition. A real Windows schema-8 run is pending and must be refreshed again
if required panel pixels are added before closure.

## Current verification

For the live PMenu compositor merge `57e3342`:

- Gate-13 presentation run `36998507566`: **453 tests**, **21 expected skips**, pass;
- full reconstruction run `36998507518`: **1,363 tests**, **22 expected skips**, pass;
- repository asset-policy run `36998507581`: pass.

The League Fixtures asset/grid integration must pass its own branch validation
before being merged and counted as canonical.

## Validly deferred to Gate 15

- exact Current Form row ordering at `0x4F4A10`;
- fully indistinguishable native sort ties;
- unresolved Squad status-icon and club-relative assignment meanings;
- pixel-perfect behavior for secondary Player Profile, Transfer, Finance,
  EAMail, Training and Scouting subpanels after their recognizable shell and
  normal navigation exist;
- rare/legacy controls and loaded-but-unconsumed resources;
- exact semantic names for neutral native state bits where the executable only
  proves their transforms.

These may remain fail-closed or explicitly neutral during Gate 13; they must
not be replaced by invented behavior.

## Gate 14 work, not Gate 13 blockers

- login/menu audio;
- match audio, video and match-view presentation;
- TGQ playback/conversion behavior;
- match presentation beyond the management-side Fixtures/PMatchInfo route.

## Stale or superseded blockers

- standalone Manager Home panel: superseded by `PMenu -> PSquadScreen`;
- generic ttk Play tab as normal launch path: superseded by
  `OriginalGameTkHost`;
- TeamSelect Start backend-only handoff: superseded by the live MANAGEMENT host;
- first-screen Windows validation: passed in Recovery 164;
- PMenu four-file binary staging: complete;
- PMenu label origin/clipping: complete;
- ordinary PMenu pointer activation: complete;
- PMatchInfo `info_popup.444` staging: complete;
- League Tables 15-file staging: complete;
- League Fixtures six-file staging: complete in the current Recovery-179
  integration checkpoint;
- `PLeagueTables+0x7FC..+0x97C` identity: closed as seven `eCText` stat
  headings with exact sort-state transforms.

## Immediate implementation boundary

Continue the smallest source-backed representative management loop. Prefer
already imported resources and persisted geometry/state over additional native
tracing. Use private executable/source tracing only where a concrete required
pixel or action remains genuinely unresolved.

Immediate order:

1. finish/verify the League Fixtures grid checkpoint;
2. render the smallest source-backed fresh Squad/tactics slice without guessing
   unresolved row fonts/icons;
3. expose the already source-bound PLeagueFixtures -> PMatchInfo dialog path and
   render its exact imported dialog resources/placements;
4. render the source-backed League Tables header/body art that can be selected
   without inventing unresolved row-state semantics;
5. extend schema 8 for that representative loop and run it on real Windows;
6. re-audit Gate 13 and, if every criterion passes, close it and immediately
   continue Gate 14.
