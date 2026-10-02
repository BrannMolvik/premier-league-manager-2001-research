# Gate 13 Closure Audit

_Audit date: 2 October 2026 KST_  
_Last reconciled during Recovery 181 after the canonical Squad/Fixtures/PMatchInfo/League Tables visual-loop and schema-8 audit integration._

## Decision

**Gate 13 remains active.** Normal `app.py` launch uses the fixed 800x600
source-backed host, PStartMenu/TeamSelect are live, TeamSelect Start reaches the
original PMenu management route, ordinary PMenu pointer presses are source-
backed, and the clean host now renders recovered PMenu row pixels instead of an
intentionally blank management canvas.

Recovery 181 advances that state substantially. The clean host now renders the
fresh PSquadScreen top controls, the exact 36-position League Fixtures grid,
the exact 760x500 `info_popup.444` PMatchInfo background through the recovered
pointer-origin clamp, and the exact League Tables header band. The schema-8
audit now walks this source-backed bitmap stack through Squad -> League Fixtures
-> explicit source-accepted PMatchInfo -> exit -> League Tables and verifies the
live Tk PhotoImage dimensions against independently derived source geometry.

Gate 13 still cannot pass yet. The expanded schema-8 contract has not been run
on real Windows 11/Tk, the source-proven PSquadScreen first+formation /
reserve+formation transition is not yet integrated as a normal modern pointer
path, ordinary fixture-cell -> secondary linked-context PMatchInfo opening
remains unbridged, and the application-owned surrounding management background
is still unresolved. Keyboard equivalence remains unproven and fail-closed; it
is not itself required for Gate 13 closure.

This audit remains criterion-driven. It does not require every obscure panel,
secondary screen, or neutral bit name before Gate 13 can close.

## Roadmap criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Simulation logic remains separated from presentation | **PASS** | `GATE13_PRESENTATION_SEPARATION_AUDIT.md`, `ManagementSourceDataBridge`, `OriginalManagementPresenter`, and the clean host keep gameplay mutation behind controller/session boundaries. The PMenu/fixtures renderers consume snapshots and decoded original art only. |
| Accessible original resources and recoverable layout/navigation are reused or converted | **PARTIAL - narrow required work remains** | First-screen, PMenu, Squad, League Fixtures, PMatchInfo, League Tables and Scouting resources/contracts are source-bound in substantial part. The fresh Squad controls, Fixtures grid, PMatchInfo popup background and League Tables header are now live. Remaining required work is the bounded Squad/formation interaction needed for the representative normal path plus any management-shell pixels actually necessary for recognizability; unresolved secondary art stays fail-closed. |
| Main-menu/login presentation, structure, navigation and timing closely follow the original | **PARTIAL - Windows refresh pending** | PStartMenu -> TeamSelect -> MANAGEMENT is integrated with native assets, hierarchy population, club selection, Back/Start behavior and fixed management geometry. Recovery 177's real Windows schema-7 receipt proves the earlier pointer route. Recovery 181 extends repository schema 8 across live PMenu plus Squad/Fixtures/PMatchInfo/League Tables bitmap geometry; a fresh real-Windows schema-8 run is required before this criterion is current for the rendered path. |
| Normal play feels recognizably like FM2001 rather than a generic replacement UI | **FAIL - close to re-audit** | The default host no longer falls back to the ttk notebook or a blank PMenu. It now renders original PMenu rows, fresh Squad top controls, exact League Fixtures grid, exact PMatchInfo popup background, and exact League Tables header. The remaining question is whether the bounded source-backed Squad/formation interaction plus unresolved surrounding shell are sufficient on the real Windows path; that judgment is deferred to the updated graphical audit rather than claimed from hosted CI. |

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
12. **Fresh Squad top-control pixels:** PR #117 integrates the exact three
    73x25 source frames plus Zurich caption masks at screen origins
    **(37,171)**, **(113,171)** and **(189,171)**.
13. **League Tables source-backed header:** PR #118 renders exact
    `league_bar.444` at **(270,152,475,19)** while unresolved row-state art
    remains fail-closed.
14. **PMatchInfo global popup geometry:** PRs #119/#120 source-close the pointer
    clamp and project only the globally valid **760x500** `info_popup.444`.
15. **PMatchInfo clean-host modal seam:** PR #122 persists that popup through
    redraws, keeps ordinary unbridged fixture/context opening fail-closed, and
    exposes a separate source-accepted exit seam.
16. **Panel-aware schema-8 contract:** PR #123 verifies the live source bitmap
    sequence for Squad -> Fixtures -> explicit PMatchInfo -> League Tables and
    records the unreconstructed secondary context instead of overclaiming it.

## Required before Gate 13 can pass

The smallest sufficient remaining closure slice is:

1. **Close the bounded Squad/formation interaction seam.** The exact
   PSquadScreen control IDs and first+reserve / first+formation /
   reserve+formation container transitions are already source-proven. Integrate
   only the transition that can be supported without inventing unresolved
   formation/player pixels or claiming unproved modern pointer equivalence.
2. **Validate the representative clean-host management loop on real Windows.**
   The repository contract now covers Squad -> League Fixtures -> explicit
   source-accepted PMatchInfo/result -> League Tables. A real Windows 11/Tk
   receipt must confirm the rendered path before recognizability is judged.
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
then. Recovery 181 keeps repository schema **8** but expands its exact
PhotoImage contract across PMenu rows, fresh Squad controls, League Fixtures
grid art, the source-accepted PMatchInfo popup, and the League Tables header.
The expanded schema-8 real Windows run is pending and must be refreshed again
if required panel pixels are added before closure.

## Current verification

Latest relevant canonical verification:

- PR #122 full reconstruction run `37009547601`: **1,379 tests**,
  **22 expected skips**, pass;
- PR #123 Gate-13 presentation run `37010700467`: **479 tests**,
  **21 expected skips**, pass;
- PR #123 repository asset-policy run `37010700447`: pass.

These hosted results validate the source/audit contract. They are not a
substitute for the pending real Windows 11/Tk schema-8 receipt.

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

1. integrate the smallest source-accepted PSquadScreen first+formation
   transition from the already-proven controls 3/4/5 contract without inventing
   unresolved formation/player pixels or modern pointer equivalence;
2. keep ordinary fixture-cell -> secondary-context PMatchInfo opening and
   owner-local PMatchInfo child transforms fail-closed unless separately proved;
3. run the expanded schema-8 audit on real Windows 11/Tk;
4. re-audit the Gate-13 roadmap criteria, including whether the unresolved
   surrounding management background is still a closure blocker once the
   source-backed normal path is viewed on Windows;
5. if every criterion passes, close Gate 13 and immediately continue Gate 14.
