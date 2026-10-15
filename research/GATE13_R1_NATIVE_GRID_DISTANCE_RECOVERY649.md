# Recovery649: native 5DA785 team grid coordinate distance and conditional 5112F0 factor

15 October 2026 KST. Canonical main baseline `d4217b3ae498bc1df2355e2148a221f1a175b6d9`, after reviewed PR758 source inputs. Active source WIP `worker/gate13-r1-native-grid-distance-649`; no PR yet. Shipped owner-authorized original `footballmanager.exe` length 4,714,541, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, **static source only**. No original native execution, no private executable committed.

## Precise original 5DA785..5DA8D9 scoring-distance input

Original `5DA2F0` invokes `5DA785` after the team+134..140/registered-user weighted FPU inputs and match-context+4C encounter selection. It obtains first/source team from ESI and other/source team from saved `[ESP+0x44]` (original opponent selected from match-context+28 getter at `5DA30A`). It reads signed **team+0x20 X coordinate** for each, and signed **team+0x24 Y coordinate** for each. For both axes the original uses native `IDIV 1000` and two optimized signed quotients:
- remainder (signed IDIV1000) multiplied by immediate magic **0x1B4E81B5** in `IMUL`, signed-high shifted six, with sign compensation, is **integer truncation of signed remainder / 600**;
- raw signed coordinate multiplied by immediate magic **0x68DB8BAD**, signed-high shifted twelve, sign correction, is **integer truncation of coordinate / 10000**.

The original native grid-cell coordinate equals the **sum** of those two quotients. The x and y differences between teams are computed in source x86 signed arithmetic and absolute-valued. The original then squares both differences through signed `IMUL`, adds to a signed DWORD, converts via native signed DWORD `FILD`, invokes x87 **FSQRT** and calls native **`668350`**. At 66835F the original flips x87 rounding-control bits via `OR AH,0x0C` and `FISTP QWORD` to **truncate toward zero**, restoring its previous x87 control word. Within a valid nonnegative 31-bit squared-sum domain, this yields Python `math.isqrt(sum)` exactly, not a rounded-to-nearest Euclidean distance.

Negative signed coordinate inputs follow signed truncation, *not* Python `//` floor. Example x= -600 produces cell -1; x= -1000 produces cell0; x= +10600 produces cell2. These are source-defined integer manipulations, not latitude/longitude, screen pixels or fixture scheduling coordinates.

At `5DA885`, original checks native truncated distance:
- **0** -> skip 5112F0 call and multiply two FPU inputs by original 0x7BD8F8 double **1.5**.
- **nonzero**, calls original **5112F0** on native match context; if returned AL true -> original 1.5 branch.
- AL false **and** distance exactly **1** -> original 0x7BD678 double **1.2** multiplier on both FPU inputs.
- AL false with distance greater than1 -> leaves the two FPU inputs unchanged (effective multiplier 1.0).
These factors modify pre-existing FPU match-power inputs; they are **not** a final score or an original RNG value.

The new `original_match_5da785_grid_distance.py` strictly consumes original native two-team pointers and exact team+20/+24 signed records, including independent saved opponent pointer from native `5DA7FB [ESP+44]`; rejects pointer alias, wrong source records, fixed-width coordinate-square overflow (source undefined/unsupported signed FILD sqrt), forged original 5112F0 return, or a 5112F0 return when the original zero-distance branch bypasses it. It returns exact projected grid differences/squared sum/truncated distance and **unexecuted** multiplier decisions, never native score mutation or GameState output.

Unit coverage checks signed positive/negative edge inputs, magic quotient equivalence against independently computed truncating signed divisions including INT32 boundaries, x/y 3-4-5 distance and √18 truncation, original source constants + modifiers, source pointer and overflow errors. Private original PE **17 exact opcode sites and 2 direct calls PASS**, plus original doubles 1.2 and 1.5. These tests are registered in focused Gate13 workflow, but **new module/test exact-head CI is not yet run** on the WIP branch.

## Next concrete original-world dependency, not yet resolved

At `5DA8D9–5DA967`, native `5DA2F0` allocates temporary QWORD output slots, zeros each explicitly, calls **40CBC0** with two QWORD output pointers and actual scoring team context. Then `5DA96C` reads the produced QWORD; if equal to 0.0, it jumps to `5DAC05`. Otherwise `5DA995` builds native 5E43B0 and 5E48D0 source transformations from the other output before reaching score/event callback code. The two outputs from **40CBC0** must be source-mapped and stored to original match-world semantics before classifying an actual score/goal event. Do not treat an integer grid distance or 1.2/1.5 adjustment as the result of original 5DA2F0.

The normal game is still the reconstructed one-human Quick Match with mode0/1/2 explicitly fail-closed. 513010 native match calculation, v38/v3c save updates, 4A7210/6168C0 dual-calendar actual event writers, 432505 original return, true 2–6 human registry, all original leagues and physical Windows11 GUI acceptance are not source-complete. Gate13 and Gates14–17 OPEN. Source-first but prioritize real player-visible integration once 40CBC0 score path qualifies; no micro CI/PR unless this slice forms a coherent reviewed milestone.


## Recovery649 follow-on: original 40CBC0 type 0x1A event-strength double pair, not invented match RNG

Further private canonical disassembly `40CBC0..40D01C`
traced actual **source dispatch by team category
DWORD team+0x14**, not a single generic rating
function. At native `40CBD4` subtracts 0x18
from this type and bounds-checks 0x31 entries
through private original selector table
`0x40CFC0`; the branch for type **0x1A**
selects `40CBF2` through index1 in native
jump table `0x40CFA0`. Other type tags
including 0x18,0x1F,0x21,0x28,0x42,0x49
follow DIFFERENT source branches and may not
safely be treated as the same team category.

The type0x1A branch gets an actual key pointer
from original `team+0x10`, calls `4056D0`,
`4056F0` and `4FA520` on the reached source
container, then dispatches returned source
enum 0..4 via exact pointer table `40CFF4`.
The original QWORD output at first arg `[EBP+8]`
is global original constant from respectively
`822040/822050/822060/822070/822080`
= **30.0,20.0,16.0,12.0,9.0**. Each case
then sets second arg `[EBP+0xC]` to
**first × 0.75**, reading the authentic
global double **0x7BD558 = 0.75**. Those
two QWORD outputs are the same source output
pointers passed by `5DA8E7..5DA967`,
subsequently read at `5DA96C` and
`5DA987`. This is a *calculating-input
branch*, not a final match result.

New `original_match_40cbc0_type1a_pair.py`
accepts source team+0x14 category exactly
0x1A, verifies reached original team+0x10
lookup-pointer identity and independently
supplied native `4FA520` enum 0..4, and
returns exact two original QWORD factors
and source jump case. It marks all callbacks
unexecuted and disallows inferring scores.
Other original team categories and unsupported
selector values **fail closed**, not default
to the type1A factors. Companion unit tests
cover all five original cases, wrong
team-category/owner inputs and original
opcode/tables/doubles and no native GUI
or mutable world claims.

Independent raw-byte original PE audit
**13/13 opcode sites**, five original
40CFF4 direct native pointer values, and
all six original constants PASS. Added
source module/tests to focused Gate13 workflow.
The earlier grid distance source helper's
**17 original PE opcode** sites also PASS.
New Python modules are source-derived but
still await exact PR-head CI; no native
original process execution or Windows11
acceptance has been claimed.

**Next high-impact source steps:** trace
other commonly reached team+0x14 branches
through 40CE09/40CF31 for 0x42 and native
5DA96C→5E43B0→5E48D0 QWORD event score
transformation; bind actual 513010/5DA2F0
team+20/+24 distance + genuine 40CBC0
factors to persistent original match world
and per-mode presentation effects. Current
portable one-human Quick3 match remains
non-equivalent and original PResults
dual-date source callback seam is not live
GameState. Gate13–17 OPEN. User-approved
milestone batching: do not force minor
standalone CI merges.


## Recovery650 continuation: full category 0x42 stages and first true score-context sink

Canonical source 40CBC0 team+14 **0x42** dispatches to 40CE09. Four
**separately reached** 4056D0/4056F0/4FA520 lookups (40CE09,
40CE83, 40CEDA, 40CF31) can repeatedly overwrite output QWORDs.
The first branch selector0..4 writes first 20/16/12/9/9, second×.75
(the last two selectors share entry 40CE69). Stage2 selector0/1
overwrites with 15/10, stage3 selector0/1 with 17/12. Finally the
40CF31 selector0..4 overwrites with (30/20/16/12/9)*0.5 and
second=first*.75; selector greater than4 leaves *previous* QWORD
bytes unchanged. Original caller 5DA8D9 zeroed both QWORD slots
before entering 40CBC0. We must not infer all four 4FA520 results
are constant; original callbacks can be revisited and per-stage
source identities remain independent. Existing broad
`original_native_40cbc0_all_paths` conservatively requires
same original source category on every call; the new strictly
bounded `original_match_40cbc0_type42_stages.py` accepts actual
per-call independent source values, forbids caller-invented
nonzero initial QWORDs, preserves previous write on later
source no-op, and never claims native callbacks executed.
Both models are source projections, not substitutes for
executing the original 4056F0/4FA520 linked event world.

More importantly, original `5DA9A1` constructs 5E43B0,
`5DA9A8` calls 5E48D0, and at **5DA9AD** stores the
calculated QWORD input at temporary stack+38. At **5DA9B3**
the original checks source 4037B0 registered team.
For a human-managed team, original `403850` chooses its
original registered user, reads user+0x694 pointer and
DWORD+0x0C, then **5DA9E4** writes that raw integer
to **original match-context (EBP+0xC)+0xD88**. The
source also computes signed FILD(user+694+0x0C) MINUS
the source 5E48D0 QWORD, keeping the difference in
temporary stack+0x30. For a non-managed team, the
original `5DA9EC` loads the source QWORD and
**5DAA00→668350** truncates to an integer; **5DAA05**
writes it to *the same context+0xD88*. This is
the first proved concrete mutable output field in
the full 5DA2F0 scoring pathway. It is not
necessarily the final public home/away score:
later 5DAA0B onward original source FPU,
RNG/world and stage work still executes.

`reconstruction/original_match_5da9ad_first_d88_sink.py`
now accepts the existing source-type
`OriginalScoredStageFreshCallbackSource` (5E48D0
first stage), previously registered full-club-key
`OriginalMatch4037B0TeamOwner`, exact
native match-context record+0xD88, and
human user+694 pointer/body when original
human branch is reached. It projects
per-source write destination, raw native managed
int32 or qualified nonhuman truncated score
factor, human FPU difference QWORD and
explicit **NO native callback/NO GameState mutation**.
It rejects forged source stage/manager identity,
invalid source human owner links, integer overflow,
unvisited fields and corrupt source records.
Tests cover both branch values/negatives,
real 13 native PE opcode site signatures and
source raw manager+694+0C integer reads.
The real mutable GameState equivalent of
context+0xD88 has not yet been source-linked
to `HumanGameplayController`/SaveLoad, so
do **not** write reconstructed match scores
from this bounded DTO.

**Important source reuse audit:** prior main already includes
`original_native_40cbc0_all_paths.py` for general
eight-branch coefficient QWORD stores and
`original_match_40cbc0_5e48d0_b_join.py` for
all four source stage input slots. These were
reviewed before adding the new first-stage D88 sink.
Do not create a second generic 40CBC0 engine or
overwrite these existing comprehensive models.
The narrow 0x42 callback-drift test is a
qualification of the prior conservative same-
category restriction, not proof of actual dynamic
native category changes.

**Unfinished:** a true source-backed native
5DA2F0 calculator must now recover the subsequent
5DAA0B..5DB1xx stages and 5DBCD0/5DBA60
before persistent match event worlds, result
screens, all modes or Gate13 can be accepted.
All tests on this WIP need exact-head CI; the
original executable has never run.
