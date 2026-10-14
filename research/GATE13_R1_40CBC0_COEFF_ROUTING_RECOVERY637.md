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
