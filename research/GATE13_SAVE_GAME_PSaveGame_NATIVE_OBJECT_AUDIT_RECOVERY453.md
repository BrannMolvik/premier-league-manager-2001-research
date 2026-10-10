# Recovery 453 — original PMenu Save Game is a concrete PSaveGame class and 760×500 source panel

_10 October 2026 KST. Independent P0-A original game functionality audit, continuing Recovery453 EAMail links. AUDIT ONLY; Codex implementation branch untouched._

## Original executable and checkpoint

At audit start, main `d5de9e20e9e0991f0e05ea43977ab8ebb35b966e`; source-driven EAMail link checkpoint now appears on main as `research/GATE13_EAMAIL_NATIVE_HYPERLINK_PLAYER_TEAM_MODAL_AUDIT_RECOVERY453.md`. Codex still at `0ae745d1b56f45cade460f03cd893849a2f53b45` when checked. Original authorized private `footballmanager.exe` size 4,714,541 SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, reverified. No original game process executed.

Original x86 source reproducibility: `objdump -d -M intel --start-address=0x47C889 --stop-address=0x47C930 footballmanager.exe`; `0x4802F0..0x4805A8`; `0x480660..0x480686`. MSVC RTTI on original vtable `0x7C34D0` has COL `0x7E40C8`, TypeDescriptor `0x81CB88` and `.?AVPSaveGame@@`. Base vtable `0x7C35D4`, COL `0x7E4118`, TypeDescriptor `0x81CBA0` `.?AUPLoadSaveGameBase@@`.

## A. Native PMenu Game Options 0x321 is not just a generic PLoadSaveGameBase panel

The original factory for PMenu ID **`0x321` (SAVE GAME)** at `0x47C889..0x47C8D8`:
1. **allocates 0x9FC bytes**, reads original context pointer **`0x8755F4`**, passes it to the `0x4802F0` constructor;
2. `0x4802F0` constructs a `PLoadSaveGameBase` foundation via `0x448310`, initializes fields (including `+0x64=0, +0x68=0, +0x70=-1` and `+0x174=context`), and installs base `PLoadSaveGameBase` vtable **`0x7C35D4`** at `0x480323`;
3. **at `0x480590`, installs FINAL derived vtable `0x7C34D0`**, whose original RTTI unequivocally identifies **`PSaveGame`**, then returns this actual UI object. This closes Recovery438's “PLoadSaveGameBase-derived UI, derived identity pending” classification;
4. the factory calls the native layout helper **`0x480660`** with four arguments `(0,0,16,0)`. This wrapper invokes `0x653320` with source **`x=0,y=0,width=0x2F8=760,height=0x1F4=500,aux=16,flags=0`** at `0x48067E`. This is a concrete original panel layout, not a modern settings page.

**Classification: EXACT source allocation, concrete PSAVEGAME class identity, member initialization and native 760×500 layout.** It does NOT prove a functional slot list, Save/Overwrite interaction, serialization success, input/return, save location or original Windows 11 GUI reproduction.

## B. Source distinction from 0x322 settings and 0x323 main-menu return

The adjacent original PMenu cases are independently distinct:
- `0x322 SETTINGS → 0x47C8DD` creates a **0x6EC-byte** custom UI through constructor **`0x46A120`**, then calls `0x4802C0` with its own layout parameters;
- `0x323 RETURN TO MAIN MENU → 0x47C928` directly calls **`PStartMenu::0x4C3280`** then jumps to factory cleanup **`0x47C9C3`** without any ordinary `PSaveGame`/management-panel object. See `research/GATE13_PMENU_RETURN_START_SPECIAL_CASE_AUDIT_RECOVERY451.md`.

The source has different construction, event, lifecycle, and return owners for all three menu children. Don't map them to one generic settings pane or global main-window button.

## C. Current clean-room gap and Codex handoff

Verified current original-looking management presenter supports only partial Squad `0xCE`, League Fixtures `0x25C`, League Tables `0x25A`; the shared `original_pmenu_activation.py` labels all other accepted menu children as `open_panel`, but unintegrated `0x321` fails closed. This prevents false save-success claims, but means **normal user Save Game through the original UI is still unavailable**.

**Codex only:** implement the actual source-qualified `PSaveGame` panel, save-slot data/confirmation and serialization after tracing original descendants and real save/load, including current manager/club state, without substituting a generic Python file dialog. Integrate ordinary menu click via 0x321, preserve native 760×500 layout, modal/window owner and life-cycle; test a genuine saved and reloaded club and at least one additional user manager on Windows 11. Read existing reconstruction save coverage before modifying it; a tested background save API alone does not close the original-facing Save Game panel.

**Status:** full original Save/Load gameplay correctness UNKNOWN; Windows11 acceptance absent. No code, assets, saves, CI, merge or gate closure. Gate13 OPEN, Gates14–17 and verified original-scope Win11 release INCOMPLETE.
