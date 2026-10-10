# Recovery 441 — native pointer-to-PSquadScreen button events 3/4/5 source route closed

_9 October 2026 KST. Independent audit-only source check following recovery440/earlier P0-C. The original canonical executable was SHA-256 verified to `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Only research evidence and ledger updated, **no game implementation, Codex branch, CI, original program launch or Win11 playtest**._

## Original class, control IDs and registration — direct byte evidence

- The source `PSquadScreen::0x4B5720` constructor owns three embedded 0x54-byte control objects at offsets **`PSquadScreen+0x37A4`**, **`+0x37F8`**, **`+0x384C`**.
- At `0x4B5872..0x4B58C5` the first child is registered with parent `PSquadScreen` and ID **3** and bound to source `squad_but_anim.444` through `0x652C50`. At `0x4B58CA..0x4B591C` the second is registered with ID **4**, and `0x4B5921..0x4B5977` the third with ID **5**, likewise bound to the original 73x25 source control. Exact English.idx source captions are `2490/2491/2492` = `1ST & RES`, `1ST FORM`, `RES. FORM`, already cross-checked in `research/GATE13_SQUAD_RESOURCE_CORRELATION.md`.
- Their concrete vtable is **`0x7BE814`**, with vtable **`+0x08 -> 0x64F3C0`**. The latter stores both source **ID into control `+0x20`** and **parent pointer into control `+0x24`**. Native vtable **`+0x6C -> 0x652CF0`** owns pointer input; it is **NOT** the ordinary `0x64F7A0` direct vtable owner. This distinction matters for the original control's extra drawable state.
- `PSquadScreen` class final vtable **`0x7C5CA4`** has `+0x0C -> 0x42DE00` (constant true acceptance) and **`+0x10 -> 0x4B8E70`** (the original Squad view action handler). These addresses are re-read from native original `.rdata`, not inferred from clean-room unit tests.

## Exact original input dispatch chain

1. Source control input virtual **`0x652CF0`** checks internal image control/flag state at **`+0x50`**, then with a concrete pointer event calls **`0x64F7A0`** at `0x652D03`. `0x64F7A0` requires source control bit **`0x2`**, rejects flag **`0x10`**, then follows native control acceptance/owner path. Its exact geometry comes from the verified original control bound at 73×25, not an arbitrary Tk rectangle.
2. If input is accepted and the callback objects exist, **`0x652D1D..0x652D29`** reads control **`+0x24` parent** and calls its virtual **`+0x0C`**, which is `PSquadScreen::0x42DE00` true.
3. **`0x652D4B..0x652D59`** reads the same parent and invokes its virtual **`+0x10`** with the **actual clicked control object** as argument. With native `PSquadScreen` vtable this is **`0x4B8E70`**.
4. `0x4B8E70..0x4B8E95` reads the clicked control's **`+0x20` ID** and branches exactly on **3**, **4**, **5**. Event3 sets combined first/reserve view, event4 sets first-team formation and global `0x87674C=0`, event5 sets reserve formation and global `0x87674C=1`. The concrete view-handler code rebinds native list/pitch owners and invokes original refresh/layout helpers including `0x653320` and `0x4B9310`.

**Classification: EXACT original source-owned pointer event acceptance → native parent callback → original 3/4/5 action and view-state producer, subject to source input flags.** This extends Recovery438 from an isolated action method into its real original selectable control owner. The original native screen-space input geometry at **(37,171)**, **(113,171)**, **(189,171)** for three 73×25 buttons is corroborated by PSquadScreen's parent offset (0,79) and source-local top-control positions (37,92), (113,92), (189,92). The source flags/conditional render frames after 4/5 selection, detailed formation/pitch bytes, pointer hover/release timing and keyboard equivalents are **not fully source-closed** and should not be invented.

## Main and current Codex branch comparison

Main `reconstruction/original_squad_resources.py::squad_view_transition(3/4/5)` and `OriginalManagementPresenter::source_accepted_squad_view_transition` describe source-accepted state transitions but `reconstruction/original_game_host.py::on_click` does **not** hit-test those actual original tab rectangles or invoke `apply_source_accepted_squad_view` for an ordinary management click. The current Codex implementation head `8702eded049643220bf4b590d8d45c2197cfd42a` adds animated button art and row background logic, but **still does not route normal tab presses to the transition**, and `_draw_squad_top_controls` returns 0 for selected controls 4/5. Existing test `test_source_accepted_squad_view_seam_changes_only_proven_container_state` invokes `apply_source_accepted_squad_view(4)` directly; that is NOT a real user mouse path acceptance test.

**Status: CONFIRMED P0 functional mismatch in main and Codex.** The original three Squad mode selectors are ordinary interactive controls; this is not an optional view modernization. Preserve the source control's native accepted event envelope (flags, click, owner, current modal/PMenu) rather than wiring a generic clickable rect that bypasses the source predicate. After dispatch, native 4/5 source UI requires more original view pixels/callbacks; don't regard a button label that changes while the formation area remains blank as finished.

## Concrete owner handoff to Codex (no edits from audit)

- Add source-qualified original screen-space 73×25 press hit-test for three native controls at (37,171), (113,171), (189,171); derive display scaling via existing native pointer normalization, respect source bit0x2/guard0x10 and popup/modal ownership. Original native `0x652CF0` is the correct owning wrapper before `0x64F7A0`, and `PSquadScreen` `+0x10` is the owner callback.
- Wire accepted event IDs **3/4/5** through the already modeled source-accepted presenter transition, but do not invent post-transition rendering. Trace original renderer/list membership/pitch and full enabled/hover/update semantics before claiming 4/5 are playable. Validate both Southport and another independent club/state, with a direct Tk click-path test rather than a manually invoked source-accepted seam.
- Continue core P0-D NEXT/MATCH native event owner/trigger/return and P0-E menu animation/latency comparison; no extra cosmetic resource audit unless needed for these core functions.

Gate 13 remains OPEN; Gates 14–17 and verified original-scope Windows 11 release remain incomplete.
