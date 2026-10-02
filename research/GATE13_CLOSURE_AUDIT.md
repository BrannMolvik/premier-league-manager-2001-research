# Gate 13 Closure Audit

_Audit date: 2 October 2026 KST_
_Last reconciled after Recovery 175 schema-6 PMenu audit integration._

## Decision

**Gate 13 remains active.** The earlier generic-ttk handoff blocker is now
closed: normal `app.py` launch enters the source-backed fixed 800x600 host,
PStartMenu/TeamSelect are live, and a successful TeamSelect Start enters the
source-proven `PMenu -> PSquadScreen` management state.

Gate 13 still cannot pass because the ordinary-management canvas deliberately
draws no guessed management pixels, the original control-acceptance boundary is
not yet mapped far enough to equate ordinary Tk clicks with native accepted
events, and the source-backed Squad/Fixtures/PMatchInfo/League Tables presenters
are not yet one playable visual loop. The post-acceptance title/child callback
itself is now source-bound and integrated through an explicit fail-closed seam.

This audit remains criterion-driven. It does not require every obscure panel or
every neutral bit name before Gate 13 can close.

## Roadmap criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Simulation logic remains separated from presentation | **PASS** | `GATE13_PRESENTATION_SEPARATION_AUDIT.md`, `ManagementSourceDataBridge`, `OriginalManagementPresenter`, and the source-backed first-screen/management hosts keep simulation mutation behind controller/session boundaries. |
| Accessible original resources and recoverable layout/navigation are reused or converted | **PARTIAL - required work remains** | First-screen, PMenu, Squad, League Fixtures, PMatchInfo, League Tables and Scouting resources/contracts are source-bound and many are provenance-imported. Normal launch now uses the source-backed host, but the management canvas still cannot compose the unresolved surrounding background, exact PMenu text placement or a complete source-backed Squad view. |
| Main-menu/login presentation, structure, navigation and timing closely follow the original | **PARTIAL - close to sufficient for Gate 13** | PStartMenu -> TeamSelect -> MANAGEMENT is integrated with native first-screen resources, hierarchy population, club selection, Back/Start behavior and the fixed PMenu/Squad parent geometry. The Recovery-175 schema-6 Windows harness covers the default clean host, preserves ordinary Tk PMenu clicks as candidate-only, and separately verifies the source-accepted callback seam, but a new real Windows 11 schema-6 receipt is still pending. |
| Normal play feels recognizably like FM2001 rather than a generic replacement UI | **FAIL** | The default host no longer falls back to the ttk notebook, but after Start it intentionally presents a blank 800x600 management canvas because source management pixels are incomplete. Candidate PMenu hit-testing is geometry-only and cannot yet navigate. |

## Closed since the earlier audit

The following blockers from the original closure audit are now closed:

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
   can project PSquadScreen (`0xCE`), PLeagueFixtures (`0x25C`) and
   PLeagueTables (`0x25A`) without importing simulation logic.
5. **PMenu pointer containment:** the live diagnostic and clean hosts now expose
   the geometry-proven candidate visible row under the pointer while explicitly
   dispatching **no** navigation.
6. **Post-acceptance PMenu action contract:** Recovery 173 source-closed the
   concrete row callbacks and Recovery 175 integrated them through a visible-row
   guarded seam. Title actions can change the expanded root without changing the
   current panel; supported child actions route transactionally into the existing
   management presenters. Ordinary Tk clicks are still not treated as accepted
   source events.
7. **Windows audit contract:** schema 6 now tests the developer viewer and the
   default clean host through New Game -> native club click -> Start ->
   MANAGEMENT, preserves real Tk PMenu clicks as non-activating candidates,
   and separately exercises the explicit source-accepted Calendar/Fixtures/
   TABLES/League Tables action seam. It requires zero guessed management
   PhotoImages and explicitly declines to claim Tk-event equivalence. The
   schema-6 contract is repository-verified; its real Windows execution is
   still pending.

## Required before Gate 13 can pass

The smallest sufficient remaining closure slice is now:

1. **Recover enough management pixels to render the fresh landing recognizably.**
   Source-bind the remaining PMenu text origin/clipping and application-owned
   management background/chrome needed for the visible PMenu/Squad landing.
   Reuse the already imported PMenu/Squad resources; do not introduce a
   substitute skin.
2. **Recover the source control-acceptance/event-equivalence boundary.** The
   post-acceptance row callback and supported panel dispatch are now integrated,
   but candidate rectangle containment alone is still not evidence that a Tk
   click is an accepted native event. Trace the original control acceptance path
   far enough to bind pointer/keyboard input without guessing.
3. **Compose one ordinary management loop in the clean host.** The user must be
   able to move through the source-backed Squad/tactics -> League Fixtures ->
   PMatchInfo/result -> League Tables path while gameplay mutations continue to
   flow through the reconstructed backend rather than presentation code.
4. **Run the integrated route on real Windows 11.** Execute the schema-6 audit
   (and extend it as the management loop becomes interactive) against the
   canonical local install and preserve the bounded receipt outside Git.

A collection of presenter snapshots or diagnostic status strings is not enough
to satisfy the normal-play criterion.

## Current blockers

### Private/native evidence blocker

The current ChatGPT execution sandbox still fails before process start with
`caas.internal.errors.ClientError`, including a trivial shell probe in
Recovery 172. The authorized source ZIP remains recoverable from the private
Library, but the unavailable process sandbox prevents a fresh executable trace
for:

- exact PMenu label origin/clipping;
- any application-owned surrounding management background layer not already
  persisted;
- original PMenu control acceptance and its pointer/keyboard event equivalence.

This is an infrastructure blocker, not a user-action blocker. Do not infer the
missing behavior from appearance or modern UI conventions.

### Local Windows validation boundary

Hosted Linux CI verifies the audit contract but cannot produce a real Windows
Tk receipt. A new schema-6 local Windows 11 run remains required before the
expanded clean-host graphical result is claimed.

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
- PMatchInfo `info_popup.444` staging: complete;
- League Tables 15-file staging: complete;
- `PLeagueTables+0x7FC..+0x97C` identity: closed as seven `eCText` stat
  headings with exact sort-state transforms.

## Immediate implementation boundary

Until the process sandbox recovers, continue only independent cloud-safe work
that improves the already-proven management path without inventing native
behavior. Highest-value examples are:

- keep the clean host, management presenter and Windows audit contract aligned;
- integrate source-backed panel composition only where source geometry/state is
  already sufficient;
- make all unresolved management pixels and activation semantics fail closed;
- prepare tests/audit coverage so fresh private evidence can be integrated
  immediately when execution is available.

When private execution recovers, the priority trace is the exact PMenu
text-origin/clipping and source control-acceptance/event-equivalence path,
followed by any still-needed application-owned background ownership evidence.
