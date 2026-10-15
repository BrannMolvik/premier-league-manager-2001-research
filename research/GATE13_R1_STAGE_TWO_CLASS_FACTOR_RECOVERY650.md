# Recovery650: original 5DAA0B and 5DAC89 score-stage coefficient selection

15 October 2026 KST, canonical main baseline `94d223fac2135641ff368428618f1310f0ef28d6` after reviewed PR759. Original owner-authorized shipped `footballmanager.exe` is 4,714,541 bytes SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; only **static disassembly**, original executable never run, changed or committed. Work branch `worker/gate13-r1-original-score-stage2-650`. Gate13–17 OPEN.

## Concrete original class coefficient lookup before 5DA250 score routine

Original first match scoring side `5DAA0B..5DAAD6` reads native source team+0x10, calls **40DED0** to convert a word, looks up the object's original named owner via **4F3B10**, reads **team+0x14** class index, and computes native class table pointer: `874BE0 + (team+0x14) * 108`. It passes this with the 4F3B10 source object to original **410FF0**. The returned full EAX is tested against 5 and branches through native jump table **0x5DB9FC**; exactly six cases are reached at `5DAA53/60/75/8B/98/AD`, and all cases write QWORD stack+18/+1C with one of **original doubles `0x821E00/08/10/18/20`: 0.9, 0.8, 0.7, 0.6, 0.5, 0.5** respectively. All values above5 (unsigned) fall through to 5DAAC3 and use final 0.5. The resulting first-side coefficient feeds FPU and a call **5DAB07→5DA250** alongside the current team class original 874C08+team+0x70 native indexed metric. It is not itself a final goal count.

Original second match scoring side `5DAC89..5DAD54` repeats the same source lookup for **opponent team EBX**, original class `[EBX+14]` and the same 874BE0 class table stride108. It makes a second, independent native **410FF0** call at **5DACC0** and dispatches its own six case addresses at **0x5DBA14**: `5DACD1/DE/F4/5DAD09/16/2C`, again original doubles 0.9 through 0.5 and >5 fallback at 5DAD41. Do not recycle first-side classification as second-side result; these are separate original callbacks and team owners.

Implementation in WIP `original_match_5daa47_stage_two_factor.py` accepts **typed actual first/second side**, team pointer+original team+14 class DWORD, owner-original global 874BE0 table pointer, actual reached `410FF0` class-table ECX and actual returned EAX. It validates **exact source pointer arithmetic including overflow** and yields the native QWORD coefficient bytes plus reached case address; it never executes original 40DED0/4F3B10/410FF0/5DA250, player RNG, score state or GUI. Tests exercise both native owner sides, 0..5 original doubles, >5 native fallback, out-of-bounds, negative/boolean/forged class inputs, original signed-safe memory range, exact original source jump tables and opcode sites. Registered in focused Gate13 source workflow but **not yet run on exact head CI**.

## Previously merged source work reused, not repeated

Prior `reconstruction/original_match_four_5da250_argument_source.py` and `reconstruction/original_native_5da250_fpu_branch_source.py` already document the four subsequent native 5DA250 arguments and FPU branches. Prior `original_native_match_v3c_entry.py` and `original_native_v38_score_stage.py` recover partial world callbacks/score latch. These are **read-only source models**, not GameState effects. Rather than duplicate them, next integration must join exact source category owner and 5DA250 argument receipts to the **live** scheduled match source and world state. The ordinary port still substitutes its own single-human Quick3 simulation and lacks native match modes0/1/2 modal renderers, native input model and genuine dual-calendar PResults event callbacks. No physical original-vs-Windows11 acceptance.

**Next original evidence:** recover 5DA250 FPU result-to-`5DAB97` clamp, `5DABCA→668350` bound and 64D540 RNG effects for BOTH teams and stages, then identify which record/score fields are persisted through native v+0x38 and v+0x3C and bridge to the already source-typed live GameState. Continue milestone batching without micro-PR and maintain agent-runtime working state. All gates remain OPEN, PR739 high-risk injury/schema48 unrelated/unmerged.


## Recovery651: stage2 class-factor to original four-stage 5DA250 arguments source join

Existing main's `original_match_four_5da250_argument_source.py`
already proves original four reached source call sites:
stage1 first `5DAB07`, stage2 second `5DAD84`,
stage3 `5DB003`, stage4 `5DB280`. The first
two receive distinct team factor inputs built at
`5DAA47` (ESI first side) and `5DACC0`
(EBX second side), respectively, with native
class-selector result from `410FF0`. The
original `5DAAC3/DAD41` fallback/mode labels
store one source QWORD `ESP+0x18..0x1F`.
The original `5DAAE5/DAD62` code later
constructs 5DA250 arguments using this factor
and the side-specific original 874C08 indexed
rating DWORD plus preserved source FPU slots.
Do **not** equate side1 and side2 team pointers,
or reuse the first-side classifier for side2.
Both 5DA250 calls receive `ECX=ESI`
original calculation context even though
the stage2 coefficient belongs to EBX opponent.

`reconstruction/original_match_stage2_5da250_factor_join.py`
now joins independently qualified
`SourceOriginalStageTwoFactor` (side+team)
with the already canonical
`OriginalFourStage5DA250Arguments` (stage,
real source ESP snapshot, native human-club
guard and 5E48D0 B write where reached).
It strictly compares original local
`ESP+18` factor QWORD **bytes**, validates
the source stage1/stage2/EBX team pointers,
and recovers source-only original QWORD A/B
argument owner without manufacturing the
actual x87 output. For source stage2
nonhuman club, native previous stack QWORD B
is *retained* rather than freshly written
from 5E48D0; the joined receipt preserves
that unresolved provenance rather than
guessing B based on current club rating.
Unit tests cover both source owner stages,
all original 0.9..0.5 selector QWORD factors,
human+694 stat access, source direct B
callback vs retained stage2 B, and
corrupt/aliased team pointers and actual
ESP snapshots. This is **first/second**
stages only, not unsupported third/fourth
stage inferred classifications.

Original source at `5DAB0C` keeps the
returned 5DA250 FPU double, at
`5DAB67/80` bounds another derived
FPU value, at `5DAB97` it checks
original literal double **1.0**,
and `5DABCA→668350` converts to integer.
At `5DABED→64D540` original RNG uses
the projected integer bound and returns
an opaque native result; this original
random return is NOT derived by class
factor or source 5DA250 original x87
branch topology. Prior
`original_native_5da250_fpu_branch_source.py`
correctly fails closed when the original
intermediate extended x87 value is
unresolved. The source helper here does
not replace that result with a Python
float formula, and ordinary Quick3
remains a separately reconstructed
simulation until both original
5DA250 and 64D540 effects qualify.

This milestone's Gate13 tests are
registered but require exact-head CI.
The original executable was source-disassembled
only; no player-visible original game,
full all-mode match engine, virtual
v38/v3c writeback, dual-calendar live
callbacks or Windows11 GUI acceptance
has been verified. Earliest remaining
roadmap gate: 13 OPEN; 14–17 OPEN.
