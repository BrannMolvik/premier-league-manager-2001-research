# Gate 13 Recovery598: original FastView 0x533270 post-loop and complete value setup

**14 October 2026 KST.** Verified canonical main baseline `3005da1aa01d0b50162ab27614a46b161f8d2d1b` after PR677's source first two-sided 1556/280-byte setup passed exact-head Gate13 `38459243240` SUCCESS and asset policy `38459243165` SUCCESS and was merged. New unpublished feature branch `worker/gate13-r1-533270-post-loop-source-598`. Gates13–17 **OPEN**, no original execution or real Windows11 GUI acceptance.

## Private original source and call graph

Owner-authorized verified original `footballmanager.exe`, exact 4,714,541 bytes SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. GNU objdump static native x86 instruction trace, never executed; no binary or unapproved original content in Git. **28/28** independently checked PE opcode sites for first aggregate path matched actual owner file. The remaining 24-slot/reset opcode assertions are also pinned as opt-in private regressions, not evidence of running the game.

Original `0x533270` after its initial TWO full-side/tactic loops performs:
- **`0x5332BE→0x631270`** on match pointer. It reads source original match DWORD`+0xFF8`. The original `sub 18; neg; sbb eax,eax; and 2; add 2` returns EXACTLY 2 when value is 18 and EXACTLY 4 otherwise. Not an arbitrary user mode enum. `0x5332C8..` loops exactly that many times.
- **`0x631290`** receives selector value from `0x631270` and three native stack output pointers. Its original jump-table cases are 0,1,2,3; mode 2 takes case2 at `0x6313C9` and averages unsigned TWO DWORDs each from match `+0x1058/+0x105C`, `+0x10B8/+0x10BC`, `+0x1118/+0x111C`. Native 32-bit sum wraps modulo 2^32 before unsigned divide-by-two. Mode4 skips through `0x6314C8` WITHOUT writing those stack output DWORDs. Their authentic values cannot be assumed zero, and must be provided from verified original native stack state when the mode4 branch is modeled.
- **`0x6CC890`** unconditionally stores the original stack triple at native globals `0xA25940 + 4*i`, `0xA25950 + 4*i`, `0xA25930 + 4*i` for each of 2 or 4 iterations, preserving entries not touched (two untouched DWORDs per array in mode2). No gameplay effects are claimed from these globals in isolation.
- **`0x533305..0x533324`** runs 24 iterations ESI=0..23; native `0x62B6B0` zero-extends each **match BYTE +0x112D+i** into a DWORD stack output; original `0x6CA900` writes it to global `0xA257B8 + 4*i`. It never interprets these bytes as derived player scores without evidence.
- **`0x533326..0x53333E`** passes *actual match object POINTER +0xB60* to `0x6CBD80`, writing global `0xA258C0`; the code retains only a pointer-offset INTENT because real heap address is not known. It copies match DWORD`+0xB68` to global `0xA25874` through `0x6CA8F0`.
- **`0x53333E..0x533354`** reads original pointer global `0x877534`, pushes result of its null comparison (1 if NULL, else 0) and writes via `0x6CA910` to global `0xA2578C`.
- **`0x6C2890`** at `0x533354` clears two consecutive 18-cell *three BYTE per cell* native arrays. It writes exactly 108 zero bytes to global `0xA14828..0xA14893`, without resetting the nearby FastView tactical scratch that begins at `0xA14898`.

## Implementation and verification levels

New `reconstruction/original_fastview_native_postloop_source.py` implements:
1. Strict immutable statistics/global arrays, source-qualified branch2 vs branch4 uninitialized stack, native DWORD unsigned wrap and global slot width;
2. 24 source BYTE-to-DWORD slots, one match pointer-relative intent, one source match scalar, original global pointer-mode flag and exact 108-byte grid reset;
3. **A cohesive complete 0x533270 value projection** combining PR677's source-ordered two-sided roster/header + tactical stage followed by the above original post-loop stages. No state is returned until both sides and all post-loop original-read inputs pass validation. It *does not* fabricate original pointer graph, player identities, real original heap or stack values, or match transitions.

`reconstruction/test_original_fastview_native_postloop_source.py` exercises 2/4 branch, arithmetic overflow, unchanged global data, 24 slots, two human/AI side setup through previously integrated fixture constructors, absent native input, invalid buffer/type/country/pointer, immutable original inputs and opt-in original opcode sites. `.github/workflows/gate13-tests.yml` includes module and tests on exact-head PR execution.

Source correctness/projection tests and PE byte-checks are **NOT** the original process running, normal-mode2 player GUI, historical original-vs-port visual acceptance, PResults/tick or Windows11 release proof. Do NOT bypass existing original-game-host Quick-only guard or publish this helper as player-visible FastView completion. Current pre-modal external state can still lack native `0x875644` player object registry and authentic original `0x533BF0` actual source pointers and input; the following real modal and result/return remain unresolved.

## Exact next task / blockers

After review and exact-head tests, source-trace and integrate the ORIGINAL 0x533270 native match/club/player participant ownership (the original `0x631270` case4 caller-stack values require authentic source proof), original live 0x5331C0 pre-modal capture→actual 0x532650 modal→post-modal 0x533CA0 world player writeback; source-qualified 0x51F490/0x51F6D0 modal ownership and native partial time/event callbacks, PResults event and conditional return. Also restore original multi-country, 2–6 human SaveLoad and UI acceptance. Neither this milestone nor previous isolated source projections pass Gates13–17. Keep runtime heartbeat on `agent-runtime` and batch branches/CI at meaningful integration.
