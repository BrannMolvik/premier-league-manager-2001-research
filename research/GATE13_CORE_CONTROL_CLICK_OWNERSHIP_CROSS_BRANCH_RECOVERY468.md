# Recovery 468 — core management physical-input ownership audit

_10 October 2026 KST. Strict audit-only source/code comparison, not implementation or Windows 11 GUI acceptance._

## Exact branch and evidence boundaries

- Canonical `main` at start: `fc857236c64b4a99feea10d9fc7e2eb5454f8944`.
- Codex implementation branch `codex/gate13-windows-playability-recovery`: `0ae745d1b56f45cade460f03cd893849a2f53b45`, unchanged at this inspection.
- `reconstruction/original_game_host.py` blobs: main `76820796c9bbf4a51b6972fd9f88099b734c1a91`, Codex `14c4436d600aa2a397779d6fe22cdc74b742bf26`.
- Shared `original_pmenu_popup.py` blob `c14309a65fef0b926c0a95f6410b3166a6e122cf`; shared `original_pmenu_activation.py` `d5f546f5d82f554afc014443a874ad174a985280`.
- Original executable evidence is independently hash-gated in `GATE13_NEXT_NATIVE_INPUT_GATES_AND_CODEX_INTEGRATION_HANDOFF_RECOVERY457.md`, `GATE13_PMENU_ALL_28_NATIVE_DISPATCH_AUDIT_2026-10-09.md` and `GATE13_PMENU_NODE_DISABLED_FLAG_LOST_AT_POINTER_RECOVERY467.md`. Original root `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, 4,714,541 bytes.
- This recovery located the authorized ZIP in ChatGPT Library at `/FM2001/Original Source/` and materialized it privately, but trivial `echo OK` and Python startup returned `caas.internal.errors.ClientError`; **no fresh original binary hash/disassembly, code test, native launch or Windows GUI observation was possible**. The observations below are cross-branch code checks against the cited *earlier* original-source receipts, not newly proven native behavior.

## Live normal-mouse route matrix

| Original control and source owner | Source-proven event/action | main physical `on_click` | Codex physical `on_click` | Claim/confidence |
| --- | --- | --- | --- | --- |
| PBg header child **ID1: EAMail** | `PBg::0x432690` case ID1 `0x4326D6` invokes original PEAMail factory `0x482BF0(0x65)` and stack helper; shared input method `0x64F7A0` controls acceptance | **NOT WIRED**: no header ID1 dispatch in management handler | **NOT WIRED**: same, despite more header rendering | CONFIRMED missing physical route; original callback independently documented |
| PBg header child **ID2: MENU** | `0x4326AE` enters source popup/stack; `0x64F7A0` has control flag, parent and notification checks | **PARTIAL**: `pmenu_open_press` click can set popup active | **PARTIAL**: same | CONFIRMED geometry-only clean helper does **not** itself verify original control `+0x18` bit2-required/bit0x10-rejected or owner virtual conditions; actual reachable rejected MENU states UNKNOWN |
| PBg header child **ID3: NEXT/MATCH** | `0x4326A4` calls `0x432190(0)` when control event accepted; original right header at `(700,0,100,95)` | **NOT WIRED** | **NOT WIRED**: the newer code draws original `back_5` and uses `native_next_at_point` only for motion/hover, not progression in `on_click` | CONFIRMED P0 absence, not cured by isolated backend `advance_original_management_turn` |
| PMenu child **0x65: EAMail** | `0x47AD60→0x47AEC0(0x65,0)` constructs `PEAMail/CMessageList` under appropriate original node/input gates | Popup row recognized, destination snapshot raises unsupported | Same | CONFIRMED second independent inbox entrance absent, not merely header mail click |
| Squad **view events 3,4,5** | `PSquadScreen::0x4B8E70` binds paired/first/reserve owners then updates list and pitch | Source-accepted presenter seam only, no ordinary tab hit-test in `on_click` | Same; new animated tab graphics/drag pathway do not wire 3/4/5 tab presses; render guards still withhold views 4/5 | CONFIRMED P0 end-to-end first-team control gap |
| PMenu **0x321 Save Game** | `0x47C889→0x4802F0` native PSaveGame; source slot actions separate from modern `.fm2k` backend saves | Recognized, unsupported destination | Same | CONFIRMED P0 native UI/save path absent |
| PMenu **0x323 Return Main Menu** | `0x47C928→0x4C3280` constructs PStartMenu as a **side effect with null factory panel return**, not ordinary panel | Erroneously modeled via generic `open_panel`, then unsupported snapshot | Same | CONFIRMED wrong **action kind** on this exceptional source path |
| TeamSelect Start **2–6 humans** | Original count/current-user index and guarded modulo manager rotation separately documented | `front_end_session.py` rejects more than one selected club | Same identical blob `7ab004fd4e5ff56886b055d4dca7014447ec7405` | CONFIRMED P0 single-user backend/save model; intentional fail-closed rather than working multi-human |

The original MENU input acceptance condition includes control `+0x18` bit2 necessary, bit0x10 absent and further owner virtual behavior (`0x64F7A0`). The clean `pmenu_open_press(x,y,active)` checks only geometry `[599,699)×[0,95)` and inactive popup; the host invokes it without a dynamic source-control flag or modal-owner value. **PARTIAL / P1 conditional gap**: do not claim a currently reachable disabled MENU button is wrongly clickable without tracing the original flag producers or observing such a state. This is a new host-acceptance boundary worth testing, but it must not displace the P0 inbox/NEXT/formation work.

## Input conflict and false-positive checks

- **Do not resurrect the retracted Recovery454 permanent PMenu latch claim.** Both hosts bind motion/leave and call `pmenu_app_pointer_dismiss` to clear the popup. Whether one stationary outside click should dismiss before motion is separate, UNKNOWN source behavior.
- Codex's `_press_original_squad_row` is called before the popup row candidate, but `_ordinary_squad_drag_owner` explicitly returns `None` when `pmenu_popup_active` is true; do **not** report an unproven drag-through-popup defect.
- `original_management_presenter.py` integrates only child 0xCE, 0x25C and 0x25A as **partial** presenters. The other 25 child routes fail closed; original 28-case factory identity exists in prior source matrix, but many native owner/control graph details remain unknown.
- Existing host/unit/backend receipts verify independent components, not the mouse-to-native-action-to-persistent-game-state journey or original Windows11 behavior.

## Codex-only next implementation acceptance, ordered by player impact

1. **P0:** connect PBg ID3 with source control acceptance, manager/roster/modals and an atomic, *source-qualified* scheduler preflight; test pointer inside/outside and full before/after controller snapshot on refusal, then an actual match/PResults return. A true click must never convert an UNKNOWN original event wrapper to CLEAR by fiat. See Recoveries 457, 460–465.
2. **P0:** wire both distinct PEAMail entries (PBg ID1 and PMenu 0x65) to one original source-owned inbox, using verified user+0x6B4 linked records, filter/sort, native CMessageList and modal links. Test delivery/selection/read state and return; do not invent generic sorted news.
3. **P0:** implement accepted Squad 3/4/5 clicks and 11-slot pitch/list rebuild, original PSaveGame 0x321, exceptional Return0x323, and multi-human owner/save model behind the existing safety guard. Verify an on-screen end-to-end single- and two-manager journey, not direct controller APIs.
4. **P1:** for MENU ID2, derive original `+0x18` flags/owner predicates for a reachable disabled/rejected case before claiming the simple geometry helper is source-equivalent. Preserve working popup pointer dismissal; no cosmetic rewrite on this audit.
5. Run normal Windows11 mouse/keyboard, loading, timing and two-club acceptance tests when source integration actually exists. Preserve the original-compatibility-only modernization freeze.

**No implementation edits, Codex branch changes, CI dispatch, original binary execution, gate closure or release claim.** Gate13 remains OPEN. Gates14–17 and the full-original-scope Windows11 release remain incomplete.
