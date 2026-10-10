# Gate 13 R1 match-phase integration checkpoint — 11 October 2026 KST

## Original behavior and evidence used

The bounded source contract comes from the canonical executable evidence already
recorded in Recoveries 471, 474, 483, 484, 487 and 490:

- a qualified human match remains owned by `PResults` / `LeagueMatch::0x513010`;
  ordinary management input cannot escape while that owner is active;
- `PPreMatch` opens when settings owner `0x875680` is null **or** mode global
  `0x877530` is sentinel 5;
- source button event 1 selects mode 3 Quick Match before calculation;
- mode 3 takes shared preparation `0x632B20`, skips only the presentation wrapper,
  and still reaches the common post-view callbacks and normal `0x432505+` return;
- PResults progress is driven by processed qualified events and uses
  `10 * trunc(80 * count / total)`, with total zero producing width zero.

The football meaning and exact clean-room effect of original context bytes
`+0x1145/+0x1150` remain unknown. The port therefore records the proven mode
preparation branch but does not invent a score/RNG adjustment.

## Reconstruction defect corrected

The normal host previously released all input ownership after the NEXT worker
published a pending human entry. A repeat NEXT could enter the mutable Side
selector, and MENU / Return / Squad / Fixtures input could leave the unresolved
match. The normal host also had no player-operated PPreMatch-to-calculator path.

## Minimum integration now implemented

- Public `advance_original_management()` refuses a pending match before the
  mutable Side selector.
- One central host owner blocks every background pointer route while PPreMatch or
  PResults owns the match.
- The exact modal predicate retains settings-owner `unknown` separately from
  known absent/present state; native sentinel 5 remains represented by no mode.
- The existing verified 800×600 PPreMatch resources are loaded off the Tk thread.
  The host draws only source-verified background, static, badge, selector-atlas and
  Zurich-caption layers; unresolved children are omitted rather than guessed.
- The four exact source rectangles accept their recovered events. Only explicit
  event 1 / mode 3 can enter the present R1 calculator; modes 0–2 fail before
  simulation until their true renderers and preparation effects are integrated.
- Quick mode 3 calculates exactly once on a staged controller, publishes an
  immutable real-event progress receipt, commits atomically, retains common
  postmatch completion, returns to the same management session, and permits the
  next NEXT action.
- Pending state still round-trips through the existing internal save codec. This
  is not a claim that original MENU Save child `0x321` exists.

## Verification and remaining acceptance boundary

Focused local run: **176 tests passed** across front-end session, Match Detail
source routing, PPreMatch source facts, original management turn, original host
and internal save. A smaller end-to-end fake-host test proves NEXT → pending
modal owner → physical Quick rectangle → one calculation → event progress →
management return → NEXT again. No GitHub Actions run was dispatched.

R1 is **not yet VISIBLE-ACCEPTED**. The normal Windows 11 path has not been run
against the authorized original installation in this checkpoint. The partial
PPreMatch still omits unresolved child pixels, and the host intentionally retains
the last source-owned frame during PResults because a complete source-backed
PResults pixel/resource contract is not yet present; it does not fabricate a
progress screen or clickable waiting strip. Gate 13 and Gates 14–17 remain open.

