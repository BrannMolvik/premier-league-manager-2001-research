# Gate 13 PScouting2K Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This contract promotes only presentation-facing facts recovered firsthand from
the canonical original FM2001 executable and exact authorized source assets.
It does not claim a complete Scouting screen, original captions, the unknown
surrounding background, remaining controls, result text, row semantics, or
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

## Proven source-resource composition

Recovery 120 correlated two exact whole-disc resources to
`PScouting2K::0x4AB150` and provenance-imported them:

| Resource | Source SHA-256 | Proven decoded geometry | Proven placement |
| --- | --- | --- | --- |
| `FM2001_Art/business/scouting/background_alpha_1.444` | `e69a94edd9814860e796ab1bb4e58a3381584efda8bad704b8c65eebbb58d899` | 571x16 | x=207, 20 rows y=192..515 step 17 |
| `FM2001_Art/business/scouting/background_2.444` | `3bc5e1a8ba9c91a75905786f969aad83bca61891ebd7e4aca40a78165a95e503` | 295x45 | (206,543) |

`reconstruction/original_scouting_resources.py` now enforces those exact
hash/geometry identities and builds only this proven transparent composition
fragment. It fails closed on wrong dimensions or non-color-key partial alpha.
It deliberately does **not** fill in the rest of the Scouting screen.

## Reconstruction contract

`reconstruction/gate13_management_source_data.py` now exposes an immutable
`ScoutingPresentationContract` containing the panel identity, search-event
chain, deterministic reseed address and six proven sort entries.

The read-only data contract still deliberately contains no guessed display
label, visual control ID, font/color/alignment rule, screen factory ID or
navigation claim. Exact background-art paths and composition rectangles live in
the separate source-resource module above because those facts are now proven.

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

Recovery 120 supplied the successful local Windows byte trace that proved the
resource ownership/geometry above. Recovery 123's cloud worker still returns
`ClientError` before process start, so no additional Scouting controls or
captions are inferred beyond that persisted evidence.

## Hosted verification

The contract was verified on PR #35 head
`96cf4c7fbf95cb86af261f4e0289104493db7b85`:

- Gate-13 focused workflow `36767384902`: **219 tests**, **19 expected
  original-source-gated skips**, zero failures;
- full reconstruction workflow `36767384882`: **1,055 tests**, **21 expected
  original-source-gated skips**, zero failures;
- repository asset-policy workflow `36767384938`: passed.

PR #35 was then squash-merged to main as
`5a4224e651b4b4a7051eb3afe1e5f4b8d8aff44e`.

These hosted runs verify reconstruction integration and the fail-closed
presentation contract. They do not execute the private licensed original bytes
or constitute a Windows graphical smoke test.

PR #47 then verified the imported-resource composition implementation on head
`2ba43f19ed29e16a609f20d03eeacef6790cf342`:

- Gate-13 focused workflow `36814179046`: **249 tests**, **20 expected
  source-gated skips**, zero failures;
- repository asset-policy workflow `36814179303`: passed.

PR #47 was squash-merged as
`757e8fec77f688bab893e155fee0bb82eaa97b6f`.

## Gate 13 consequence

This narrows the remaining Scouting presentation gap, but does not close Gate
13. The two proven art fragments/placements are implemented; the surrounding
Scouting presentation, caption/control bindings and navigation remain open.
The active cross-screen resource step has moved to Squad ownership correlation,
followed by the real Windows graphical/normal-play audit.
