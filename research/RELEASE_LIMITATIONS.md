# Release Limitations

_Pre-release working list. This file is intentionally not a Gate-17 sign-off._

The Windows 11 modernization is not ready for release yet. The final
gate17_release_readiness audit deliberately refuses this document while it
still identifies itself as pre-release.

## Current unresolved release blockers

- Gate 13 remains the earliest incomplete validation gate. The real Windows
  PStartMenu/TeamSelect graphical audit still requires an actual Windows GUI
  run with the canonical private executable/source inputs. TeamSelect hierarchy
  item/input/selection-state semantics and broader management-screen
  presentation fidelity are still incomplete.
- Gate 14 is only partly advanced. The original startup TGQ identity and the
  simulation-to-presentation match-event seam are source-backed, but original
  audio playback, converted media integration and recognizably original match
  presentation remain unfinished.
- Gate 15 still contains the active fidelity gaps recorded in
  research/FIDELITY_GAPS.md, including original save compatibility and several
  bounded simulation/finance/transfer uncertainties.
- Gate 16 now has repeated annual-regeneration soak coverage, six-seed
  complete-season stress, three consecutive fully played synthetic seasons and
  five verified internal save/reload round-trips across those seasons. It still
  lacks canonical real-data multi-season evidence, broader competition stress,
  sustained autonomous transfer churn, broader deterministic-seed coverage and
  closure of all remaining long-duration state-growth risks.
- Gate 17 does not yet have a verified installable release archive or clean
  Windows 11 installation receipt.

## Final-review rule

Before release, replace this working list with the actual limitations that
remain intentionally accepted after Gates 13 through 16 are audited. Do not
remove a limitation merely to satisfy the release tool. The final document
must describe the shipped build honestly, and the final Windows release audit
must run against the same clean repository commit and archived build recorded
in its evidence receipts.
