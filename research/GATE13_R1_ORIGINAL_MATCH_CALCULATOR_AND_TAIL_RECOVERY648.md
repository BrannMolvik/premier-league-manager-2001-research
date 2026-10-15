# Recovery648: original LeagueMatch 513010 calculator-to-world ordering

15 October 2026 KST. Original owner-authorized footballmanager.exe, 4,714,541 bytes, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Static disassembly only, never executed. Baseline main 73d42e9dab03c90d43bc1d5bd96916801c8bc110; Gate13 and Gates14–17 OPEN.

## Confirmed first-hand source

- 5130C2 calls native Match virtual+34 and tests AL. False calls 512D80 cleanup and jumps to 513294, but STILL invokes native v+38 and v+3C. No 5DA2F0 calculation on this false path.
- True v+34 calls 516080. True 516080 invokes 512D80 but jumps to 513235 then checks match+44 again at 513238. Therefore 516080 true is NOT an unconditional no-calculation branch.
- When 516080 false, 5130F4 tests human flag bit0x10 and complete flag bit0x20. Human/not completed may open PPreMatch, prepare mode, invoke match v+28 and mutate team state. A v+28 return of six jumps to 513238, which is NOT enough to prove that the actual calculator is skipped. Other paths use 632B20.
- Source 513238 reloads match+44 bit0x20 after ALL these callbacks. If clear, source 513252 invokes 5DA2F0 native match calculation. Only afterward at 513257 does source reload match+44 human bit0x10, and when true dispatch original mode0 -> 533D80(0), mode1 -> 533D80(1), mode2 -> 5331C0 FastView, mode3 -> no GUI presentation wrapper.
- Every route then joins 513294 native virtual+38 score latch and 5132A9 native virtual+3C world writeback. Skipping a match calculation is NOT permission to skip post-calc callbacks. Do not replace 3D/FastView with Quick3 or publish provisional score before verified native world changes.

## Implemented on WIP feature branch

reconstruction/original_match_513010_postcalc_phase.py models only source-reached v+34, 516080, post-preparation flags+44, post-calculator flags+44 and reached native mode. It returns the precise common calculator, presentation and mandatory v38/v3c ordering. It neither calculates a score nor mutates an event nor claims native GUI execution. It fails closed for unvisited native values.

test_original_match_513010_postcalc_phase.py covers actual mode0/1/2/3 wrappers, false v+34 still reaching v38/v3c, true 516080 not skipping calculator, bit5 completion, reloaded postcalculator human flag, wrong-source-field rejection. Fifteen exact original PE opcode signatures have been independently verified against canonical PE; optional test also checks five direct CALL targets. No exact-head CI has yet been run on the current WIP branch; no reviewable PR yet.

## Exact next player-visible dependency

Source-map native 5DA2F0 team, seed, match RNG and context writing and compare to the reconstructed GameState match calculation. Determine which original v38/v3c side effects and 533D80/5331C0 mode-specific presentations can be source-backed without fabricating an original match. Then join genuine primary+secondary 4A7210/6168C0 dated event callback producer, original saved 2–6-human state, and 432505 conditional management return. Original full game/physical Windows11 comparison and Gate13–17 audits remain OPEN. High-risk PR739 remains separate/unmerged.

This source finding is a recoverable investigation checkpoint under the user-approved milestone batching policy, not a stand-alone PR or release claim.


## First checked calculator dependency, original 5DA2F0 (not yet implemented)

Local canonical bounded disassembly `5DA2F0..5DA605` confirms:
- Incoming `ECX` is an actual original team-object pointer and stack argument `[EBP+8]` is native match context. At `5DA303`, it reads the context's `+0x28` virtual Side getter before using team objects.
- `5DA31A` invokes original `4037B0` on that team. If the result is false, native jumps to `5DA538` and reads **team+0x140,+0x13C,+0x138,+0x134**, converting the DWORDs to x87 floating-point variables with sign/range checks. These exact fields are source-required original calculation inputs, not inferable from completed score data.
- For true `4037B0`, the original first obtains team via `403850` and repeatedly reads team **+0x694/+0x6B0** (callee `618E00` and `65D920/65DA60/65D9B0`), and invokes `4290A0`, then computes x87 fdivr/fmul ratios. It eventually joins the alternative branch at `5DA5CF`. The different source branches cannot safely be treated as an identical single team-rating getter.
- `5DA5D9` starts a separate match+0x4C owner/pointer branch and may skip at `5DA5F9`. Not yet established how it writes final context scores; this requires continuing the callee source graph rather than inventing native RNG or player ratings.

**Next exact source slice:** analyze `4037B0,403850,4290A0,618E00,65D920,65DA60` callback types and 5DA5CF+ score writes, then map only validated source numeric inputs to the existing reconstructed `HumanGameplayController`. Original 5DA2F0 calculation equivalence, rounding/RNG, 533D80/5331C0 native modal lifecycles and original save state remain UNVERIFIED. Do not model their success as the result of calling modern `play_user_primary_match` alone.


## Recovery649: original 4037B0 registered club and concrete non-managed numeric team inputs

Static canonical source `5DA2F0` (private PE SHA833bf95e)
starts by passing the selected actual team pointer to `4037B0`.
This is not a vague "user team" bool: `4037B0` passes the
team through `4139E0`, which reads **team+0x04
FULL DWORD owner key**, traverses original 874C10+9CC
manager-linked list (node+0 user pointer; user+5B4
context pointer) and compares each **context+0x04
FULL DWORD** using `4139F0`. It stops on first
matching registered manager, returns AL=1, and
otherwise returns AL=0. The separate `403850`
lookup then uses `413B40`, which masks the team
owner key to **16 bits**. Full-key membership
and low16 manager lookup are different operations:
never assume one proves the other or choose an
arbitrary user when two full keys share the low16.

For a source-confirmed **4037B0 AL false**,
`5DA538→5DA5CF` reads exact native fields
`team+0x140`, `+0x13C`, `+0x138`, `+0x134`
(in this *decreasing* order). Each is a DWORD
zero-extended into an x87 `FILD QWORD`. The
first two (*+140*, *+13C*) are compared against
native double **200000.0** at 0x7D73D8.
Values **greater** than the limit are zeroed in
their resulting double stack slots; values equal
to 200000 are retained. The other two (*+138*,
*+134*) are not subject to this comparison on
this branch. Native uint32 0xFFFFFFFF thus
becomes positive 4294967295.0 through the
zero-extended QWORD, not a signed -1.0.
Only this bounded input branch has been recovered;
the original nonhuman scoring result is **not**
computed by projecting these four numbers.

`reconstruction/original_match_5da2f0_team_inputs.py`
now takes actual native club-team bytes, full ordered
manager-linked records and exact full-key match,
and returns source-typed registration branch result.
Only original AL=false qualifies a second source
function to extract and convert four native team
inputs from the **same team+4 key** after callback.
It rejects malformed/reordered link chains, alias
and unsupported type drift, and cannot claim source
native callback execution, score calculation or
GameState mutation. The companion five-unit-test
module verifies full-key vs colliding low16 human
owner, first match stopping before unreached tail,
threshold boundary, uint32 conversion and
negative pointer/mutated record cases.

### Original source 5DA5D9: explicit encounter owner/v+18 fallback and numeric tier

After both human or nonhuman team-numeric branches
meet at **5DA5CF**, native code reads
`match_context+0x4C` into EBX and calls its
virtual **+0x18**. If this returns zero and
`encounter+0x04` is nonzero, it selects that
alternate pointer before calling virtual +0x18
**again**. If the second virtual result is zero,
the original jumps directly to **5DA746** and
checks match-context v+0x28, invoking
`5DBCD0` twice when v+28==6 or
`5DBA60` twice otherwise, with opposite
team argument order. If second v+18 returns
nonzero, original reads selected encounter+0x3C,
subtracts match context virtual+0x60 EAX,
and selects an original tier integer:
`diff==2 -> 30` at 0x821088;
`diff==3 -> 20` at 0x82108C;
`diff==4 -> 15` at 0x821090;
every other 32-bit diff -> **14** (15-1).
Native 0x821094 additionally contains **10**
and is used in subsequent x87 `FDIVR`
calculation. These are concrete input factors,
**not** scores, percentage values or a license
to guess modern RNG.

The new `original_match_5da5d9_encounter_tier.py`
captures actual reached original initial/selected
encounter pointers, source v+18 outputs, match
context+4C identity, optional match-context v+60
EAX and returns branch/tier. Source methods and
all mutations remain unexecuted. Six regression
tests cover v+18 no-alternate, distinct alternate,
failed second v+18, all exact numeric tiers,
unsigned wraparound, alias/missing-pointer
rejection and actual original global tier bytes.

All **26** newly asserted 4037B0/4139E0/5DA538
and 5DA5D9/5DA6xx native opcode sites were
independently compared byte-for-byte against the
canonical shipped private PE in this recovery:
**26/26 PASS**. The WIP source modules/tests have
been registered in Gate13 CI but full Python
unit tests are **not yet certified** on exact GitHub
head; original executable not launched. This
improves native match-calculation input fidelity,
but **DOES NOT** complete original LeagueMatch,
Quick Match replacement, modes0/1/2, v38/v3c
persistence or the original player match return.
Original two date registries, multi-human saves
and true Win11 interactive release audits still
unresolved. Keep Gate13 and Gates14–17 OPEN.

**Next:** trace exact **5DA746** v+28
`5DBCD0/5DBA60` return values and the 5DA785
team+20/+24 signed integer distance math,
then 5DA8D9→40CBC0 and 5DA9A6 native event-score
mutations. Map those exact original world fields
to saved `GameState` and ordinary one-match
fixtures before allowing automatic source-derived
progress or mode0–3 playback. Re-review actual
ordinary user gameplay, not only isolated source
unit tests, at the next coherent PR.
