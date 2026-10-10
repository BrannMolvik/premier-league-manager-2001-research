# Recovery 454 corrected by Recovery 455 — PMenu outside-pointer dismissal IS integrated in both hosts

_10 October 2026 KST. **MANDATORY ERRATUM / RETRACTION:** the first version of this audit mistakenly concluded `pmenu_app_pointer_dismiss` was never invoked. That claim was **WRONG**. Recovery455 inspected the full original and Codex host pointer-motion methods, verified the existing dismissal call, and corrected the underlying evidence. This file preserves the original report path to prevent later references from reviving the false finding. Strict audit-only; no game code, Codex branch, assets, saves, CI or Windows test._

## Why the earlier P0 latch diagnosis was wrong

The earlier audit focused on **`original_game_host.py::on_click`** and searched assignments that included initialization, while overlooking the actual pointer-motion handler **`on_fixtures_pager_motion`**. The mistaken conclusion that popup True could never reset during normal management interaction is invalid.

Verified both branch blob identities at Recovery455:
- **`main` host `reconstruction/original_game_host.py` blob `76820796c9bbf4a51b6972fd9f88099b734c1a91`**: `canvas.bind("<Motion>", self.on_fixtures_pager_motion)` around line507; `on_fixtures_pager_motion` starts around line1502; calls `pmenu_app_pointer_dismiss(int(event.x),int(event.y))` around line1528; sets **`pmenu_popup_active=False`** around line1529 and redraws. `<Leave>` also delegates to a synthesized outside-motion event.
- **Codex `codex/gate13-windows-playability-recovery`** host blob **`14c4436d600aa2a397779d6fe22cdc74b742bf26`**: `canvas.bind("<Motion>", self.on_fixtures_pager_motion)` around line517; the handler around line1736 invokes dismissal helper around line1772 and clears the state around line1773, then redraws; `<Leave>` uses `on_fixtures_pager_leave` in the same way.
- Shared original input helper **`reconstruction/original_pmenu_popup.py` blob `c14309a65fef0b926c0a95f6410b3166a6e122cf`** contains both `pmenu_open_press` and `pmenu_app_pointer_dismiss`; the latter **IS CALLED** on both branches. The previous report and some Recovery454 matrix/ledger statements that said “imported but never called” are therefore **retracted**.
- The normal **`on_click`** path does **not itself** call dismissal. But a pointer already moved outside the popup triggers the normal <Motion> route, so there is no justification for asserting the popup is permanently latched. Whether a *stationary outside click* must dismiss without any preceding motion is **NOT PROVEN**, and is not declared a source mismatch here.

## Original PBg pointer event and ownership evidence (retained)

The private canonical original `footballmanager.exe` has SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** (4,714,541 bytes). Reproduce disassembly `0x432970..0x4329E5` and original `.rdata` **`PBg` vft `0x7BEE8C +0x2C→0x432970`**. The native callback's original pointer/event semantics are not necessarily a click; the vtable slot and current Tk motion binding make it reasonable to test it as pointer behavior instead of forcing a click-only interpretation.

Original native `0x432970` accepts only source event arg0==0 and only when global modal-stack top **`0x877960::0x532960`** equals active popup **`0x876760`**. Under those guards:
- **x < 524** at `0x432992..` triggers native **`0x4329F0`** to close the popup;
- **y < 96 and x > PBg+0x52C** at `0x4329B5..` triggers the same close;
- both paths subsequently call PMenu header ID2 control virtual **`+0x98` with argument0** to restore control visual/pressed state.

The clean helper models the boundary `x>700`; the actual native source field `PBg+0x52C` and modal-stack guard should continue to be independently verified for equivalence rather than presumed correct because both host code and original source have superficially similar conditions.

## Current classification and Codex action

**SOURCE original dismissal: CONFIRMED. Clean-room motion dismissal: PRESENT and INTEGRATED in both branches. Code-level permanent popup latch defect: RETRACTED, FALSE.** Remaining aspects — moving out of popup vs clicking without pointer motion, modal ownership when other dialogs are open, frame reset, menus with unsupported child route, repeated open-close and cross-club Win11 acceptance — **UNVERIFIED**. Do not file a P0 bug claiming the helper is absent; this would divert Codex from genuinely missing source functionality.

Actual high-confidence Gate13 blockers still include: neither normal host `on_click` dispatches native EAMail direct header control or NEXT/MATCH progression, normal Squad 3/4/5 formation buttons are unhandled, Save Game0x321 and Return Main0x323 are not source-faithfully integrated, and only 3 of 28 PMenu children have partial presenter implementations. These are independent, true P0/P1 gaps documented elsewhere.

**Codex-only acceptance plan:** write normal Tk UI tests for `PMenu open → move outside to dismiss → reopen` in multiple club contexts, stationary click behavior as a separate source comparison, and header state reset after stack transitions. Source-control input tests should not be replaced by calls directly to the helper. **Do not write a redundant dismissal hook based on this retracted report.**

No original executable Windows run, CI, game changes, Codex branch merge or gate closure. Gate13 remains OPEN; Gates14–17 and verified Win11 release INCOMPLETE.
