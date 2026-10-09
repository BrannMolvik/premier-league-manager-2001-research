# Recovery 442 — original PBg NEXT press gates, competition/date branches and original return destinations

_9 October 2026 KST. Source-first, audit-only continuation from Recovery441 main `4c0cbcc01bfb5339a0988f144501722a5600e88d`. This is the P0-D original normal management NEXT/MATCH path, **not** an implementation of a new match engine. Codex branch read-only: `8702eded049643220bf4b590d8d45c2197cfd42a`._

## Authenticity and reproducibility

A new `sha256sum` on the independently recovered private original `footballmanager.exe` yielded **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Disassembly source is the hash-gated original PE at `/mnt/data/fm2001_private/footballmanager.exe`. Bounded original x86 trace for the entire first-class progression method was generated privately with:

```text
objdump -d -M intel --start-address=0x432190 --stop-address=0x43268a footballmanager.exe
objdump -d -M intel --start-address=0x430992 --stop-address=0x4309c9 footballmanager.exe
objdump -d -M intel --start-address=0x432690 --stop-address=0x432707 footballmanager.exe
objdump -d -M intel --start-address=0x5d39c0 --stop-address=0x5d3a10 footballmanager.exe
objdump -d -M intel --start-address=0x64f7a0 --stop-address=0x64f85a footballmanager.exe
```

Only summarized source evidence is added to Git. No proprietary executable, ZIP, raw disassembly dump, bitmap or serialized original data is committed.

## A. Native physical-input acceptance and actual PBg owner call

**Reconfirmed original call chain:**

1. `PBg::0x430992..0x4309C9` constructs the child at **`PBg+0x524`**, registers `parent=PBg` and **control ID3**, then calls the original drawable/control initializer `0x5D3900` with wrapper `0x943A50`. Native graphic `back_5.444` is verified and source screen rectangle is **`(700,0,100,95)`** (cf. `reconstruction/original_management_next.py` and earlier direct resource evidence).
2. The original `0x5D39C0` pointer-control path updates its control's visual flag state, delegates press acceptance to **`0x64F7A0`**, updates the control again and schedules parent/window work via **`0x5329D0`**. The accepted input is **not** just any click in the NEXT rectangle.
3. `0x64F7A0` first enforces the source bitmap-control enabled flag **bit 0x02** at **`0x64F7A5..0x64F7AF`** and rejects source flag **0x10** at `0x64F7B5..0x64F7BA`. It then uses the owning parent virtual **`+0x0C`** as an optional acceptance predicate `0x64F7D3..0x64F7DF` and, if accepted, calls the parent virtual **`+0x10`** at `0x64F815..0x64F81C`.
4. **`PBg` final vtable `0x7BEE8C`** has **`+0x0C -> 0x42DE00`** constant-true and **`+0x10 -> 0x432690`**, which reads the actual child ID at **`+0x20`**. For ID3 at **`0x4326A4`** it calls **`0x432190(0)`**. ID1 routes directly to the original inbox, and ID2 opens the real PMenu (Recovery441).

**Classification:** CONFIRMED original gated control acceptance and callback owner. The exact native state/pressed/hover transitions and runtime gating for each simulation state still require a live source-valid interaction; the bitmap alone must not be converted into unconditional calendar advance.

## B. Independent full-body branch audit of original `PBg::0x432190`

The routine spans **`0x432190..0x432687`** and has multiple materially different work and return branches. This is a control-flow result, not a high-level guess about all football rules.

| Original instruction range | Observed source condition and operation | Fidelity boundary |
| --- | --- | --- |
| `0x432196..0x4321E1` | reads original date-like global **`0x9847FC`**, both **`0x8755D4/0x8755E4`**, control **`PBg+0x524`**, sends resulting neutral data via child virtual **`+0x70`** with argument1 | Proves a control-state refresh **before** competition/calendar branches; not proof how user-facing NEXT/MATCH caption changes |
| `0x4321E4..0x432241` | loads current user via **`0x4139D0`**, then source user **`+0x5B4`**, queries via **`0x4079D0 -> 0x615D10`**, and checks a calculated next-date against another derived candidate via **`0x510A20`**. Stores comparison flag (EBX) only if both object and date checks match | Proves real schedule gating, not an unconditional one-day change. Candidate class and exact calendar semantics require independent field typing |
| `0x432241..0x4322ED` | on matching candidate, calls its virtual **`+0x18`**, source **`0x4F3DC0`** and **`0x407FE0`**; additional `0x875680` check governs `0x404A80`, `0x404A70`, `0x409C90`, `0x405A20` sequence | Conditional original match/competition preparation and gameplay activity. Do NOT equate these addresses with completed native 3D match visualization |
| `0x4322ED..0x432340` | branches on returned pointer/byte flags, and on **`[0x8755D4]+1`** compared with **`0x8755E4`**; on one path prepares **state flag2** at `0x432333`, another enters source event handling at `0x432340`, another invokes **`0x431F70`** at `0x4324FE` | Proves conditional progress cases rather than a single always-advance route; branch context meanings still neutral |
| `0x432340..0x4323E5` | branches through original **`0x4056F0`**, nested virtual **`+0x24`** tests, **`0x4F4070, 0x4F8BD0, 0x4F8FF0`** and finally, in one case, calls user setter **`0x42C6C0(3)`** and window-stack helper **`0x532920`** | A real source event/state transition; integer3 is a caller argument, not yet a named `MATCH_COMPLETE` state |
| `0x4323E5..0x4324B9` | source branch compares neutral condition, uses original string/record bytes and **`0x450990`** in one case, or original **`0x407F40`**, **`0x407410`** and source-backed window-state checks in the other | Main match/no-match user-visible meaning not yet fully typed, no invented date or league labels |
| **`0x4324B9..0x4324F7`** | opens original **panel ID `0xCE`** via **`0x482BF0`**, places it through **`0x5ED2A0`**, and in the shared continuation calls original user state setter **`0x42C6C0(2)`** | CONFIRMED **return-to-Squad panel route** reachable from progression routine; source flag2 not a fabricated modern enum |
| `0x432505..0x432554` | formats the global `0x9847FC` using **`0x64CCD0,0x64CE30`**, calls current-user UI update **`0x413AC0`**, then checks original global `0x875680`, user predicate **`0x4290F0`**, and **`0x516010`** | Date/UI repaint and post-progress state checks are part of the original function; do not skip as “presentation only” |
| **`0x4325DF`** | clears original global **`0x875614`** and invokes original **`PStartMenu` constructor `0x4C3280`**, returning from this routine | CONFIRMED **start-menu path under a distinct guarded condition** (among preceding predicates and `0x8755E4 <= 1`) |
| **`0x4325F7..0x43261F`** | branches on earlier byte flags; in one case sets **`0x8755D4=0`**, then continues to reconstruct original management shell `0x4C2FB0` | CONFIRMED original position reset + shell recreation, not always a match or Squad transition |
| **`0x43261F..0x43267D`** | if local state==2, computes signed **`(0x8755D4+1) modulo 0x8755E4`** by `idiv`, storing remainder back in **`0x8755D4`**, then checks/destroys prior PMenu stack owner and calls **`0x4C2FB0`** | EXACT arithmetic and shell lifecycle at those VAs; not yet a proven “day count” or “round count” higher-level name |

**Key correctness warning:** The modulo divisor **`0x8755E4`** and date global `0x9847FC` are distinct. The `0x8755D4` counter update is source-real and **must not** be represented as unconditional date increment in a clean-room NEXT implementation. The original may also enter PStartMenu rather than remain in management. Gate13 acceptance should exercise these different source branches with controlled fixture/club states.

## C. Reconstructed current main/Codex outcomes and concrete regression

- `main` on GitHub lacks original NEXT button dispatch in its normal `reconstruction/original_game_host.py::on_click`.
- `codex/gate13-windows-playability-recovery` at `8702eded049643220bf4b590d8d45c2197cfd42a` includes the source bitmap/caption `reconstruction/original_management_next.py`, and hover-state bits via `native_next_at_point`, but **normal `on_click` does not perform the original source PBg action ID3**. Neither branch has a normal native-look screen path that establishes the original conditional `0x432190` producer and its several possible game/UI outcomes.
- The existence of independent modern/gameplay advance methods and any developer-mode match visualizer does **not** close original management usability. Likewise a correct MATCH caption does not imply true progression.
- **Severity P0, CONFIRMED missing original navigable control path in both current implementations.** Qualify source press control flags and original route semantics *before* invoking a modeled transition; preserve the PBg action1 direct inbox, action2 PMenu and action3 NEXT differences. Do not merge three into one management click handler.
- Confirm source cases across Southport and another independent club/competition snapshot. No real Windows 11 acceptance screenshot, timing, video/sound, or original game process was produced in this audit; original data-specific predicate truth values are not yet measured.

## D. Next exact original-file questions for the implementation owner

1. Recover object/class and producer meanings for **`0x8755D4/0x8755E4/0x875680`**, user **`+0x5B4`**, `0x4079D0/0x615D10/0x510A20` candidate and `0x407FE0` response.
2. Follow `0x432190` through call tree `0x4F3DC0` / `0x407F40` / `0x404A70` / `0x409C90` and panel `0x431F70` to tie actual original match, results, calendar and progression states to source labels.
3. Source-qualify `PBg+0x524` physical pointer down/up/disabled semantics and `0x5329D0` transitions; then connect normal native-look NEXT click through those gates to verified functionality.
4. Preserve context-sensitive direct EAMail, PMenu, Squad and PStartMenu entry/return; add native button click-path tests across two actual clubs, original data invariants, realistic match/no-match fixture conditions, and qualified Win11 visual/interaction receipts.
5. Preserve Codex's exclusive game implementation branch. This audit worker writes only research and ledger; no CI or original asset staging.

**Gate 13 is OPEN; Gates 14–17 and verified full original-scope Windows 11 release remain incomplete.**
