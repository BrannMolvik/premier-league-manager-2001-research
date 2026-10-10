# Recovery 449 — original Match+0x44 bit0x20 is set on a derived side-reversed LeagueMatch clone

_9 October 2026 KST. Independent Gate13 P0-D original-file fidelity audit continuing source-verified match-status producers from Recovery448. Research only: no game implementation/assets/saves, Codex edits, CI, original executable process launch, merge, gate closure or Windows 11 acceptance._

## Verified provenance and current owner

Read live main/CURRENT_STATE and `agent-runtime` before work: main at `337d03bba66462916c4d206fb8832fdb2abe2084`; worker `audit_only`, `implementation_allowed=false`, Codex owns gameplay/UI implementation. Current Codex branch at `0ae745d1b56f45cade460f03cd893849a2f53b45` includes a further source-font correction from `0188c82a988baa898bf657c372dbb4367ee2659a`, **not** NEXT click or EAMail integration.

Original private `/mnt/data/fm2001_private/footballmanager.exe`: 4,714,541 bytes, rechecked SHA256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Reproduce native disassembly with:
```
objdump -d -M intel --start-address=0x4A75FE --stop-address=0x4A76BE footballmanager.exe
objdump -d -M intel --start-address=0x4A7990 --stop-address=0x4A7B2C footballmanager.exe
objdump -d -M intel --start-address=0x512F20 --stop-address=0x513004 footballmanager.exe
objdump -d -M intel --start-address=0x5132E0 --stop-address=0x5133BF footballmanager.exe
objdump -d -M intel --start-address=0x5136E0 --stop-address=0x513723 footballmanager.exe
objdump -d -M intel --start-address=0x511370 --stop-address=0x51145C footballmanager.exe
```

## A. Source confirmation: the bit0x20 writer is a *paired Side-state reversal*, not an isolated flag setter

At native original **`0x512F20`**, after `or [Match+0x44],0x20` at **`0x512F2A..0x512F2D`**, original code performs a paired transformation between two distinct concrete **`Side`** participant object payloads `Match+0x14` and `Match+0x28` (Recovery448 verified RTTI `Side` vtable `0x7C4D50` for both).

The original **`0x512F80..0x512FFB`** writes these neutral fields:

| New field | Native source value | Proof addresses |
| --- | --- | --- |
| `+0x18` | previous `+0x2C` | `0x512F78..0x512F80` |
| `+0x1C` | previous `+0x30` | `0x512F83..0x512F98` (repeated equivalent source stores) |
| `+0x24` | previous `+0x38` | `0x512FD6..0x512FDD` |
| `+0x2C` | previous `+0x18` | `0x512F43,0x512FE8` |
| `+0x30` | previous `+0x1C` | `0x512F54,0x512FF4` |
| `+0x38` | previous `+0x24` | `0x512F6C,0x512FED` |
| `+0x20`, `+0x34` | previous opposite `+0x34`, `+0x20` respectively | `0x512F9B,0x512FE0` |
| `+0x22`, `+0x36` | previous opposite `+0x36`, `+0x22`, with bounded low-bit `xor/and` adjustments | `0x512FA3..0x512FD2`, `0x512FE4..0x512FFB` |

**Exact source classification:** a paired participant/Side state reversal **plus** marker bit0x20. The source modifies paired fields *within the existing Match object*; this is not evidence of reversing dates or incrementing fixtures.

## B. Independently found actual caller creates a new derived LeagueMatch and reverses THAT object

Within original source `0x4A75FE..0x4A767D`, a qualification chain tests event/match kinds and club conditions. On its qualified path, it:

1. allocates a **new `0x50`-byte object** at `0x4A760D..0x4A7619`, `esi`;
2. calls original **`0x4A7990`** at `0x4A762C` to **copy an existing Match/Event's fields into the new object**;
3. overwrites its derived vtable with concrete **`LeagueMatch` vft `0x7C4C24`** at `0x4A7633`, so the new object is a LeagueMatch and contains copied **Side** participant vtables at `+0x14,+0x28` as verified at `0x4A7A1C` and `0x4A7A89` inside `0x4A7990`;
4. **calls `0x512F20` on that NEW object** at `0x4A767B..0x4A767D` to reverse its participants and set `+0x44 bit0x20`.

`0x4A7990` copies the native Event/Match data up through `Match+0x4C`, installs initial Match vtable `0x7C4CE4`, and the caller then installs the final `LeagueMatch` vtable. The source Match object is not the target of the `0x512F20` invocation at this call site.

**Strong source conclusion:** at this specific results/competition branch, **bit0x20 is attached to a newly derived, participant-reversed LeagueMatch**. It is misleading to label bit0x20 a generic "played" bit or assume the source fixture is mutated in place by this caller. A reversal/derived-leg interpretation is **PROBABLE**, but the exact original football label (replay, second leg, venue reversal, fallback) **remains UNKNOWN** until the enclosing competition kind and data-specific branch are typed. Do not hardcode either high-level label.

## B2. Proven original calendar insertion of the derived reversed LeagueMatch

Following the actual `0x4A767D -> 0x512F20` reversal **further along the same original caller** yields the missing scheduled-event lifecycle:

- After `0x4A767D`, a qualified path continues through native match/competition and event-record processing; at `0x4A78A4..0x4A78B0` the original loads **current game date `0x9847FC`**, source base **`0x947AE0`** (equal to original `0x947AD8 +0x08`), computes **`current_date+1 - calendar_base`**, and passes the retained derived-match pointer **`EBX`** to the original **`0x615A60`** insertion routine on calendar family **`0x947AD8`**.
- This adds a source-original **relative requested slot** for the derived match, not an ad hoc virtual fixture on an unsourced screen. The insertion helper `0x615A60` may change the final relative slot under its native conflict handling `0x615890` (Recovery446).
- The complete source chain on the qualifying derived-object path is now **`0x4A760D` allocate 0x50 → `0x4A7990` copy source Match → `0x4A7633` install concrete LeagueMatch vtable → `0x4A767D` reverse participant Side fields/set bit0x20 → `0x4A78B0` insert into calendar 0x947AD8 for requested next-day slot**.
- The source conditional in `0x4A75C8..` and intervening participant/event state must still be retained. It would be incorrect to create a reversed match on *every* NEXT press or to guarantee that source conflict resolution leaves the fixture on the requested following date.

**Exact:** original allocation/clone/participant reversal/status mark/native calendar family and requested relative offset are now all instruction-verified. **Probable but NOT named:** this is part of a replay/second-leg/derived league match workflow; the precise original football reason is not source-closed. No live original Win11 input or multi-club fixture state was recorded.

## C. Other status-bit producer context and correctness consequence

Recovery448 separately identified `Match+0x44` constructor default **0**, bit0 writer `0x511370` and bit0x40 writer `0x514640`. Additional original inspection shows the bit0 writer `0x511370` is called by both `0x5132E0` and `0x5136E0`; its body invokes multiple underlying participant/competition helpers and conditional match hooks after setting bit0, including `0x5127A0` on one path. This substantiates *match processing* as the context, but not the exact caption/visible lifecycle of bit0.

The native NEXT selector `0x615C50` excludes bits0,0x20,0x40 for its ordinary caller arguments, and different source lifecycle functions use different masks. For implementation, **do not conflate the three flags or treat a newly derived participant-reversed match as the same event object**, and do not implement status masks by generic fixture flags without owning source rule/evidence. Compare dynamic event availability with actual original manager/competition context.

## D. Codex handoff, source boundaries and next audit

- Existing Codex source schedule and cup progression contain meaningful bounded fixture/leg models. This audit **does not** conclude the clean-room's cup progression is all missing or wrong; the original reverse-clone lifecycle must be compared at the precise dynamic NEXT/PResults boundary, not only by method names.
- **P0 original playability remains blocked:** ordinary native-look `NEXT/MATCH` input is not wired to actual source progression, EAMail not an integrated usable inbox, Squad selected 4/5 formation clicks still fail original view completeness. Codex remains exclusive owner; this audit has not modified its code.
- Next independent source step: trace the enclosing `0x4A75FE` event-kinds and clone scheduling insertions into calendar, then audit core EAMail data action semantics or original first-team/formation UI control against the current Codex HEAD. Source-check multiple clubs/managers; do not substitute a Windows GUI test with local disassembly.

**No original executable running, Windows11 GUI receipt, CI or gate closure. Gate13 earliest incomplete; Gates14–17 and verified original-scope Windows11 release incomplete.**
