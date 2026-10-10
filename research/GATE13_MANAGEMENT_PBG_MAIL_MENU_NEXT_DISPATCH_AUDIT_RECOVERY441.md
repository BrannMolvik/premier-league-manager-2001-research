# Recovery 441 — original shared PBg EAMail/PMenu/NEXT action ownership

_9 October 2026 KST. Continuation of Daniel's P0 original core-game-function audit after EAMail modal and Squad tab verification in this recovery. No implementation, asset, save, CI, merge, Codex branch or Windows playtest. Canonical local original `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` was reverified before inspecting `0x430940..0x4309C9`, `0x432690..0x432707` and `0x432190..0x43254B`._

## Confirmed original owner and three action cases

Native RTTI independent `.rdata` check for vftable `0x7BEE8C`: COL `0x7E0808`, TypeDescriptor **`0x819CC8` `.?AVPBg@@`**. Concrete owner `PBg` virtual **`+0x10 -> 0x432690`**; parent acceptance virtual `+0x0C -> 0x42DE00` constant-true. This class owns an original shared management background/control tree, not a menu-row panel.

The original `0x432690` method reads clicked child object's source **event/control ID `+0x20`**, subtracts 1, then distinguishes exactly:

| Native child ID | Handler/case | Exact native source action | Original meaning/source proof limits |
| --- | --- | --- | --- |
| **1** | `0x4326D6` | compares current window stack `MyWindow::0x532960` to original inbox singleton `0x876758`. If not already active, calls `0x482BF0(menu_id=0x65)` on PMenu owner `0x876760`, then enters the returned content object via **`0x5EC060`** with original stack flags. | **Direct EAMail opening from PBg header/action**, distinct from expanding EAMail root and choosing child0x65 in the PMenu; exact caption/pixel hit region and resulting inbox data still require a separate source control contract |
| **2** | `0x4326AE` | checks whether the top panel is already `PMenu` singleton `0x876760`; otherwise calls window-state helper **`0x5329D0`** and **`0x5EBEA0`** to bring the original PMenu onto the stack. | Original **PMenu popup activation**; this proves action owner beyond a mere decorative menu-header image |
| **3** | `0x4326A4` | pushes argument **0** and calls original member routine **`0x432190`**. | Original **NEXT/MATCH/date progression action entry**, separate from its rendered state/bitmap/hover; actual match/no-match gameplay downstream requires additional source tracing |

Source control registration for NEXT at `0x430992..0x4309C9` creates child **`PBg+0x524`**, registers callback with source event ID **3**, and invokes original bitmap/control initialization **`0x5D3900`**. Original graphic `FM2001_Art/Generic/Background_buttons/back_5.444` has 100×380 source dimensions and a source-proven four-frame 100×95 crop, with original native view bounds **`(700,0,100,95)`**; those resource/render details are corroborated by the existing `reconstruction/original_management_next.py`, not inferred from the glyph name.

## Verified NEXT source producer boundary, not yet end-to-end game result

`PBg::0x432190` is more than a redraw callback. In its first block `0x432190..0x432241` it accesses original static date `0x9847FC`, calendar globals `0x8755D4/0x8755E4`, the original current user through **`0x4139D0`**, user `+0x5B4`, and source schedule/lookup helpers **`0x4079D0, 0x615D10, 0x510A20`**.

The code conditionally selects source match/simulation follow-on paths: `0x432241..0x4322ED` reaches checks and source-bound gameplay methods `0x4F3DC0`, `0x407FE0`, `0x404A80`, `0x404A70`, `0x409C90`, `0x405A20`; `0x432340..` branches through fixture/match callbacks and an original `0x42C6C0` game-user state update / window stack interaction; `0x4324B9..0x4324F7` can reenter a `PSquadScreen` panel through `0x482BF0(menu_id=0xCE)` and `0x5ED2A0`; `0x4324FE` calls `0x431F70` for a separate scenario.

**Classification:** original click-owner/control-ID/action dispatch is **CONFIRMED**; original action function includes real source state/competition/advance work and one return-to-Squad path; exact match/no-match branch conditions, effects, save/replay, transition timing and source-visible acceptance remain **PARTIAL/UNKNOWN** until full CFG/object-meaning trace and original multi-club runtime receipt. Do not assume `0x432190` can be replaced with a generic “advance one day” callback or that all returns land in Squad.

## Main and Codex reconstruction gap and priority

- In `main`, `reconstruction/original_game_host.py` does not integrate a native NEXT button/action into the default original-look management `on_click` path and recognizes the PMenu opener only.
- In current Codex branch `8702eded049643220bf4b590d8d45c2197cfd42a`, `original_management_next.py` and `_draw_management_next_control` render the original NEXT/MATCH icon/caption and mouse-motion hover logic sets `management_next_flags`; **`on_click` does not dispatch `(700,0,100,95)` to a native `0x432190`-equivalent gameplay route**.
- Both still have no PEAMail destination, so neither provides the original PBg direct inbox action1 either. The PMenu action2 is partially integrated, but dynamic popup/event timing remains separate evidence.
- **Severity P0 CONFIRMED normal gameplay-path mismatch.** This distinction cannot be covered by a developer-only match simulation command or pure visual screenshot acceptance; a user cannot activate NEXT/MATCH through the standard original-looking management control and observe the original match transition.

## Minimum implementation handoff to Codex — no changes here

1. Preserve PBg's **three distinct original control IDs** and their current-panel stack guards. Source-qualify the physical press acceptance for PBg+0x524, normal mouse coordinates/scale, enabled/hover/pressed-state transitions and match availability. Do not implement by treating an ordinary press as unconditional advancement.
2. Trace `0x432190` exact source clock/match branch, next-step side effects, initial condition and navigation into/out of fixtures/match/management. Wire NEXT to this proven producer chain only after corresponding clean runtime semantics are validated, and test the **real native-look click path** end-to-end.
3. Treat header EAMail action1 as a separate source-backed route, opening the real `PEAMail` via original panel and stack owner. Audit its control rectangle/resources and recurrence guard before integration; absence of inbox remains a distinct blocker.
4. Test PMenu action2 activation/dismissal and no duplicate stack pushes. Prove source state transitions across Southport and an independent club/state, not Southport-specific. Codex owns implementation and Windows 11 acceptance; audit worker changes no game code.

Gate 13 remains OPEN, Gates14–17 and full original shipped-scope Windows 11 release incomplete.
