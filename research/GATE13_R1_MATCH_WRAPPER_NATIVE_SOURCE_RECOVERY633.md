# Gate 13 R1: original match-mode handoff phase order (Recovery633)

15 October 2026 KST, source-only private executable trace, no original process execution. Original exact `footballmanager.exe` length 4,714,541 bytes; independently SHA-256 verified `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` in this recovery. Do not put the original executable in Git.

## Newly independently verified original native ordering

At the **conditional reached point** `0x513238` inside native `0x513010`, original x86 reads mutable processing-object `[esi+0x44]`, checks bit `0x20` and skips straight to `0x513294` if set. If clear, `0x513244..0x513252` resolves the native left context and calls `0x5DA2F0`, **before any presentation wrapper**. This routine has significant original world/stat-related calls; do **not** equate it with a harmless preview or the entire source-qualified game calculator without further reachability/world proof.

At `0x513257`, the original **re-reads** `BYTE [esi+0x44]` *after* `0x5DA2F0`; it only enters modal selection when bit `0x10` is then set. Never assume the two flag snapshots are identical. At `0x51325D..0x513294`, actual mode `877530` sends 2 to `0x5331C0` FastView, 0/1 to `0x533D80` with variant 0/1, and 3 to no wrapper. The prior 0x513010 entry/virtual+28 predicates are separate prerequisites, **not** proven by a phase receipt. `0x513294` then calls processing object's native virtual **+0x38** and **+0x3C**, in that order, after any mode wrapper; these post callbacks are not qualified merely because a synthetic match result exists.

Bounded original FastView `0x5331C0`: `0x5328B0` signal; `0x5329D0`; `0x533270` view preparation; `0x533BF0`; `0x51F490`; synchronous `0x532650` modal at `0x533236`; `0x533CA0` subsequent stage at `0x53323C` and `0x51F6D0` stack teardown. The wrapper has distinct, not yet faithfully reproduced, resource/input/timing semantics. Original 3D `0x533D80` separately sets up 3D and calls `0x533270`, `0x533FE0` before its own graphics/modality; treating either as Quick3 is wrong.

## Confirmed pre-presentation native owner world-write barrier

Fresh original SHA-verified static disassembly of `0x5DA2F0..0x5DB9F8` strengthens the integration requirement. At `0x513074..0x51307C`, the outer processor computes `edi = esi+0x14` (its first embedded side wrapper) and calls that wrapper's vtable+0; this identifies which original source binding is later reused, but does not identify a portable club/player yet. Native `0x513244→0x513248` calls `[edi]->vft+0`, passing that returned object's pointer as `ecx` to `5DA2F0`. At `5DA301`, that callee captures it into `esi`. **This owner is not automatically the outer `0x513010` match-processing object's `esi`.** Source identity must be reconciled before any portable `GameState` write.

Within the reached callback completion path, `5DB7F8` stores object DWORD `+0x148`, `5DB7FE` stores `+0x160`, and `5DB80E..5DB904` initializes/updates `+0x144`. Native `5DB90A..5DB9EC` also writes `+0x124`, `+0x128`, BYTE `+0x130`, DWORD `+0x12C`, and flag DWORD `+0xE8`. Earlier FPU/user-context calls and arithmetic are not completely qualified, so these addresses are **exact source-level mutable offsets**, not guessed semantic names. The normal match cannot safely replace the entire callback with a render-only preview or synthesized Quick result.

Ten additional original executable opcode signatures for this returned-object ownership and its state writes passed **10/10** independently using the private canonical PE. No original process, native world update, Save/Load or GUI execution is claimed.

## Newly source-verified early vtable+34 routing: do not enter a mode prematurely

The original match processor can bypass **both** the pre-wrapper
`0x5DA2F0` calculation and the user-visible Match Detail mode
before it even reaches `0x513238`. The original instruction
`5130C2: call [LeagueMatch vtable+0x34]` branches on `AL`:
if **zero**, it invokes `0x512D80` at `0x5130CE`, then jumps
`0x5130D6→0x513294` to run the *post* virtual+0x38/+0x3C callbacks,
without entering the source handoff or any presentation choice.
If **nonzero**, `0x516080` is called. Its **nonzero** result calls
`0x512D80` at `0x5130EA`, then jumps to `0x513235→0x513238`.
Its zero result proceeds to `0x5130F4` through subsequent conditional
preparation, the later virtual+0x28 and side probes, eventually reaching
`0x513238` if native intervening calls return.

Consequently, a `SourceMatchModeHandoffPhase` is only valid where the
outer route **actually reached** `0x513238`; it cannot be inferred
from a pending match or even a selected mode. The new
`source_original_match_router_guard` separately requires true
original AL zero/nonzero results at their reached sites and explicitly
distinguishes early `512D80`, handoff reachability, and the common
post-callback stage; it does not invent the results of either call.
The unqualified original vtable+0x34 or `516080` callback cannot be
replaced with a modern boolean computed from prototype state.

New 14 exact opcode signatures from `0x5130C2` to `0x5130F9`
were independently checked **14/14** against the private
SHA-verified original executable. The combined phase,
owner-state and entry-guard set now covers **44/44** separately
checked original signature sites in a bounded static inspection.
This is *not* original game execution or a verified live dispatch.

## Counterexample: selecting a mode is not a native mode read

`0x513238` tests original object+44 bit0x20 **before** the
`0x51325D` global `0x877530` read. If bit0x20 is set, the
original jumps directly to `0x513294`; it does not execute the
**outer** `0x51325D` mode read, does not call `5DA2F0`, and does not
open 3D or FastView. Earlier v+34 may already have cached the mode.
Even if that bit is clear, `0x513257` rereads object+44 bit0x10;
if **clear**, this route also skips that OUTER `0x51325D` read and presentation
but does call `5DA2F0`. The *distinct* earlier `0x5130C2`
vtable+34 AL zero path also bypasses `0x513238` completely,
calls `512D80`, and reaches the post callbacks.

The initial source-only helper prematurely required a valid mode even
on these two branches, which risked fabricating an original `0x877530`
lookup or attributing Quick mode3 to a path that never queried it.
Corrected source contract: `mode=None` when the outer `0x51325D` was not
reached, fail closed if a caller supplies a guessed/unobserved mode,
and require a valid original mode **only when both flag gates permit
the actual native global read**. A typed guarded route now combines
the two entry callback results and the two independent +44 flag
snapshots and always marks +38/+3C as **outstanding**. It does not
run the original calculator or complete a real match.

## Earlier virtual+34 caches the mode even on an outer dispatch bypass

**Source correction to the narrower read-site finding above:** native
`0x510D60`, the common original virtual+0x34 prepare handler,
**unconditionally reads global `0x877530` at `0x510D95` and stores it
as context DWORD `+0xD3C` at `0x510D9B`** on its reached path,
BEFORE the outer `0x5130C2` receives the callback result. All seven
source-authenticated LeagueMatch virtual+0x34 slots are either
`0x510D60` itself or wrapper `0x511120` that first calls it.
Consequently, an absent `0x51325D` **outer mode dispatch read**
does **not** mean the original mode was globally unobserved or the
context lacked a cached mode. The optional mode field in the new
source dispatch receipt means **only that the OUTER mode read did not
happen**; it never claims `0x510D60` had not already cached it.

`source_original_v34_mode_context_store_from_reached` models exactly
this ONE original source store for an authenticated v+34 match owner and
a separately reached processing-context byte array at `0x510D95`.
It accepts all uint32 values, including native unresolved sentinel
`5`, without pretending `5` is a user-selectable presentation mode.
The other native `510D60` mutations of side IDs, event counters
`+D0C/+D10`, clearing arrays and return AL remain separate and
**unexecuted**. Six additional private canonical PE instruction
signatures were checked **6/6**, bringing this combined bounded
source audit to **50/50** opcode signature comparisons. This corrects
the original summary's otherwise overbroad "not read" interpretation.

## Reuse existing post-presentation world adapters, do not rebuild them

Current `main` already contains `reconstruction/original_native_match_result_latch.py`
for native `0x51329D` virtual+0x38: original `0x5112A0`
copies score WORDs from match-processing context `+0xD4C/+0xD50`
to the match record `+0x3C/+0x3E`, while some source classes
route via `0x5136C0` and require additional mutable `0x513570`
processing. Likewise
`reconstruction/original_native_match_v3c_entry.py` already
models the strictly bounded original `0x5132A9` virtual+0x3C
prefix, `0x511370` match+0x44 bit0 write, and a combined
**zero-event-only** v38→v3c prefix requiring native
context counters `+0xD0C/+0xD10` zero on wrapped owners.
Neither helper executes native callbacks, dynamic scorer events
nor a normal modern career match.

The next useful source-backed vertical integration should qualify the
actual *same* match/first-side native owner through `513010`,
`5DA2F0`, mode wrapper, reached context state and vtable-backed
post callbacks, then use these **existing** source modules instead
of creating competing source adapters or announcing a result merely
because the wrapper returned. Any nonzero event counter requires full
native `513570` and later v3c world semantics before publish.

## Evidence, artifact and integration boundary

Twenty private canonical PE opcode signatures (exact addresses `513238,51323C,51323F,513242,51324E,51324F,513252,513257,51325B,51325D,51326A,513272,51328C,51329D,5132A9,5331FD,5331FE,53322B,533236,53323C`) were checked by a bounded private local Python byte comparator, **20/20 passed**, no executable invocation. New `SourceMatchModeHandoffPhase` in `reconstruction/gate14_match_detail_route_source.py` records two separately reached source flags, the optional pre-wrapper call, conditional original presentation wrapper, and afterward the two virtual callbacks. It is immutable source-only, **not a match transaction, not a real GameState mutation, not native window/input and not original-game observation**.

The new regression tests cover four modes, a modified second native flag, skipping both calls when bit0x20 is set, invalid/missing flags, and optional original PE byte signatures. Local branch test execution and new PR exact-head CI remain unverified; no PR/open CI required for a source-only investigation fragment. Collect this into a source-backed actual player-visible normal NEXT→PPreMatch→all four modes→PResults→management return milestone, with full entry predicates, real `0x5DA2F0` effects, post-virtual world and UI/SaveLoad verification, rather than prematurely publishing a Quick result for modes0–2.

Original all-league, multi-human, physical Windows11 GUI and Gates13–17 release acceptance remain OPEN.
