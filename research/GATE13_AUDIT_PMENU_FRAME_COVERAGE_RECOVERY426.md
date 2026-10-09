# Recovery 426 — PMenu animation/frame coverage and integrated-menu audit

_9 October 2026 KST. Audit-only continuation from `main` commit `e39831930156ec19cf1f764176d92662809a8cc8`; compared read-only Codex branch `cbbb15d9242883f2f5185a002b0a5e7443a53ba1` and prior canonical original-source reports. No code/assets/tests/save/schema/implementation branch modification and no gate closure._

## A. Confirmed PMenu renderer is static while the native source owns multiple animation frames

- **Direct reconstruction evidence:** `reconstruction/original_management_canvas.py::_row_art` obtains `arrow_state = pmenu_arrow_state_from_bits(row.arrow_state_bits)`, then calls either `pmenu_title_arrow_source_row(arrow_state, 0)` or `pmenu_child_arrow_source_row(arrow_state, 0)`: both pass **literal frame zero**. This rendering file does not invoke `pmenu_arrow_update`. `build_management_pmenu_render` composes one static overlay snapshot.
- **Direct host evidence:** `reconstruction/original_game_host.py::_draw_management_host` renders/caches by resource identity + immutable `frame.presentation.menu` snapshot, reuses it across unchanged redraws. Neither `_row_art` nor this host's PMenu render path provides a time/frame input.
- **Existing independently source-traced original control contract:** `research/GATE13_PMENU_CHROME_TRACE.md` Recovery 148 maps original transition `0x652780`, periodic update `0x6527F0`, state selection `0x652AE0`, direction bit `0x8`; child arrow has state 0/1 **11 frames each**, state 2 **1 frame** (23 physical 29px rows); title has state 0 **11 frames**, states 1/2 **1 frame** (11 physical 58px frames). `reconstruction/original_pmenu_chrome.py` contains bounded functional `pmenu_arrow_update`/frame offsets but that contract is not linked to live PMenu state/time.
- **Classification:** **CONFIRMED missing dynamic renderer integration**. Whether the original reaches an advancing frame in a particular user input/hover event, and its exact event-to-bit/timing scheduling, remains **UNRESOLVED** pending original interaction/clock trace. Do not assert a specific blue/arrow animation appearance or invent timing. A source-qualified implementation would bind exact state bits, frame transitions, and timer update to the live presenter, then invalidate the render cache when warranted, preserving original pixels.

## B. Confirmed broad menu coverage boundary

Source-backed static `PMENU_ROOT_NODES` contains **9 roots**. Their 9 child arrays contain exactly **28 child nodes**: Team 6; Transfers 3; Calendar 2; TABLES 2; Analysis 3; ADMIN 5; ACCOUNTS 3; EAMail 1; GAME OPTIONS 3. The separate five-entry team-order subarray is *not* counted because its main-tree ownership is unresolved.

In `reconstruction/original_management_presenter.py::build_management_panel_snapshot`, the only integrated panel conditions are:
1. `SQUAD_PANEL_CODE` (`0xCE`);
2. `LEAGUE_FIXTURES_PANEL.menu_id` (`0x25C`);
3. `LEAGUE_TABLES_PANEL.menu_id` (`0x25A`).

Every other child raises `OriginalManagementPresentationError`. Hence **3 of 28 static child routes currently have live integrated presenters, and 25 do not**. This is a **CONFIRMED code coverage limitation**, not proof that all 28 original actions must be separate full screens or that all are required specifically for Gate 13. The original functional-scope Gate-17 mission cannot be claimed complete from a 3-panel host.

**Concrete EAMail impact:** PMenu root `0x1` and child `0x65` appear in the recovered menu topology/English.idx; selecting that child obtains a source-accepted child action but the presenter lacks `0x65`, so cannot display inbox. The host catches `Exception` in its `on_click` PMenu handler and records only `last_status`, leaving the incomplete menu pathway. The original `MPMEAMail` message event classes are **not** an inbox panel constructor or global message ordering proof. Preserve fail-closed behavior until panel/factory/queue/owner/source geometry is recovered.

## C. Original input/timing and static boundary

Original PMenu row input path is already source-backed to `0x64F7A0` and concrete callbacks `0x47AC60 / 0x47AD60` with [0,201)x[0,29) local hit and control flags (`0x2` required, `0x10` guard). The Tk host dispatches mouse-press to the bounded action. This does **not** establish native periodic arrow update, original keyboard support, full child factory behavior, or popup dismissal event equivalence. Current `reconstruction/test_original_pmenu_popup.py` exercises synthetic open/dismiss and source geometry; `test_original_game_host.py` tests fake-Tk popup/render cache, not the shipped executable's visual timing.

**Potential cache issue, not an existing confirmed regression:** once true original frame state is recovered, including neither frame nor clock in the cached snapshot would incorrectly reuse static PNGs. Correct renderer design is for the implementation owner to prove and carry the native frame state in its cache key; no code changes here.

## D. Source access and exact next audit

The existing trusted private original source ZIP remains recorded under `research/ORIGINAL_SOURCE_LOCATOR.md`. In this Recovery 426, local `container.exec` and private `python.exec` both failed at launch even on a trivial command with `caas.internal.errors.ClientError`; do not claim fresh hashes, new original disassembly, tests, or Windows GUI acceptance. Previous audits `RECOVERY424` / `RECOVERY425` remain canonical for the Squad row-background and EAMail dispatch address leads.

**Next source-backed audit priority:** (1) when private execution is restored, hash-verify canonical PE and trace final `PSquadPlayerRow` `0x7C57BC`, `0x443E70 +0x2C` row wrapper, control frame/selection state and exact owner transforms; (2) read `0x47AEC0` low dispatch guard and **candidate only** `0x47CA04` for EAMail `0x65`, resolve actual case/RTTI; (3) verify native PMenu `0x6527F0` update scheduling and `0x432970` popup-dismissing event semantics; (4) report exact address/CFG/owner/timing findings to Codex. Maintain existing original-only freeze, **audit-only** worker role, Gate 13 OPEN, and no Gate-17 full release claim.

_This is a non-implementation, isolated source-review checkpoint; no CI was dispatched for markdown-only evidence._
