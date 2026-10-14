# Gate13 Recovery605: original League rank full-key ties must remain unresolved

**14 October 2026 KST.** Canonical main after reviewed PR697 `0054ba0a30ffb9f740108769552699e8ca9b7105`; source-authorized private `footballmanager.exe` 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` independently byte-verified locally. Static original x86 disassembly ONLY, original executable never launched. Branch `worker/gate13-native-league-rank-tie-failclosed-605`.

## Shipped original exact owners

Original Scottish League vtable **0x7C9C94** (v+0x3C=0x6170A0, Scottish synthetic cycle interception) and generic League vtable **0x7C9AC0** (v+0x3C=0x616FC0) each have original virtual **+0x38=0x4F4720**. At source 0x4F4723 the method passes comparator **0x4F45E0** to qsort original 0x668DA4 over the actual native League+0x34 list with League+0x38 count. Source 0x4F4940 calls that v+0x38 sorter on an unranked owner (League+0x40 bit0 CLEAR), writes each native member rank+0x28 as 1-based position, and sets the cache bit.

Original 0x4F45E0 comparison reads two original native team/League membership records. It orders the recovered source numeric ranking fields as points (`3*win+draw`) DESC, games played ASC, goal difference DESC, goals for DESC, goals against ASC, then dereferences actual club short-name pointers and lexicographically compares original byte strings. Original native string loop 0x4F46CF..0x4F46F3 STOPS at the first 0x00 byte. If *every* source field including the native C-string is equal, the comparator returns **zero**, so the resulting physical native qsort order depends on an original array/insertion state that clean-room Python club ID ordering does not prove.

Locally read-only verified **14/14** exact opcode sites and **both** Scottish/generic vtable+0x38 pointer DWORDs in private original PE, using the exact opt-in test included in this branch. This is **SOURCE-VERIFIED** bounded comparator behavior, not original GUI observation.

## Actual normal gameplay discrepancy

`LiveProceduralLeagueState.exact_ranking` already failed closed for unresolved *numeric* ties without a source short-name key, but **silently accepted equal full source keys** by Python stable sorting if two distinct clubs shared all the source numeric fields and short name. The same error occurred in `GameState.refresh_procedural_league_group_position_rankings` for original type-3 cross-group pool selection. That could publish an unsupported rank / UEFA qualifying or subsequent Cup participant even though original source qsort tied. A short name containing a native NUL byte could also create falsely distinct names because Python bytes compared beyond the terminator.

Additionally, `GameState.record_procedural_league_result` directly called `str(...).encode("cp1252")` **after a real match result had already been recorded**, so an unrepresentable club short name could raise `UnicodeEncodeError` on the real ordinary result path and leave an unexpected partial result/exception instead of retaining the already recorded match with ranking pending.

## Source-qualified live fix

- `reconstruction/procedural_league_state.py`: exact ranking refuses a duplicate original numeric + NUL-trimmed CP1252 short-name key. Rejects unsupported provider type instead of casting to fake bytes; retains symbolic ranking pending and clears an existing stale published type-2 ranking.
- `reconstruction/game_state.py`: cross-group type-3 rank stage uses the existing CP1252 resolver, NUL-trims before comparison, rejects duplicates and unencodable names, and never publishes a type-3 order unsupported by original source. Ordinary `record_procedural_league_result` now uses safe existing byte resolver, recording results without a Unicode encoding crash.
- `reconstruction/competition_state.py`: applies the same original native C-string comparison rule to the already otherwise exact Premier League table and its rank; stops using suffixes *after* NUL as fictional ordering evidence.
- `reconstruction/test_procedural_league_state.py` and `reconstruction/test_competition_state.py` regress identical full keys, embedded-NUL byte suffix distinctions, original CP1252 source order, already-published stale rank withdrawal, normal `GameState` type-3 consumer pending/accepted states, and harmless malformed short name after a normal result. Opt-in private original PE source proof includes both original League vtables. Gate13 workflow registers the changed live code/tests.

**Acceptance boundaries:** Feature-branch hosted CI/asset/privacy review still pending. No original native qsort after-equal physical order, source club-pointer registry, live Scottish ranking recomputation/pair-generation `0x617500`, original match modes/real R1 results and Windows11 GUI playtest yet. Gates13–17 remain OPEN.

**Next:** After exact-head tests and reviewed integration, use source-qualified actual League rankings and original shared RNG/solver to produce Scottish post-split half-group pair arrays `+0x74/+0x7C` in the actual live game schedule, then native +0x4F2B24 club getter/world registration and regular NEXT→PPreMatch/all modes→PResults→return. Do not reopen earlier PR697 or reconstruct unknown original state with fallback club IDs.
