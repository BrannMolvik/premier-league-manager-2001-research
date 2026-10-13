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


## Recovery590 follow-up: polymorphic validator and original edit-node identity

A second independent 19/19 authenticated original PE instruction-site check passed locally (59/59 combined static checks in this recovery). This does not validate a live match or GUI.

The original native 0x633020 function first invokes 0x633240 at 0x633040, short-circuiting to zero when that result is zero (0x63304E/0x633058). Otherwise, it allocates/transfers temporary linked nodes, loops the source records, invokes 0x6331A0 at 0x633107 and OR-accumulates the result. The native 0x633240 and 0x6331A0 use virtual slot +4 of polymorphic original linked-list records. Function 0x6331A0 seeds scratch state through 0x6348E0 and obtains a result via 0x634DF0. The full polymorphic predicate identities, validator effects and ownership are still UNKNOWN. A substituted validator that returns zero unconditionally would incorrectly permit 0x6C2770 and must NOT be used.

The original queued replacement edit-node constructor 0x6335D0 calls 0x633400 to establish the source-player index in object DWORD +4, assigns original vtable 0x7D7F90, then records destination-player index in object DWORD +8. The caller 0x52EC28..0x52EC90 appends this source 12-byte object into the original edit list after running 0x6C2770, incrementing screen+0x48AC. The node itself does not prove the eventual modal/match consumer, persisted replacement, or synchronous two-sided writeback; those are the exact next source dependencies. No live queue implementation or Windows 11 acceptance is claimed.


## Recovery590: exact native auxiliary child selection and second-callback conditions

An additional 13/13 independently authenticated original PE instruction probes matched 0x651AC0..0x651B55 (now **72 original static instruction-site probes** matched during this recovery, across three sets). Original 0x651AC0 invokes base 0x64F7A0 first; base return zero aborts with no dropdown selection or parent second callback. On nonzero base return, native child vft+0x98 and +0x9C obtain a dropdown owner, then its collection virtual+0x20 produces an integer selected index. A **0xFFFF sentinel** sets child BYTE +0x40 to 1 and child handler result 0; otherwise source sets status0, saves index to child DWORD +0x3C, optionally updates associated rendering owner +0x2C from row-array +0x38[index*8] and calls 0x64F600; handler result becomes 1. Crucially, the native second parent vft+0x10 callback occurs **after either sentinel/non-sentinel branch**, if the child registered event field +0x20 and its supplied input callback argument are both nonzero. It does not require a successful selected index, nor imply a legal player swap. When status is 1, the separately observed 0x52EBDC edit path aborts. There can also be an earlier base vft+0x10 call: do not synthesize a one-click-only dispatch without mapping the original input producer.

The WIP module now contains an immutable and strictly typed `SourceFastViewAuxChildInputOutcome` / `source_fastview_aux_child_input_outcome_651ac0` with tests for base-denied, sentinel, both callback gates, source status/index, and invalid inputs. **This is only bounded control-flow projection, NOT live input handling**. New tests are committed but WIP suite and exact-head CI have not yet run. Next source target remains polymorphic 0x633020/0x6331A0/0x633240 predicates and native UI input/selection consumer, followed by actual mode2 match, results, and management return.
