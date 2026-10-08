# Original Squad row-drop producer

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Implementation evidence gate: PSquadScreen virtual +14 is `4B9350`, following
the row-name drag retained by +10 `4B8E70` in +CC. The reconstruction omitted
this producer entirely. The minimum repair is its transactional selection/role
producer, followed by the already-qualified `4B7500` refresh, not click-to-toggle,
a dropdown, scrolling, automatic bench filling or formation-slot reassignment.

`4B9692..4B999F` handles populated drops. Both players pass `41FA50` (a loan
ownership guard, NOT injury checking). The target's original XI/reserve/bench
kind and role/aux are retained. `406BE0` / `406DF0` receives literal role **one**,
excluded pointer **null** (`4B973D/3F`). Its result writes original esp+14:
the +1C store is under two pushed arguments, NOT the retained aux at esp+1C.
For first XI count eleven, zero existing role-one players and dragged role one,
`4B97DF..F3` forces role one/aux zero. Clearing
the target runs `4181B0`; its new kind comes from the dragged player's still-live
selection. For XI this copies the dragged current role/aux; for bench it resets
to preferred role. The dragged player then receives the retained target kind
and role/aux (or preferred reset). Finally the two +244 roster words swap,
and `4B8C50` refreshes ordering. Setter transitions through reserve XI swap
the retained +152/+153 bytes, so these must not be lost in a Python flag swap.

`4B9486..4B9673` handles actual empty-row owners. It preserves dragged role/aux
for XI, rejects the exact occupancy == capacity test and loan guard, and uses
the retained raw row index and translated target index for its first/reserve
branch. Bench/clear resets preferred role. The native comparisons themselves
are authoritative; do not replace equality with >= or infer a modern drop zone.

Pointer ownership comes from `4B8DB0` / `4B8E00` -> `4B6DF0`: half-open actual
row rectangles, plus the count of preceding native empty owners. Null player
lookup slots are not empty owners. `4B56B0 -> 4B7FD0/6510F0` retains width226,
y154, minimum row height17; vtable `7C5AF4` +A0/+A4 -> `4466E0/446710` takes
max(native row height16, minimum17). The source panel y79 and parent origins
37/418 apply; stats cells are outside this player drag owner. Press excludes
strict interiors (67,107) / (448,488); shirt-number drag is x<67 / x<448.
Drop retains full player-row bounds. Empty-target pane classification uses the
translated index >=20, not an invented pane test. Cursor rendering and the
human match-input bridge remain separate required acceptance boundaries.

The existing confirmed participant producer `510CD0` (see `FINDINGS.md`,
"Match participant construction and runtime selection flags") walks +244
roster order and tests `417F50/417F60`. It does not zip human players to the
AI formation table or rerun an AI selector. Native Squad match preparation
must therefore retain actual current role/aux and filter already-live flags.
The prototype's `current_selection -> _prepare_human_selection` presently
clears selection and reassigns formation-table slots; that is the defect fixed
by a read-only native branch. Existing complete XI/bench, ownership,
availability and Non-EU validation remains conservative/fail-closed; this
change does not claim to recover every native pre-match acceptance warning.
The subsequent exact ordinary advance trace corrects one over-strict adapter
guard: `PBg` vtable `7BEE8C` +10 -> `432690` receives the embedded
`NextGameBtn` (+524), registered with event 3 at `430995..9B1`, and calls
`432190`. At `43226E..277` the next-match checks call `407FE0`, whose
`407FF4..7FFD` invokes `407C00` with argument **0**. `407C00` first requires
selected/eligible substitute counts to match and checks `418050` per selected
player; at `407CAD..CD1`, argument 0 bypasses the exact-quota branch and
returns **selected substitutes <= 408500 quota**. Argument nonzero is the
separate exact-quota case. Thus the primary read-only bridge must accept an
eligible underfilled bench, not manufacture players or require the maximum.
The same chain calls `407770(1)`; `4077C4..7FDB` tests native role-one
occupancy ==1. Retain this goalkeeper guard along with complete XI/ownership,
availability and Non-EU guards. The ordinary advance control itself is not
yet integrated: tomorrow-match warning/acceptance and day/UI lifecycle still
need binding before claiming user-visible normal play.
Native role bytes/flags and ordered roster already survive schema48, so no
new save schema or synthetic report context is required.

Four hundred deterministic bounded comparisons execute actual `4B9486` /
`4B9692` state CFGs, setter/role-byte helpers and +244 roster-word writes.
They compare every player's selection/current/retained reserve bytes, order,
acceptance and first-active setter calls, including self-drops and empty owners.
Ownership/count/capacity leaves are explicit primary test inputs, not a native
process or proof of otherwise-unqualified live loan contexts.

## Live integration verification

The default paired host's press/release callbacks now bind the row-name state
producer and native membership refresh. Source shirt-number/role-column
boundaries and modal/changed-owner/outside-release guards are covered.
Canonical Southport and Liverpool filled their three initially empty bench
owners (without autofill), retained XI11/bench5 through disk save and fresh
process reload, and retained every roster ID in paired presentation. The
withdrawn Windows/Tk test drove public `on_click/on_script_arrow_release`
callbacks with verified source resources; all 30/35 players and all image
bounds passed inside 800x600. This is not external mouse/normal-launch/audio
acceptance. Southport's fresh reload advanced to its 2000-08-19 Conference
fixture and returned `HumanPrimaryMatchdayOutcome`, then saved. Complete
captured-report publication/rendering for that procedural fixture is not
claimed by the calculation check.

323 integrated focused tests passed (17.966s); the added disk-roundtrip
regression also passes (24 row-drop tests / 0.436s).
Full regression ran 3,026 tests / 291.933s / 18 expected skips, with the same
three failures and one error in the disjoint Gate17 complete-package-lock
digest checks. Full-suite green is not claimed; the added disk-roundtrip
regression was verified separately after full-suite discovery.

Private script SHA-256:
`qualify-squad-row-drop.py`:
`c70cd99f4196bb7a4c376b953ac4566461af2a293c7a0bf1d26eec345f5cc593`;
`verify-native-row-route.py`:
`902633acea1d4737f5ade87b0edfd6497b2be06b14d44a7dd374c22a4f8fb635`;
`verify-native-paired-tk.py`:
`80a9a4aef32ad33b3c004c921b4bc8d5457a37686dbc32b1d6617c7ae3f17fad`.

Native drag-cursor rendering and ordinary host advance/pre-match acceptance
remain required; no new hands-on build or Gate13 completion is claimed.

Secondary/loan-list side effects and shirt-number drag (`+D0`, `4B9A10`) remain
outside this bounded primary row-name producer. No original process is needed
for the bounded canonical-function comparison; private dumps/emulation receipts
remain outside Git. This is not a new Windows normal-launch acceptance claim.
