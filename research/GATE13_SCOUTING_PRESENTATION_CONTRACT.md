# Gate 13 PScouting2K Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes only presentation-facing facts that were already
recovered firsthand from the canonical original FM2001 executable. It does not
claim a complete Scouting screen, original captions, geometry, artwork, or
navigation.

The source executable remains the canonical SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Proven panel identity and search action

Existing executable analysis establishes:

| Item | Proven original value |
| --- | --- |
| RTTI class | `PScouting2K` |
| TypeDescriptor | `0x81C9C0` |
| Complete Object Locator | `0x7E3D20` |
| vtable | `0x7C2E6C` |
| source-path literal | `D:\Projects\FM2001\Applications\FootballManager\MenuPan.cpp` |
| event handler | `0x4ADB50` |
| search event code | **31** |
| event dispatch target | `0x4AE0FB` |
| result-vector/search routine | `0x4AE970` |
| deterministic panel-state reseed | `0x4AF7F0` |

`0x4AE970` builds the candidate vector, invokes the recovered panel-state
reseed path, and performs the source-backed deterministic shuffle. A nested
path through `0x4AEAE0` can perform the secondary vector/reseed stage.

This is a genuine original interaction anchor, but event code 31 must not be
turned into a guessed button rectangle or caption until those are independently
recovered.

## Proven result-sort dispatch

The original `0x4AEEA0` dispatch selects six qsort comparators:

| Mode | Neutral recovered input semantics | Direction | Comparator |
| ---: | --- | --- | --- |
| 0 | player name | ascending | `0x4AF020` |
| 1 | age | ascending | `0x4AF0B0` |
| 2 | six-entry match-history average | descending | `0x4AF200` |
| 3 | preferred-position display string | descending | `0x4AF270` |
| 4 | current/registered club display name | ascending | `0x4AF0F0` |
| 5 | monetary/value result | descending | `0x4AF190` |

The neutral wording above describes what the comparator reads. It is not
evidence that the original Scouting UI used those exact visible column labels.

## Reconstruction contract

`reconstruction/gate13_management_source_data.py` now exposes an immutable
`ScoutingPresentationContract` containing the panel identity, search-event
chain, deterministic reseed address and six proven sort entries.

The contract deliberately contains no:

- display-label field;
- visual control ID;
- rectangle or row geometry;
- original art path;
- font/color/alignment rule;
- screen factory ID or navigation claim.

Those omissions are fidelity safeguards, not missing defaults. Future original
Scouting presentation must add each item only when primary evidence supports it.

The existing `scouting_search_rows()` remains a separate read-only data
projection and delegates actual search behavior to the reconstructed,
source-mapped `PScouting2K` backend pipeline.

## Verification boundary

Hosted focused tests can verify that these already established constants remain
stable and that presentation code does not invent absent labels/controls.
They cannot substitute for new original-byte analysis or a Windows graphical
test.

At recovery 101, the canonical private source ZIP materializes successfully,
but trivial shell and Python execution still fail with `ClientError`.
Therefore this checkpoint makes **no new disassembly claim**.

## Gate 13 consequence

This narrows the remaining Scouting presentation gap, but does not close the
Gate 13 original-resource criterion. Original Scouting artwork, screen layout,
caption bindings, control geometry and navigation remain open alongside the
other normal-play management screens.

The source-critical next step remains the original Button/Zurich/ten-resource
first-screen audit when byte execution returns.
