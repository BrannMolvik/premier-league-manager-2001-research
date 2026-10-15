# Recovery642: 5DB37C four scored stage QWORD totals → nonhuman match context

15 October 2026 KST. Canonical main `318f981666be13dfa14394ff1eaceeab906d57b5` (PR752 safely merged, exact-head Gate13 2,044 tests/186 skipped and asset policy SUCCESS); Gate13 and Gates14–17 remain OPEN. Source private original disc-root `footballmanager.exe`: 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, independently checked and statically disassembled only, not executed/committed.

## Original 5DA8E7–5DA923 zero-initialized four stage results

At original 5DA8E7/E8 two `PUSH`ed coefficient output pointers temporarily shift stack by eight bytes. Therefore original paired DWORD zero stores 5DA8EB/F3 correspond to post-call stage1 QWORD `[S+60..67]`, 5DA8FB/903 stage2 `[S+58..5F]`, 5DA90B/913 stage3 `[S+68..6F]`, and 5DA91B/923 stage4 `[S+50..57]`, where S is the actual native ESP restored after 40CBC0's `RET 8`. If original x87 stage guard skips a stage and there are no aliased side effects, its direct QWORD result remains **zero**; reject supplied altered skipped slots rather than assuming other results. This is separate from 5DA92B/933 B parameter initialization corrected in PR752.

## Native x87 668350 integer return and pair order

At `5DB37C`, original calls `668350` at `5DB380` for stage3 QWORD `S+68`; then `5DB38B` for stage1 QWORD `S+60`; `ADD EBX,EAX` at 5DB394 creates **EBX = (low32(trunc(stage3)) + low32(trunc(stage1))) mod 2^32**. It calls `668350` at `5DB39A` for stage4 `S+50` then `5DB3A5` for stage2 `S+58`, with `ADD EDI,EAX` at `5DB3AA` creating **EDI=(stage4+stage2) mod2^32**, and copies EDI to native `[S+18]` at `5DB3AE`. Independently verified original `668350` temporarily saves x87 CW, sets truncating RC=11, FISTP signed64, restores original CW and returns low EAX (high EDX unused here). Nonfinite/overflow signed64 conversion does not receive invented values and is deliberately rejected.

Human callbacks, a source local byte flag, and selected user+694 may modify first component and emit native 5DC510 side effects; the pair is **PRE-human**, not a final score, context or event count.

## Only reached nohuman + source flag zero direct context

Source `5DB3B2 CALL 4037B0` original human predicate false branches `5DB3BD JE 5DB4CF`, then original `[S+0xF] == 0` makes `5DB4D1 JE 5DB6FA`. No human selected user+694 and no native 5DC510 callback on this direct path. Native `5DB6FC` writes EBX to its local QWORD lower half, `5DB704` reads ECX from saved `[S+18]`, and `5DB70F–726` computes total and writes original native match processing-context **D84 = (EBX+ECX) mod 2^32**, **D8C=EBX**, **D90=ECX**. Existing `original_native_5db6fa_context_tail.py` independently sources nonzero component suffix D94=2, D98=2, D9C=4; use it without inventing FPU zero/NaN behavior.

New `original_match_four_stage_integer_totals.py` source reads actual stage QWORDs and independently supplied booleans; new `original_match_nonhuman_stage_context_join.py` joins the two nonzero components to existing original context receipt with actual pointer identity and nohuman/flag0 evidence. Both outputs explicitly `original_native_executed=False` and `live_game_state_updated=False`. Nine locally executed targeted unit tests PASS, including original canonical PE opcode bytes for every initialization, 668350 call, ADD and the two exact nohuman branch displacement targets. Register on focused Gate13 workflow. This is bounded source proof, **not** real GameState, SaveLoad, normal NEXT→PPreMatch all modes→PResults→management, original graphical acceptance or Windows11 release.

NEXT: resolve original human/flag-nonzero branches at 5DB3C3..5DB6F5 (native 5DC510, two manager user+694 fields, first-side score adjustment), then stage QWORD producers and original FPU ratio; integrate actual native scoring callbacks/side/context into live GameState with original ordinary player lifecycle. Continue on same unopened branch until a cohesive feature milestone for PR/CI. PR739 high-risk injury state remains separate/unmerged.

## Further original first-side HUMAN branch source obligation (Recovery642)

The first-side human path must **NOT** be replaced by the direct nonhuman
context join plus `user+694[0]`. Native `5DB3C3` selects human branch when
the first-side 4037B0 source gate is true and `[S+0xF]==0` (different
route if flag nonzero). Reached `5DB450/5DB4B3` reads selected
`user+0x670` and calls **5DC510 twice**, each taking a distinct native
constructed argument and source state. Only **after** both does `5DB4BE`
get `user+694` and `5DB4C4 ADD EBX,[ECX+0]` before jumping to 5DB6FA.
The native 5DC510 itself has nontrivial effects: original 5DC586
`FADD QWORD [ESI+0x10]`, 5DC599 `FSTP QWORD [ESI+0x10]`, calls native
5DC650 at 5DC5D4, and calls **617D70 event/record queue** at 5DC63A.
It pushes and restores EBX, ESI, EDI and returns `RET 0x24`, consistent
with EBX preserved across this call, but state/event effects are NOT.
The separate second-side 5DB5F0/5DB692 reached callback calls are also
not part of the false-4037B0+flag0 direct branch. PE identity tests
for original two first-side callsites, EBX bonus, 5DC510 mutable owner
and 617D70 queue have been added. Until exact native 5DC510 payload,
recipient and event lifetime are joined to GameState/SaveLoad, source
projection must fail closed on these human/alternate paths. The nohuman
route label means `4037B0(ESI)` is false and the native flag is zero;
do **not** assume it proves every possible other participant is AI.

**Next:** source trace native 5DC510 received argument layouts and
5DC650→617D70 payload and record ownership, plus all three original
5DB4D7+ alternate branches; then actual GameState/player-visible
R1 flow. No native execution, full original career, GUI or Win11
acceptance claimed.

## Native nested 5DC650 state and event path (Recovery642 continued)

The original `5DC510` caller invokes `5DC650` at 5DC5D4 **before**
its own `617D70` at 5DC63A. New independent disassembly of original
`5DC650..5DC887` shows two conditional flow families selected from
native EDI argument at 5DC672: nonnull target at 5DC680, null target at
5DC768. Both perform `5E48D0` QWORD source comparisons with
`FNSTSW AH bit0x1` guard; *each* may return early without an event
when an independently source-required pointer is null (5DC6A8 / 5DC790).
Otherwise 5DC6E3–E7 or 5DC7D5–D9 performs original
`FSUBR QWORD [ESI]` then `FSTP QWORD [ESI]`, where
`ESI=EBX+0x10` and `EBX` is the selected 5DC650 original state owner.
It may allocate a 0x20-byte record and then `5DC86B CALL 617D70`
with an allocated data-link pointer or null if allocation fails.
Source `5DC887 RET 0x28` establishes this callback's cleanup.
There is **no source-safe blanket claim** every 5DC650 call queues
a substantive event, nor proof the resulting first-side state can be
reconstructed simply by an EBX score adjustment. Exact original argument
constructor values, FPU status/NaN/error cases, alternate recipient and
queue side effects still require integration evidence. A new optional original
PE regression checks source direct path, both early exits, mutable
ESI-owner stores, and queue call. This is static source proof only.

## Original 617D70 queue order and owner linkage

A further original-disassembly verification of the shared `0x617D70`
called after the 5DC510/5DC650 callbacks establishes an **ordered
intrusive doubly-linked tail append**, not immediately a rendered Inbox
notice or finalized match event. Its `ECX` is the original queue-owner
object; `[ECX+0x8]` is the current tail pointer and `[ECX+0x4]`
is the head pointer. Argument `[ESP+4]` is the new linked node.
For nonempty queue, `617D7B` writes **oldtail+4=newnode**,
`617D7E` clears **newnode+4=0**, `617D88` writes
**newnode+8=oldtail**, and `617D8B` updates **owner+8=newnode**.
For empty queue, `617D91/94` sets both **owner+8=owner+4=newnode**
and `617D97/9E` clears both newnode links. `RET 4` consumes
the one node argument. Original PE bytes were checked independently
for both branch families; a read-only optional original-PE regression
was added.

The two native 5DC510 callback calls are meaningful state mutations
and append ordered wrapper nodes to a queue *owned by their actual
selected +0x670 source object*. Do **not** automatically reclassify
this as the game's per-user +0x6B4 Inbox, or invent an original message
identity; native payload, queue lifetime, delivery/render and SaveLoad
still need original source evidence. Existing GameState live behavior
is not changed by this source trace.


## Recovery643: original human callback dispatch and 5DC510 payload contract

Independent static `objdump -D -b binary -m i386 -M intel` of the **unchanged**
private original `footballmanager.exe` (4,714,541 bytes,
SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
resolves native `5DB3BD–5DB6FA` control flow, **without running the game**.

With source flag zero and first `4037B0` true, native invokes **two**
`5DC510` callbacks (5DB456,5DB4B9), then reads selected native
`user+694 DWORD0` into EBX at 5DB4C4. Flag zero with no first human
passes directly to 5DB6FA with **no** callbacks or bonus.

With nonzero flag, both kinds of first initial owner divert to 5DB4D7:
the first-side predicate is **rechecked** at 5DB4D9; only when false,
the second is probed at 5DB4E6. If neither is human it skips to 5DB6FA.
When entered, first is checked again at 5DB4F5 and may invoke calls
5DB58D,5DB5F0; the second is checked at 5DB5F9 *after the first-side
callbacks* and may invoke 5DB692,5DB6F5. So zero, two or four callback
calls are source possible, in that order, and source predicates must
not be cached across native mutable callbacks. This path does **not**
execute the 5DB4C4 first-path EBX bonus.

`5DC510` accepts 0x24 bytes of by-value native arguments (`RET 24h`).
Source 5DC5E7–5DC627 copies the first 16 bytes to newly allocated
0x20-byte payload offsets +0..+0F, source word at argument +10 to
payload +10, and three source DWORDs at argument +14,+18,+1C to
payload +14,+18,+1C. The source does **not** initialize two payload
bytes +12..+13, which a portable adapter must not fabricate as a proven
native value. Original 5DC5D9 allocates 0x20 payload **after nested
5DC650**, and original 5DC62B allocates a separate 0x0C-byte wrapper;
5DC634 stores payload-or-null at wrapper+0, then native 617D70 appends
the wrapper to the original selected +670-owner queue. If the payload
allocation fails, source 5DC629 assigns a null payload but still
attempts wrapper creation. The exact wrapper allocation-failure
consequence is **not** safely determined and must not be simulated as
normal success.

New **source-only**, original-PE-backed portable modules:
`original_match_human_callback_dispatch.py` for the original reached
callback site sequence / predicate guards, and
`original_match_5dc510_event_payload.py` for the field-copied payload
layout without pretending the unknown padding is initialized. Tests
`test_original_match_human_callback_dispatch.py`: eight locally
executed tests **PASS** with `FM2001_ORIGINAL_EXE` set to the actual
private source; native signatures include all six callback sites,
branch/control and allocator/wrapper copy bytes. They are registered
for focused Gate13 CI but no PR or remote CI has been run while this
feature branch remains unopened.

**Not proven or implemented:** native 5E48D0/5E43B0 exact argument
values, actual nested 5DC650 effects, allocation and callback
execution, +670 queue lifecycle/SaveLoad, score mutations in
GameState, GUI / original NEXT→PPreMatch modes0–3→PResults→return,
other original leagues, multi-human or Windows 11 acceptance.

**Next executable work:** source-derive both original 5DB3CB and
5DB4F3 argument constructors via 404410/5E43B0 and identify
original downstream consumer of these +670 record wrappers. Then
integrate actual per-user queue + match component mutation into
saved GameState and true normal PPreMatch/all modes/PResults/return.
Keep this same branch, batch reviewed milestone before PR/CI,
and do not close Gate13 on a source-only component.


## Recovery643 continued: original +670 queue read-back for scored records

A bounded static original trace now links the record appended by
`5DC510 → 617D70` to an original consuming callback **without assuming
all 617D70 queues are Inbox mail**. Original `5DC890`, a native
low16 numeric dispatcher, contains actual calls to `5DD1F0`
(e.g., `5DC910`). At `5DD1FB`, `5DD1F0` starts at the
same queue-owner **+4 first pointer** that `617D70` appends to. It
iterates `node+4` next, dereferences **node+0 → payload**, and at
`5DD21F–227` compares requested WORD `[EBP+8]` against the
stored **payload+0x10 WORD** from the `5DC510` copy above.
Only on matching word does it call `5E48D0` with zero scale flag
for the payload's first QWORD and check the x87 comparison to native
literal QWORD zero `0x7BD5F8`; negative/NaN-condition paths may
skip. Subsequent native `64D060` at `5DD278` and `64D020`
at `5DD2AE` test actual source-owned three-DWORD argument contexts
against the payload+0x14..0x1C values before `5DD2BB–C4`
adds the record's first double into a running QWORD total. Original
returns the floating result via x87 at `5DD2D3`, `RET 0x1C`.
A private-PE regression now verifies nine native opcode sites and five
real call targets, including `5DC890 → 5DD1F0`.

This is **source proof of the same linked-queue record format and a compatible native read-back**, not proof of one identical live per-user queue object, strengthening
the player-scoring dependency: dropping queued payloads or replacing
them with an inbox flag would change the original score calculation.
It is still **not a source-verified complete scorer**. The original
`5E43B0→5E4410` constructor can conditionally transform
its double input and use original native scaling state
`0x87AD88`, so we must not simply use a guessed 0.002 product.
The original filters `64D060/64D020`, producer query arguments
and x87 control/results need full source proof. No source-safe
assumption about final GameState score, original native callback
execution, complete alternate team score or GUI acceptance follows.

**Next:** trace native `5DD1F0` input predicates and callers, then
bind exactly matched queued record outcomes to source-proven
5DB37C score calculation, native human +670 state, live GameState and
SaveLoad. Follow with whole normal NEXT/PPreMatch 0–3/PResults/return,
multi-human, original leagues and Gate13–17 Windows11 validation.


## Recovery643: original 64D060/64D020 record range guards fully source-bounded

Further independent static native disassembly resolves two predicates
previously open in the paragraph above: `64D060` is original **signed**
lexicographic (DWORD0,DWORD1,DWORD2) **greater-than-or-equal**
and `64D020` is signed lexicographic **less-than-or-equal**,
both inclusive. Native `CMP/JGE/JLE` short-circuits after the first
unequal element; never apply unsigned ordering or three separate
componentwise comparisons. `5DD1F0` supplies payload+0x14,+0x18,+0x1C
as comparison-side triple and user/query stack words +0C,+10,+14
as lower bound, +18,+1C,+20 as upper bound. Filter results guard
the original contribution. Additional original PE byte checks cover
all six native compare element checks and native queue-head/type/
zero/x87 predicate sites.

New bounded immutable module
`reconstruction/original_match_5dd1f0_queue_query.py` validates the
**actual supplied complete** native owner+4/+8 linked wrapper chain,
each 0x0C wrapper and 0x20 payload identity, subtype WORD+0x10,
finite nonnegative first-double x87 guard, and original two inclusive
signed lexicographic source comparisons, returning **ordered eligible
contributions**, not a guessed total. It rejects malformed/partial
chains, duplicate wrappers/payload owners, NaN/Infinity, absent signed
query triples and native pointer aliasing. Source scope explicitly
marks native x87 sum and live GameState as NOT executed.
Six locally run corresponding unit tests PASS with actual hashed private
PE, including source compare signatures. Focused Gate13 workflow
registered the module/tests. No PR or remote CI yet while this coherent
feature branch remains open to continued source work. **This is a bounded source-matched original queued-record selection
component**, not a proven identity join between the selected human +670
writer and a reached 5DC890 reader in the actual original player journey and is not original-game runtime observation or completed
player-visible match.

Remaining scoring inputs: actual `5E43B0/5E4410` normalized
record double, `5DD1F0` produced query triples/types from reached
match states, x87 sum/control environment and full original human-side
callbacks, other side and processing context; only then may a source-safe
real `GameState` and all-mode normal player match be implemented.

**Recovery643 owner-identity correction:** Original native `5DC510`
appends a record through one concrete selected `user+670` pointer;
`5DC890→5DD1F0` independently queries an object of the matching
queue-owner layout. We have proved reader/writer *structure* and
native per-record filter semantics, but we have NOT yet source-joined
the same concrete selected user's pointer across those native call
chains. The readback source receipt therefore explicitly reports
`original_same_owner_instance_proven=False`. Reached owner and query
callers must be checked before any live original score/world claim.

## Recovery643 next owner-identity target: original indexed +670 score reader

A bounded actual original `5DC890` caller at native **451021** uses
`ECX=[EAX+index*4+0x670]` from a registered-user `4139D0`
lookup; `index=[ESI+0xE0]` at 451014 and `EAX` is returned from
`4139D0 → 413B10` over the original `0x874C10+0x9CC` manager
list. The source writer in original first-side scoring,
`5DB450`, instead loads **`ECX=[selected_user+0x670]`**,
with no dynamic index. Thus the score-record **reader can use an
indexed +670 pointer**, potentially a different subqueue or selected
manager. A real matching owner requires source-qualified selected user,
registered-list index and **the actual +670 slot index**, not merely
equal payload layout. New private PE regression preserves this
one explicit reader callsite and writer comparison.

**Exact next join:** trace the 451021 enclosing original current-manager
and score-query context, `4139D0` record index, 5DC890 numeric
dispatch, and first-side selected user identity at 5DB3CB/5DB502,
then determine which specific +670 reader slots can see the record
produced by original 5DB456/4B9. Prove type and query arguments and
normal match GameState callbacks before making a live score change.

## Recovery643 additional constructor narrowing: first human 5E43B0 zero-type path

Bounded original PE stack reconstruction of first-side human
`5DB41B–435` and `5DB47E–498` shows two reached record
constructors. Each immediately pushes a distinct native record
selector (1 then 2) that is **left for the outer 5DC510
call**, followed by **two zero DWORD constructor fields**,
then an eight-byte scored QWORD. Native `5E43B0 RET 0x10`
consumes precisely that eight-byte QWORD and the two zero
DWORDs; the earlier selector push remains on the stack.
`5E43B0` stores the second constructor DWORD (zero) at
result+8 and passes the QWORD plus first DWORD (also zero)
to `5E4410`. Because the first constructor DWORD is zero,
`5E4410` takes `5E4438–440` **exact low/high DWORD copy**
rather than the nonzero flag's runtime scalar `0x87AD88`;
because result+8 is zero, `5E445A–5E4821` returns before
any nonzero category normalization. A separate FPU compare
to zero is performed but cannot change the already copied
double on this reached category-zero branch.

This **does resolve** the two top-level first-human
`5E43B0` record-double copies as raw rounded QWORD
values from their upstream native weighted x87 stage sums.
It does **not** imply all `5E43B0` calls are raw
(with other flags native scaling/normalization occurs),
does not resolve the nested `5DC510→5DC650` constructor,
and does not recover the original upstream weighted
float inputs or actual writer/reader +670 owner identity.
Original native opcode and four call-target regression was
added to the existing human callback test; all source uses
remain static, with no real match or original program launch.

Next: calculate exact source weighted QWORDs and source flags
for the original first/second sides, join same concrete
registered native owner and slot at readback, and integrate
the full GameState scoring/queue context only where original
x87 behavior and native callbacks are independently qualified.


## Recovery644: corrected native reader registry lookup to global+9C4 (source correction)

Reopening original private PE at native `0x4139D0`, `0x413B10`,
`0x451005–0x451026`, and `0x5DB450` disproves the previous
**club-word-index** interpretation. The actual original does:

- **451005** reads WORD `[ESI+D8->club+4]` into DX, preserving the
  upper half of EDX. **45100E PUSH EDX** leaves it as the next
  `5DC890` query's low16 dispatch selector.
- **451009** loads native root `ECX=874C10` and **45100F CALL
  4139D0**. That wrapper reads **DWORD `[874C10+9C4]`**
  as a zero-based *registered-manager ordinal*, pushes it for
  `413B10`, and returns `RET` without consuming the separately
  pushed EDX query argument.
- **413B10** walks `874C10+9CC` linked-manager entries by counting
  from zero, returns node+0 user pointer; on an out-of-range ordinal
  it returns null. Normal original invocation of `45101A` must not
  be assumed successful for an out-of-range ordinal.
- **451014/45101A** reads source presenter+E0 DWORD as second
  index, then dereferences `[ordinal-selected-user+0x670+4*index]`
  to obtain `ECX` queue object. **451021 CALL 5DC890** consumes
  numeric selector and both by-value range triples.
- **Writer is different**: 5DB3CB→403850→413B40 selects the FIRST
  registered user whose context+4 equals (first-side club DWORD+4
  masked with FFFF), then 5DB450 loads **selected-user+670** with
  *no* indexed offset.

Therefore a source-verified writer/reader join requires **three**
independent choices: global+9C4 registered-user ordinal,
presenter+E0 slot index and first-side full-key human gate +
413B40 masked-key selection. Comparing only low16 club keys or a
source record type gives a false owner. `5DC890` also dispatches
among original numeric categories on the retained query WORD;
`0x66` is one source-direct call into `5DD1F0`, while other
categories may call the aggregator more than once.

Corrected feature WIP
`reconstruction/original_match_451021_indexed_owner.py` and
`test_original_match_451021_indexed_owner.py` project a complete
source supplied `+9CC` manager chain, source `+9C4` ordinal,
`+E0` queue slot, original full/masked writer key and both actual
reached pointers. It preserves separate flags for selected user
identity and selected queue pointer equality. They are **snapshot
possibilities**, explicitly NOT proof the registration list could not
mutate between original writer and reader, no simulated GameState,
no native score or Windows GUI observation.

**Verification:** original 4,714,541-byte SHA833bf95e unchanged;
11 decisive exact original PE signature sites and four direct call
targets were executed and passed locally. The newly authored module
and test have been added to the focused Gate13 CI workflow but have
not yet been separately run under remote CI. Earlier Recovery643
text claiming `4139D0` used the club-word as list ordinal is
**superseded by this correction**. Prior WIP/source conclusions
unaffected: +670 source record layout, original 617D70 append,
5DD1F0 type/float/signed bound checking, conditional callbacks.
No reason to merge PR739 or close Gate13 on this snapshot.

NEXT source qualified feature: bind the numeric `0x66` selector
through `5DC890` with caller-supplied exact two range triples and
the source-matched reader queue pointer, before an actual original
match GameState/SaveLoad integration. Then complete original weighted
score/stage owner and full native NEXT→PPreMatch 0–3→PResults→return.


## Recovery644: first joined original 451021 numeric 0x66 queue query

The corrected source owner projection now has a bounded *caller →
numeric dispatcher → score-record queue selection* seam.

Original `451005 MOV DX,[club+4]` followed by PUSH EDX at
`45100E` makes low16 numeric `5DC890` selector; original
`4139D0` does **not** consume that pushed EDX because it returns
with plain `RET`. `5DC890` masks the selector with FFFF and
branches on the source values: at `5DC8C3/8CC/8D1/8D4`, case
**0x66** follows the single native call `5DC910→5DD1F0`
after building *two 12-byte triple operands* and pushing the
requested subtype **0x66**. Other numeric cases (including
0x00,0x64,0xC8) have different call/count/aggregation paths
and cannot be aliased to case 0x66.

`reconstruction/original_match_451021_numeric66_queue_join.py`
joins the **same source-selected native reader queue pointer** from
the `874C10+9C4` selected registered user and presenter +E0 slot,
to independently supplied original 0x0C queue owner/list and exact
two original three-DWORD query range operands. It reuses original
`5DD1F0` signed inclusive range/type selection and preserves
actual ordered record contributions. Wrong slot, wrong reader
queue pointer, missing manager chain, or a selector other than
0x66 fails closed. Even when original read and write queue
pointers match in a supplied snapshot, the module does **not**
claim original in-process manager identity/absence of mutation,
execute native x87 accumulation, update GameState, or produce
a real match score.

An additional four-method synthetic/counterexample test module
`test_original_match_451021_numeric66_queue_join.py` and the
separate manager-ordinal tests are registered on focused
Gate13 CI. Independently locally checked **11 canonical PE
opcode sites and 3 direct x86 call targets** of the joined
numeric-0x66 path (all PASS); local previous Recovery643
14 original callback/queue unit tests were also run again
against the private original and passed 14/14. The newly
added Python owner/join tests themselves are **not yet locally
or remotely executed**; do not represent them as passed.
No executable launch, PR or CI since this WIP is still not a
complete original GameState player feature.

**Next source target:** trace exact **normal matched caller**
of `451021`: original `[874C10+9C4]` current registered manager
ordinal, source presenter+E0 slot, two date/query triples
constructed at `404410→41C580`, and source vtable/score-reader
return ownership. Cover other reached `5DC890` numeric cases,
native 5DC510/650 mutable world and x87 result before committing
a real source-preserving GameState match/SaveLoad. Full NEXT,
PPreMatch modes0–3, PResults visible callbacks/return, Inbox,
multi-human/leagues and Win11 player tests remain mandatory.


## Recovery644 follow-up: native direct-call inventory and higher-priority +670 candidates

A read-only scan of the unchanged original PE's `E8 rel32`
direct call sites identified 134 raw sites targeting `5DC890`,
36 targeting `5DD1F0` (all internal to the 5DC890 dispatch
region), 22 targeting `5DC510` (including six R1 5DB456/B9,
5DB58D/F0,5DB692/F5), and only one targeting `5DA2F0`
at **513252**. This is a **raw call-target candidate inventory**,
not a source-qualified reachability list: arbitrary E8 byte patterns
still need instruction/function boundary verification.

Among the `5DC890` candidates, direct original
`5E178C` receives a statically reached `0x65` selector
and `5E1814` gets `0x66`; their enclosing native code
loads `[EBP+0x670]` at `5E1756` and again at
`5E17D1`, with further uses around `5E18E7`,
`5E1975`, and `5E1A94`. These are promising
*base +670 queue* / numeric-scoring source anchors
closer to the score-world structure than the 451021
**presenter-indexed** reader. At 5E178C and 5E1814,
however, actual ECX has passed through temporary
stack slots: **do not assert ECX equals [EBP+670]
without exact stack-ownership proof**. The 0x65 route
also differs from source-direct 0x66, and a paired
5DD650 call may mutate native score state.

**Priority on resumption:** trace native 5E17xx exact
call-frame/stack+0x670 queue owner, reached user
identity and pair of 0x65/0x66 queries and 5DD650;
trace callers to the 5E17xx function back into real
R1 513252→5DA2F0 if source-reachable. Prefer
this genuine scored user-world candidate to more
incidental 451021 presenter UI variants. Keep
GameState and SaveLoad blocked until a proven actual
normal-match owner/call chain exists. No original
game launch or Windows GUI proof occurred.
