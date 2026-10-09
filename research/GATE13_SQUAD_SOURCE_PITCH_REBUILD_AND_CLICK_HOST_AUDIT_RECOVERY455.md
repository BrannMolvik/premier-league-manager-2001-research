# Recovery 455 — original Squad controls 3/4/5 rebuild pitch state and live Codex only draws combined view

_10 October 2026 KST. Continue strict **AUDIT ONLY** Gate13 P0-C original-functionality mission from Recovery454. No reconstruction source edits, original copyrighted binaries/assets, user saves, Codex implementation branch changes, CI, merges, Windows11 execution or gate closure._

## Identity and controlled source boundary

- Checked latest `main` `33fb6589b124990a181ea8344657b5cd6b2f0ba7`, `research/CURRENT_STATE.md` (prioritize core clickable original PMenu/inbox/first-team/NEXT), and agent runtime `audit_only/implementation_allowed=false`. Codex implementation head **`0ae745d1b56f45cade460f03cd893849a2f53b45`** is unchanged.
- The actual authorized private `footballmanager.exe` was SHA-256 rechecked: **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, size **4,714,541 bytes**.
- GNU `objdump -d -M intel` reproduction: original `0x4B5872..0x4B5977`, `0x652CF0..0x652D76`, `0x4B8E70..0x4B909B`, `0x4B60A0..0x4B62FE`, `0x4C1890..0x4C18BE`. This report adds proof to the original pointer source report `research/GATE13_SQUAD_TAB_NATIVE_POINTER_OWNER_AUDIT_RECOVERY441.md`; do not duplicate its work.

## A. Rechecked original genuine three-button pointer acceptance

The source constructor registers concrete `PSquadScreen` embedded buttons and IDs **3 at +0x37A4, 4 at +0x37F8, 5 at +0x384C**. Original `0x4B58C3` sets first local control x **0x25=37**, y **0x5C=92**, next `0x4B5918` x **0x71=113**, y92, last `0x4B5970` x **0xBD=189**, y92. Each is 73×25 from source graphic owner, and `PSquadScreen` origin **(0,79)** results in screen rectangles:

| Original control | Native screen rectangle, half-open | Event/control index | Destination |
| --- | --- | --- | --- |
| 1ST & RES | **[37,110)×[171,196)** | 3 | Combined first/reserve lists |
| 1ST FORM | **[113,186)×[171,196)** | 4 | First-team formation container + pitch |
| RES. FORM | **[189,262)×[171,196)** | 5 | Reserve-team formation container + pitch |

The actual concrete control input virtual **`0x7BE814 +0x6C→0x652CF0`** is **state conditional**:
- if control's **`+0x50` nonzero**, at `0x652D03` calls `0x64F7A0` on the native event and checks source accept result, retains original parent/ID, calls **parent vft+0x0C** (native `PSquadScreen::0x42DE00` true) and then **vft+0x10→0x4B8E70`** (the actual handler);
- if control's **`+0x50` zero**, at `0x652D70` dispatches **`0x652B50`** instead; this is not the same verified accepted-click path. This branch should not be modeled as unconditional click acceptance.
- original generic `0x64F7A0` independently gates bit0x2 and rejects bit0x10, as Recovery441 already recorded.

**Classification: EXACT** button IDs, pointer owner and local/native screen geometry; physical GUI input phase and control+0x50 lifecycle are **PARTIAL/UNKNOWN**.

## B. Original formation view modes have shared nontrivial pitch/roster update *after* selection

`PSquadScreen::0x4B8E70` clearly handles child ID minus three. **This is more than toggling a title bitmap.**

- **ID5 RES. FORM** `0x4B8E9B..0x4B8F0C` binds **reserve source list `PSquadScreen+0x1030`** to active roster/formation owner **`+0x3714`**, sets reserve source flag/mode to2, recalculates its owner geometry `0x653320`, triggers native related UI control `+0x3744` vft+0x34, invokes `0x4B9310` and writes **`global 0x87674C=1`** before entering the common refresh.
- **ID4 1ST FORM** `0x4B8F11..0x4B8F7F` similarly binds **first-team list `+0x130`** to the same owner **`+0x3714`**, adjusts local source mode to2, calls the same layout/UI recalculation methods and writes **`0x87674C=0`**.
- **ID3 COMBINED** `0x4B8F84..0x4B9024` separately binds the **first team to `+0x3714`** and **reserve team to `+0x3744`**, lays out both, invokes `0x4B9310` on the first with literal parameter **0x25=37** and on second with **0x1A2=418**, then joins the same common refresh. This is a real dual-list view. It does not merely disable the formation pitch.
- **All three** paths merge at `0x4B9027`. Native source calls `0x64F600` on **both roster owners** and the adjacent `+0x3774` control, then `0x4B60A0(0)` on native pitch/controller **`+0x1F30`**. It calls **`0x4B6270` exactly eleven times** with consecutive indexes **0..10** (`0x4B904D..0x4B9059`), then invokes pitch/controller virtual **`+0x48` with argument1**, recomputes native synthesized view objects via `0x4C1890` and `0x4B6910`, and queues global UI update `0x877960::0x532C10`.
- Native pitch/controller **`0x4B60A0`** changes its behavior based on **`0x87674C`**: reserve mode nonzero immediately routes to **`0x4B5ED0`**; first-team mode0 operates on stored selected roster, word array at list `+0x244` and source player list global **`0x875640`** with club/user context. Subsequent indexed update `0x4B6270` also branches on **`0x87674C`**, reading first-team selected player IDs or calling `0x4662A0` for reserve-mapped entries, then **writes owner-relative per-slot layout/state fields and queues `0x64F600`**. This proves *different data ownership* for the two formation modes. It does **not** prove the exact rendered shirt positions or the semantics of all source player data fields.

**Source fidelity consequence:** the switch to a 1ST/RES formation is a multi-owner state/data/layout refresh. A clean `squad_view_transition` mask alone does **not** reproduce it. The ten-plus-one slot loop is **0..10 exactly**, not a guess from normal football rules. Actual team membership, drag/drop results and original player pixels remain UNVERIFIED.

## C. Updated live implementation comparison — two independent missing stages

Read original code at the latest Codex head:
- `reconstruction/original_squad_resources.py` blob `356b6cd5428fadc423bb12a58f46396949893639` has three **source-accepted descriptive** transitions `squad_view_transition(3/4/5)`, representing combined, first formation, reserve formation and source team index. It explicitly does not claim pointer-event qualification or result pixels.
- `reconstruction/original_management_presenter.py` Codex blob `8cee4bca0686475b4b0a41922b9600afe70879ed` offers `source_accepted_squad_view_transition`; neither that seam nor `original_game_host.py::apply_source_accepted_squad_view` is a normal Tk pointer-click action.
- `reconstruction/original_game_host.py` Codex blob `14c4436d600aa2a397779d6fe22cdc74b742bf26` **does not call** `apply_source_accepted_squad_view` or hit-test three 73×25 controls in its `on_click`. Its **`_draw_squad_top_controls`** at about line1461 **returns** if selected `transition.control_id != 3`, `_draw_squad_rows` around line1497 also rejects non-3, and further Squad render/animation paths `_squad_tabs_live` explicitly require **`squad_view_control_id == 3`**. These are deliberate fail-closed seams, but **4/5 are not implemented original formation modes**. It is misleading to call the tabs "working" because the source art animates or a developer-only seam changes container selection.
- Both main and Codex share the original 3/4/5 source transition model and neither integrates true formation modes through normal gameplay. Codex restores additional artwork and source fonts but does not yet reproduce the new native 11-slot refresh pathway.

**Status: CONFIRMED** source original input/formation owner and host code-level absence. **UNPROVEN** runtime exact input animation/flags, full formation layout/per-slot pixel effects, roster membership mutations, true Windows11 user acceptance, two-club parity. Not a gate close.

## D. Required Codex actions in order, without architectural reset

1. **Restore actual user input** with source-qualified hit-testing at the exact three rectangles, respecting modal/PMenu ownership, native `0x652CF0` state branch and ordinary mouse sequencing; source event IDs3/4/5 must reach the existing presenter transition *only* on proven acceptance.
2. Implement and source-audit active `+0x3714/+0x3744` owner rebinding, source formation team selector **`0x87674C`**, and **11-entry pitch refresh**, preserving original player membership, selected rows, model-state updates and exact roster/pitch resource rendering. Until then keep post-view pixels fail-closed rather than inventing abstract dots or modern pitch diagrams.
3. Test the **real click sequence** `Squad combined → 1ST FORM → RES. FORM → combined`, both with roster data and after a save/reload, at least two clubs/managers. Ensure PMenu outside-click dismiss correctly releases input (Recovery454) and PBg direct mail/NEXT buttons are not intercepted by stale overlay state.
4. Verify original Windows11 game host's visible pixels, interaction latencies, window transport and actual match readiness, not just isolated callbacks; Codex owns implementation/test and audit owner does not dispatch CI or close gates.

**Gate13 OPEN; Gates14–17 and verified original-scope Windows11 release INCOMPLETE.**
