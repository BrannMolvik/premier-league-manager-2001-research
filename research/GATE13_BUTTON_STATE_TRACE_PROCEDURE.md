# Gate 13: reproducible original Button@ease source-trace procedure

_Status: canonical private run completed 1 October 2026 KST. Native grouping,
hover direction and Zurich caption placement are recovered; mask-4's
user-facing semantic name remains open._

## Completed canonical run - 1 October 2026 KST

Windows-local execution cleared the earlier infrastructure blocker. The
canonical ZIP and executable hashes passed, Capstone 5.0.9 ran from private
storage, the TeamSelect `0x81EC10` / `0x7C7650` canary passed, and constructor
writes corroborated the sole `Button@ease_2001` candidate: TypeDescriptor
`0x81AD90`, COL `0x7E0B90`, CHD `0x7E0B80`, vftable `0x7BF4CC`.

Native group/frame selection, pointer-inside animation direction, Zurich line
origins and native color values are durable in
`research/GATE13_BUTTON_NATIVE_TRACE.md` and regression code. The exact ten
first-screen resources are provenance-imported and the readiness/asset-policy
guards pass. The rest of this file preserves the reproducible collection
procedure and historical caution boundaries.

## Why this is the current source-critical task

The port has the canonical original PStartMenu and TeamSelect background
compositions, real Zurich font masks, recovered English STR/IDX command labels,
original 23-source-frame action atlases, hierarchy-source art loading, and
test-backed menu/team navigation. The completed executable trace now binds the
three native frame groups and PStartMenu caption placement. Source pixels alone
were not treated as interaction semantics; every promoted mapping is tied to
the original Button/Zurich code path.

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

## Newly consolidated PRIOR firsthand Button input and state path

This section uses **pre-existing real-original-executable findings** in
`research/EXECUTABLE_ANALYSIS.md` ("TeamSelect start-button dispatch is
RNG-clean") and the concrete source-code anchors already tied to the
canonical executable SHA. It is a closer existing-evidence starting point,
**not** a fresh disassembly run and **not** proof of any atlas source-frame
index, hover timing, caption origin or common Button vtable layout.

The earlier trace already proved that TeamSelect's embedded control at
`+0x3690` is RTTI `Button@ease_2001`, has event `+0x20=0x2A`
and owner `+0x24=TeamSelect` (assigned by `0x64F3C0`). The actual
existing documented click path is:

```text
Button@ease_2001 input 0x64F7A0
  -> owner virtual +0x0C = TeamSelect 0x5CFA50 (returns 1)
  -> optional UI/sound callback (0x984810 -> 0x5DBFC0)
  -> Button state update (0x64F710 is a prior verified state helper)
  -> owner virtual +0x10 = TeamSelect event handler 0x4DA480
  -> reads [button+0x20] == 0x2A
  -> 0x4DA4A5 calls 0x4C41C0 (new-game construction)
```

The generic Button setup chain
`0x652FD0 -> 0x651E30 -> 0x651BA0 -> 0x64F380`
passes a NULL optional callback pointer for this specific
TeamSelect Start control at `+0x28`, eliminating that optional
notification on its normal click path. The existing control-state
findings independently name `0x64F3E0` as a *state-bit* toggle,
`0x64F710/0x64F750` as state-bit helpers,
`0x64F510` as the state-enable forwarding virtual and
`0x64F520` as the refresh forwarding virtual. The `+0x1C`
control callback mask distinguishes optional callback selection.
For the proven control-refresh branch in prior research, argument
`1` to `0x64F3E0` requests *state bit 1*; **bit 1 MUST NOT
be interpreted as original animation atlas source frame 1.**

The updated private trace helper now also captures bounded windows
at `0x64F380`, `0x64F3C0`, `0x64F3E0`,
`0x64F510`, `0x64F520`, `0x64F710`,
`0x64F750`, `0x64F7A0`, `0x4DA480`
and `0x5CFA50`. The candidate direct-call scan includes the
most relevant of those endpoints. This is a narrower source-backed
route than searching arbitrary class-vtable raw pointer bytes.

**First original-byte question once execution returns:** identify the
shared `Button@ease_2001` virtual **draw/update** entry points and
which struct field references actual per-frame atlas index.
Establish the data-flow from the verified state-bit updates through
those true draw/update methods to the 23 source atlas rows. Then
independently recover the Zurich font glyph render x/y/baseline,
color and clipping. Do not infer draw behavior or native text
placement from the known TeamSelect owner-event path alone.

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

## Superseded recovery execution boundary

At the earlier recovery checkpoint, both simple shell and the alternate
visible Python execution mechanism returned `ClientError`. Therefore no
new first-hand executable bytes, full original navigation timing, hover-state
index, label baseline, or opt-in original-byte pass is claimed by this
helper's synthetic CI. This blocker was cleared by the completed canonical
run recorded above; this paragraph remains as historical recovery context.

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

## Candidate MSVC RTTI path to the actual shared Button virtual table

Previous firsthand analysis already identifies the embedded TeamSelect
`Button@ease_2001` class and confirms that this executable has 32-bit
MSVC type descriptors, Complete Object Locators (COL), class hierarchy
descriptors (CHD) and vftables (for example TeamSelect's type descriptor
`0x81EC10` and known class vftable `0x7C7650`). These findings
justify a narrower **source-analysis method**, not a guess at the
actual Button vftable address or virtual method numbering.

`reconstruction/gate13_button_rtti_candidates.py` searches the exact
hash-gated canonical PE32 image's *file-backed non-code sections* for
the decorated `Button@ease_2001` type name, candidate 8-byte-prefix
TypeDescriptors, aligned x86 COL references with signature zero,
readable CHD/base array pointers, and potential `vftable[-1]`
COL pointers with executable-section-valued first virtual slots.
The bounded report retains every plausible distinct vftable
candidate; multiple inheritance/subobject offset is not discarded.
These are **byte-pattern candidates** only, not dynamically validated
RTTI ownership or virtual draw/update roles. No source frame
assignment, original caption placement or timeline is recovered
by the scanner.

After re-extracting and SHA-verifying only the canonical original
executable into a PRIVATE location, run:

```text
python reconstruction/gate13_button_source_trace.py "<verified-private-original-footballmanager.exe>" --inspect-button-rtti-candidates --inspect-class-vtable-candidates --scan-direct-control-transfer-candidates --output "<private-folder-outside-repository>/button-rtti-and-input-candidates.json"
```

`--inspect-button-rtti-candidates` adds potentially relevant
indirect-method *entry addresses* to the optional near-direct
CALL/JMP candidate-target scan. Those extra code pointers are explicitly
`UNVERIFIED`; the linear scan cannot resolve **indirect** virtual
calls or prove CFG reachability. Compare the resulting candidate COL,
CHD and table addresses with actual Ghidra MSVC RTTI and constructor
vftable writes. Independently establish the shared Button draw,
input and update virtual slots before following the already documented
real input/state-bit path `0x64F7A0`,
`0x64F3E0`, `0x64F710/0x64F750` to the 23 atlas
source-frame state transitions. Confirm Zurich glyph layout/color
through the true original render path separately.

The synthetic mini-PE tests verify field offsets, file-backed section
checks, null pointers, corrupted RTTI/CHD, alignment, multiple candidate
subobjects and explicit candidate-only classifications; hosted CI does
**not** prove that this decorated spelling exists in the private
licensed original or that any candidate is a genuine original
Button vftable. If the actual canonical original yields zero candidates,
inspect its real RTTI decorated name and inheritance encoding in Ghidra
instead of silently inventing a different class address.

## Known-positive calibration: do not trust a naked Button RTTI hit

The prior FIRSTHAND canonical original executable research in
`research/EXECUTABLE_ANALYSIS.md` establishes two exact independent
reference points for `PMain@TeamSelect`:

- MSVC decorated TypeDescriptor `.?AVPMain@TeamSelect@@`
  at **`0x81EC10`**;
- its native class vftable at **`0x7C7650`**.

The newly integrated RTTI candidate report now also runs the **exact same
pattern parser** against this *already verified* reference. It explicitly
records whether the resulting `TypeDescriptor -> COL -> CHD -> vftable`
candidate chain recovers the known pair. The private opt-in canonical original
source test now requires that check to pass. A synthetic fixture independently
confirms positive and wrong-pair/altered-CHD rejection. The default licensed
original is never bundled in GitHub Actions, so a hosted synthetic pass
**does not** assert that the known-positive calibration succeeded against
the actual original.

If the original executable's known-positive reference is not recovered,
treat all other automatically proposed RTTI/vftable relationships as
**unvalidated and unsuitable for UI implementation**. Inspect the original
RTTI representation, PE section mapping and source code in Ghidra before
continuing. Even a passing known-positive calibration only validates the
pattern against one independently proven class; each new Button vftable
candidate still requires constructor/vftable-write/CFG adjudication and
separate authentic animation-frame/font positioning proof.

## Enforced CLI known-positive reference (not just a report flag)

The real-source `--inspect-button-rtti-candidates` CLI now **fails closed
before writing an output report** if the MSVC RTTI locator cannot
recover both independently previously proven original TeamSelect
anchors: decorated `.?AVPMain@TeamSelect@@` TypeDescriptor at
`0x81EC10` and vftable `0x7C7650`. It also refuses
missing, malformed or mismatched calibration metadata. Previously the
opt-in unit test required this canary, but the CLI itself still
saved and could cross-reference *uncalibrated* Button candidates;
that unsafe gap has been closed.

A failure does **not** mean the original game lacks the class; it
means the current RTTI pattern parser has not earned confidence
against a known firsthand control. Preserve the original executable,
inspect the actual RTTI structure/descriptor and compiler-specific
layout in Ghidra, and correct the parser or decorated spelling
using original-byte evidence. Until that happens, rerun the plain
original-byte window trace without `--inspect-button-rtti-candidates`
and manually adjudicate its evidence instead of bypassing the canary.

Synthetic hosted tests exercise both positive and negative CLI
paths and assert that a negative canary creates **no private report**.
Only a later exact-hash original executable run can prove that the
positive-control match actually succeeds on original bytes.
