# Recovery589: original FastView tactics native dual-callback and guarded input ownership

Date: 13 October 2026 KST. Active validation Gate 13. Canonical main baseline at investigation start: `5972020c8e11342a81e396731628786ab3336c3b`. Continuing the existing `worker/gate13-r1-fastview-native-pointer-hit-owner-588` feature branch (was already 2 commits ahead of main), **not** opening a new PR solely for this source checkpoint.

## Original-source identity and verification scope

Owner-authorized original private extracted-disc `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, downloaded privately from the verified original Drive source ID `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`. Independently compared length/digest and static native PE bytes. **26/26 independently checked direct native byte/VTABLE sites passed** (16 initial and 10 further instruction checks; overlapping test sites deliberately consolidated in the new opt-in source regression test). No original executable launch, interactive input observation, game save mutation, screenshot acceptance or Windows 11 GUI playtest. Proprietary bytes are not stored in Git.

Existing accepted Recovery588 constraints remain: four 11-row FastViewTactics original arrow artwork/child-owner arrays = 44 arrow inputs with exact per-row high IDs; eight 61..68 scroller controls; two separate 11-row high event families; 70-DWORD working side payload; actual match modal and result/return remain unintegrated.

## New native input facts, distinguished from mouse behavior

**Native child event/owner binding is explicit.** Original routine `0x64F3C0` copies original event-ID argument into control `+0x20` and original screen/parent pointer into control `+0x24`, then returns. The already recovered actual FastViewTactics parent VTABLE at `0x7CACFC` has **two distinct original callbacks**:
- `vft+0x0C = 0x52E3C0` (a native event-receipt/guard callback).
- `vft+0x10 = 0x52E3F0` (the complex previously traced actions/event dispatcher).

**Generic input's first-stage parent callback is not guessed.** Native base `0x64F7A0` checks `[child+0x18]` flag **bit1 set and bit4 clear** at `0x64F7A5..0x64F7BA`; otherwise returns zero at `0x64F854`. When source event `child+0x20` and the relevant caller's passed parameter are nonzero, `0x64F7D3..0x64F7DC` invokes screen `vft+0x0C` using the exact stored `child+0x24` owner, then rejects on a zero result. On successful continuation `0x64F818..0x64F81C` invokes the screen's separate `vft+0x10`. Native child worker `0x651AC0` first calls the generic base via `0x651ACB`, then performs selection/indexing and an additional conditional screen `vft+0x10` call at `0x651B4E..0x651B55` (again only with actual source event and passed parameter nonzero). This is a **source path to the actual modal's handler**, not proof about physical pointer-down/up ordering, double activation, graphics hit region, or screen lifetime.

**0x52E3C0's 11-row special case is distinct from its return value.** It reads `event+0x20`; for exactly `0x8877AE..0x8877B8` calls `0x52F690` with integer row `eventID-0x8877AE`. For every event including outside this family it returns 1 (`0x52E3E0`). Do NOT infer out-of-range IDs are rejected or that `0x52F690` simply draws a passive preview. It reads current side/club and mapped-row globals and loops through further conditional records; its full source effects are not yet qualified.

**Fifth-family +0x40 status is a necessary gate, not an Apply permission.** The original getter `0x651AB0` only reads BYTE `[child+0x40]`. `FastViewTactics::0x52EBDC` calls it on `screen+0x263C+0x44*row`; `0x52EBE3` skips entire subsequent `0x633020`/potential `0x6C2770` source path when returned byte is **nonzero**. Zero merely permits later validation (not proof mutation is legal or completed). Source child worker `0x651AC0` writes status1 if returned selection/index equals native sentinel `0xFFFF` and status0 otherwise (`0x651B0B..0x651B1E`), with additional child redraw/index effects. This status must **not** be renamed “selected”, “up” or “down” until the original producer/result semantics are traced.

The earlier `0x651E30 → 0x651BA0 → 0x64F380` is the image-control setup/rectangle route. The user-triggered callback is on the verified **distinct** `0x64F7A0 → vft+0x0C → vft+0x10` and `0x651AC0 → vft+0x10` routes, under the gates described above. Native `0x651F40` bit2-selected frame WORDs from the preexisting two WIP commits remain bounded source frame selection; they are not independently classified as hover/down/up art.

## Bounded implementation and self-checks

In the existing active branch:
- `reconstruction/original_fastview_tactics_selection.py`: no-live-state helpers for the original base flag preconditions, callback `0x52E3C0` 11-row event special-case and +0x40 byte gate; identifiers for both callbacks and original owner/child offsets. No clicked-event simulation, mutable player effects or fake PResults.
- `reconstruction/test_original_fastview_tactics_selection.py`: strict signed/bool/value counterexamples; 11 real IDs, unrelated IDs still accepted by first callback rather than rejected, flag bit1/bit4 matrix; status0 only a necessary condition; opt-in original source PE bytes and exact VTABLE pointers. Required CI is not yet claimed on this unfinished branch; authenticated original static checks passed independently.

### Next exact source-backed task

1. Trace **full `0x651AC0` selection return and `0x64F7A0` input coordinates/pointer producer** to establish when +0x0C and +0x10 are invoked and avoid duplicate event delivery in the Windows-compatible port; record actual hit regions and sprite state/frames.
2. For fifth family, reverse original `0x52F690` and `0x633020` current-player/staff/side preconditions plus **two unmapped original high-ID 11-row producer control arrays** (`screen+0x265C + 0x44*row` and `screen+0x1A34 + 0x40*row`). Reconstruct only evidence-proven side effects.
3. Build an **actual source-faithful live mode2 FastViewTactics** with proper linked-list edits, the nested modal/outer match once-only, real PResults then normal management return and original-window player journeys, and verify true Windows 11 GUI. Continue other incomplete original modes, 2–6 humans, all originally playable countries/leagues, Save/Load and Gates 14–17 without declaring any gate complete early.

**Status:** source-only partial audit, source verification independent; gameplay integration MISSING; player-visible/Win11 acceptance NOT performed. Gate 13 and all later gates remain OPEN.
