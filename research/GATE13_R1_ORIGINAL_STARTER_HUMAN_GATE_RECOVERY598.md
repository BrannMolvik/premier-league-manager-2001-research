# Recovery598: Original FastView starter human-owner and signed counter

**14 October 2026 KST.** Baseline merged main 35cc3eb97a148c0784d313dda73ac3c3e4daeda0 after PR679, Gate13 exact-head 38461414756 SUCCESS and asset/privacy 38461414722 SUCCESS. WIP worker/gate13-r1-original-starter-human-gate-598. Gates13–17 remain OPEN.

## Original source reference

Owner-authorized original footballmanager.exe, 4,714,541 bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Original statically disassembled via GNU objdump, **NOT launched**. Independent original opcode sites verified and pinned in opt-in regression; original exe not in Git.

Shipped native 0x4182F0 first XI status routine after 0x418160/0x418180/0x418170 calls 0x417340. **0x417340 is now source-resolved**, calling 0x417270, moving return club pointer to ECX then tail-jumping to 0x4037B0 global human-owner predicate. Source 0x417270 sign-extends **original player WORD+0x10**; a negative index selects global 0x874B94 fallback original club, a nonnegative index selects 0x874B90 + 0x2A8*index. Source 0x4037B0 scans the *entire* linked human-manager list 0x874C10+0x9CC, comparing original club DWORD+0x04 against each human's controlled club. It is not a random callback and does not test only the current human manager.

If 0x417340 yields a human-owned club, source 0x4182F0 skips 0x41EDF0. If not human, player DWORD+0x14 bit0x2000 also skips; otherwise original calls 0x41EDF0. That method reads original player DWORD+0x14 bit0x1000, returning without further source dereference if absent. If set, it clears bit0x1000 and sign-extends **DIFFERENT original player WORD+0x72** to select global 0x874B90 club 0x2A8*index or fallback 0x874B94. It tests selected owner DWORD+0x1A8 count with original **SIGNED JLE** at 0x41EE33; decrements count ONLY for signed-positive DWORD 1..0x7FFFFFFF, not for highbit 0x80000000..0xFFFFFFFF, zero or negative. The previous PR675 immutable helper incorrectly decremented any nonzero unsigned DWORD, now source-corrected.

## Source implementation and limitations

On feature branch, reconstruction/original_fastview_original_starter_human_gate.py requires original PR679 typed 592-byte native player record and actual source-supplied 680-byte club array/fallback, extracts separate signed player WORDs +0x10 and +0x72, uses original global all-human club registry to gate starter 0x41EDF0 and returns immutable status/counter intents. It does not demand player+0x72 count when original source skips it. reconstruction/original_fastview_player_world_writeback.py corrects signed-positive count. Focused tests in test_original_fastview_original_starter_human_gate.py cover true human gates, all managers, field index separation, highbit counter, fallback negative, skipped owner read, malformed pointers and opt-in private original opcode sites. .github/workflows/gate13-tests.yml includes new source and tests.

This is NOT authentic 0x5331C0 live FastView mode2, 0x533CA0 ordered actual native GameState write, PResults event ticks, original management return, Win11 GUI/installation proof or full selectable countries/leagues/multi-human/SaveLoad. Preserve Quick-only guard. Do not assert source projections are finished gameplay, close Gate13–17, or execute private original program without permission.

**Next:** exact-head CI and privacy review, then source owner of original match/player/club object 0x5331C0 modal and 0x533CA0 world commit with true original time/events/PResults. Only valid source-backed complete player journeys meet gate criteria.