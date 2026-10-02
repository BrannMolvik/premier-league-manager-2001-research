# Gate 13 Closure Audit

_Audit date: 2 October 2026 KST_

## Decision

**Gate 13 remains active.** The source recovery is substantially ahead of the
integrated runtime presentation, but the current application still enters the
generic ttk Play tab for ordinary management. That surface is explicitly a
prototype and does not yet make normal play recognizably FM2001.

This audit is intentionally criterion-driven. It does not require every
unresolved executable detail or every obscure original panel before Gate 13 can
pass.

## Roadmap criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Simulation logic remains separated from presentation | **PASS** | `GATE13_PRESENTATION_SEPARATION_AUDIT.md`, the read-only management bridge, and the first-screen, Squad, League Tables and PMatchInfo presenters keep simulation imports outside presentation modules. |
| Accessible original resources and recoverable layout/navigation are reused or converted | **FAIL - required work remains** | Exact first-screen, PMenu, Squad, Fixtures, PMatchInfo, League Tables and Scouting resources/contracts exist, but several are not composed into the live ordinary-management surface. The generic prototype therefore remains the effective replacement for normal play. |
| Main-menu/login presentation, structure, navigation and timing closely follow the original | **PARTIAL - not yet a gate pass** | The corrected Windows 11 PStartMenu -> TeamSelect audit passes with native resources, hierarchy population, selection and Back/Start behavior. A successful Start still hands off to the generic prototype instead of the source-proven PMenu -> PSquadScreen route. |
| Normal play feels recognizably like FM2001 rather than a generic replacement UI | **FAIL** | `reconstruction/app.py` still identifies itself as a prototype and uses ttk notebook/tree controls for ordinary management. Source-backed presenters do not yet form one integrated playable management path. |

## Required before Gate 13 can pass

The smallest sufficient closure slice is one complete, source-backed normal
gameplay path:

1. TeamSelect Start must enter the source-proven `PMenu` shell and fresh-user
   `PSquadScreen` landing instead of stopping at a backend handoff message.
2. The live management canvas must compose the already recovered PMenu chrome,
   Zurich text, Squad row/view controls and original resources without a modern
   substitute skin.
3. That path must navigate through the core ordinary loop needed to manage and
   play a fixture: Squad/tactics -> League Fixtures -> PMatchInfo/result ->
   League Tables, using the existing read-only bridge and action boundary.
4. A real Windows/Tk audit must exercise the integrated route, verify original
   resource dimensions/state transforms, and prove that gameplay actions still
   use the reconstructed backend rather than duplicated presentation logic.

The exact implementation may be incremental, but a collection of disconnected
presenter snapshots is not enough to satisfy the normal-play criterion.

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

- a standalone Manager Home panel: superseded by `PMenu -> PSquadScreen`;
- first-screen Windows validation: passed in Recovery 164;
- PMenu four-file binary staging: complete;
- PMatchInfo `info_popup.444` staging: complete;
- League Tables 15-file staging: complete;
- `PLeagueTables+0x7FC..+0x97C` identity: closed as seven `eCText` stat
  headings with exact sort-state transforms;
- cloud/private process-start failure: not a blocker in the current Windows
  Codex environment.

## Optional polish

- exhaustive reconstruction of every non-core menu branch before the first
  integrated management path exists;
- animation/state semantic labels not required to reproduce the proven frame
  transform;
- screens or resources known only from filenames without executable ownership;
- styling changes motivated by modernization rather than original evidence.

## Immediate implementation boundary

Continue with the PMenu -> PSquadScreen integrated presentation seam. Reuse the
already imported PMenu/Squad resources and current Squad presenter. The next
private trace should be limited to evidence genuinely needed to compose that
route, especially remaining PMenu text origin/clipping and visible-row
expansion behavior. Do not restart closed first-screen or League Tables work.
