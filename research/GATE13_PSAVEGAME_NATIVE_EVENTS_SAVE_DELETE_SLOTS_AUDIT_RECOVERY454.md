# Recovery 454 — native PSaveGame events, actual original .sav writes and slot deletion

_10 October 2026 KST. Independent source-first Gate 13 P0-A original playable navigation/save audit; strict **AUDIT ONLY**. Codex remains sole implementation owner. No game code, original assets, user saves, CI, merge, branch implementation or Windows 11 gate acceptance._

## Live checkpoint, original executable and reproducibility

- Confirmed main **`9224fdf0deca71922eb753f76a63ef198d506f55`**, `research/CURRENT_STATE.md` binding P0 game-functionality and fidelity audit, and `agent-runtime` **`worker_role=audit_only`, `implementation_allowed=false`**.
- Latest Codex implementation branch `0ae745d1b56f45cade460f03cd893849a2f53b45` unchanged during this audit. Previous Recovery453 verified PMenu child0x321 → native `PSaveGame` RTTI vft0x7C34D0, base `PLoadSaveGameBase` vft0x7C35D4 and original panel rect(0,0,760,500).
- Private original `/mnt/data/fm2001_private/footballmanager.exe`, **4,714,541 bytes**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, reverified with local `sha256sum` and `objdump -d -M intel`. Original bytes, disc and raw disassembly are not committed.
- Reproduce the precise instructions with `objdump -d -M intel`: `0x47AEC0..0x47AF2D`, `0x47C928..0x47C9E3`, `0x4C53E0..0x4C594C`, `0x50D730..0x50D74D`, `0x50D9B0..0x50DA35`, `0x50E1F0..0x50E2A2`, `0x50E2B0..0x50E2F0`. The original `objdump -p` Win32 imports independently identify `0x7BD0D4=DeleteFileA`, `0x7BD0D0=MoveFileA`. Original RTTI includes `.?AVPSaveGame@@`.

## A. Native PSaveGame dispatch table is source-specific — not generic Save button

Original `PSaveGame` final vtable **`0x7C34D0+0x10→0x4C53E0`** reads native child event ID from `event+0x20`, subtracts 1 and range-checks 7 entries (`0x4C53FA..0x4C5407`). Its absolute jump table is at **`0x4C5950`**:

| Original child event ID | Original jump target | Verified action effect / limitation |
| --- | --- | --- |
| **1** | `0x4C591D` | gated update of list/control `PSaveGame+0x738` using current `+0x730` selection, only if another selected field differs; no file I/O in this target |
| **2** | `0x4C591D` | same list-control update |
| **3** | `0x4C591D` | same list-control update |
| **4** | `0x4C5941` | no-op exit from this event callback |
| **5** | `0x4C5726` | sets **`PSaveGame+0x174=-1`**, updates native selected control, refreshes text/name control `+0x964`; later branches copy/compare selected name with original global `0x874BA0` |
| **6** | **`0x4C540E`** | source **save/write path** with an eligibility guard for a non-new slot, name copy to global `0x874C14`, new-slot allocation/scan if `+0x174==-1`, original game UI synchronization and **`0x50D9B0` actual serial/write helper** |
| **7** | **`0x4C5864`** | source **slot deletion/compaction path** gated by original `0x4506B0`, then invokes `0x50E1F0(selected_slot)` to delete selected save and renumber later files, updates `PSaveGame+0x174=-1` and UI controls |

**Classification:** actual event-ID jump table, native record/list vs write vs delete call edges are **EXACT**. Source child labels, exact physical hit rectangles, keyboard acceptance and every follow-up/return behavior remain **UNKNOWN**; do **not** map 1/2/3 to invented labels or assume 4 is never emitted by UI.

## B. Native original save files and actual writing

- Original helper `0x50D730` emits path through C-style format literal **`0x827F54 = "%s\\games\\%d.sav"`**, with root supplied by global `0x87BAE8` and a numerical slot argument. This is the source directory/name policy; original C runtime/current working path and Windows 11 install location cannot be inferred from the literal alone.
- `0x50D9B0` calls `0x50D730(slot)` and opens via runtime `0x66A164` with original mode literal **`0x827FA0="wb"`**. On failure, it calls original `0x450990` with literal error **"Unable to open save game file for writing (a BAD THING(tm)!"** at `0x827F64`. On success, it starts serializing manager-owner state `0x874C10` via `0x413E20`, loops **all `0x8755E4` registered managers** through `0x413B10→0x426FE0`, writes original global/manager/competition fields using source `0x667FA7` and related helpers. Full binary format/readback/atomicity is **not** source-closed in this audit.
- Original `0x50E2B0`, when a new slot is chosen, probes numbered `%s\\games\\%d.sav` from slot0 via source `0x66A164` mode **`0x81E168="rb"`**, incrementing until a file open fails and returning the first unavailable slot. It is **not** a generic system file picker or timestamp-based automatic directory.
- Original `PSaveGame+0x174` is the concrete selected slot, initialized to `-1` for new entry (source `0x4C5370`), then set to `0x50E2B0` result in event6 on that path. Existing-slot overwrite takes a separately gated path. User-visible confirmation, filename collision policy beyond this source, save file corruption, and platform permissions remain open.

**Critical**: original `0x50D9B0` is the actual save writer; implementation of a source-looking Save button without this state/slot behavior **is not functional original Save Game**.

## C. Native deletion renumbers save slots; slot identity is positional

The original **`0x50E1F0`**, called by event7 after a native eligibility check:

1. builds selected save file path `%s\\games\\%d.sav` and imports **`DeleteFileA`** via original IAT **`0x7BD0D4`** at **`0x50E214`**;
2. probes subsequent numbered slot filenames using `0x50D730` and `"rb"` at `0x50E226..0x50E245`. For each existing slot, it builds the preceding slot's path, calls original IAT **`MoveFileA`** at **`0x50E26B`**, then advances to the next;
3. adjusts global original selected slot **`0x8755F4`**: equal to deleted index→`-1`, greater than deleted index→decrement by one at `0x50E271..0x50E297`.

This is a **real source slot compaction/renumbering transaction**. Clean-room behavior that leaves orphaned gaps or ties persistent selection to an unshifted slot number would diverge. Note that source does not independently prove per-call `DeleteFileA`/`MoveFileA` success/failure handling; Windows permission and overwrite safety require implementation tests. Do not test by deleting user files; use dedicated synthetic temporary saves and sample-game state.

## D. Additional high-value original PMenu Return to Main source control-flow nuance

A bounded recheck of the original `PMenu` factory `0x47AEC0` confirms it initializes `ESI=0` at **`0x47AEE3`**. The special native child **`0x323`** case **`0x47C928`** calls `PStartMenu::0x4C3280`, then jumps straight to cleanup **`0x47C9C3`** *without setting ESI*; source cleanup **`0x47C9D2`** moves ESI to return EAX. Thus the factory **returns NULL after invoking the PStartMenu transition** on that original path. Caller `0x47AD60` checks for NULL at `0x47ADC3..0x47ADC5` and bypasses the ordinary child panel push at `0x47ADE4→0x5ED2A0`.

**Original semantic rule:** Return to Main creates/enters `PStartMenu` as a **side-effecting special command with no ordinary panel return object**. Treating it as a failed panel load or trying to push the factory return as a normal child would be wrong. This is more precise than merely saying it calls the start menu; it explains the native call-return guard that prevents accidental stack injection.

## E. Exact current main/Codex mismatch and minimal owner handoff

Verified code:
- Both main and Codex share exact `reconstruction/original_pmenu_activation.py` blob `d5f546f5d82f554afc014443a874ad174a985280`: every accepted child classified `action_kind="open_panel"`.
- Both `reconstruction/original_management_presenter.py::build_management_panel_snapshot` recognize only three partially integrated child IDs: Squad0xCE, LeagueFixtures0x25C and LeagueTables0x25A, failing closed on all other panel routes. Thus **PMenu Save0x321, Return0x323, original EAMail0x65 remain unusable by ordinary native-look clicking** regardless of sophisticated backend work.
- Latest Codex `original_game_host.py::on_click` handles PMenu popup row hits and 3 partial panel navigation, but does not hand child 0x321 to native PSaveGame action/event dispatch, or 0x323 to PStartMenu special command.
- Codex implementation owner should **first provide ordinary input-to-original action routing**, then PSaveGame slot selection/write/delete/return with source-proven filename, preserving serialized manager identity and all users, and separately Return0x323 as null-return special command. Add non-destructive temp-directory integration tests for create/overwrite/delete/compact/reload, two managers/clubs, and actual Windows11 GUI/save receipts before gate acceptance. A developer-only serializer or mock button does not meet Gate13.
- Audit role cannot implement/call CI, merge, close gates or simulate an actual Windows desktop UI. The verified source observations are actionable but do not mean any broken original control was fixed.

**Gate 13 OPEN; Gates 14–17 and verified original-scope Windows 11 release INCOMPLETE.**
