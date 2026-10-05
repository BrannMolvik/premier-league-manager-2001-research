# Release Limitations

_Pre-release working list. This file is intentionally not a Gate-17 sign-off._

The Windows 11 modernization is not ready for release yet. The final
`gate17_release_readiness` audit deliberately refuses this document while it
still identifies itself as pre-release.

## Current unresolved release blockers

- Gate 14 is the earliest incomplete validation gate. The match presentation
  consumes reconstructed match state/events without duplicating simulation
  logic and remains separated from core management play. Source-backed progress
  includes retained PlayerRow dynamic-energy and English text pixels, multiple
  FastView component rasters, parameterized score/team nested construction,
  GoalFlash relative row/formatting behavior, ScoreCompositeMain outer
  ownership, four embedded outer-control registrations, the native packed-16
  font blend rule, canonical BNK bank ownership/playback entrypoints and sample
  decoding, plus chant selection/timing. Normal Windows startup media and the
  bounded first-screen `AudioHooks (10,0) -> menus.bnk slot 2` press route are
  integrated. Strict external Windows 11 acceptance tooling exists for both and
  PR #462 can run the two human-confirmed checks transactionally, but neither
  private external receipt exists yet. The current release blockers are broad
  semantic/application-wide audio binding and login/menu integration; those two
  real-Windows acceptance receipts; complete score/team nested pixels;
  GoalFlash absolute timing/position and raster pixels; ScoreCompositeMain
  geometry/content/pixels; the four embedded controls'
  geometry/resources/state/pixels; complete global FastView
  ordering/flattening; chant event semantics; source-backed SCI/3D choreography;
  source navigation into FastView; and final recognizable-original match
  workflow verification. The authorized private source archive can be
  materialized, but current shell and notebook execution fail with
  `caas.internal.errors.ClientError`; no missing source semantics are inferred
  from that infrastructure failure.

- Gate 15 remains a work-ahead fidelity sweep. The active ledger is
  `research/FIDELITY_GAPS.md` and the current reconciliation is
  `research/GATE15_READINESS_AUDIT.md`. Remaining bounded items include the
  exact secondary-startup tie/bucket shape, fully indistinguishable native
  league-table qsort ties, original PLM2001 save compatibility, residual player
  negotiation branches, same-day transfer ordering, the remaining special Cup
  receipt caller/applicability boundary, and finance/board residuals. Gate 13
  presentation residuals deliberately deferred by the completed Gate 13 are
  now Gate-15 fidelity backlog items. Gate 14's still-open roadmap criteria
  remain prerequisites rather than limitations that Gate 15 may accept away. Deterministic fallbacks and
  fail-closed behavior must continue to be labeled honestly until every final
  item is fixed, proven irrelevant, or explicitly accepted in the final audit.

- Gate 16 completion criteria are already prevalidated by committed work-ahead,
  including six deterministic synthetic seeds, destructive annual regeneration
  and save-growth soaks, five years of autonomous transfer churn, mixed
  shared-primary competition stress, and two independent canonical shipped-data
  seeds that each completed three annual qualification/regeneration cycles.
  Gate 16 is intentionally not marked complete while Gates 14-15 remain open.
  When those prerequisites close, the relevant full suite must be rerun and
  `research/GATE16_READINESS_AUDIT.md` reconciled against the then-current
  runtime rather than repeating already-proven stress work now.

- Gate 17 has substantial release-audit and packaging infrastructure, but the
  release target is still blocked by both repository-side full-scope capability
  and external Windows evidence. The current full-scope preflight remains
  fail-closed where shipped functionality is not yet present, including the
  source-proven six-simultaneous-human-user requirement and procedural-secondary
  TeamSelect scopes that still lack a distinct live runtime owner,
  human-continuation/save serialization path, and complete owner-correct
  continuation capability. Other full-scope owner/objective/progression
  blockers remain whatever the canonical preflight reports at final validation;
  they must not be bypassed by hand-edited receipts. After all Gates 1-16 are
  actually complete, Gate 17 still requires one final archive/version/commit to
  pass a real external Windows 11 client-workstation clean install, the three
  gameplay receipts, a separate `full_original_scope.json` receipt covering
  every originally selectable/playable league/country and required career
  systems, and the final release-readiness audit. Hosted CI and Windows Server
  do not substitute for those external receipts.

## Final-review rule

Before release, replace this working list with the actual limitations that
remain intentionally accepted after Gates 14 through 16 are audited. Do not
remove a limitation merely to satisfy the release tool. Every Gate-15 ledger
row finalized as `accepted_documented` must be carried here using its exact gap
name, followed by a meaningful user-facing explanation; fixed and
`proven_irrelevant` rows are not release limitations. The final document must
describe the shipped build accurately, and the final Windows release audit must
run against the same clean repository commit and archived build recorded in its
evidence receipts.
