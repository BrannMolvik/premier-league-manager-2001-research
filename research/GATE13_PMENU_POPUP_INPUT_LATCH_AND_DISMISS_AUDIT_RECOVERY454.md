# Recovery 454 — original PMenu popup dismissal is source-implemented but the live host leaves its popup state latched

_10 October 2026 KST. Second source- and live-Codex-backed Gate13 original navigation audit after native Save-Game events. STRICT audit-only, no gameplay code, assets/saves, CI, Codex edits, branch merge, gate change or Windows11 runtime claim._

## Source and branch identity

Beginning main at `9224fdf0deca71922eb753f76a63ef198d506f55`, Recovery454 SaveGame report checkpoint at `2e9bf9a9626f9e0fb37aa5e97c8e65c9ec2dbc0b`. Current Codex head `0ae745d1b56f45cade460f03cd893849a2f53b45` (unchanged throughout) and authoritative `research/CURRENT_STATE.md` PMenu gameplay-first, agent-runtime audit_only. Canonical authorized original `footballmanager.exe` **SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** independently rehashed. Bounded disassembly original `0x432970..0x432A05` and `0x47AD60..0x47AEAB`; no original program execution.

## A. Original PBg actually has an overlay-aware pointer dismissal callback

Original **`PBg::0x432970`** processes an event only for its own accepted branch when first argument is zero (`0x432974..0x43297C`). At **`0x43297C..0x43298C`** it checks original stack owner **`0x877960::0x532960`** equals active popup **`0x876760`** before accepting outside-pointer dismissal. This is an explicit source **PMenu-top modal-stack guard**, not an unconditional 'any click closes menu'.

Within that guard, the original interprets a pointer coordinate object:
- **x < 0x20C (524)** at `0x432992..0x43299C` invokes **`0x4329F0`** to dismiss the original popup;
- **y < 0x60 (96)** and **x > source `PBg+0x52C`** at `0x4329B5..0x4329C9` invoke the same `0x4329F0`;
- after either accepted dismissal it calls **original ID2 PMenu header control+0x98 with 0**, restoring the header's pressed/state behavior at `0x4329A1..0x4329B5` or `0x4329CE..0x4329E2`.

`PBg+0x52C` derives from the native right/header control transform. The clean-room helper has already modeled its bound as `x>700`, but that runtime value is not independently measured in this audit, so retain the **source field**, do not invent edge semantics or a globally unconditional 'click any outside area closes'. This is **EXACT** original predicate/stack/coordinate dispatch, with original physical event producer/button-down phase still PARTIAL.

## B. Both main and Codex already possess a source-backed predicate — but live host never calls it

Exact source module **`reconstruction/original_pmenu_popup.py`** has the **same blob `c14309a65fef0b926c0a95f6410b3166a6e122cf`** on main and Codex. It declares:
```python
def pmenu_open_press(x, y, *, active):
    return not active and 599 <= x < 699 and 0 <= y < 95

def pmenu_app_pointer_dismiss(x, y):
    return x < 524 or (y < 96 and x > 700)
```
The host imports **both** functions on both branches (source file around **line106**), but `pmenu_app_pointer_dismiss` has **zero call sites** inside `reconstruction/original_game_host.py` (ordinary live source, not just tests). Main host blob `76820796c9bbf4a51b6972fd9f88099b734c1a91`; Codex host blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`.

Live `on_click` (Codex **lines2287–2542**, management subtree around **2335–2418**) sets `self.pmenu_popup_active=True` on a source-accepted menu header click. If the popup remains active and **no recognized menu row candidate** is found, the code states “PMenu popup owns input; no source-bounded PMenu candidate row” and returns. It does **not** evaluate `pmenu_app_pointer_dismiss`, reset `self.pmenu_popup_active=False`, queue `redraw`, or restore header control state there.

A global scan of **every line** in each host source finds assignments to `pmenu_popup_active=False` **only in initialization and management-start/reset flows** (Codex about lines404 and1773; main about392 and1529); the only transition assigning True is the header click. Thus no ordinary management PMenu outside-click can unlatch the live popup variable, and even selecting an integrated child leaves it True unless a separate reset route fires.

**CONFIRMED code-level functional defect:** the existing original-looking PMenu popup can become **latched open** in the normal game host. It intercepts outside clicks while active, instead of exposing the source's qualified dismiss action. This is separate from recognized-but-unintegrated 25 menu child actions; even the three partial panels can be obstructed by the overlay state. **NOT asserted:** original Windows UI input timing, exact popup draw frame and every mouse-up event state, since no original Windows process or Tk GUI acceptance test was run.

## C. Concrete Codex-only implementation/acceptance handoff

1. Integrate the already recovered source `pmenu_app_pointer_dismiss` in the *ordinary management input* flow, respecting original **active popup/top-of-stack/owner** predicates; restore PMenu header ID2 control state when the original qualifies, not on every random click.
2. Track the **popup overlay state separately from selected menu child**. An accepted child switch should not be blocked by a permanent overlay or by an unsupported child loader exception. For real native child `0x323` Return to Main, preserve original side-effecting `PStartMenu` command with null factory return (Recovery454 SaveGame audit).
3. Add real physical input regression tests `open → outside dismiss → reopen → choose Squad/Fixtures/Tables → click underlying panel`, with x boundary cases 523/524 and PMenu rect 599..698, plus upper-right cutout and at least two clubs/managers. An ad hoc call to popup helper without invoking host `on_click` is **not** sufficient.
4. Existing code already has correct composite 100×95 PMenu source rect and a correct helper; do not spend new work re-tracing already resolved static bitmap dimensions. Prioritize real click path, then missing native inbox button and NEXT progression.

**Severity:** P0-E menu responsiveness / P0-A navigation. It does not complete functional Gate13. Gates14–17 and original full Windows11 release remain incomplete. No implementation/CI/playtest performed by audit worker.
