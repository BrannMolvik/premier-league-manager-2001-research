# Recovery 444 — PResults is a native event-progress owner, not merely static results artwork

_9 October 2026 KST; original-file fidelity sweep P0-D. **AUDIT ONLY**, source analysis against hash-verified authorized original. No game implementation/asset/save/schema change, Codex branch write, CI run, original executable runtime launch or Windows 11 playtest._

## Source and checkpoint

- Live starting main `7d61fdad0cb300b94561a0178636ce288539b309`; `research/CURRENT_STATE.md` makes ordinary original NEXT/MATCH, PMenu, EAMail and first-team function audit primary. Runtime requires `worker_role=audit_only`, `implementation_allowed=false`. Codex implementation branch head `8702eded049643220bf4b590d8d45c2197cfd42a` is unchanged.
- Privately rehashed `/mnt/data/fm2001_private/footballmanager.exe` to canonical **SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Original byte disassembly can be reproduced with `objdump -d -M intel --start-address=0x4A7190 --stop-address=0x4A7210 footballmanager.exe`, `0x4A83F0..0x4A8520`, `0x4A8260..0x4A8280`, `0x6168C0..0x61698B`, `0x431F70..0x432190`. All raw source output remains outside Git.
- This report distinguishes **the original `PResults` class (RTTI final vft `0x7C4B84`)** from a speculative static final-score-only “Results” screen; it has a real original event-progress display while scheduled work is processed. The source proves its progress role, not its complete on-screen behavior, class caption or match score/result field semantics.

## A. Concrete progress counters and exact native drawing update

**CONFIRMED from original `PResults` instruction sequence:**

1. Original `0x4A83F0` initializes the results-processing pass with **`mov [edi+0x64],0` at `0x4A83FB`**, resets neutral global index `0x8755D4=0`, and loops original `0x615D10` candidate lookup over the `0x8755E4` user-context family.
2. After bounded candidate and source clock calculations at `0x4A84EA`, **`0x4A84E9..0x4A84F4` calls `0x4A7210(upper_date)`, adds the already accumulated `PResults+0x64` value, and stores the sum at `PResults+0x68`**. The total therefore depends on original event candidate counting and the already accumulated work. This is **NOT** proof that the denominator is always “number of matches,” even if some processed objects are matches.
3. During qualified original scheduled-event processing at **`0x616914..0x616925`** and **`0x616966..0x616978`**, the code obtains the live original `PResults` owner via global **`0x876860`**, calls **`PResults::0x4A71F0`**, and returns to the event-list walk. Original `0x4A8260` calls the event processing helper **`0x6168C0`** for two calendar/event list containers `0x947AD8` and `0x947AF0`.
4. `PResults::0x4A71F0` performs **`inc dword [ecx+0x64]`**, calls `PResults::0x4A7190` and queues an original UI refresh through window owner `0x877960` / `0x5329D0`. This is **real progress driven by actual traversed original scheduled work**, not a timer-driven fake animation.
5. Original `0x4A7190` checks total **`PResults+0x68`** for zero. If zero, progress width is zero. Otherwise, for the ordinary non-overflow positive counter/total domain, its signed divide/multiply sequence computes **`native_progress_width = 10 * trunc((80 * processed_count) / total_count)`**, where `processed_count=PResults+0x64`, `total_count=PResults+0x68`. It then sets:
   - `PResults+0x264 = native_progress_width` (one embedded control field);
   - `PResults+0x280 = PResults+0x278 + native_progress_width` (another child control's bound);
   - `PResults+0x25C=0`, followed by `0x64F600(PResults+0x270)` to update the actual original visual control.
   The native width is thus quantized into multiples of 10 over a nominal 800-pixel extent, not an inferred CSS-style percentage or an arbitrary time duration.
6. Original `0x4A83D0` refreshes the PResults UI at `0x4A7280`, checks the two event collections via `0x4A8260`, then calls `0x4A8070`; `0x4A83F0` advances date **`0x9847FC`** inside its own bounded original branch at `0x4A84F7..` before subsequent work. Date changes and progress ticks belong to the source simulation lifecycle, not an independent GUI-only ticker.

**Classification: EXACT source instruction-level progress counter, per-event producer calls, zero guard, arithmetic, retained owner, and GUI update destinations; PARTIAL game-state semantics and visual/timing fidelity.** A modern implementation should never display a fabricated progress bar driven only by wall-clock time nor assume that each tick means a finished 3D match.

## B. Recovery443 negative clickable-strip result remains binding

This audit searched the original PE's direct code references to global **`0x876860`**. Independent additional source accesses were found at `0x61691B` and `0x61696D`, both **real progress callbacks `0x4A71F0`**; constructor `0x4A70BA` installs the global and destructor `0x4A7121` clears it. These do **not** call `PResults::0x4A87E0` to return to PMenu. The proven `0x4A87E0` virtual `+0x10` still constructs PMenu for non-null argument; **its native accepted event producer remains UNKNOWN**.

The `waiting_back_2.444` original bottom bitmap still has original control ID 0 and **`0x64F7A0` skips parent action callbacks for ID 0**. In particular, neither the event-progress callbacks nor an image's existence supports “click bottom 800×87 strip to return.” Do not implement that wrong route without new source proof.

## C. Reconstruction comparison and Codex handoff

- Main and Codex have no original `PResults` 800×600 panel wired to the normal management `NEXT` click. Codex `original_management_next.py` covers source graphics/caption and hover, **not** source NEXT progression or source `PResults` counter ownership. A generic simulator/standalone test interface does not reproduce native `PResults`.
- **P0 implementation owner contract (Codex):** preserve original conditional `PBg::0x432690` control3 → `0x432190` game advancement; when the original source condition creates `PResults`, show source-backed 800×600 panel and faithfully project `processed_count`, `total_count`, ten-pixel quantization and source event-driven UI updates. Respect original zero-total/partial progress and wait until lifecycle return is source-proven. Avoid invented clickable waiting art.
- **Next audit work:** (1) determine original message/event producer invoking `PResults+0x10 -> 0x4A87E0` with nonzero argument; (2) type `0x4A7210` scheduled item class/flags and its actual counter cardinality vs `0x6168C0` event producer; (3) recover output/transition after `0x4A83F0` and `PResults` owner lifecycle, original resource/frame and all input timing; (4) test multiple clubs and fixture states in actual Windows original-compatible validation. Preserve original BEHAVIOR FIRST and the modernization freeze.

No original game process execution, Windows acceptance or tests/CI. **Gate 13 remains OPEN, Gates 14–17 and the verified full original-country Windows 11 release incomplete.**
