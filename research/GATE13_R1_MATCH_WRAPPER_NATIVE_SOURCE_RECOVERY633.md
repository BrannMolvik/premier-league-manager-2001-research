# Gate 13 R1: original match-mode handoff phase order (Recovery633)

15 October 2026 KST, source-only private executable trace, no original process execution. Original exact `footballmanager.exe` length 4,714,541 bytes; independently SHA-256 verified `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` in this recovery. Do not put the original executable in Git.

## Newly independently verified original native ordering

At the **conditional reached point** `0x513238` inside native `0x513010`, original x86 reads mutable processing-object `[esi+0x44]`, checks bit `0x20` and skips straight to `0x513294` if set. If clear, `0x513244..0x513252` resolves the native left context and calls `0x5DA2F0`, **before any presentation wrapper**. This routine has significant original world/stat-related calls; do **not** equate it with a harmless preview or the entire source-qualified game calculator without further reachability/world proof.

At `0x513257`, the original **re-reads** `BYTE [esi+0x44]` *after* `0x5DA2F0`; it only enters modal selection when bit `0x10` is then set. Never assume the two flag snapshots are identical. At `0x51325D..0x513294`, actual mode `877530` sends 2 to `0x5331C0` FastView, 0/1 to `0x533D80` with variant 0/1, and 3 to no wrapper. The prior 0x513010 entry/virtual+28 predicates are separate prerequisites, **not** proven by a phase receipt. `0x513294` then calls processing object's native virtual **+0x38** and **+0x3C**, in that order, after any mode wrapper; these post callbacks are not qualified merely because a synthetic match result exists.

Bounded original FastView `0x5331C0`: `0x5328B0` signal; `0x5329D0`; `0x533270` view preparation; `0x533BF0`; `0x51F490`; synchronous `0x532650` modal at `0x533236`; `0x533CA0` subsequent stage at `0x53323C` and `0x51F6D0` stack teardown. The wrapper has distinct, not yet faithfully reproduced, resource/input/timing semantics. Original 3D `0x533D80` separately sets up 3D and calls `0x533270`, `0x533FE0` before its own graphics/modality; treating either as Quick3 is wrong.

## Evidence, artifact and integration boundary

Twenty private canonical PE opcode signatures (exact addresses `513238,51323C,51323F,513242,51324E,51324F,513252,513257,51325B,51325D,51326A,513272,51328C,51329D,5132A9,5331FD,5331FE,53322B,533236,53323C`) were checked by a bounded private local Python byte comparator, **20/20 passed**, no executable invocation. New `SourceMatchModeHandoffPhase` in `reconstruction/gate14_match_detail_route_source.py` records two separately reached source flags, the optional pre-wrapper call, conditional original presentation wrapper, and afterward the two virtual callbacks. It is immutable source-only, **not a match transaction, not a real GameState mutation, not native window/input and not original-game observation**.

The new regression tests cover four modes, a modified second native flag, skipping both calls when bit0x20 is set, invalid/missing flags, and optional original PE byte signatures. Local branch test execution and new PR exact-head CI remain unverified; no PR/open CI required for a source-only investigation fragment. Collect this into a source-backed actual player-visible normal NEXT→PPreMatch→all four modes→PResults→management return milestone, with full entry predicates, real `0x5DA2F0` effects, post-virtual world and UI/SaveLoad verification, rather than prematurely publishing a Quick result for modes0–2.

Original all-league, multi-human, physical Windows11 GUI and Gates13–17 release acceptance remain OPEN.
