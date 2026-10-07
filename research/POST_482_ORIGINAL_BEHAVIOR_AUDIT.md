# Retrospective Original-Behavior Audit — Post-#482 Work

_Status: REQUIRED BEFORE FURTHER GAMEPLAY/PRESENTATION IMPLEMENTATION_

## Scope

Audit **all merged work from the reopening of Gate 13 / issue #482 through the current main HEAD**, not only the most recent PR.

The audit is retrospective because the stronger original-behavior-first policy was added after substantial work had already landed. The purpose is to determine which recent changes are genuinely source-backed, which are Windows 11 compatibility-only, which are unsupported reconstruction assumptions, and which are deferred modernization.

Do not assume a change is correct because:
- its tests pass;
- CI is green;
- it was previously reviewed or merged;
- it appears visually plausible;
- it improves responsiveness;
- it resembles an earlier reconstruction;
- another worker described it as "source-backed" without reproducible evidence.

## Required inventory

Enumerate every merged PR/commit in scope and classify each changed surface.

At minimum inspect any work affecting:

- PStartMenu / TeamSelect;
- startup FMV decoding, conversion, geometry, aspect, timing, input, skip behavior and WPF/Tk hosting;
- fullscreen/window/input compatibility;
- New Game lifecycle and loading/performance changes;
- resource loading/caching/deferred loading;
- management shell/PMenu routing;
- Squad/header/player-row content, fonts, colors, icons, z-order and state binding;
- tactics/team selection;
- fixtures/results/table/player profile/transfers/finances/messages/training/scouting presentation;
- PPreMatch/FastView/3D/match-detail routing and presentation;
- audio/music/SFX behavior;
- simulation/gameplay changes merged during the same period;
- packaging/runtime changes that alter observable behavior;
- Settings or any other non-original extension.

Pure documentation, CI, provenance and release-material changes may be classified as non-behavioral, but still enumerate them so the audit has no silent gaps.

## Classification for each item

Use exactly one primary classification:

1. **ORIGINAL-PROVEN**
   - user-visible/gameplay behavior matches direct original evidence.
2. **COMPATIBILITY-EQUIVALENT**
   - implementation mechanism differs only because of Windows 11/runtime constraints, while externally observable behavior is proven equivalent to the original.
3. **RESEARCH/INFRASTRUCTURE-ONLY**
   - no game behavior/presentation semantics changed.
4. **DEFERRED-MODERNIZATION**
   - intentionally non-original feature; must not participate in the current baseline.
5. **UNSUPPORTED**
   - implementation exists without adequate original-behavior evidence.
6. **INCONCLUSIVE**
   - evidence is insufficient or conflicting; further original-source investigation is required.

For ORIGINAL-PROVEN and COMPATIBILITY-EQUIVALENT, cite the exact reproducible evidence: executable addresses/control flow, original resource identity/layout, direct original observation, or previously established finding with valid provenance.

A test of the reconstruction is not sufficient evidence by itself.

## Mandatory questions per behavior-affecting PR/change

For every behavior-affecting change answer:

1. What did the shipped original do?
2. What exact evidence establishes that?
3. What did this change implement?
4. Does it change anything player-visible or simulation-visible?
5. Is the implementation the minimum compatibility adaptation?
6. Are any semantics guessed, approximated, or inferred?
7. Does the current test suite verify original behavior, or merely current reconstructed behavior?
8. What corrective action is required?

## Corrective action rules

- **ORIGINAL-PROVEN:** retain.
- **COMPATIBILITY-EQUIVALENT:** retain, but document why the mechanism differs and why output/semantics remain equivalent.
- **RESEARCH/INFRASTRUCTURE-ONLY:** retain if otherwise valid.
- **DEFERRED-MODERNIZATION:** isolate/disable from the normal original-baseline path; preserve for later only if it does not contaminate source reconstruction.
- **UNSUPPORTED:** do not leave it silently active. Revert, isolate, or replace with a fail-closed/unresolved boundary until original evidence is recovered.
- **INCONCLUSIVE:** no further implementation on that semantic boundary until the original is investigated.

Do not rewrite an unsupported feature into a new guess merely to make the audit green.

## Settings-specific requirement

The merged Settings extension is already known to be non-original and must be classified **DEFERRED-MODERNIZATION**.

It is not a Gate-13 completion requirement under the current freeze. Verify that:
- the original/default menu path does not depend on it;
- source reconstruction tests can exercise the original menu baseline without it;
- it is not used as evidence for original PStartMenu geometry/navigation;
- no new Settings work is performed during the freeze.

If clean isolation requires a code change, make the smallest isolation change and preserve the work for a later explicitly authorized modernization phase.

## External failures that must be reconciled with the audit

The audit must explicitly explain how recently merged claims relate to Daniel's actual Windows evidence:

- intro video still misframed/offset inside the movie field;
- Escape during startup invokes fullscreen behavior instead of original startup semantics;
- menu transitions remain extremely slow;
- fresh Southport Squad remains incomplete with blank/missing header/name content.

Any earlier merged claim contradicted by this evidence must be downgraded/corrected. Historical documents may remain, but current truth must not preserve a disproven completion claim.

## Deliverable

Create a complete audit table with, for every in-scope merged PR/commit:

- identifier/title;
- files/subsystem;
- behavioral impact;
- original evidence;
- classification;
- confidence;
- corrective action;
- correction commit/PR if needed.

Then provide a section named **Unsafe or Unproven Active Behavior** containing every item that must be corrected before another external acceptance build.

Finally provide **Audit Exit Criteria**:

- all in-scope merges enumerated;
- every behavior-affecting item classified;
- no unsupported/deferred-modernization behavior contaminates the original baseline;
- contradicted completion/status claims corrected;
- exact next source-backed Gate-13 task identified;
- focused/full tests run after any corrective changes.

Do not declare this audit complete while an in-scope behavior-affecting merge remains unclassified.
