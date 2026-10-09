# Recovery 451 — PMenu Return to Main is a native start-menu transition, not an ordinary management panel

_10 October 2026 KST. Second independently verified Gate13 P0-A original-file sweep after Recovery451 EAMail delivery audit. STRICT AUDIT ONLY._

## Reproducible source facts

Verified original `footballmanager.exe` SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, using private original executable. Source `objdump -d -M intel` ranges `0x47AD60..0x47ADF0` and `0x47C8DD..0x47C951`.

Under its original selection-node bit0/bit1 guards, `PMenu` child `0x47AD60` calls native factory **`0x47AEC0(id,0)`** at `0x47ADB9`, usually receiving a non-null management panel to enter through stack helper `0x5ED2A0`. However the original factory **ID `0x323` (Return to Main Menu)** at **`0x47C928`** calls **`0x4C3280`** (RTTI source `PStartMenu`; see `research/GATE13_PMENU_ALL_28_NATIVE_DISPATCH_AUDIT_2026-10-09.md`) and jumps directly at `0x47C92D` to **`0x47C9C3`** cleanup, rather than constructing the panel object like ordinary cases. Thus source navigation semantics are distinct for this action. Its original unsaved-progress prompt, animation, and final window-owner stack behavior remain separately unverified.

The neighboring options remain separate original objects:
- **`0x321` Save Game** enters source `0x4802F0` / `0x480660` load-save UI owner with a distinct object;
- **`0x322` Settings** allocates 0x6EC-byte source UI object via `0x46A120` and `0x4802C0`;
- **`0x323` Return to Main** directly builds `PStartMenu` with `0x4C3280`, without an ordinary panel presenter.

**Classification: EXACT source ID→action distinction; PARTIAL lifecycle and user-visible return.** It would be incorrect to route all three actions through the same generic management-panel presenter or invent a modern settings UI.

## Direct main/Codex code comparison (current recovery)

Re-read `reconstruction/original_pmenu_activation.py` on both branches. The **same exact blob** `d5f546f5d82f554afc014443a874ad174a985280` implements `resolve_pmenu_row_action`. It treats every accepted **child** as `action_kind="open_panel"` with `panel_factory_arguments=(menu_id,0)`, including `0x323`, although a native direct start-menu transition is a different action category.

Re-read the management presenters separately: `main` blob `2c23adf12a3378a53793e5a8036d3dc950034dad`; latest Codex blob `8cee4bca0686475b4b0a41922b9600afe70879ed`. Both integrated `build_management_panel_snapshot` branches handle only Squad `0xCE`, League Fixtures `0x25C`, League Tables `0x25A`, and **raise/fail-close for other child IDs**. Consequently `0x323` recognized as a menu item is NOT the original ordinary-click route back to `PStartMenu`. This is an **implementation-coverage gap**, not evidence that fail-closed behavior silently changes saves or that the app unexpectedly performs a return. The root/child menu matrix and 25 additional destinations remain separately enumerated in Recovery438.

## Codex-only acceptance contract

- Preserve original PMenu state guards and distinguish **`expand_root`**, ordinary **`open_panel`**, **`save_game_original_ui`**, **`settings_original_ui`**, and **`return_to_pstartmenu`**. These suggested action-kind labels are *clean-room design descriptions*, not original class names; choose naming suited to existing architecture.
- Route original child `0x323` to source-compatible `PStartMenu` and correct window/manager lifecycle after verifying original prompt/exit semantics. Do not bypass save/exit confirmation if the source has it, or claim reliable save/load from the current unintegrated child0x321.
- Test ordinary PMenu click path and return to New Game/TeamSelect with at least two club states; assess window stack, gameplay/saves and menu selection. Keep unsupported routes explicitly fail-closed until source-verified.

No code implementation or Windows11 GUI receipt was produced. **Gate13 OPEN, Gates14–17 and original-scope verified Windows11 release INCOMPLETE.**
