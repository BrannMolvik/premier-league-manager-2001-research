# Squad drop re-audit — 9 October 2026 KST

## Evidence gate before changing production

Original: populated row-name release4B9350 ->4B9692 retains target kind/role/aux,
uses the appropriate First/Reserve role-one and selected-XI counts, then may
force retained target role1/aux0 before assigning it to the dragged player.
Both native paths4B9743/4B97BA reach guard4B97D2..F3. It requires zero role-one
players on the TARGET side, exactly11 selected on that side and dragged role1.

Defect: `original_squad_row_drop.py` restricts the guard to target_kind4 (First
XI), despite handling target_kind2 (Reserve XI) in the same source branch.
Minimum repair: remove that First-only restriction and use the target kind for
the selected count. Keep setter order, reserve-byte swaps, roster word swaps,
role ordering, ownership guards and pointer geometry unchanged.

Canonical exe SHA256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Independent audit followed actual control flow and executed the original state
CFG/setters. Primary agent independently reran its counterexample. Full N30,
quota5, FirstXI11/bench5, ReserveXI11/bench3 is used, not merely an N12 fixture
whose upstream preparation would clear reserves. Actual4B7500 orders First
goalkeeper id11 at0 and Reserve target id0 at16. Native dragged id11 becomes
Reserve role1/aux0; the port instead retains target role2/aux3. Other compared
bytes agree. This is not established as Daniel's screenshot's cause.

## Caller and input qualification

Current ordinary paired host stores the source player/index and membership on
press, maps the release through `original_squad_row_at_point`, rejects changed
owner/modal/outside cases and calls `HumanGameplayController.drop_original_squad_row`.
The controller validates live IDs/kinds/roles against retained membership.
`GameState.drop_original_primary_squad_row` rejects secondary/loan contexts,
supplies actual current role/aux/reserve bytes and applies4B7500 ordering after
the transaction. With full first bench, source index0 maps left slot0 and target
index16 maps right slot0. The correction requires no synthetic UI field/input.

The arranged unit fixture covers that full-bench boundary, but the actual
production-loader test also reaches it from unchanged fresh Southport using
only three ordinary public host press/motion/release gestures:

1. Reserve GK S. Dickinson -> empty First bench row13. Reserve XI falls to10,
   First bench rises to3; the actual empty Reserve XI owner is row10.
2. Unselected D. Morley -> that Reserve XI owner. Reserve XI returns to11,
   with zero current role-one players. No direct state arrangement is used.
3. First GK B. Stewart -> Reserve M. Clark (right row0). The original guard
   executes. Stewart becomes Reserve role1/aux0; Clark becomes First role1/aux0.

Actual Windows/Tk public callbacks at 1x and 1.5x retain all30 IDs and match
native selection/current/aux/reserve bytes after every drop. Physical and
normalized coordinates, retained indices, player IDs and post-drop rows are
recorded privately. Disk save and a separate Python process reload retain all
bytes, order, row locations and human starter/substitute IDs at each scale.
This is test-owned withdrawn Tk, not physical mouse or visible acceptance.

Independent native ordering/slot execution reproduces the same three gestures,
boundaries19/18/18, ordinary empty owners and final player locations. Native
fresh startup itself is not observed: initial inputs are the canonical-data
adapter's retained fresh Southport records.

## Unknowns and acceptance status

SOURCE-VERIFIED: bounded primary/no-loan guard and counterexample. The expanded
264-case adversarial matrix executes actual ownership/selection predicates,
First/Reserve counts, role occupancy/capacity initialization and the state
CFG/setters/roster writes:264 matches,16 guard hits, no mismatches. Cases include
same-XI and self-drop, count10/11/12, source kinds, roles and auxiliary bytes;
count12 is an injected guard boundary, not ordinary post-ordering reachability.
Quota408500=5 and first-active side-effect qualification417340=true remain
explicit fixture leaves. The three-gesture ordering harness executes actual
4B7500/4B6FE0, with its getter/refresh predicate fixtures recorded privately;
it is not all of4B8C50's formation/UI side effects. Dense emulator IDs are a
bijection of live IDs, not a different roster. Independent reviewer:
independent_squad_contract; primary agent reran the264 matrix.
INTEGRATION-VERIFIED: the bounded corrected guard, live owner refresh and disk/
fresh-process persistence at1x/1.5x; no loan-list setter side effect is claimed.
VISIBLE-ACCEPTED: no; Daniel's exact multiple-mouse-move report is unreplicated.
No broader drop/cursor/shirt/loan/pre-match acceptance is inferred.

Regression: three new tests failed before the repair; all passed afterward.
Final focused Squad/host/gameplay/save suite:276 tests/46.359s, all passed.
Asset policy passed. Completed full reconstruction recheck at8f31fe5e:
3,101 tests/339.633s/25 expected skips; three failures and one error, all in
the already recorded disjoint Gate17 complete package-lock digest checks
(`test_gate17_ffmpeg_toolchain_provenance`). No additional failure, no waiver
or Gate17 changes. The full suite is NOT green; no Gate13 completion claimed.

Private scripts remain outside Git:
`work/independent-drag-audit/verify-reserve-role-one.py`,
`verify-first-drop-and-gaps.py`, `audit-guard-matrix.py`,
`audit-native-gesture-sequence.py`, and `work/verify-reserve-guard-ordinary-ui.py`.
Private receipts and saves remain outside Git; older delivered folders/user
saves are untouched. Receipts SHA256 at verification:

- 1x: `2245fa9af2a3a70e967e56489f142582884e996544c0c20392e33fab3c0249f3`
- 1.5x: `499264067fedc6e326541b4c548f88bbb755cab75097991bbc0df70b41d19d24`

Final receipts use production-module SHA256
`4376f731051e9f80b63761c1030cab875548bf1e90c87f27aa7a731ed8cd3a14`.
Actual30 populated Tk background owners/90 cell items and bounds were inspected
after every drop. Empty owner lists are paired-presenter data, not separate
Tk empty-pixel reads; source text/name projection is not an all-pixel proof.
