# Gate 13: reproducible original Button@ease source-trace procedure

_Status: bounded inspection tool implemented, native state behavior unresolved.
Source identity and entry points below were established in prior first-hand
executable research; this document does not claim new disassembly._

## Why this is the current source-critical task

The port now has the canonical original PStartMenu and TeamSelect background
compositions, real Zurich font masks, recovered English STR/IDX command labels,
original 23-source-frame action atlases, hierarchy-source art loading, and
test-backed menu/team navigation. Those inputs are **not** sufficient to
assign frame indices to idle, hover, down/up, disabled or animate states or to
recreate original label alignment/color. Source pixels are not interaction
semantics.

The exact canonical original executable is the private authorized
`footballmanager.exe` with SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Its source archive is located by `research/ORIGINAL_SOURCE_LOCATOR.md`.
Do not use or commit a public/repacked alternative without proving identity.

## Repeatable initial evidence collection

`reconstruction/gate13_button_source_trace.py` is a bounded,
canonical-hash-gated PE32 i386 reader. It maps original virtual addresses to
file-backed sections and records exact bounded original instruction bytes
alongside raw, **unvalidated pointer-byte occurrence candidates**. Optional
Capstone linear disassembly is an analyst aid, not proof of xrefs or a complete
control-flow graph. It never changes original binaries.

Once container or local Windows byte execution works, extract only the
already-verified original executable to a *private* path, then run:

```text
python -m pip install "capstone>=5,<6"
python reconstruction/gate13_button_source_trace.py "<verified-private-footballmanager.exe>" --disassemble --output "<private-folder-outside-repository>/button-trace.json"
python -m unittest -v test_gate13_button_source_trace
```

If Capstone is unavailable, omit `--disassemble` and collect mapped exact
byte windows and raw pointer candidates first. The script refuses an output
path under the Git repository to avoid inadvertently publishing executable
content. The opt-in test validates the actual source mapping when
`FM2001_ORIGINAL_EXE` points at the canonical private source, but ordinary
hosted CI uses a synthetic PE fixture.

Already recovered code anchors (bounded inspection windows, **not** claimed
whole function boundaries):

| VA | Prior proven role |
| --- | --- |
| `0x4C1BA0` | PStartMenu primary action setup |
| `0x4C3770` | PStartMenu event dispatch |
| `0x4D885F` | TeamSelect Back/Start setup |
| `0x5F4500` | Shared original `button_type_1.444` frame geometry initializer |
| `0x652FD0` | Shared `Button@ease_2001` action/control initializer |
| `0x657650` | Original EAUK bitmap font loader |

Previously identified address-value candidates that can help narrow further
xref work: menu atlas handle `0x946590`, button-font global
`0x9197E0`, PStartMenu vtable `0x7C64E0`, and TeamSelect vtable
`0x7C7650`. A matching raw 4-byte pattern alone is **never** a proven
instruction, actual global load, vtable slot, dynamic control call, or
data-flow edge.

## Manual adjudication after collecting bytes

1. Use the canonical Ghidra analysis (or a second independently verified
   static x86 disassembler) to find callers/callees and RTTI/vtable dispatch
   for `Button@ease_2001` and the control setup at `0x652FD0`.
2. Follow constructor assignments to the shared atlas, frame sizes and
   initial state. Trace actual draw/update and mouse enter/leave/down/up
   paths, including any disabling conditions. Confirm which source atlas row
   each state chooses and whether animation uses an offset, timer or an
   additional draw path.
3. Follow text-glyph rendering from shared font handle `0x9197E0`.
   Recover origin, baseline, pair-kerning application, font color, disabled
   treatment, clipping and control-size alignment from the actual caller
   and callee, not from a modern typography heuristic.
4. Repeat relevant behavior checks for TeamSelect's
   `choice_start_anim.444` and hierarchy `choice_league_but_*.444`.
   Record separately what is common inherited button logic and what is
   screen-specific.
5. Persist only the minimal source-backed instruction ranges and their
   evidence/recovery addresses in a dedicated research trace; add exact
   original-byte regression tests if available. Connect proven native
   transitions/alignment to the existing original first-screen presenter.
   Retain unknown states unimplemented until evidence closes them.

The private report itself is a scratch artifact; the final durable repository
research should contain concise recovered facts, addresses, hashes, test
results and explicit remaining boundaries, not a proprietary executable
dump. Do not promote Gate 13 or proceed to Gate 14 before its full audit.

## Current execution boundary

At the current recovery checkpoint, both simple shell and the alternate
visible Python execution mechanism returned `ClientError`. Therefore no
new first-hand executable bytes, full original navigation timing, hover-state
index, label baseline, or opt-in original-byte pass is claimed by this
helper's synthetic CI. It exists to make the **next actual executable
inspection** reproducible once execution access returns.

## Additional bounded source leads for exact Button state recovery

`reconstruction/gate13_button_vtable_xref_candidates.py` adds two strictly
candidate-only inspection stages to the exact-hash-gated original PE32
inspector. Its seed addresses are the already established **PStartMenu and
TeamSelect class** vtables; these are **not** asserted to be the
`Button@ease_2001` shared vtable. The first stage reads at most 12 raw
file-backed uint32 slots per class vtable, identifies pointers mapping to
PE `.text`, and stops at the section boundary rather than interpreting
adjacent data as additional entries. No slot meanings are inferred.

The second stage uses optional Capstone 5 to scan original `.text` for
candidate **direct** near CALL/JMP branch destinations matching the previously
established code entry points and any plausible class-vtable code pointers.
This is a *linear-disassembly byte lead only*. Embedded source data,
misaligned instructions, missed indirect/vtable calls, cross-function
fall-through, and unreachable branches can invalidate results. Only
independent original CFG/manual control/data-flow analysis can promote a
candidate to a native button-state or font-layout fact.

With the same private, exact-SHA-verified original executable:

```text
python reconstruction/gate13_button_source_trace.py "<verified-private-footballmanager.exe>" --inspect-class-vtable-candidates --scan-direct-control-transfer-candidates --output "<private-folder-outside-repository>/button-trace-expanded.json"
```

The `--scan-direct-control-transfer-candidates` flag also enables the
bounded class-vtable stage automatically. The existing `--disassemble`
flag may independently include linear instruction windows. Keep all raw
instruction reports **outside the tracked repository**. Cross-check the
plausible pointers with manual Ghidra RTTI/vtable inheritance evidence,
follow candidate draw/hover/update paths and recover actual atlas row
changes and Zurich baseline/color before changing the user-facing
renderer.

Synthetic host CI installs only Capstone and checks the bounded vtable
parsing, edge candidate classification, true direct near CALL/JMP test
fixtures, and source classification boundaries. No native original
Button@ease state mapping is claimed by these synthetic tests.
