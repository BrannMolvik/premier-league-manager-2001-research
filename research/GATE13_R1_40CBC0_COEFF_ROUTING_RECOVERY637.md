# Gate 13 R1 recovery637: upstream original 5DA967 -> 40CBC0 coefficient selector

**15 October 2026 KST. Source-only active WIP. Gate13 and Gates14–17 OPEN.**

Canonical private original `footballmanager.exe` 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, static PE inspection only; original EXE was **not executed, exported, shared or committed**.

Immediately after original `0x5DA8E9–0x5DA95C` initializes four branch-dependent double accumulators, original `0x5DA967` calls `0x40CBC0` with **ECX=ESI**, the same first-side club pointer already distinguished from outer match processing object in merged PR745. Two independent native stack output QWORD pointers are passed (do not guess which is the visible coefficient or substitute synthetic values). Original `0x40CBC0` reads DWORD first-side club+0x14, subtracts 24 modulo 32bit, checks unsigned <=49, then dispatches through *native* selector bytes `0x40CFC0` and jump DWORD pointers at `0x40CFA0`. Only seven values in the inclusive 24..73 range choose a nondefault jump target; **every other value** including outside this range enters `0x40CF31` default.

| Native club+0x14 | Selector | Original target |
|---|---|---|
| 24 | 0 | `0x40CE83` |
| 26 | 1 | `0x40CBF2` |
| 31 | 2 | `0x40CEDA` |
| 33 | 3 | `0x40CCC9` |
| 40 | 4 | `0x40CD5D` |
| 66 | 5 | `0x40CE09` |
| 73 | 6 | `0x40CDB3` |
| All other native DWORD values | 7 if 24..73, else direct | `0x40CF31` |

**Independent source recheck:** exactly 50/50 original private jump-selector bytes, 8/8 jump-table DWORD destinations, five x86 40CBD4/40CBDA/40CBE3/40CBE5/40CBEB opcode-site signatures, and original SHA all match. No original binary data itself is part of Git. The source-only `reconstruction/original_native_40cbc0_coeff_route.py` and tests record exact first-side pointer identity and selector target; they explicitly say neither original coefficient output, callback, native match, nor GameState was executed.

**Do not confuse choosing a route with computing coefficients.** The targets run further independent control chains, including original first-side club+0x10 read, calls `0x4056D0`, `0x4056F0`, and `0x4FA520` to return branch categories, and further branch-specific QWORD global constants at `0x822040...`, `0x822140...` and multipliers `0x7BD558/0x7BD6A8`. Branches can fall through (not a flat direct lookup). Native game-world floats `+0x50/+0x58/+0x60/+0x68` are subsequently mutated via `0x5DA250`, human original `0x42B0E0`, player/club/RNG and eligibility callbacks. The source selector alone cannot make the normal NEXT -> PPreMatch modes0–3 -> PResults -> management transition happen.

**Next exact task:** source-qualify `0x4FA520` decoded native club+0x10 branch output and all 40CBC0 0–7 route-specific output writes, their signed/constant/fallthrough cases, before joining two initial double coefficients to the real match producer streams. Preserve selected manager and first-side owner identity, human+694/source registry gates from merged PR745. Then complete true original GameState match/SaveLoad, v38/v3c, all presentation modes, 2–6 human/countries, and Gate13–17 actual Windows 11 GUI/install release audits. Do not merge this WIP branch as a complete match or mark any gate complete.

## Reached 40CBC0 category dependency 4056D0→4056F0→4FA520 (same WIP branch)

Fresh exact original x86 confirms the native per-route calls use `[club+0x10]` as an argument to original `0x4056D0`, which writes the **low WORD** of the stack argument into a four-byte temporary and clears the next WORD; `0x4056F0` calls `0x4F3B10` to obtain the actual temporary/native query object. The following native `0x4FA520` does **not** simply return a passed match-mode integer; it calls `0x4FA510` which calls `0x4F8FF0` then `0x410FF0` and obtains its own category DWORD.

At original `0x4FA530` it reads **signed** WORD native object+0x20, computes `(signedIndex << 6) mod 2^32` at `0x4FA534`, then reads indexed DWORD `[global_0x876C50 + displacedOffset + 0x24]` at `0x4FA537`. If that source DWORD is `0x21`, original `0x4FA543–0x4FA562` maps category 3→2 and 4→3; all other category values are unchanged, and **every category** is unchanged when the indexed DWORD != `0x21`. This exact exception must be preserved for the original coefficient branches, not normalized into a generic fixed category. The native computed address for negative signed indices uses wrapped DWORD arithmetic, but **valid object and global heap ownership** are not yet source established, so never invent memory at the address.

Added `original_native_4fa520_category_source.py` and tests to the **unopened** `worker/gate13-r1-40cbc0-coeff-source-637` branch, requiring separately reached original query object, signed indexed slot pointer/bytes, 4FA510 output and global base. The source-only model performs no 4FA510, 4FA520, heap dereference, floating coefficient write or live GameState operation. Independently rechecked **11/11 original 4FA520 opcode samples** and all 50 original jump selector entries/eight native targets in source branch. The two new modules' Python test suite is not yet hosted in CI; do not call this player-visible or gate-accepted.

**Exact next source step:** resolve `0x4F3B10` temporary-to-object ownership and the `0x4F8FF0→0x410FF0` produced category for real native club+0x10. Then source-qualify each 40CBC0 exceptional/default target's actual **two QWORD output writes**, including fallthrough, global coefficient table identities and original FPU multipliers; join their outputs to the later 5DA2F0 score accumulator producers and actual normal player match lifecycle. Keep all original countries, up to six humans and real Windows11 GUI release unverified until genuine end-to-end audits.

## Reached native 4056D0/4056F0/4F3B10 source owner, with first-user independence

Independent original disassembly closes another upstream pointer-identity boundary. Original 40CBC0's reached branch reads original first-side club DWORD+0x10. `0x4056D0` writes exactly its low **WORD** into a native four-byte temporary at +0, and clears the next WORD at +2, then `0x4056F0` calls `0x4F3B10` with that temporary pointer. The native `0x4F3B10` checks query lowWORD against `0xFFFF`:
- For `0xFFFF`, original source selects global `0x876BC8` head, NOT the indexed bucket array.
- Otherwise, native `MOVSX` signed WORD, multiplies by four, selects reached `[global_0x876C44_base + signedIndex*4]` head; source negative WORDs use wrapped 32-bit pointer arithmetic, not unsigned index normalization.
- It iterates actual linked native objects by **DWORD node+0x10**, compares query highWORD against node **WORD+0x22**, returns the first matching node pointer or zero if head/chain ends. A zero means original next dereference for `0x4FA520` is not source-qualified and portable projection must fail closed. A manager registry, active-user pointer, or club ID is not this linked query object.

The new `original_native_40cbc0_coeff_route.py` staged 4056D0 helper, `original_native_4f3b10_query_owner.py`, and `original_native_40cbc0_query_category_join.py` enforce actual first-side native pointer/club+14 route, query byte identity, signed bucket address, precise reached first matching +0x22 linked node, and EXACT same node pointer and raw bytes read by later `0x4FA520`. Cross-club, forged query, early-match extra links, cycles, replaced source objects, NULL match, wrong global owner and record/slot alias fail closed. The 4FA520 stage then only projects its source category exception; original `4FA510` and actual subsequent coefficients remain unexecuted. New test files cover the above, and the private original PE was separately checked against **13 additional 4056F0/4F3B10 instruction signatures** and 5 4056D0 signatures. This active WIP has not yet passed hosted exact-head tests, cannot be treated as live GameState integration or visible original match correctness.

**Next exact source producer:** the complete original branch-specific QWORD coefficient outputs of `0x40CBC0–0x40CF95` for all eight native dispatch entries, including fallthrough and successive re-queries; establish `0x4F8FF0→0x410FF0` genuine category from original tables and selected native object, then join original 0x5DA2F0 floating streams and user+670 callbacks. Continue true NEXT→PPreMatch modes0–3→PResults/return, actual all-original content and physical Windows11 Gate13–17 audits, none of which is complete.
