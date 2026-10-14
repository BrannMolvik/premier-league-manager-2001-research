# Recovery623: source original 0x418220 role/aux swap and 4085D0 full qualified variant

**14 October 2026 KST.** Baseline main `a75bc6f61848b69df845ccf69c78c3d4a1812754` after verified PR721: original 0x4085D0 bounded source-eligibility and paired player/category world writes, exact-head Gate13 1,730 tests/138 expected skips and repository asset policy PASS. Source private original `footballmanager.exe` size 4,714,541 bytes SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` independently hash-confirmed. PE static disassembly only; original game has not been executed or committed to Git. Gates13–17 remain OPEN.

## High-impact missing original side effect now source-closed

Original native `0x4182F0` calls `0x418180`. If player DWORD+0x174 **bit0** is set, `0x418180` calls `0x418220` **before clearing** +0x174 bit0; `0x418170` then clears +0x174 bit1. Original `0x418220` is **not** an arbitrary reset or a value pulled from modern RuntimePlayer. Native disassembly reveals the exact two-way exchange:

1. Read native player DWORD+0x248 source role-object pointer.
2. `0x4EA3C0` extracts original role BYTE object+3 masked to low **5** bits, `0x4EA3D0` extracts object+4 low **4** bits.
3. `0x4EA330` writes native player BYTE+0x152 reserve-role value into role-object BYTE+3 **low5 only**, keeping upper3 source bits. `0x4EA350` writes native player BYTE+0x153 reserve auxiliary into object BYTE+4 **low4 only**, preserving upper4 bits.
4. Store the *previous extracted* object role/aux bytes back to player+0x152 and player+0x153 (zero-extended masked values, not unmasked original bytes).
5. This function by itself leaves player+0x174 intact. The **caller** `0x418180` clears bit0, and `0x418170` clears bit1. Both stages must be represented before claiming source parity.
6. Later in source `0x4085D0`, a separate final `0x4EA350` takes the original `0x406BE0` peer count and **overwrites object+4 LOW4 again**. Thus doing the order backwards is wrong and would change lineup/category bytes.

## Source-bounded implementation

Added `reconstruction/original_native_418220_role_swap.py`, requiring reached player through +0x248 and exact resolved original role-object pointer and bytes. It projects the complete native 0x418220 exchange without allocating objects, running callbacks or changing live GameState.

Extended `source_original_4085d0_qualified_mutating_leaf` from PR721: when original +0x174 bit0 is set, it projects 418220 on the staged post-bitmask player and source role object, then clears +0x174 bits0/1 before qualifying exact registered-manager `0x417340` at-call player snapshot and optional unqualified `0x41EDF0` club-counter gate. Finally it applies the peer count to the post-swap category object+4 low nibble. The new receipt differentiates `role_swap_projected` from `role_swap_executed=false` and `live_game_state_updated=false`, so no source-only simulation is misreported as a native or modern GameState effect.

Regression tests cover high bits preservation, role/aux mask semantics, original +0x174 not changed inside 418220, true/false flags, invalid pointer and malformed source, source composed player/category final order and 16 SHA-qualified original opcode signatures. Focused Gate13 CI, asset policy and patch review required before merging.

**Limit:** This still operates on immutable reached-native records. An unregistered player without status+0x14 bit13 may call `0x41EDF0`, which changes native player+0x14 bit12 and original registered club+0x1A8 quota; the narrow path rejects it. No actual native 4197C0/5127A0 callback execution, GameState saved source role-object mutation, PPreMatch modes 0/1/2/3, PResults, long-career and Windows11 GUI test is established.

**NEXT:** source-close `0x41EDF0` registered-club+0x1A8 owner with exact +0x72 vs +0x10 distinction, add source-qualified atomic club-counter effect, then map the combined original 0x4085D0/0x418220 player+team writes into live saved GameState without conflating generic reserve/status fields. Continue normal player-facing R1 NEXT→PPreMatch all modes→PResults→return, all original shipped countries/leagues, multi-human and Gates13–17 release verification.
