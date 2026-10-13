# Recovery590: authenticated native FastView row refresh and side-swap source

**Date:** 13 October 2026 KST. **Gate:** 13 (OPEN; Gates 14–17 also OPEN).  
**Main baseline:** `cda9847706ee4024106c5120440f0404f5a4bca1`, following merged PR #665.  
**WIP branch:** `worker/gate13-r1-fastview-row-refresh-source-590`. **Status:** BOUNDED ORIGINAL SOURCE, NOT LIVE INTEGRATION OR WINDOWS GUI ACCEPTANCE.

## Original identity / independent evidence

Owner-authorized original extracted `footballmanager.exe` from Daniel's private connected Google Drive, original SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` (4,714,541 bytes). Recovery590 locally read this exact authenticated PE32 **statically** using `objdump -D -M intel` and a separate PE RVA-to-file-offset signature probe. **40/40 original instruction-site probes matched**, with no original process launch. Local private original binary and scratch code are not committed.

Source callback path recovered earlier: original human `FastViewTactics` vtable at `0x7CACFC`; base `0x64F7A0` may call parent vft+0x0C and then vft+0x10; child `0x651AC0` may additionally invoke vft+0x10 when its own event and input argument are nonzero. Such callbacks are **not proven to mean one logical click**, and a future port cannot naively dispatch both and risk repeated edit commits.

## Source 0x52F690: non-passive row/list refresh

This source function is reached by first parent callback `0x52E3C0` for event IDs `0x8877AE..0x8877B8`; its 0-based argument is the visible row. Authenticated instructions show:

- `0x52F69B/0x52F6A1/0x52F6C1`: current club `screen+0x90`, native byte `screen+0xB45`, and selected player mapping `screen+0xB46+visible_row`.
- `0x52F6C8` and `0x52F6FB`: club roster count at global `0xA14BCC + club*1556`; if equal to 11, the additional-option loop is skipped.
- `0x52F6E6`: the selected club player guard at global `0xA14C0C + club*1556 + player*72` can enable bypass independently from nonzero `screen+0xB45`.
- `0x52F721..0x52F7F7`: for source roster slots 11 through count-1, read the mapped player index from `screen+0xB46+slot`. Skip it if `screen+0xB58+player` is zero; without bypass, also skip nonzero original club guard flag. Source separately calls name formatting at `0x635EC0`/`0x66876F`, builds original text/list entries at `screen+0x4768/0x4848/0x4864`, and writes the NULL terminal at `0x52F80D`. The strings and actual dropdown interaction are NOT reproduced by the new source projection.
- `0x52F818..0x52F880`: if `screen+0xA68 == 11`, redraw **all 11** controls at `screen+0x263C + 0x44*i` using virtual +0x3C. Also redraw all if both `screen+0xB44` and mapped player-specific `screen+0xB6D+3*player` are nonzero. Otherwise redraw only the clicked visible row when the mapped triplet flag is nonzero; with that flag zero, this path invokes no row redraw. This is **not** proof of mouse hit geometry, complete font behavior, list option selection, or a playable modal.

The WIP source projection `source_fastview_native_candidates_52f690` preserves the order/gates of accepted *player indices*, not the native formatted labels. `source_fastview_redraw_rows_52f690` preserves only native redraw target decisions. It fails closed on unsupported or missing caller-supplied source snapshots. It does **not** modify original GUI objects.

## Source 0x633020 validator / 0x6C2770 actual side mutation

`0x52EBD6..0x52EBE3` retrieves the original 11-row child status `+0x40` and skips all guarded work if it is nonzero. On status zero, `0x52EBE9..0x52EC0D` obtains the selected dropdown player index by indexing `screen+0x4848` with the native child `+0x3C`, then calls `0x633020` with source edit-list owner, visible-row mapped player, selected target, current club and 280-byte side payload. `0x52EC15..0x52EC23` **skips replacement on AL nonzero**; only AL zero reaches `0x6C2770`. The validator's internal list/visitor and possible side effects are **not yet fully understood**; treating status zero alone as edit permission would be incorrect.

Authenticated `0x6C2770..0x6C2829` shows a concrete *raw primitive* after that opaque gate:
1. Read native ordered count from side DWORD `+0x14`; locate the first index of the source and target player bytes in side `+0xF2[0..count)`, defaulting to zero in the original if not found.
2. Decrement side BYTE `+0xF0`, reset side BYTE `+0x104[target]` to zero.
3. Swap source and target player values in the two located `+0xF2` entries.
4. Copy source-player DWORD to target-player DWORD at side offsets `+0x18 + 4*player` and `+0x60 + 4*player`.
5. Adjust side BYTE `+0xF1`: increment if original club guard source flag is nonzero; decrement if original club guard target flag is nonzero, with 8-bit wraparound.

`source_fastview_6c2770_side_payload_value_only` makes an **immutable** projection of those native 280-byte side-buffer effects for bounded known-world inputs. It deliberately fails closed if either player is absent from the source ordering, instead of copying the original unsafe default-position-zero behavior without verified validator/world-state prerequisites. It **does not run** `0x633020`, mutate a live match, send a user mouse event, or append the later original edit node `0x6335D0`. At `0x52EC28..0x52EC90` the real handler allocates and queues a node and increments native edit count `screen+0x48AC`; that must remain a separate validated transaction, never inferred from the immutable buffer transform.

## Implementation/test disposition

The branch contains source-bounded projections in `reconstruction/original_fastview_tactics_selection.py` and new deterministic/counterexample tests in `reconstruction/test_original_fastview_tactics_selection.py`. The owner-original PE instruction probes are also opt-in tests under `FM2001_ORIGINAL_EXE`. Private local verification: **40/40 static original instruction signatures matched**. **Feature-branch Python unit suite and exact-head GitHub CI have not run**; no PR is open, no merge or current-game acceptance is claimed. Preserve the branch until a coherent source-backed mode2 vertical integration/review is ready under `WORKER_MILESTONE_BATCHING_POLICY.md`.

## Exact next action

1. Reverse full `0x633020` / `0x633240` / `0x6331A0` validator inputs, side effects, and AL polarity, plus original `0x6335D0` edit-node ownership and actual `0x651AC0` pointer/selection return. Use source-proven bounded tests, no synthetic click permission.
2. Resolve how 0x52F690's mutable original dropdown strings/options map to the native second-family control's selection and renderer. Connect actual modal owner/true two-sided writeback without double-dispatch; require negative/out-of-range paths.
3. Integrate live original mode2 only when source-complete; then original PResults event processing and normal management return. Verify actual Windows 11 GUI separately. Continue full Gate13, later Gates14–17, all selectable leagues/countries, 2–6 users, Save/Load and release audit. Do not mark Gate13 complete because the source helper tests pass.
