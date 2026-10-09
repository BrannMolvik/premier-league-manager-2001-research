# Recovery 440 — PEAMMessage native event routing, Escape forwarding and detail geometry

_9 October 2026 KST. Independent Gate-13 original-file fidelity audit of the already-identified EAMail path. Strict AUDIT ONLY: no game code/assets/saves changed, no Codex branch changes, CI, merge, gate closure, original game execution or Windows 11 acceptance._

## Scope and reproducibility

- Re-read current main/CURRENT_STATE and `agent-runtime` first: Daniel's P0 original core menu/inbox/first-team/NEXT mission remains authoritative, `worker_role=audit_only`, `implementation_allowed=false`.
- Canonical **privately held original** `footballmanager.exe` SHA-256 was independently rechecked during this session as **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. The original disc, executable and disassembly remain **outside Git**.
- Disassembly reproduction, if the authorized original binary is available: `objdump -d -M intel --start-address=0x473500 --stop-address=0x4735d6 footballmanager.exe`; `0x4735e0..0x473770`; `0x473870..0x473882`; `0x6539f0..0x653a0c`; `0x659650..0x65966c`; `0x4712f0..0x471375`; verify vtable pointer dwords at `0x7C2714` and original import-address table `0x7BD2D8`. For original `.text`/`.rdata` VA data the file offset is `VA-0x400000`.

## A. PEAMMessage detail action IDs 5..16 are now partitioned EXACTLY by original bytes

The original, RTTI-identified `PEAMMessage` virtual table at `0x7C2714` has:
- `+0x10 -> 0x473500`: native bounded detail event callback;
- `+0x20 -> 0x4735E0`: separate pointer/control-category event processing;
- **`+0x34 -> 0x473870`**: keyboard-code handling below.

At `0x473512..0x473529`, `0x473500` computes `event_id - 5` from original event object `+0x20`, rejects values outside `0..11`, reads **original 12 bytes** from `0x4735C8`:

```text
00 00 00 00 00 00 00 01 02 02 02 00
```

The three actual addresses stored in the jump table `0x4735BC` are `0x473530`, `0x473573`, `0x473543`. Thus the exact source dispatch is:

| Event ID | Native target | Source-visible operation; do NOT invent a button label |
| --- | --- | --- |
| **5..11, 16** | `0x473530` | passes 16-bit event ID to `0x6539F0`, forwarding a `WM_USER` notification to the owner |
| **12** | `0x473573` | passes `PEAMMessage+0xB20` byte and two coordinates derived from owner fields to underlying **message object virtual `+0x2C`**; conditional nonzero return triggers `0x473890` |
| **13..15** | `0x473543` | evaluates original font-height wrapper `0x9269F0`, multiplies by detail metric `+0xCB0`, updates embedded control `PEAMMessage+0xA0C+0x44`, calls `0x64F600` only when changed |

This is **not twelve independent action buttons**, nor a proven user-visible “reply,” “delete,” or “close” mapping. The separately invoked `+0x20 -> 0x4735E0` handler branches on the underlying message class's virtual `+0x0C` code and an event object's `+0x20` value, rejecting/control-routing specific ranges before message-object virtual calls; physical pointer event equivalence remains unproven.

## B. Escape is a source-proven parent event, not an unconditional fullscreen exit

`PEAMMessage` vtable **`+0x34 -> 0x473870`** checks input word `0x1B` (ASCII/virtual key Escape). Only for that code it pushes **`0x10`** to `0x6539F0`. The wrapper `0x6539F0` masks `0x10` to 16 bits, loads its owner/control `+0x64` and passes `(message=0x400, wParam=0x10, lParam=0)` into `0x659650`; the target `0x659650` is confirmed to call the **`PostMessageA`** import at `0x7BD2D8`.

**CONFIRMED:** Escape-code input to the original detail owner posts a `WM_USER (0x400)` message with code **16** to an owner window; the above detail event16 path also forwards code16 via the same source notification. **NOT YET CONFIRMED:** whether/when that receiver disposes the detail screen, what other callbacks it invokes, and whether restoring the inbox selection/scroll is delayed or immediate. A posting operation is not itself proof of a completed modal close or a direct return-to-inbox action. Next trace the destination window owner/WM_USER handler and `PExplodingDialog` stack removal, then validate source-visible return.

**Current reconstruction comparison (BOTH):** main and Codex `reconstruction/original_game_host.py` bind `root.bind("<Escape>", self.leave_fullscreen)`. Their `leave_fullscreen` toggles global `self._fullscreen` to false while an ordinary host screen is active; current Codex special-cases startup media, but **neither has a live `PEAMMessage` modal capable of delivering native event16**. This is a **confirmed absence of source-compatible context-specific Escape dispatch** for the original inbox detail; do not claim current code's Escape was observed opening/closing a currently nonexistent inbox, and do not infer Escape's original behavior on all other screens.

## C. Detail panel native geometry and stack layering

The row repeat-activation helper `0x471270` constructs `PEAMMessage` (0xD08-byte object via `0x472CD0`), clears bit `0x02` at original message field `+0x08`, then at `0x47134E..0x471360` calls original **`0x653320` layout helper** with size **`0x2C6 × 0x1A4 = 710 × 420`** and dynamic x/y from globals `0x8779C0` / `0x8779C4`. The source logic bounds/adjusts those origins rather than using an invariant center screen position. `0x471365..0x47136D` pushes the actual detail object, `0x8000` and argument1 to native stack-entry helper **`0x5EB540`**. This verifies a distinct original layered native detail UI with original layout/stack ownership, not an ordinary main-panel replacement or a guessed modern Tk dialog.

**Classification:** exact original instruction- and resource-address-level event/size/stack contract; **PARTIAL** end-to-end EAMail fidelity, because receiver/return/visual assets/fonts/button labels/message semantic field typing and multi-club original input observations are still UNKNOWN.

## Hand-off order (Codex implementation owner; no authorization for this audit-only worker)

1. Trace **`PostMessageA(WM_USER,16)` receiver** to prove actual Escape close/return sequencing and existing selected-message snapshot restoration, before implementing Escape mapping for EAMail detail.
2. Decode `PMessageRow` native physical acceptance/row control event 0 vs repeat activation and `PEAMMessage` event IDs/control destinations, button resources and text.
3. Preserve **710×420 native detail panel dimensions with original relative x/y source logic**, `PEAMMessage` lifecycle, scroll/text sizing semantics and all verified native flags; no generic HTML/ttk mailbox or fixed modern popup.
4. Compare main and current Codex ordinary in-game path on **more than one club mailbox** (Southport plus an independent club/state), then trace original Squad-tab 3/4/5 and NEXT input to real original-looking game progression.

Still **NO Windows 11 full playtest receipt**, and Gate 13 remains OPEN. Gates 14–17 / complete original-scope Windows 11 release remain incomplete.
